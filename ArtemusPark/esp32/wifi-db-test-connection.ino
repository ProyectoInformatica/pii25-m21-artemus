#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

#define DHT_PIN 4
#define DHT_TYPE DHT11
#define LDR_PIN 34
#define MQ_PIN 35
#define FAN_PIN 18
#define MOTOR_PIN 19
#define LEDS_PIN 12

const char* ssid = "Israel's Ultra 24";
const char* password = "cacadevaca";
const char* serverName = "http://10.165.41.204:5000/api/sensor";

DHT dht(DHT_PIN, DHT_TYPE);

void sendSensorData(String type, float value, String sensorId) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        String serverPath = String(serverName) + "?type=" + type + "&value=" + String(value) + "&sensor_id=" + sensorId;
        http.begin(serverPath.c_str());
        http.GET();
        http.end();
    }
}

void setup() {
    Serial.begin(115200);
    dht.begin();

    pinMode(FAN_PIN, OUTPUT);
    pinMode(MOTOR_PIN, OUTPUT);
    pinMode(LEDS_PIN, OUTPUT);

    digitalWrite(FAN_PIN, LOW);
    digitalWrite(MOTOR_PIN, LOW);
    digitalWrite(LEDS_PIN, LOW);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }
}

void loop() {
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();
    int ldrValue = analogRead(LDR_PIN);
    int mqValue = analogRead(MQ_PIN);

    if (!isnan(temperature)) {
        sendSensorData("temperature", temperature, "TempSens1");
    }
    if (!isnan(humidity)) {
        sendSensorData("humidity", humidity, "HumiditySens1");
    }

    sendSensorData("light", (float)ldrValue, "LightSens1");
    sendSensorData("smoke", (float)mqValue, "SmokeSens1");

    if (temperature > 25.0) {
        digitalWrite(FAN_PIN, HIGH);
    } else {
        digitalWrite(FAN_PIN, LOW);
    }

    if (ldrValue < 1000) {
        digitalWrite(LEDS_PIN, HIGH);
    } else {
        digitalWrite(LEDS_PIN, LOW);
    }

    if (mqValue > 2000) {
        digitalWrite(MOTOR_PIN, HIGH);
    } else {
        digitalWrite(MOTOR_PIN, LOW);
    }

    delay(10000);
}