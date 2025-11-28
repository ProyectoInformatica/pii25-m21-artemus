import unittest
from ArtemusPark.controller.Sensor_Controller import SensorController


class ScheduleTest(unittest.TestCase):
    """
    Clase de prueba para validar la lógica de apertura y cierre del parque
    contenida en SensorController.
    """

    # Horarios definidos en SensorController son: OPEN_HOUR = 9, CLOSE_HOUR = 18

    # ----------------------------------------------------
    # 1. Pruebas de APERTURA (Hora 9)
    # ----------------------------------------------------

    def test_park_opening_transition(self):
        """Prueba que el parque se abre a las 9:00."""

        # 1. Crear controlador y establecer el estado inicial a 8:00, cerrado
        controller = SensorController()
        controller.simulated_hour = 8
        controller.park_open = False

        # Simular el paso de 8:00 a 9:00
        # El parque aún está cerrado a las 8:00 (is_open_time = False),
        # pero la hora avanza a 9:00.
        _, is_open = controller.advance_simulated_hour()
        self.assertFalse(is_open, "Fallo: No debería estar abierto a las 8:00.")
        self.assertEqual(controller.simulated_hour, 9, "Fallo: La hora debe ser 9.")

        # Simular el paso de 9:00 a 10:00
        # Ahora que la hora es 9, la lógica debe cambiar el estado a ABIERTO.
        msg, is_open = controller.advance_simulated_hour()
        self.assertTrue(is_open, "Fallo: El parque DEBE abrir a las 9:00.")
        self.assertEqual(controller.simulated_hour, 10, "Fallo: La hora debe ser 10.")
        self.assertIn("PARK OPEN", msg, "Fallo: Mensaje de apertura no encontrado.")

    # ----------------------------------------------------
    # 2. Pruebas de CIERRE (Hora 18)
    # ----------------------------------------------------

    def test_park_closing_transition(self):
        """Prueba que el parque se cierra a las 18:00."""

        # 1. Crear controlador y establecer el estado inicial a 17:00, abierto
        controller = SensorController()
        controller.simulated_hour = 17
        controller.park_open = True

        # Simular el paso de 17:00 a 18:00
        # El parque aún está abierto (is_open_time = True), hora avanza a 18:00.
        _, is_open = controller.advance_simulated_hour()
        self.assertTrue(is_open, "Fallo: Debe permanecer abierto a las 17:00.")
        self.assertEqual(controller.simulated_hour, 18, "Fallo: La hora debe ser 18.")

        # Simular el paso de 18:00 a 19:00
        # Ahora que la hora es 18, la lógica (OPEN_HOUR <= hour < CLOSE_HOUR) es FALSE,
        # por lo que debe cambiar el estado a CERRADO.
        msg, is_open = controller.advance_simulated_hour()
        self.assertFalse(is_open, "Fallo: El parque DEBE cerrar a las 18:00.")
        self.assertEqual(controller.simulated_hour, 19, "Fallo: La hora debe ser 19.")
        self.assertIn("PARK CLOSED", msg, "Fallo: Mensaje de cierre no encontrado.")

    # ----------------------------------------------------
    # 3. Prueba de Ciclo de 24 Horas
    # ----------------------------------------------------

    def test_24_hour_cycle(self):
        """Prueba que la hora se reinicia a 0 después de 23:00."""

        controller = SensorController()
        controller.simulated_hour = 23

        # Simular el paso de 23:00 a 0:00
        controller.advance_simulated_hour()
        self.assertEqual(
            controller.simulated_hour, 0, "Fallo: La hora debe reiniciarse a 0."
        )


if __name__ == "__main__":
    unittest.main()
