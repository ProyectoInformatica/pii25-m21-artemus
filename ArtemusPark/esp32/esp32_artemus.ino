#include <DHT.h>

#define DHT_PIN 4
#define DHT_TYPE DHT11

#define LDR_PIN 34
#define MQ_PIN 35
#define FAN_PIN 18
#define MOTOR_PIN 19
#define LEDS_PIN 12

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  pinMode(FAN_PIN, OUTPUT);
  pinMode(MOTOR_PIN, OUTPUT);
  pinMode(LEDS_PIN, OUTPUT);
  
  digitalWrite(FAN_PIN, LOW);
  digitalWrite(MOTOR_PIN, LOW);
  digitalWrite(LEDS_PIN, LOW);
}

void loop() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  int ldrValue = analogRead(LDR_PIN);
  int mqValue = analogRead(MQ_PIN);
  
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Error reading DHT");
  } else {
    Serial.print("Temp: ");
    Serial.print(temperature);
    Serial.print("C  Hum: ");
    Serial.print(humidity);
    Serial.print("%  ");
  }
  
  Serial.print("LDR: ");
  Serial.print(ldrValue);
  Serial.print("  MQ: ");
  Serial.println(mqValue);

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

  delay(2000);
}