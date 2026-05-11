import time
import sqlite3
import logging
import random
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request

from ArtemusPark.model.Temperature_Model import TemperatureModel
from ArtemusPark.model.Humidity_Model import HumidityModel
from ArtemusPark.model.Light_Model import LightModel
from ArtemusPark.model.Smoke_Model import SmokeModel

from ArtemusPark.repository.Temperature_Repository import save_temperature_measurement
from ArtemusPark.repository.Humidity_Repository import save_humidity_measurement
from ArtemusPark.repository.Light_Repository import save_light_event
from ArtemusPark.repository.Smoke_Repository import save_smoke_measurement

app = Flask(__name__)

handler = RotatingFileHandler('artemus_api.log', maxBytes=100000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

DB_PATH = 'ArtemusPark/bbdd/artemus.db'


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "project": "Artemus Park IoT System",
        "version": "1.1.0",
        "status": "running",
        "endpoints": ["/status", "/ping", "/api/sensor", "/api/debug/latest", "/api/debug/inject"]
    }), 200


@app.route('/status', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "uptime": time.time(),
        "database": "connected"
    }), 200


@app.route('/ping', methods=['GET'])
def ping_check():
    return jsonify({"msg": "pong"}), 200


@app.route('/api/sensor', methods=['GET'])
def receive_sensor_data():
    sensor_type = request.args.get('type')
    raw_value = request.args.get('value', type=float)
    sensor_id = request.args.get('sensor_id')

    if raw_value is None or not sensor_id or not sensor_type:
        app.logger.warning(f"Invalid request: {request.args}")
        return jsonify({"error": "Missing parameters", "received": request.args}), 400

    value = int(raw_value)
    current_time = time.time()

    try:
        if sensor_type == 'temperature':
            data = TemperatureModel(value=value, status="OK", sensor_id=sensor_id, timestamp=current_time)
            save_temperature_measurement(data)
        elif sensor_type == 'humidity':
            data = HumidityModel(value=value, status="OK", sensor_id=sensor_id, timestamp=current_time)
            save_humidity_measurement(data)
        elif sensor_type == 'light':
            data = LightModel(value=value, status="OK", is_on=(value < 1000), sensor_id=sensor_id,
                              timestamp=current_time)
            save_light_event(data)
        elif sensor_type == 'smoke':
            data = SmokeModel(value=value, status="OK", sensor_id=sensor_id, timestamp=current_time)
            save_smoke_measurement(data)
        else:
            return jsonify({"error": "Invalid sensor type"}), 400

        app.logger.info(f"Saved {sensor_type} from {sensor_id}: {value}")
        return jsonify({"status": "success", "sensor": sensor_id}), 200
    except Exception as e:
        app.logger.error(f"Error saving data: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/debug/latest', methods=['GET'])
def get_latest_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        results = {}
        tables = ['temperature_measurements', 'humidity_measurements', 'light_events', 'smoke_measurements']

        for table in tables:
            cursor.execute(f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT 3")
            results[table] = cursor.fetchall()

        conn.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/debug/inject', methods=['GET'])
def inject_fake_data():
    stype = request.args.get('type', 'temperature')
    sid = request.args.get('id', 'DEBUG_01')
    val = random.randint(15, 35)

    url = f"/api/sensor?type={stype}&value={val}&sensor_id={sid}"
    with app.test_client() as client:
        response = client.get(url)
        return jsonify({
            "action": "injection",
            "target_url": url,
            "response": response.get_json()
        }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)