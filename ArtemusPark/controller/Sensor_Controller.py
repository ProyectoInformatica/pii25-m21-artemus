import logging 
import threading 
import time 
from datetime import datetime 
from typing import List ,Optional 


from ArtemusPark .controller .Humidity_Controller import HumidityController 
from ArtemusPark .controller .Temperature_Controller import TemperatureController 
from ArtemusPark .controller .Wind_Controller import WindController 
from ArtemusPark .controller .Door_Controller import DoorController 
from ArtemusPark .controller .Light_Controller import LightController 
from ArtemusPark .controller .Smoke_Controller import SmokeController 
from ArtemusPark .config .Park_Config import OPEN_HOUR ,CLOSE_HOUR 


from ArtemusPark .model .Humidity_Model import HumidityModel 
from ArtemusPark .model .Temperature_Model import TemperatureModel 
from ArtemusPark .model .Wind_Model import WindModel 
from ArtemusPark .model .Door_Model import DoorModel 
from ArtemusPark .model .Light_Model import LightModel 
from ArtemusPark .model .Smoke_Model import SmokeModel 


from ArtemusPark .repository .Wind_Repository import save_wind_measurement 
from ArtemusPark .repository .Humidity_Repository import save_humidity_measurement 
from ArtemusPark .repository .Temperature_Repository import save_temperature_measurement 
from ArtemusPark .repository .Door_Repository import save_door_event 
from ArtemusPark .repository .Light_Repository import save_light_event 
from ArtemusPark .repository .Smoke_Repository import save_smoke_measurement 


from ArtemusPark .service .Wind_Risk_Service import check_wind_risk 
from ArtemusPark .service .Smoke_Risk_Service import check_smoke_risk 

logger =logging .getLogger (__name__ )


class SensorController :

    def __init__ (self ):

        self .running =False 
        self .park_open =False 

        self .humidity_history :List [HumidityModel ]=[]
        self .temperature_history :List [TemperatureModel ]=[]
        self .wind_history :List [WindModel ]=[]
        self .door_history :List [DoorModel ]=[]
        self .light_history :List [LightModel ]=[]
        self .smoke_history :List [SmokeModel ]=[]

        self .humidity_controller =HumidityController (on_new_data =self ._on_humidity )
        self .temperature_controller =TemperatureController (
        on_new_data =self ._on_temperature 
        )
        self .wind_controller =WindController (on_new_data =self ._on_wind )

        self .smoke_controller =SmokeController (
        controller_ref =self ,on_new_data =self ._on_smoke 
        )

        self .door_controller =DoorController (
        controller_ref =self ,on_new_data =self ._on_door 
        )

        self .light_controller =LightController (
        controller_ref =self ,on_new_data =self ._on_light 
        )

    def _on_humidity (self ,data :HumidityModel ):
        """Callback al recibir datos de humedad."""
        self ._ensure_timestamp (data )
        self .humidity_history .append (data )
        save_humidity_measurement (data )

    def _on_temperature (self ,data :TemperatureModel ):
        """Callback al recibir datos de temperatura."""
        self ._ensure_timestamp (data )
        self .temperature_history .append (data )
        save_temperature_measurement (data )

    def _on_wind (self ,data :WindModel ):
        """
        Callback al recibir datos de viento.
        """
        self ._ensure_timestamp (data )
        self .wind_history .append (data )
        save_wind_measurement (data )

        risk_result =check_wind_risk (data )
        if risk_result .is_risky :
            alert_msg =f"[WIND ALERT] {risk_result .message }"
            print (alert_msg )
            logger .warning (alert_msg )

    def _on_door (self ,data :DoorModel ):
        self ._ensure_timestamp (data )
        self .door_history .append (data )
        save_door_event (data )

    def _on_light (self ,data :LightModel ):
        self ._ensure_timestamp (data )
        self .light_history .append (data )
        save_light_event (data )

    def _on_smoke (self ,data :SmokeModel ):
        self ._ensure_timestamp (data )
        self .smoke_history .append (data )
        save_smoke_measurement (data )

        risk_result =check_smoke_risk (data )

        if risk_result .is_emergency :

            msg =f"[FIRE EMERGENCY] {risk_result .message }"
            print (msg )
            logger .critical (msg )

            if not self .park_open :
                print (">>> EMERGENCY PROTOCOL: FORCING GATES OPEN <<<")
                self .park_open =True 

        elif risk_result .status =="WARNING":

            msg =f"[SMOKE WARNING] {risk_result .message }"
            print (msg )
            logger .warning (msg )

    def _is_open_time (self ,hour :int )->bool :
        return OPEN_HOUR <=hour <CLOSE_HOUR 

    def simulate_time_and_status (self ):
        """Actualiza el estado de apertura según la hora real."""
        while self .running :
            hour =datetime .now ().hour 
            is_open_time =self ._is_open_time (hour )

            if is_open_time and not self .park_open :
                self .park_open =True 
                print (f"\n--- PARK OPEN at {hour }:00 ---")
            elif not is_open_time and self .park_open :
                self .park_open =False 
                print (f"\n--- PARK CLOSED at {hour }:00 ---")

            print (
            f"[Real Time: {hour }:00] Park {'OPEN'if self .park_open else 'CLOSED'}"
            )

            time .sleep (30 )

    def start (self ):
        """Inicia los sensores y el reloj del parque."""
        self .running =True 

        num_standard_sensors =5 
        num_light_sensors =5 
        door_sensors =2 

        print ("--- Starting Sensors and Park Clock ---")

        threading .Thread (target =self .simulate_time_and_status ,daemon =True ).start ()

        for i in range (num_standard_sensors ):
            sensor_num =i +1 

            threading .Thread (
            target =self .humidity_controller .run ,
            daemon =True ,
            args =(f"HumiditySens{sensor_num }",),
            ).start ()

            threading .Thread (
            target =self .temperature_controller .run ,
            daemon =True ,
            args =(f"TempSens{sensor_num }",),
            ).start ()

            threading .Thread (
            target =self .wind_controller .run ,
            daemon =True ,
            args =(f"WindSens{sensor_num }",),
            ).start ()

            threading .Thread (
            target =self .smoke_controller .run ,
            daemon =True ,
            args =(f"SmokeSens{sensor_num }",),
            ).start ()

        for i in range (num_light_sensors ):
            sensor_num =i +1 
            threading .Thread (
            target =self .light_controller .run ,
            daemon =True ,
            args =(f"LightSens{sensor_num }",),
            ).start ()

        for i in range (door_sensors ):
            sensor_num =i +1 
            threading .Thread (
            target =self .door_controller .run ,
            daemon =True ,
            args =(f"DoorSens{sensor_num }",),
            ).start ()

        print ("Sensors are now active.")

    def _ensure_timestamp (self ,data ):
        if not getattr (data ,"timestamp",None ):
            data .timestamp =time .time ()

    def stop (self ):
        """Detiene la simulación."""
        print ("\n--- Stop request received. Waiting for threads to finish... ---")
        self .running =False 
        time .sleep (6 )
        print ("Controller and threads stopped.")

    def latest_humidity (self )->Optional [HumidityModel ]:
        return self .humidity_history [-1 ]if self .humidity_history else None 

    def latest_temperature (self )->Optional [TemperatureModel ]:
        return self .temperature_history [-1 ]if self .temperature_history else None 

    def latest_wind (self )->Optional [WindModel ]:
        return self .wind_history [-1 ]if self .wind_history else None 

    def latest_light (self )->Optional [LightModel ]:
        return self .light_history [-1 ]if self .light_history else None 

    def latest_smoke (self )->Optional [SmokeModel ]:
        return self .smoke_history [-1 ]if self .smoke_history else None 
