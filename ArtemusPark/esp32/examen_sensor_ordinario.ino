
// Exmane  - Rodrigo Diaz Martinez
// Sensor ordinario simulado
//
// El sensor devuelve dos datos: alfanumerico y solo numerico
// Como no tenemos la libreria real del sensor,
// se simulan las funciones:
// - inicializarsensor()
// - comprobardatosdisponibles()
// - leerDatosordinarios()



// librerias necesarias para WiFi y MySQL
#include <WiFi.h>
#include <MySQL_Connection.h>
#include <MySQL_Cursor.h>


// CONFIGURACION WIFI

char ssid[] = "WIFI";
char pass[] = "Contraseña1";



// configuracion MYSQL


// IP del servidor donde esta la base de datos MySQL
IPAddress server_addr(192, 168, 1, 100);

// Puerto de MySQL
int server_port = 3306;

// Usuario y contraseña de MySQL
char db_user[] = "root";
char db_password[] = "";


// Cliente WiFi y conexion MySQL
WiFiClient client;
MySQL_Connection conn((Client *)&client);



// pines dele sensor


#define SENSOR_RX 16
#define SENSOR_TX 17


=
//estructura para datos del sensor


// Esta estructura representa los dos datos que devuelve el sensor:
// - valorNumerico: dato entero
// - valorTexto: dato alfanumerico

struct DatosOrdinarios {
    int valorNumerico;
    char valorTexto[100];
};



// FUNCIONES SIMULADAS DEL SENSOR


// Simula la inicializacion del sensor con los pines RX y TX
void inicializarsensor(int pinRX, int pinTX) {

    Serial.print("Sensor ordinario inicializado en RX: ");
    Serial.print(pinRX);
    Serial.print(" y TX: ");
    Serial.println(pinTX);
}


// simula la comprobacion de datos disponibles
bool comprobardatosdisponibles() {

    // En una libreria real, aqui se comprobaria si el sensor
    // tiene datos pendientes de lectura.
    // Para la simulacion devolvemos true.
    return true;
}


// Simula la lectura de datos del sensor ordinario
DatosOrdinarios leerDatosordinarios() {

    DatosOrdinarios datos;

    // Simulamos un valor numerico entre 0 y 100
    datos.valorNumerico = random(0, 101);

    // Segun el valor numerico, simulamos un estado alfanumerico
    if (datos.valorNumerico < 40) {
        strcpy(datos.valorTexto, "BAJO");
    } else if (datos.valorNumerico <= 70) {
        strcpy(datos.valorTexto, "NORMAL");
    } else {
        strcpy(datos.valorTexto, "ALTO");
    }

    return datos;
}



//  databaseinsert()
// Recibe los dos valores del sensor y los guarda en MySQL


void databaseinsert(int valorNumerico, char valorTexto[]) {

    // Crear consulta SQL
    char query[300];

    sprintf(
        query,
        "INSERT INTO artemus.Sensor_Ordinario "
        "(valor_numerico, valor_texto) "
        "VALUES (%d, '%s')",
        valorNumerico,
        valorTexto
    );

    // Crear cursor para ejecutar la consulta SQL
    MySQL_Cursor *cursor = new MySQL_Cursor(&conn);

    // Ejecutar INSERT
    cursor->execute(query);

    // Liberar memoria del cursor
    delete cursor;

    // Mensaje de comprobacion
    Serial.println("Datos insertados en la BBDD");
}



// SETUP
// Se ejecuta una sola vez al iniciar


void setup() {

    // Iniciar monitor serie
    Serial.begin(115200);

    // Inicializar semilla para valores aleatorios
    randomSeed(analogRead(0));

    // Inicializar el sensor ordinario simulado
    inicializarsensor(SENSOR_RX, SENSOR_TX);

    // Conectar a WiFi
    WiFi.begin(ssid, pass);

    Serial.print("Conectando a WiFi");

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("WiFi conectado");

    // Conectar con MySQL
    Serial.println("Conectando con MySQL...");

    if (conn.connect(server_addr, server_port, db_user, db_password)) {
        Serial.println("MySQL conectado");
    } else {
        Serial.println("Error al conectar con MySQL");
    }
}



// LOOP
// el bucle que siempre esta ejcutandose


void loop() {

    // comprobar si el sensor tiene datos disponibles
    if (comprobardatosdisponibles()) {


        DatosOrdinarios datos = leerDatosordinarios();   // Leer datos simulados del sensor ordinario

        // Separar los dos datos
        int valorNumerico = datos.valorNumerico;
        char valorTexto[100];

        strcpy(valorTexto, datos.valorTexto);

        // Mostrar datos por consola
        Serial.print("Valor numerico: ");
        Serial.println(valorNumerico);

        Serial.print("Valor texto: ");
        Serial.println(valorTexto);

        // Si MySQL sigue conectado, insertar en BBDD
        if (conn.connected()) {
            databaseinsert(valorNumerico, valorTexto);
        } else {
            Serial.println("No hay conexion con MySQL");
        }
    }

    // Esperar 1 segundo antes de la siguiente lectura
    delay(1000);
}