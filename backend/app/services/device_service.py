"""
设备服务 - 处理设备连接、数据采集和同步
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import asyncio
from abc import ABC, abstractmethod

from app.models.device import (
    Device, DeviceType, DeviceStatus, ConnectionType,
    DeviceDataRecord, DeviceCommand
)
from app.models.patient import Patient
from app.models.health_record import (
    HealthRecord, BloodPressure, BloodSugar, HeartRate, Weight, HealthRecordType
)
from app.services.device_parser import parse_device_data

class DeviceConnector(ABC):
    """设备连接器基类"""
    
    @abstractmethod
    async def connect(self, config: Dict[str, Any]) -> bool:
        """连接设备"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """断开连接"""
        pass
    
    @abstractmethod
    async def read_data(self) -> Optional[Dict[str, Any]]:
        """读取数据"""
        pass
    
    @abstractmethod
    async def send_command(self, command: str, params: Dict[str, Any]) -> bool:
        """发送命令"""
        pass

class BluetoothConnector(DeviceConnector):
    """蓝牙连接器"""
    
    def __init__(self):
        self.device = None
        self.connected = False
    
    async def connect(self, config: Dict[str, Any]) -> bool:
        """连接蓝牙设备"""
        mac_address = config.get("mac_address")
        # 实际实现需要使用 BLE 库 (如 bleak)
        # 这里只是示例
        self.connected = True
        return True
    
    async def disconnect(self) -> bool:
        self.connected = False
        return True
    
    async def read_data(self) -> Optional[Dict[str, Any]]:
        if not self.connected:
            return None
        # 读取蓝牙数据
        return {}
    
    async def send_command(self, command: str, params: Dict[str, Any]) -> bool:
        if not self.connected:
            return False
        return True

class WiFiConnector(DeviceConnector):
    """WiFi 连接器"""
    
    def __init__(self):
        self.base_url = None
        self.connected = False
    
    async def connect(self, config: Dict[str, Any]) -> bool:
        """连接 WiFi 设备"""
        ip = config.get("ip")
        port = config.get("port", 80)
        self.base_url = f"http://{ip}:{port}"
        self.connected = True
        return True
    
    async def disconnect(self) -> bool:
        self.connected = False
        return True
    
    async def read_data(self) -> Optional[Dict[str, Any]]:
        if not self.connected or not self.base_url:
            return None
        
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/data")
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            print(f"WiFi read error: {e}")
        
        return None
    
    async def send_command(self, command: str, params: Dict[str, Any]) -> bool:
        if not self.connected or not self.base_url:
            return False
        
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/command",
                    json={"command": command, "params": params}
                )
                return response.status_code == 200
        except Exception as e:
            print(f"WiFi command error: {e}")
            return False

class APIConnector(DeviceConnector):
    """API 连接器（用于云平台设备）"""
    
    def __init__(self):
        self.api_url = None
        self.api_key = None
        self.connected = False
    
    async def connect(self, config: Dict[str, Any]) -> bool:
        """连接 API"""
        self.api_url = config.get("api_url")
        self.api_key = config.get("api_key")
        self.connected = bool(self.api_url and self.api_key)
        return self.connected
    
    async def disconnect(self) -> bool:
        self.connected = False
        return True
    
    async def read_data(self) -> Optional[Dict[str, Any]]:
        if not self.connected:
            return None
        
        import httpx
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}/data", headers=headers)
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            print(f"API read error: {e}")
        
        return None
    
    async def send_command(self, command: str, params: Dict[str, Any]) -> bool:
        if not self.connected:
            return False
        
        import httpx
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/command",
                    json={"command": command, "params": params},
                    headers=headers
                )
                return response.status_code == 200
        except Exception as e:
            print(f"API command error: {e}")
            return False

class GatewayConnector(DeviceConnector):
    """网关连接器（用于多设备网关）"""
    
    def __init__(self):
        self.gateway_url = None
        self.device_id = None
        self.connected = False
    
    async def connect(self, config: Dict[str, Any]) -> bool:
        """连接网关"""
        self.gateway_url = config.get("gateway_url")
        self.device_id = config.get("device_id")
        self.connected = bool(self.gateway_url and self.device_id)
        return self.connected
    
    async def disconnect(self) -> bool:
        self.connected = False
        return True
    
    async def read_data(self) -> Optional[Dict[str, Any]]:
        if not self.connected:
            return None
        
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.gateway_url}/devices/{self.device_id}/data"
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            print(f"Gateway read error: {e}")
        
        return None
    
    async def send_command(self, command: str, params: Dict[str, Any]) -> bool:
        if not self.connected:
            return False
        
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.gateway_url}/devices/{self.device_id}/command",
                    json={"command": command, "params": params}
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Gateway command error: {e}")
            return False


class DeviceConnectorFactory:
    """设备连接器工厂"""
    
    _connectors = {
        ConnectionType.BLUETOOTH: BluetoothConnector,
        ConnectionType.WIFI: WiFiConnector,
        ConnectionType.API: APIConnector,
        ConnectionType.GATEWAY: GatewayConnector,
    }
    
    @classmethod
    def get_connector(cls, connection_type: ConnectionType) -> Optional[DeviceConnector]:
        """获取对应连接类型的连接器"""
        connector_class = cls._connectors.get(connection_type)
        if connector_class:
            return connector_class()
        return None


class DeviceService:
    """设备服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def register_device(
        self,
        device_sn: str,
        device_name: str,
        device_type: DeviceType,
        connection_type: ConnectionType,
        connection_config: Dict[str, Any],
        patient_id: Optional[int] = None,
        brand: Optional[str] = None,
        model: Optional[str] = None
    ) -> Device:
        """注册新设备"""
        
        # 检查设备是否已存在
        existing = self.db.query(Device).filter(Device.device_sn == device_sn).first()
        if existing:
            raise ValueError(f"设备已存在: {device_sn}")
        
        # 创建设备记录
        device = Device(
            device_sn=device_sn,
            device_name=device_name,
            device_type=device_type,
            connection_type=connection_type,
            connection_config=connection_config,
            patient_id=patient_id,
            brand=brand,
            model=model,
            status=DeviceStatus.OFFLINE
        )
        
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        
        return device
    
    async def connect_device(self, device_id: int) -> bool:
        """连接设备"""
        device = self.db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise ValueError(f"设备不存在: {device_id}")
        
        connector = DeviceConnectorFactory.get_connector(device.connection_type)
        if not connector:
            raise ValueError(f"不支持的连接类型: {device.connection_type}")
        
        try:
            success = await connector.connect(device.connection_config)
            if success:
                device.status = DeviceStatus.ONLINE
                device.last_online = datetime.now()
                self.db.commit()
            return success
        except Exception as e:
            device.status = DeviceStatus.ERROR
            self.db.commit()
            raise e
    
    async def collect_data(self, device_id: int) -> Optional[Dict[str, Any]]:
        """从设备采集数据"""
        device = self.db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise ValueError(f"设备不存在: {device_id}")
        
        if device.status != DeviceStatus.ONLINE:
            raise ValueError(f"设备未在线: {device.status}")
        
        connector = DeviceConnectorFactory.get_connector(device.connection_type)
        if not connector:
            raise ValueError(f"不支持的连接类型: {device.connection_type}")
        
        # 读取原始数据
        raw_data = await connector.read_data()
        if not raw_data:
            return None
        
        # 解析数据
        parsed_data = parse_device_data(device.device_type.value, raw_data)
        
        # 保存数据记录
        record = DeviceDataRecord(
            device_id=device.id,
            patient_id=device.patient_id,
            raw_data=raw_data,
            data_type=parsed_data.get("data_type"),
            parsed_data=parsed_data,
            quality="good" if parsed_data.get("is_valid") else "error",
            measured_at=datetime.now()
        )
        
        self.db.add(record)
        self.db.commit()
        
        # 如果数据有效，同步到健康记录
        if parsed_data.get("is_valid") and device.patient_id:
            await self._sync_to_health_record(device.patient_id, parsed_data)
        
        return parsed_data
    
    async def _sync_to_health_record(self, patient_id: int, parsed_data: Dict[str, Any]):
        """同步数据到健康记录"""
        data_type = parsed_data.get("data_type")
        
        # 创建健康记录
        record_type_map = {
            "blood_pressure": HealthRecordType.BLOOD_PRESSURE,
            "blood_sugar": HealthRecordType.BLOOD_SUGAR,
            "heart_rate": HealthRecordType.HEART_RATE,
            "weight": HealthRecordType.WEIGHT,
            "temperature": HealthRecordType.TEMPERATURE,
        }
        
        record_type = record_type_map.get(data_type)
        if not record_type:
            return
        
        health_record = HealthRecord(
            patient_id=patient_id,
            record_type=record_type,
            record_date=datetime.now(),
            source="device",
            is_abnormal=False
        )
        
        self.db.add(health_record)
        self.db.flush()
        
        # 添加详细数据
        if data_type == "blood_pressure":
            bp = BloodPressure(
                health_record_id=health_record.id,
                systolic=parsed_data.get("systolic"),
                diastolic=parsed_data.get("diastolic"),
                pulse=parsed_data.get("pulse")
            )
            self.db.add(bp)
        
        elif data_type == "blood_sugar":
            bs = BloodSugar(
                health_record_id=health_record.id,
                value=parsed_data.get("value"),
                unit=parsed_data.get("unit", "mmol/L"),
                measurement_time=parsed_data.get("measurement_time")
            )
            self.db.add(bs)
        
        elif data_type == "heart_rate":
            hr = HeartRate(
                health_record_id=health_record.id,
                bpm=parsed_data.get("bpm"),
                is_resting=parsed_data.get("is_resting", True)
            )
            self.db.add(hr)
        
        elif data_type == "weight":
            w = Weight(
                health_record_id=health_record.id,
                value=parsed_data.get("value"),
                height=parsed_data.get("height"),
                bmi=parsed_data.get("bmi")
            )
            self.db.add(w)
        
        self.db.commit()
    
    async def send_command(
        self,
        device_id: int,
        command: str,
        params: Dict[str, Any]
    ) -> bool:
        """向设备发送命令"""
        device = self.db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise ValueError(f"设备不存在: {device_id}")
        
        connector = DeviceConnectorFactory.get_connector(device.connection_type)
        if not connector:
            raise ValueError(f"不支持的连接类型: {device.connection_type}")
        
        # 记录命令
        cmd_record = DeviceCommand(
            device_id=device_id,
            command=command,
            params=params,
            status="sent",
            sent_at=datetime.now()
        )
        
        self.db.add(cmd_record)
        self.db.commit()
        
        # 发送命令
        try:
            success = await connector.send_command(command, params)
            cmd_record.status = "success" if success else "failed"
            cmd_record.completed_at = datetime.now()
            self.db.commit()
            return success
        except Exception as e:
            cmd_record.status = "failed"
            cmd_record.result = {"error": str(e)}
            cmd_record.completed_at = datetime.now()
            self.db.commit()
            raise e
    
    def get_device_data_history(
        self,
        device_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[DeviceDataRecord]:
        """获取设备数据历史"""
        query = self.db.query(DeviceDataRecord).filter(
            DeviceDataRecord.device_id == device_id
        )
        
        if start_date:
            query = query.filter(DeviceDataRecord.measured_at >= start_date)
        if end_date:
            query = query.filter(DeviceDataRecord.measured_at <= end_date)
        
        return query.order_by(DeviceDataRecord.measured_at.desc()).limit(limit).all()
    
    def get_patient_devices(self, patient_id: int) -> List[Device]:
        """获取患者的所有设备"""
        return self.db.query(Device).filter(Device.patient_id == patient_id).all()
    
    async def sync_all_devices(self, patient_id: int) -> Dict[str, Any]:
        """同步患者所有设备数据"""
        devices = self.get_patient_devices(patient_id)
        
        results = {
            "total": len(devices),
            "success": 0,
            "failed": 0,
            "data": []
        }
        
        for device in devices:
            try:
                if device.status == DeviceStatus.ONLINE:
                    data = await self.collect_data(device.id)
                    if data:
                        results["success"] += 1
                        results["data"].append({
                            "device_id": device.id,
                            "device_name": device.device_name,
                            "data": data
                        })
            except Exception as e:
                results["failed"] += 1
                results["data"].append({
                    "device_id": device.id,
                    "device_name": device.device_name,
                    "error": str(e)
                })
        
        return results