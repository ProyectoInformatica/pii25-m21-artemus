#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "Israel's Ultra 24";
const char* password = "cacadevaca";
// IP de tu ordenador donde corre XAMPP
const char* serverName = "http://10.165.41.204/insertar.php";

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected");
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        
        int valorSimulado = random(0, 100);
        String serverPath = String(serverName) + "?valor=" + String(valorSimulado);
        
        http.begin(serverPath.c_str());
        
        int httpResponseCode = http.GET();
        
        if (httpResponseCode > 0) {
            Serial.print("HTTP Response code: ");
            Serial.println(httpResponseCode);
            String payload = http.getString();
            Serial.println(payload);
        } else {
            Serial.print("Error code: ");
            Serial.println(httpResponseCode);
        }
        http.end();
    } else {
        Serial.println("WiFi Disconnected");
    }
    
    delay(10000); // Envía datos cada 10 segundos
}