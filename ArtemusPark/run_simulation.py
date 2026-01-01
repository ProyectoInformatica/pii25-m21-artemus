import time


import sys
import os

""" Script para ejecutar la simulación de sensores """
sys.path.append(os.getcwd())

from controller.Sensor_Controller import SensorController

if __name__ == "__main__":
    controller = SensorController()
    controller.start()

    try:
        print("------------------------------------------------")
        print("📡 SIMULADOR DE SENSORES ARTEMUS INICIADO")
        print("   Generando datos en archivos JSON...")
        print("   Presiona Ctrl + C para detener.")
        print("------------------------------------------------")
        while True:

            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()
        print("\n🛑 Simulador detenido.")
