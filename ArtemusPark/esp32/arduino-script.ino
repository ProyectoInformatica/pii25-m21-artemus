// Librerias
#include <WiFi.h>
#define USING_HOST_NAME false
#include <MySQL_Generic.h>
#include <DHT.h>
#include <time.h>
// #include <SensorBiordinario.h>   // libreria del sensor biordinario (simulada abajo)


// Pines sensores existentes
#define DHT_PIN     4
#define DHT_TYPE    DHT11
#define LDR_PIN     34
#define MQ_PIN      35

// Pines actuadores
#define FAN_PIN      18   // Ventilador -> activa si temp > 28 C
#define MOTOR_PIN    19   // Motor puerta -> pulso DOOR_TIME_MS al abrir/cerrar
#define LEDS_PIN     12   // LEDs -> activa si luz < 3000
#define DOOR_TIME_MS 2500 // Duracion del pulso del motor (ms)

// Pines sensor biordinario
#define BIORD_RX_PIN  16   // UART RX del sensor biordinario
#define BIORD_TX_PIN  17   // UART TX del sensor biordinario


// Umbrales de control
#define TEMP_THRESHOLD   28.0
#define LDR_THRESHOLD    3000
#define MQ_THRESHOLD     2000

#define INITIAL_TIME     3000
#define LOOP_TIME        10000

// Horario del parque
#define OPEN_HOUR   9    // Hora de apertura (9:00)
#define CLOSE_HOUR  18   // Hora de cierre   (18:00)

// NTP (hora real por red)
#define NTP_SERVER          "pool.ntp.org"
#define GMT_OFFSET_SEC      3600   // UTC+1 (CET)
#define DAYLIGHT_OFFSET_SEC 3600   // +1h adicional en verano (CEST)


// IDs de sensores en BD
#define ID_SENSOR_TEMP    22   // temp_01  · id_tipo 1
#define ID_SENSOR_HUM     25   // hum_01   · id_tipo 2
#define ID_SENSOR_LIGHT   32   // light_01 · id_tipo 5
#define ID_SENSOR_AIR     28   // smoke_01 · id_tipo 6
#define ID_SENSOR_BIORD   36   // biord_01 · id_tipo 7

#define ID_ZONE           1
#define ID_ROLE           3


// Credenciales WiFi
char ssid[] = "wifi-database"; // CAMBIAR POR TU WIFI
char pass[] = "kkdevac4"; // CAMBIAR POR TU CONTRASEÑA DEL WIFI


// Credenciales MySQL
IPAddress server_addr(172, 27, 81, 221); // IP DEL SERVIDOR MYSQL
uint16_t  server_port = 3306; // PUERTO SERVIDOR MYSQL
char db_user[]     = "esp32user"; // USUARIO MYSQL ESP32
char db_password[] = "tu_password"; // PASSWORD MYSQL ESP32


// Struct datos sensor biordinario
// leerDatosOrdinarios() devuelve [int, char[]]
struct DatosBiordinario {
    int  numerico;
    char alfanumerico[64];
};


// Objetos globales
MySQL_Connection conn((Client *)&client);
DHT              dht(DHT_PIN, DHT_TYPE);
MySQL_Query      q(&conn);
MySQL_Query      q2(&conn);

bool ultimoEstadoParque = false;


// Control de la puerta
void accionarPuerta(const char* motivo) {
    Serial.printf("PUERTA: accionando (%s)\n", motivo);
    digitalWrite(MOTOR_PIN, HIGH);
    delay(DOOR_TIME_MS);
    digitalWrite(MOTOR_PIN, LOW);
    Serial.println("PUERTA: detenida");
}

// Hora real via NTP
void sincronizarHora() {
    configTime(GMT_OFFSET_SEC, DAYLIGHT_OFFSET_SEC, NTP_SERVER);
    struct tm timeinfo;
    int intentos = 0;
    while (!getLocalTime(&timeinfo) && intentos < 10) {
        delay(500);
        intentos++;
    }
    if (getLocalTime(&timeinfo)) {
        Serial.printf("Hora NTP sincronizada: %02d:%02d:%02d\n",
                      timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec);
    } else {
        Serial.println("No se pudo sincronizar hora NTP");
    }
}

int obtenerHora() {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) return -1;
    return timeinfo.tm_hour;
}


// Registrar sensores en la BD al iniciar
void registrarSensores() {
    Serial.println("\nRegistrando sensores en BD...");
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
        { ID_SENSOR_BIORD, 7, "Biord_1" },
    };

    char checkQuery[100];
    for (int i = 0; i < 5; i++) {
        sprintf(checkQuery,
            "SELECT COUNT(*) FROM artemus.Sensor WHERE id_sensor = %d",
            sensores[i].id);

        bool yaExiste = false;
        if (q2.execute(checkQuery)) {
            row_values *fila = q2.get_next_row();
            if (fila && atoi(fila->values[0]) > 0) {
                yaExiste = true;
            }
        }

        if (yaExiste) {
            Serial.printf("  Sensor '%s' (id=%d) ya existe, omitiendo\n",
                          sensores[i].name, sensores[i].id);
            continue;
        }

        sprintf(query,
            "INSERT INTO artemus.Sensor "
            "(id_sensor, id_zone, id_type, id_role, name, active, installed_at) "
            "VALUES (%d, %d, %d, %d, '%s', 1, NOW())",
            sensores[i].id, ID_ZONE, sensores[i].id_type, ID_ROLE, sensores[i].name);

        if (q.execute(query)) {
            Serial.printf("  Sensor '%s' (id=%d) registrado\n",
                          sensores[i].name, sensores[i].id);
        } else {
            Serial.printf("  Error al registrar sensor '%s', posiblemente ya registrado\n",
                          sensores[i].name);
        }
    }
}


// Funcion auxiliar: insertar Measurement + tabla especifica
void insertarMedicion(int id_sensor, const char *tabla,
                      const char *campo, float valor, bool esFloat, bool ok, int is_on = -1) {
    char query[300];

    sprintf(query,
        "INSERT INTO artemus.Measurement (id_sensor, status, elec_consumption, timestamp) "
        "VALUES (%d, %d, 0, NOW())",
        id_sensor, ok ? 1 : 0);

    if (!q.execute(query)) {
        Serial.printf("  Error en Measurement (sensor %d)\n", id_sensor);
        return;
    }
    Serial.printf("  Measurement insertado (sensor %d) - estado: %s\n",
                  id_sensor, ok ? "OK" : "ERROR");

    if (!ok) return;

    if (!q2.execute("SELECT LAST_INSERT_ID()")) {
        Serial.println("  Error obteniendo LAST_INSERT_ID");
        return;
    }

    column_names *cols = q2.get_columns();
    row_values   *row  = q2.get_next_row();
    if (!row) {
        Serial.println("  Sin resultado en LAST_INSERT_ID");
        return;
    }

    int lastId = atoi(row->values[0]);
    Serial.printf("  id_measurement: %d\n", lastId);

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
        Serial.printf("  %s.%s = %.2f insertado\n", tabla, campo, valor);
    } else {
        Serial.printf("  Error en %s (sensor %d)\n", tabla, id_sensor);
    }
}


// DatabaseInsert: insertar datos del sensor biordinario en la BD
// Recibe el valor numerico (int) y el valor alfanumerico (char[]) del sensor.
void DatabaseInsert(int numericValue, char* alphanumericValue) {
    char query[400];

    // 1. Insertar en Measurement
    sprintf(query,
        "INSERT INTO artemus.Measurement (id_sensor, status, elec_consumption, timestamp) "
        "VALUES (%d, 1, 0, NOW())",
        ID_SENSOR_BIORD);

    if (!q.execute(query)) {
        Serial.println("  Error en Measurement (sensor biordinario)");
        return;
    }
    Serial.println("  Measurement insertado (sensor biordinario)");

    // 2. Obtener el ID recien insertado
    if (!q2.execute("SELECT LAST_INSERT_ID()")) {
        Serial.println("  Error obteniendo LAST_INSERT_ID");
        return;
    }

    row_values *row = q2.get_next_row();
    if (!row) {
        Serial.println("  Sin resultado en LAST_INSERT_ID");
        return;
    }

    int lastId = atoi(row->values[0]);
    Serial.printf("  id_measurement: %d\n", lastId);

    // 3. Insertar en tabla Biordinario con el ID real
    sprintf(query,
        "INSERT INTO artemus.Biordinario (id_measurement, numeric_value, alphanumeric_value) "
        "VALUES (%d, %d, '%s')",
        lastId, numericValue, alphanumericValue);

    if (q.execute(query)) {
        Serial.printf("  Biordinario insertado: num=%d  alfa='%s'\n",
                      numericValue, alphanumericValue);
    } else {
        Serial.println("  Error en tabla Biordinario");
    }
}


// Simulacion de la libreria del sensor biordinario
void inicializarSensor(int pin_RX, int pin_TX) {
    Serial.printf("Sensor biordinario inicializado (RX=%d, TX=%d)\n", pin_RX, pin_TX);
}

bool comprobarDatosDisponibles() {
    return true;
}

DatosBiordinario leerDatosOrdinarios() {
    DatosBiordinario datos;
    datos.numerico = random(0, 100);
    snprintf(datos.alfanumerico, sizeof(datos.alfanumerico), "DATO_%d", datos.numerico);
    return datos;
}


void setup() {
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

    // Conexion WiFi
    Serial.print("Conectando a WiFi");
    WiFi.begin(ssid, pass);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi conectado - IP: " + WiFi.localIP().toString());

    // Conexion MySQL
    Serial.print("Conectando a MySQL...");
    while (conn.connectNonBlocking(server_addr, server_port, db_user, db_password) != RESULT_OK) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nMySQL conectado!");

    // Sincronizar hora por NTP
    sincronizarHora();

    // Inicializar sensor biordinario
    inicializarSensor(BIORD_RX_PIN, BIORD_TX_PIN);

    // Registrar sensores fisicos en la BD
    registrarSensores();
}


void loop() {
    Serial.printf("[MEM] Heap libre: %d bytes\n", ESP.getFreeHeap());

    // Reconectar WiFi si se perdio
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
            Serial.println("\nWiFi reconectado - IP: " + WiFi.localIP().toString());
        } else {
            Serial.println("\nNo se pudo reconectar al WiFi, reintentando en el proximo ciclo");
            delay(LOOP_TIME);
            return;
        }
    }

    // Reconectar si se perdio la conexion MySQL
    if (!conn.connected()) {
        Serial.println("Reconectando a MySQL...");
        conn.connectNonBlocking(server_addr, server_port, db_user, db_password);
        delay(5000);
        return;
    }

    // 1. Leer sensores existentes
    float humidity    = dht.readHumidity();
    float temperature = dht.readTemperature();
    int   ldrValue    = analogRead(LDR_PIN);
    int   mqValue     = analogRead(MQ_PIN);

    bool tempOk  = !isnan(temperature);
    bool humOk   = !isnan(humidity);
    bool ldrOk   = (ldrValue >= 0 && ldrValue <= 4095);
    bool mqOk    = (mqValue  >= 0 && mqValue  <= 4095);
    bool fanOn   = temperature > TEMP_THRESHOLD;
    bool ledsOn  = ldrValue   < LDR_THRESHOLD;

    int  horaActual    = obtenerHora();
    bool parqueAbierto = (horaActual >= OPEN_HOUR && horaActual < CLOSE_HOUR);

    Serial.printf("Temp: %s  Hum: %s  Luz: %d  CO2: %d\n",
                  tempOk ? String(temperature).c_str() : "ERROR",
                  humOk  ? String(humidity).c_str()    : "ERROR",
                  ldrValue, mqValue);

    // 2. Insertar mediciones existentes en BD
    insertarMedicion(ID_SENSOR_TEMP,  "Temperature", "temperature",       temperature, true,  tempOk);
    insertarMedicion(ID_SENSOR_HUM,   "Humidity",    "relative_humidity", humidity,    true,  humOk);
    insertarMedicion(ID_SENSOR_LIGHT, "Lighting",    "value",             ldrValue,    false, ldrOk, ledsOn ? 1 : 0);
    insertarMedicion(ID_SENSOR_AIR,   "Air_Quality", "co2_level",         mqValue,     false, mqOk);

    // 3. Leer y almacenar datos del sensor biordinario
    if (comprobarDatosDisponibles()) {
        DatosBiordinario datos = leerDatosOrdinarios();
        DatabaseInsert(datos.numerico, datos.alfanumerico);
    } else {
        Serial.println("Sensor biordinario: sin datos disponibles");
    }

    // 4. Control de actuadores
    digitalWrite(FAN_PIN,  fanOn  ? HIGH : LOW);
    digitalWrite(LEDS_PIN, ledsOn ? HIGH : LOW);

    // Puerta: detectar transicion horaria y actuar una sola vez
    if (parqueAbierto && !ultimoEstadoParque) {
        accionarPuerta("apertura automatica horario");
    } else if (!parqueAbierto && ultimoEstadoParque) {
        accionarPuerta("cierre automatico horario");
    }
    ultimoEstadoParque = parqueAbierto;

    Serial.printf("Hora: %02d | Parque: %s | Ventilador: %s | LEDs: %s\n",
                  horaActual,
                  parqueAbierto ? "ABIERTO" : "CERRADO",
                  fanOn  ? "ON" : "OFF",
                  ledsOn ? "ON" : "OFF");

    delay(LOOP_TIME);
}
