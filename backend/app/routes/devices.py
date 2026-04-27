"""
设备管理路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.models.device import Device, DeviceType, DeviceStatus, ConnectionType, DeviceDataRecord
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.services.auth import get_current_user, require_role
from app.services.device_service import DeviceService

router = APIRouter()

@router.get("/", summary="获取设备列表")
async def get_devices(
    device_type: Optional[DeviceType] = None,
    status: Optional[DeviceStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取设备列表"""
    query = db.query(Device)
    
    # 根据角色过滤
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient:
            query = query.filter(Device.patient_id == patient.id)
        else:
            return {"devices": [], "total": 0}
    
    # 按类型过滤
    if device_type:
        query = query.filter(Device.device_type == device_type)
    
    # 按状态过滤
    if status:
        query = query.filter(Device.status == status)
    
    total = query.count()
    devices = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "devices": [
            {
                "id": d.id,
                "device_sn": d.device_sn,
                "device_name": d.device_name,
                "device_type": d.device_type.value,
                "brand": d.brand,
                "model": d.model,
                "connection_type": d.connection_type.value,
                "status": d.status.value,
                "last_online": d.last_online,
                "patient_id": d.patient_id,
            }
            for d in devices
        ]
    }

@router.get("/{device_id}", summary="获取设备详情")
async def get_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取设备详情"""
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 权限检查
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or device.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="无权查看此设备")
    
    return {
        "id": device.id,
        "device_sn": device.device_sn,
        "device_name": device.device_name,
        "device_type": device.device_type.value,
        "brand": device.brand,
        "model": device.model,
        "connection_type": device.connection_type.value,
        "connection_config": device.connection_config,
        "status": device.status.value,
        "last_online": device.last_online,
        "patient_id": device.patient_id,
        "capabilities": device.capabilities,
        "firmware_version": device.firmware_version,
        "created_at": device.created_at,
    }

@router.post("/register", summary="注册新设备")
async def register_device(
    device_sn: str,
    device_name: str,
    device_type: DeviceType,
    connection_type: ConnectionType,
    connection_config: Dict[str, Any],
    patient_id: Optional[int] = None,
    brand: Optional[str] = None,
    model: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN]))
):
    """注册新设备"""
    service = DeviceService(db)
    
    try:
        device = await service.register_device(
            device_sn=device_sn,
            device_name=device_name,
            device_type=device_type,
            connection_type=connection_type,
            connection_config=connection_config,
            patient_id=patient_id,
            brand=brand,
            model=model
        )
        
        return {
            "message": "设备注册成功",
            "device_id": device.id,
            "device_sn": device.device_sn
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{device_id}/connect", summary="连接设备")
async def connect_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """连接设备"""
    service = DeviceService(db)
    
    try:
        success = await service.connect_device(device_id)
        return {
            "message": "设备连接成功" if success else "设备连接失败",
            "connected": success
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{device_id}/collect", summary="采集设备数据")
async def collect_device_data(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从设备采集数据"""
    service = DeviceService(db)
    
    try:
        data = await service.collect_data(device_id)
        if data:
            return {
                "message": "数据采集成功",
                "data": data
            }
        else:
            return {
                "message": "无法获取数据",
                "data": None
            }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{device_id}/command", summary="发送设备命令")
async def send_device_command(
    device_id: int,
    command: str,
    params: Dict[str, Any] = {},
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """向设备发送命令"""
    service = DeviceService(db)
    
    try:
        success = await service.send_command(device_id, command, params)
        return {
            "message": "命令发送成功" if success else "命令发送失败",
            "success": success
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{device_id}/history", summary="获取设备数据历史")
async def get_device_history(
    device_id: int,
    days: int = Query(7, ge=1, le=365),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取设备数据历史"""
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 权限检查
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or device.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="无权查看此设备")
    
    service = DeviceService(db)
    start_date = datetime.now() - timedelta(days=days)
    records = service.get_device_data_history(device_id, start_date=start_date, limit=limit)
    
    return {
        "device_id": device_id,
        "total": len(records),
        "records": [
            {
                "id": r.id,
                "data_type": r.data_type,
                "parsed_data": r.parsed_data,
                "quality": r.quality,
                "measured_at": r.measured_at,
            }
            for r in records
        ]
    }

@router.get("/patient/{patient_id}", summary="获取患者的所有设备")
async def get_patient_devices(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取患者的所有设备"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    # 权限检查
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此信息")
    
    service = DeviceService(db)
    devices = service.get_patient_devices(patient_id)
    
    return {
        "patient_id": patient_id,
        "devices": [
            {
                "id": d.id,
                "device_sn": d.device_sn,
                "device_name": d.device_name,
                "device_type": d.device_type.value,
                "brand": d.brand,
                "model": d.model,
                "status": d.status.value,
                "last_online": d.last_online,
            }
            for d in devices
        ]
    }

@router.post("/patient/{patient_id}/sync", summary="同步患者所有设备数据")
async def sync_patient_devices(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """同步患者所有设备数据"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    # 权限检查
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此设备")
    
    service = DeviceService(db)
    results = await service.sync_all_devices(patient_id)
    
    return {
        "message": "同步完成",
        "results": results
    }

@router.get("/types/supported", summary="获取支持的设备类型")
async def get_supported_device_types():
    """获取支持的设备类型"""
    from app.services.device_parser import DeviceParserFactory
    
    return {
        "device_types": [
            {"value": dt.value, "label": dt.value.replace("_", " ").title()}
            for dt in DeviceType
        ],
        "supported_parsers": DeviceParserFactory.get_supported_types(),
        "connection_types": [
            {"value": ct.value, "label": ct.value.replace("_", " ").title()}
            for ct in ConnectionType
        ]
    }