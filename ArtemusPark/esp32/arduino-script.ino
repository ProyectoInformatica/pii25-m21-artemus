// ═══════════════════════════════════════════════
//  ARTEMUS — ESP32 · Sensores + MySQL + Control
// ═══════════════════════════════════════════════

// ── Librerías ────────────────────────────────────
#include <WiFi.h>
#define USING_HOST_NAME false
#include <MySQL_Generic.h>
#include <DHT.h>


// ── Pines ────────────────────────────────────────
#define DHT_PIN     4
#define DHT_TYPE    DHT11
#define LDR_PIN     34
#define MQ_PIN      35

#define FAN_PIN     18    // Ventilador  → activa si temp  > 28 °C
#define MOTOR_PIN   19    // Extractor   → activa si CO₂   > 2000
#define LEDS_PIN    12    // LEDs        → activa si luz    < 3000


// ── Umbrales de control ───────────────────────────
#define TEMP_THRESHOLD   28.0
#define LDR_THRESHOLD    3000
#define MQ_THRESHOLD     2000

#define INITIAL_TIME     3000
#define LOOP_TIME        10000


// ── IDs de sensores en BD ─────────────────────────
#define ID_SENSOR_TEMP    22   // temp_01  · id_tipo 1
#define ID_SENSOR_HUM     25   // hum_01   · id_tipo 2
#define ID_SENSOR_LIGHT   32   // light_01 · id_tipo 5
#define ID_SENSOR_AIR     28   // smoke_01 · id_tipo 6

#define ID_ZONE           1
#define ID_ROLE           3


// ── Credenciales WiFi ─────────────────────────────
char ssid[] = "igomez-fedora";
char pass[] = "cacadevaca";


// ── Credenciales MySQL ────────────────────────────
IPAddress server_addr(172, 27, 81, 221);
uint16_t  server_port = 3306;
char db_user[]     = "esp32user";
char db_password[] = "tu_password";


// ── Objetos globales ──────────────────────────────
// WiFiClient client ya está declarado dentro de MySQL_Generic.h
MySQL_Connection conn((Client *)&client);
DHT              dht(DHT_PIN, DHT_TYPE);
MySQL_Query      q(&conn);    // globales para evitar fragmentación de heap
MySQL_Query      q2(&conn);   // globales para evitar fragmentación de heap


// ── Registrar sensores en la BD al iniciar ────────
void registrarSensores() {
    Serial.println("\n── Registrando sensores en BD ──");
    char query[300];

    struct {
        int         id;
        int         id_type;
        const char *name;
    } sensores[] = {
        { ID_SENSOR_TEMP,  1, "Temp_1"  },
        { ID_SENSOR_HUM,   2, "Hum_1"   },
        { ID_SENSOR_LIGHT, 5, "Light_1" },
        { ID_SENSOR_AIR,   6, "Air_1"   },
    };

    for (int i = 0; i < 4; i++) {
        sprintf(query,
            "INSERT IGNORE INTO artemus.Sensor "
            "(id_sensor, id_zone, id_type, id_role, name, description, active, installed_at) "
            "VALUES (%d, %d, %d, %d, '%s', NULL, 1, NOW())",
            sensores[i].id, ID_ZONE, sensores[i].id_type, ID_ROLE, sensores[i].name);

        if (q.execute(query)) {
            Serial.printf("  ✔ Sensor '%s' (id=%d) registrado\n",
                          sensores[i].name, sensores[i].id);
        } else {
            Serial.printf("  ✘ Error al registrar sensor '%s'\n", sensores[i].name);
        }
    }
}


// ── Función auxiliar: insertar Measurement + tabla específica ──
void insertarMedicion(int id_sensor, const char *tabla,
                      const char *campo, float valor, bool esFloat, bool ok, int is_on = -1) {
    char query[300];

    // 1. Insertar en Measurement con estado según si el sensor funciona
    sprintf(query,
        "INSERT INTO artemus.Measurement (id_sensor, status, elec_consumption, timestamp) "
        "VALUES (%d, %d, 0, NOW())",
        id_sensor, ok ? 1 : 0);  // 1 = OK, 0 = ERROR

    if (!q.execute(query)) {
        Serial.printf("  ✘ Error en Measurement (sensor %d)\n", id_sensor);
        return;
    }
    Serial.printf("  ✔ Measurement insertado (sensor %d) — estado: %s\n",
                  id_sensor, ok ? "OK" : "ERROR");

    // Si el sensor falló no insertamos en la tabla específica
    if (!ok) return;

    // 2. Obtener el ID recién insertado
    if (!q2.execute("SELECT LAST_INSERT_ID()")) {
        Serial.println("  ✘ Error obteniendo LAST_INSERT_ID");
        return;
    }

    column_names *cols = q2.get_columns();
    row_values   *row  = q2.get_next_row();
    if (!row) {
        Serial.println("  ✘ Sin resultado en LAST_INSERT_ID");
        return;
    }

    int lastId = atoi(row->values[0]);
    Serial.printf("  → id_measurement: %d\n", lastId);

    // 3. Insertar en tabla específica con el ID real
    if (is_on >= 0) {
        if (esFloat) {
            sprintf(query,
                "INSERT INTO artemus.%s (id_measurement, is_on, %s) VALUES (%d, %d, %.2f)",
                tabla, campo, lastId, is_on, valor);
        } else {
            sprintf(query,
                "INSERT INTO artemus.%s (id_measurement, is_on, %s) VALUES (%d, %d, %d)",
                tabla, campo, lastId, is_on, (int)valor);
        }
    } else if (esFloat) {
        sprintf(query,
            "INSERT INTO artemus.%s (id_measurement, %s) VALUES (%d, %.2f)",
            tabla, campo, lastId, valor);
    } else {
        sprintf(query,
            "INSERT INTO artemus.%s (id_measurement, %s) VALUES (%d, %d)",
            tabla, campo, lastId, (int)valor);
    }

    if (q.execute(query)) {
        Serial.printf("  ✔ %s.%s = %.2f insertado\n", tabla, campo, valor);
    } else {
        Serial.printf("  ✘ Error en %s (sensor %d)\n", tabla, id_sensor);
    }
}


// ═══════════════════════════════════════════════
void setup() {
// ═══════════════════════════════════════════════

    Serial.begin(115200);
    delay(INITIAL_TIME);
    dht.begin();

    // Pines actuadores
    pinMode(FAN_PIN,   OUTPUT);
    pinMode(MOTOR_PIN, OUTPUT);
    pinMode(LEDS_PIN,  OUTPUT);

    digitalWrite(FAN_PIN,   LOW);
    digitalWrite(MOTOR_PIN, LOW);
    digitalWrite(LEDS_PIN,  LOW);

    // Conexión WiFi
    Serial.print("Conectando a WiFi");
    WiFi.begin(ssid, pass);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\n✔ WiFi conectado — IP: " + WiFi.localIP().toString());

    // Conexión MySQL
    Serial.print("Conectando a MySQL...");
    while (conn.connectNonBlocking(server_addr, server_port, db_user, db_password) != RESULT_OK) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\n✔ MySQL conectado!");

    // Registrar sensores físicos en la BD
    registrarSensores();
}


// ═══════════════════════════════════════════════
void loop() {
// ═══════════════════════════════════════════════

    Serial.printf("[MEM] Heap libre: %d bytes\n", ESP.getFreeHeap());

        // Reconectar WiFi si se perdió
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi perdido, reconectando...");
        WiFi.disconnect();
        WiFi.begin(ssid, pass);
        int intentos = 0;
        while (WiFi.status() != WL_CONNECTED && intentos < 20) {
            delay(500);
            Serial.print(".");
            intentos++;
        }
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("\n✔ WiFi reconectado — IP: " + WiFi.localIP().toString());
        } else {
            Serial.println("\n✘ No se pudo reconectar al WiFi, reintentando en el próximo ciclo");
            delay(LOOP_TIME);
            return;
        }
    }

    // Reconectar si se perdió la conexión
    if (!conn.connected()) {
        Serial.println("Reconectando a MySQL...");
        conn.connectNonBlocking(server_addr, server_port, db_user, db_password);
        delay(5000);
        return;
    }

    // ── 1. Leer sensores ──────────────────────────
    float humidity    = dht.readHumidity();
    float temperature = dht.readTemperature();
    int   ldrValue    = analogRead(LDR_PIN);
    int   mqValue     = analogRead(MQ_PIN);

    bool tempOk  = !isnan(temperature);
    bool humOk   = !isnan(humidity);
    bool ldrOk   = (ldrValue >= 0 && ldrValue <= 4095);
    bool mqOk    = (mqValue  >= 0 && mqValue  <= 4095);
    bool fanOn   = temperature > TEMP_THRESHOLD;
    bool ledsOn  = ldrValue    < LDR_THRESHOLD;
    bool motorOn = mqValue     > MQ_THRESHOLD;

    Serial.printf("Temp: %s  Hum: %s  Luz: %d  CO2: %d\n",
                  tempOk ? String(temperature).c_str() : "ERROR",
                  humOk  ? String(humidity).c_str()    : "ERROR",
                  ldrValue, mqValue);

    // ── 2. Insertar mediciones en BD ──────────────
    insertarMedicion(ID_SENSOR_TEMP,  "Temperature", "temperature",       temperature, true,  tempOk);
    insertarMedicion(ID_SENSOR_HUM,   "Humidity",    "relative_humidity", humidity,    true,  humOk);
    insertarMedicion(ID_SENSOR_LIGHT, "Lighting",    "value",             ldrValue,    false, ldrOk, ledsOn ? 1 : 0);
    insertarMedicion(ID_SENSOR_AIR,   "Air_Quality", "co2_level",         mqValue,     false, mqOk);

    // ── 3. Control de actuadores ──────────────────

    digitalWrite(FAN_PIN,   fanOn   ? HIGH : LOW);
    digitalWrite(LEDS_PIN,  ledsOn  ? HIGH : LOW);
    digitalWrite(MOTOR_PIN, motorOn ? HIGH : LOW);

    Serial.printf("Actuadores — Ventilador: %s  LEDs: %s  Extractor: %s\n",
                  fanOn ? "ON" : "OFF", ledsOn ? "ON" : "OFF", motorOn ? "ON" : "OFF");

    delay(LOOP_TIME);
}