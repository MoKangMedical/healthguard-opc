# HealthGuard OPC 硬件对接指南

## 支持的设备类型

### 1. 血压计 (Blood Pressure Monitor)
- **品牌**: Omron (欧姆龙), Yuwell (鱼跃), AND, Microlife, Beurer
- **连接方式**: 蓝牙, WiFi, USB
- **数据**: 收缩压, 舒张压, 脉搏

### 2. 血糖仪 (Blood Glucose Meter)
- **品牌**: Accu-Chek (罗氏), OneTouch (强生), Contour (拜耳), Sinocafe (三诺)
- **连接方式**: 蓝牙, USB
- **数据**: 血糖值, 测量时间状态

### 3. 心率监测器 (Heart Rate Monitor)
- **品牌**: Fitbit, Garmin, Apple Watch, Huawei Watch, Xiaomi Mi Band
- **连接方式**: 蓝牙, API (云同步)
- **数据**: 心率 (BPM), HRV, 活动状态

### 4. 体重秤 (Weight Scale)
- **品牌**: Xiaomi, Huawei, Withings, Tanita
- **连接方式**: 蓝牙, WiFi
- **数据**: 体重, BMI, 体脂率, 肌肉量

### 5. 血氧仪 (Pulse Oximeter)
- **品牌**: Nonin, Contec, Zacurate, ChoiceMMed
- **连接方式**: 蓝牙, USB
- **数据**: SpO2, 脉搏, 灌注指数

### 6. 体温计 (Thermometer)
- **品牌**: Braun, Omron, Microlife
- **连接方式**: 蓝牙, WiFi
- **数据**: 体温值, 测量部位

## 连接方式

### 蓝牙连接 (Bluetooth)
适用于: 手持设备、穿戴设备

```python
# 配置示例
{
    "connection_type": "bluetooth",
    "connection_config": {
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "protocol": "BLE",
        "service_uuid": "00001810-0000-1000-8000-00805f9b34fb"
    }
}
```

### WiFi 连接
适用于: 智能家居设备、网关设备

```python
# 配置示例
{
    "connection_type": "wifi",
    "connection_config": {
        "ip": "192.168.1.100",
        "port": 80,
        "protocol": "http",
        "auth_token": "your-device-token"
    }
}
```

### API 连接
适用于: 云平台设备、第三方服务

```python
# 配置示例
{
    "connection_type": "api",
    "connection_config": {
        "api_url": "https://api.device-cloud.com/v1",
        "api_key": "your-api-key",
        "device_id": "device-123"
    }
}
```

### 网关连接 (Gateway)
适用于: 多设备集中管理

```python
# 配置示例
{
    "connection_type": "gateway",
    "connection_config": {
        "gateway_url": "http://192.168.1.50:8080",
        "device_id": "bp-001",
        "auth_token": "gateway-token"
    }
}
```

## API 接口

### 设备管理

#### 注册设备
```http
POST /api/devices/register
Content-Type: application/json
Authorization: Bearer {token}

{
    "device_sn": "BP2024001",
    "device_name": "客厅血压计",
    "device_type": "blood_pressure",
    "connection_type": "bluetooth",
    "connection_config": {
        "mac_address": "AA:BB:CC:DD:EE:FF"
    },
    "patient_id": 1,
    "brand": "Omron",
    "model": "HEM-7130"
}
```

#### 连接设备
```http
POST /api/devices/{device_id}/connect
Authorization: Bearer {token}
```

#### 采集数据
```http
POST /api/devices/{device_id}/collect
Authorization: Bearer {token}
```

#### 获取数据历史
```http
GET /api/devices/{device_id}/history?days=7&limit=100
Authorization: Bearer {token}
```

#### 同步所有设备
```http
POST /api/devices/patient/{patient_id}/sync
Authorization: Bearer {token}
```

## 数据解析

### 血压数据格式
```json
{
    "data_type": "blood_pressure",
    "systolic": 120,
    "diastolic": 80,
    "pulse": 72,
    "unit": "mmHg",
    "is_valid": true
}
```

### 血糖数据格式
```json
{
    "data_type": "blood_sugar",
    "value": 5.6,
    "unit": "mmol/L",
    "measurement_time": "fasting",
    "is_valid": true
}
```

### 体重数据格式
```json
{
    "data_type": "weight",
    "value": 70.5,
    "height": 175,
    "bmi": 23.0,
    "body_fat": 18.5,
    "muscle_mass": 35.2,
    "unit": "kg",
    "is_valid": true
}
```

## 扩展开发

### 添加新设备类型

1. 在 `device_parser.py` 中创建解析器:

```python
class NewDeviceParser(BaseDeviceParser):
    SUPPORTED_DEVICES = {
        "brand": ["model1", "model2"]
    }
    
    def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        # 解析逻辑
        return {
            "data_type": "new_type",
            "value": raw_data.get("value"),
            "is_valid": True
        }
    
    def validate(self, parsed_data: Dict[str, Any]) -> bool:
        # 验证逻辑
        return True
```

2. 注册到工厂:

```python
DeviceParserFactory.register_parser("new_type", NewDeviceParser)
```

### 添加新连接方式

1. 在 `device_service.py` 中创建连接器:

```python
class NewConnector(DeviceConnector):
    async def connect(self, config: Dict[str, Any]) -> bool:
        # 连接逻辑
        return True
    
    async def disconnect(self) -> bool:
        return True
    
    async def read_data(self) -> Optional[Dict[str, Any]]:
        # 读取数据逻辑
        return {}
    
    async def send_command(self, command: str, params: Dict[str, Any]) -> bool:
        return True
```

2. 注册到工厂:

```python
DeviceConnectorFactory._connectors[ConnectionType.NEW_TYPE] = NewConnector
```

## 常见问题

### Q: 设备连接失败怎么办？
A: 检查以下几点:
1. 设备是否开机
2. 网络/蓝牙是否正常
3. 配置信息是否正确
4. 设备是否在范围内

### Q: 数据解析失败怎么办？
A: 检查以下几点:
1. 原始数据格式是否正确
2. 数据是否在合理范围内
3. 是否支持该设备型号

### Q: 如何提高数据同步成功率？
A: 建议:
1. 保持设备固件更新
2. 使用稳定的网络连接
3. 定期检查设备状态

## 技术支持

如有问题，请联系:
- GitHub Issues: https://github.com/MoKangMedical/healthguard-opc/issues
- Email: support@example.com