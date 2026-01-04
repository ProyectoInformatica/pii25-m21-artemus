import time 
from dataclasses import dataclass ,field 


@dataclass 
class SmokeModel :
    """Modelo de datos para sensores de humo/calidad de aire."""

    value :int 
    status :str 
    sensor_id :str 
    name :str =""
    timestamp :float =field (default_factory =time .time )
