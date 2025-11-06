# Esta línea me sirve para importar lo que tengo dentro de modelo
from ArtemusPark.model.Humidity_Temperature_Controller import (
    Humidity_Temperature_Controller,
)

controller = Humidity_Temperature_Controller()
# Con esto llamo a la función de humedad
controller.humidity()
# Y con está a la de temp
controller.temperature()
