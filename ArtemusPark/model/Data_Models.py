from dataclasses import dataclass


@dataclass
class SensorData:
    temperature: float
    humidity: int
    wind_speed: int
    air_quality: int
    capacity_current: int
    capacity_max: int


@dataclass
class Alert:
    title: str
    message: str
    severity: str  # critical, warning, info
    time: str
