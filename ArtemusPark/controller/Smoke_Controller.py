import logging 
import random 
import time 
from typing import Callable ,Optional 

from ArtemusPark .model .Smoke_Model import SmokeModel 

logging .basicConfig (
filename ="smoke_controller.log",
level =logging .INFO ,
format ="%(asctime)s - %(levelname)s - %(message)s",
)


class SmokeController :
    def __init__ (
    self ,
    controller_ref =None ,
    on_new_data :Optional [Callable [[SmokeModel ],None ]]=None ,
    ):
        self .controller_ref =controller_ref 
        self .on_new_data =on_new_data 

    def run (self ,name :str ):
        """Simula el detector de humo."""
        if not self .controller_ref :
            logging .error ("SmokeController needs controller_ref to run.")
            return 

        while self .controller_ref .running :

            value =random .randint (0 ,100 )

            if value >95 :
                status ="ALARM"
                msg =f"[{name }] CRITICAL: Fire detected! ({value } density)"
            elif value >40 :
                status ="WARNING"
                msg =f"[{name }] Warning: Smoke detected ({value } density)"
            else :
                status ="CLEAR"
                msg =f"[{name }] Air is clear ({value } density)"

            data =SmokeModel (value =value ,status =status )

            print (msg )
            logging .info (msg )

            if self .on_new_data :
                self .on_new_data (data )

            time .sleep (1 )
