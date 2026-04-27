"""
设备数据解析器 - 支持各种品牌和型号的健康设备
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

class BaseDeviceParser(ABC):
    """设备数据解析器基类"""
    
    @abstractmethod
    def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析原始数据"""
        pass
    
    @abstractmethod
    def validate(self, parsed_data: Dict[str, Any]) -> bool:
        """验证数据有效性"""
        pass

class BloodPressureParser(BaseDeviceParser):
    """血压计数据解析器"""
    
    # 支持的品牌和型号
    SUPPORTED_DEVICES = {
        "omron": ["HEM-7121", "HEM-7124", "HEM-7130", "U726T"],
        "yuwell": ["YE660", "YE680", "YE8800C"],
        "and": ["UA-651", "UA-1030T"],
        "microlife": ["BP A2 Basic", "BP A6 Plus"],
        "beurer": ["BM27", "BM54"],
    }
    
    def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析血压数据
        
        支持的数据格式:
        1. {"systolic": 120, "diastolic": 80, "pulse": 72}
        2. {"sys": 120, "dia": 80, "hr": 72}
        3. {"bp": {"high": 120, "low": 80}, "heart_rate": 72}
        """
        result = {
            "data_type": "blood_pressure",
            "systolic": None,
            "diastolic": None,
            "pulse": None,
            "unit": "mmHg"
        }
        
        # 尝试不同的字段名
        if "systolic" in raw_data:
            result["systolic"] = int(raw_data["systolic"])
            result["diastolic"] = int(raw_data.get("diastolic", 0))
            result["pulse"] = int(raw_data.get("pulse", 0))
        elif "sys" in raw_data:
            result["systolic"] = int(raw_data["sys"])
            result["diastolic"] = int(raw_data.get("dia", 0))
            result["pulse"] = int(raw_data.get("hr", 0))
        elif "bp" in raw_data:
            bp = raw_data["bp"]
            result["systolic"] = int(bp.get("high", 0))
            result["diastolic"] = int(bp.get("low", 0))
            result["pulse"] = int(raw_data.get("heart_rate", 0))
        
        return result
    
    def validate(self, parsed_data: Dict[str, Any]) -> bool:
        """验证血压数据"""
        sys = parsed_data.get("systolic", 0)
        dia = parsed_data.get("diastolic", 0)
        
        # 合理范围: 收缩压 60-250, 舒张压 40-150
        return 60 <= sys <= 250 and 40 <= dia <= 150 and sys > dia

class BloodSugarParser(BaseDeviceParser):
    """血糖仪数据解析器"""
    
    SUPPORTED_DEVICES = {
        "accu-chek": ["Active", "Guide", "Performa"],
        "one-touch": ["Select Plus", "Ultra Plus"],
        "contour": ["Plus ONE", "Next ONE"],
        "sinocare": ["Safe-Accu", "GA-3"],
    }
    
    def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析血糖数据
        
        支持的数据格式:
        1. {"glucose": 5.6, "unit": "mmol/L"}
        2. {"value": 100, "unit": "mg/dL"}
        3. {"blood_sugar": 5.6, "meal_status": "fasting"}
        """
        result = {
            "data_type": "blood_sugar",
            "value": None,
            "unit": "mmol/L",
            "measurement_time": None  # fasting, before_meal, after_meal
        }
        
        # 获取血糖值
        value = raw_data.get("glucose") or raw_data.get("value") or raw_data.get("blood_sugar")
        
        if value is not None:
            value = float(value)
            # 如果单位是 mg/dL，转换为 mmol/L
            if raw_data.get("unit") == "mg/dL":
                value = value / 18.0
            result["value"] = round(value, 1)
        
        # 获取测量时间状态
        result["measurement_time"] = raw_data.get("meal_status") or raw_data.get("measurement_time")
        
        return result
    
    def validate(self, parsed_data: Dict[str, Any]) -> bool:
        """验证血糖数据"""
        value = parsed_data.get("value", 0)
        # 合理范围: 1.0-33.3 mmol/L
        return 1.0 <= value <= 33.3

class HeartRateParser(BaseDeviceParser):
    """心率监测器数据解析器"""
    
    SUPPORTED_DEVICES = {
        "fitbit": ["Charge 5", "Sense", "Versa 3"],
        "garmin": ["Venu 2", "Forerunner 255"],
        "apple": ["Watch Series 8", "Watch Ultra"],
        "huawei": ["Watch GT 3", "Band 7"],
        "xiaomi": ["Mi Band 7", "Mi Watch"],
    }
    
    def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析心率数据
        
        支持的数据格式:
        1. {"heart_rate": 72, "is_resting": true}
        2. {"bpm": 72, "status": "resting"}
        3. {"hr": 72, "activity": "sleep"}
        """
        result = {
            "data_type": "heart_rate",
            "bpm": None,
            "is_resting": True,
            "hrv": None  # 心率变异性
        }
        
        # 获取心率值
        bpm = raw_data.get("heart_rate") or raw_data.get("bpm") or raw_data.get("hr")
        if bpm is not None:
            result["bpm"] = int(bpm)
        
        # 判断是否静息状态
        status = raw_data.get("status") or raw_data.get("activity", "")
        result["is_resting"] = status.lower() in ["resting", "sleep", "idle", ""]
        
        # 获取 HRV
        result["hrv"] = raw_data.get("hrv")
        
        return result
    
    def validate(self, parsed_data: Dict[str, Any]) -> bool:
        """验证心率数据"""
        bpm = parsed_data.get("bpm", 0)
        return 30 <= bpm <= 220

class WeightScaleParser(BaseDeviceParser):
    """体重秤数据解析器"""
    
    SUPPORTED_DEVICES = {
        "xiaomi": ["Mi Scale 2", "Mi Body Composition Scale 2"],
        "huawei": ["Smart Scale 3"],
        "withings": ["Body+", "Body Cardio"],
        "tanita": ["BC-401", "RD-953"],
    }
    
    def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析体重数据
        
        支持的数据格式:
        1. {"weight": 70.5, "height": 175, "bmi": 23.0}
        2. {"kg": 70.5, "cm": 175}
        3. {"weight_kg": 70.5, "body_fat": 18.5, "muscle": 35.2}
        """
        result = {
            "data_type": "weight",
            "value": None,
            "height": None,
            "bmi": None,
            "body_fat": None,
            "muscle_mass": None,
            "unit": "kg"
        }
        
        # 获取体重
        weight = raw_data.get("weight") or raw_data.get("kg") or raw_data.get("weight_kg")
        if weight is not None:
            result["value"] = float(weight)
        
        # 获取身高
        height = raw_data.get("height") or raw_data.get("cm") or raw_data.get("height_cm")
        if height is not None:
            result["height"] = float(height)
        
        # 计算或获取 BMI
        bmi = raw_data.get("bmi")
        if bmi is not None:
            result["bmi"] = float(bmi)
        elif result["value"] and result["height"]:
            height_m = result["height"] / 100
            result["bmi"] = round(result["value"] / (height_m ** 2), 1)
        
        # 体脂率和肌肉量
        result["body_fat"] = raw_data.get("body_fat")
        result["muscle_mass"] = raw_data.get("muscle") or raw_data.get("muscle_mass")
        
        return result
    
    def validate(self, parsed_data: Dict[str, Any]) -> bool:
        """验证体重数据"""
        weight = parsed_data.get("value", 0)
        return 20 <= weight <= 300

class PulseOximeterParser(BaseDeviceParser):
    """血氧仪数据解析器"""
    
    SUPPORTED_DEVICES = {
        "nonin": ["Onyx Vantage 9590"],
        "contec": ["CMS50D", "CMS50E"],
        "zacurate": ["500DL", "Pro Series"],
        "choiceMMed": ["MD300C2"],
    }
    
    def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析血氧数据
        
        支持的数据格式:
        1. {"spo2": 98, "pulse": 72}
        2. {"oxygen": 98, "heart_rate": 72}
        """
        result = {
            "data_type": "pulse_oximeter",
            "spo2": None,
            "pulse": None,
            "perfusion_index": None
        }
        
        result["spo2"] = raw_data.get("spo2") or raw_data.get("oxygen") or raw_data.get("SpO2")
        result["pulse"] = raw_data.get("pulse") or raw_data.get("heart_rate") or raw_data.get("pr")
        result["perfusion_index"] = raw_data.get("pi") or raw_data.get("perfusion_index")
        
        if result["spo2"]:
            result["spo2"] = int(result["spo2"])
        if result["pulse"]:
            result["pulse"] = int(result["pulse"])
        
        return result
    
    def validate(self, parsed_data: Dict[str, Any]) -> bool:
        """验证血氧数据"""
        spo2 = parsed_data.get("spo2", 0)
        return 70 <= spo2 <= 100

class ThermometerParser(BaseDeviceParser):
    """体温计数据解析器"""
    
    SUPPORTED_DEVICES = {
        "braun": ["ThermoScan 7", "No Touch + Forehead"],
        "omron": ["MC-872", "MC-246"],
        "microlife": ["NC 150", "MT 1931"],
    }
    
    def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析体温数据
        
        支持的数据格式:
        1. {"temperature": 36.5, "unit": "C"}
        2. {"temp_c": 36.5}
        3. {"temp_f": 97.7}
        """
        result = {
            "data_type": "temperature",
            "value": None,
            "unit": "°C",
            "measurement_site": None  # oral, forehead, ear, armpit
        }
        
        temp = raw_data.get("temperature") or raw_data.get("temp_c")
        
        # 如果是华氏度，转换为摄氏度
        if temp is None:
            temp_f = raw_data.get("temp_f")
            if temp_f is not None:
                temp = (float(temp_f) - 32) * 5 / 9
        
        if temp is not None:
            result["value"] = round(float(temp), 1)
        
        result["measurement_site"] = raw_data.get("site") or raw_data.get("measurement_site")
        
        return result
    
    def validate(self, parsed_data: Dict[str, Any]) -> bool:
        """验证体温数据"""
        temp = parsed_data.get("value", 0)
        return 34.0 <= temp <= 43.0


class DeviceParserFactory:
    """设备解析器工厂"""
    
    _parsers = {
        "blood_pressure": BloodPressureParser,
        "blood_sugar": BloodSugarParser,
        "heart_rate": HeartRateParser,
        "weight_scale": WeightScaleParser,
        "pulse_oximeter": PulseOximeterParser,
        "thermometer": ThermometerParser,
    }
    
    @classmethod
    def get_parser(cls, device_type: str) -> Optional[BaseDeviceParser]:
        """获取对应设备类型的解析器"""
        parser_class = cls._parsers.get(device_type)
        if parser_class:
            return parser_class()
        return None
    
    @classmethod
    def register_parser(cls, device_type: str, parser_class: type):
        """注册新的解析器"""
        cls._parsers[device_type] = parser_class
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """获取支持的设备类型"""
        return list(cls._parsers.keys())


def parse_device_data(device_type: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    解析设备数据的便捷函数
    
    Args:
        device_type: 设备类型
        raw_data: 原始数据
    
    Returns:
        解析后的数据
    """
    parser = DeviceParserFactory.get_parser(device_type)
    if parser:
        parsed = parser.parse(raw_data)
        parsed["is_valid"] = parser.validate(parsed)
        return parsed
    else:
        return {
            "data_type": device_type,
            "raw_data": raw_data,
            "is_valid": False,
            "error": f"Unsupported device type: {device_type}"
        }