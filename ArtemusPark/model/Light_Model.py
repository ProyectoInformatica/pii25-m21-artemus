import time 
from dataclasses import dataclass ,field 


@dataclass 
class LightModel :
    """Modelo de datos para sensores de luz."""

    value :int 
    status :str 
    is_on :bool 
    sensor_id :str 
    name :str =""
    timestamp :float =field (default_factory =time .time )
