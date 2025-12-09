import time

# Asegúrate de que Python encuentre la carpeta ArtemusPark
import sys
import os

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
            # Mantener el script vivo
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()
        print("\n🛑 Simulador detenido.")
