import time 
from dataclasses import dataclass ,field 


@dataclass 
class WindModel :
    """Modelo de datos para sensores de viento."""

    speed :int 
    state :str 
    sensor_id :str 
    name :str =""
    timestamp :float =field (default_factory =time .time )
