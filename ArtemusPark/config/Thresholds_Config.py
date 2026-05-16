"""Umbrales de alerta y control del sistema Artemus Park."""

# ── Sensores Arduino (ESP32) ──────────────────────────────────────────────────
TEMP_THRESHOLD: float = 28.0  # °C  — ventilador activa si temp  > 28
LDR_THRESHOLD: int = 3000  # ADC — LEDs activan si luz        < 3000
MQ_THRESHOLD: int = 2000  # ADC — extractor activa si CO₂   > 2000
SENSOR_LOOP_SECONDS: int = 10  # Intervalo de envío del Arduino (segundos)

# ── Viento ────────────────────────────────────────────────────────────────────
WIND_WARNING_THRESHOLD_KMH: int = 20  # Aviso en dashboard
WIND_RISK_THRESHOLD_KMH: int = 40  # Riesgo alto

# ── Estado online de sensores ─────────────────────────────────────────────────
SENSOR_ONLINE_WINDOW_SECONDS: int = 30  # Sin datos > 30s → sensor offline
