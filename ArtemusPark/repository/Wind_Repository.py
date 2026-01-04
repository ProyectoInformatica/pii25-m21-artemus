import json 
from pathlib import Path 
from typing import List ,Dict ,Any 
from datetime import datetime 
from ArtemusPark .model .Wind_Model import WindModel 


BASE_DIR =Path (__file__ ).resolve ().parent .parent 
DATA_DIR =BASE_DIR /"json"/"wind"


def _serialize_measurement (measurement :WindModel )->Dict [str ,Any ]:
    """Convierte el modelo a un diccionario serializable."""
    return {
    "sensor_id":measurement .sensor_id ,
    "timestamp":measurement .timestamp ,
    "speed":measurement .speed ,
    "state":measurement .state ,
    }


def save_wind_measurement (measurement :WindModel )->None :
    """Guarda un registro en un archivo JSON diario."""
    DATA_DIR .mkdir (parents =True ,exist_ok =True )

    today =datetime .now ().strftime ("%Y-%m-%d")
    file_path =DATA_DIR /f"wind_{today }.json"

    if file_path .exists ():
        try :
            data =json .loads (file_path .read_text (encoding ="utf-8"))
        except json .JSONDecodeError :
            data =[]
    else :
        data =[]

    data .append (_serialize_measurement (measurement ))
    file_path .write_text (json .dumps (data ,indent =2 ),encoding ="utf-8")


def load_all_wind_measurements ()->List [Dict [str ,Any ]]:
    """Carga todos los registros de los archivos JSON diarios."""
    if not DATA_DIR .exists ():
        return []

    all_data =[]
    for file_path in sorted (DATA_DIR .glob ("wind_*.json")):
        try :
            file_content =file_path .read_text (encoding ="utf-8")
            data =json .loads (file_content )
            if isinstance (data ,list ):
                all_data .extend (data )
        except json .JSONDecodeError :
            continue 

    return all_data 
