from dataclasses import dataclass 
from ArtemusPark .config .Wind_Config import RISK_THRESHOLD_KMH 
from ArtemusPark .model .Wind_Model import WindModel 


@dataclass 
class WindRiskResult :
    is_risky :bool 
    threshold_kmh :int 
    current_speed_kmh :int 
    message :str 


def check_wind_risk (measurement :WindModel )->WindRiskResult :
    """
    Compara la medición actual con el umbral de riesgo.
    """
    speed =measurement .speed 
    threshold =RISK_THRESHOLD_KMH 

    is_risky =speed >threshold 

    if is_risky :
        message =f"Wind speed {speed } km/h is ABOVE risk threshold ({threshold } km/h)."
    else :
        message =(
        f"Wind speed {speed } km/h is within safe/normal range "
        f"(threshold: {threshold } km/h)."
        )

    return WindRiskResult (
    is_risky =is_risky ,
    threshold_kmh =threshold ,
    current_speed_kmh =speed ,
    message =message ,
    )
