#include <WiFi.h>
#define USING_HOST_NAME false
#include <MySQL_Generic.h>

// ── WiFi ──────────────────────────────────────
char ssid[] = "igomez-fedora";
char pass[] = "cacadevaca";

// ── MySQL ─────────────────────────────────────
IPAddress server_addr(172, 27, 81, 221);
uint16_t  server_port = 3306;
char db_user[]     = "esp32user";
char db_password[] = "tu_password";

// client ya está declarado dentro de MySQL_Generic.h, no lo declares tú
MySQL_Connection conn((Client *)&client);

void setup() {
    Serial.begin(115200);
    delay(2000);

    Serial.print("Conectando a WiFi");
    WiFi.begin(ssid, pass);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\n✔ WiFi conectado — IP: " + WiFi.localIP().toString());

    Serial.println("Conectando a MySQL...");
    while (conn.connectNonBlocking(server_addr, server_port, db_user, db_password) != RESULT_OK) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\n✔ MySQL conectado!");

    // En esta librería se llama MySQL_Query, no MySQL_Cursor
    MySQL_Query query(&conn);
    if (query.execute("INSERT INTO artemus.Measurement (id_sensor, status, elec_consumption, timestamp) VALUES (33, 1, 0, NOW())")) {
        Serial.println("✔ INSERT ejecutado correctamente");
    } else {
        Serial.println("✘ Error en el INSERT");
    }


    conn.close();
}

void loop() {}