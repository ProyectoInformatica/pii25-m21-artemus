import threading
import time
import mysql.connector
import socket
from datetime import datetime

# =====================================================================
# CONFIGURACIÓN GLOBAL Y CANDADO DE SEGURIDAD
# =====================================================================
DB_CONFIG = {
    "host": "localhost",
    "database": "artemus",
    "user": "root",
    "password": "",
    "port": 3306
}

# Pongo el sem de 1 para no parar a todos
sem = threading.Semaphore(1)


# =====================================================================
# SISTEMA DE AUDITORÍA (Mantenimiento de Registros)
# =====================================================================
def registrar_auditoria(mensaje):
    """
    Guarda el evento en un archivo de texto con la hora exacta.
    Utiliza un bloque 'with' para gestionar el candado de forma limpia y estructurada.
    """
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea_registro = f"[{hora}] {mensaje}\n"
    conseguido = True
    while conseguido:
        if sem.acquire(timeout=1):
            try:
                with open("auditoria_artemus.log", "a") as archivo:
                    archivo.write(linea_registro)
                sem.release()
                conseguido = False
            except Exception as e:
                print(f"Error al crear archivo: {e}")
                sem.release()
        else:
            time.sleep(1 / 3)


# =====================================================================
# 1. INICIALIZACIÓN DEL POOL
# =====================================================================
def inicializar_pool():
    try:
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="artemus_pool",
            pool_size=5,
            pool_reset_session=True,
            **DB_CONFIG
        )
        print(" Pool de conexiones inicializado. Capacidad máxima: 5 simultáneas.")
        return pool
    except mysql.connector.Error as e:
        print(f"Error crítico al conectar con el servidor: {e}")
        return None


# =====================================================================
# 2. EL TRABAJO DEL HILO (Lógica Estructurada + Logging)
# =====================================================================
def procesar_peticion_usuario(id_usuario, pool, conexion_cliente):
    """
    Gestiona la petición. Los reintentos son para la BBDD.
    La conexión de red se cierra solo al finalizar todos los intentos.
    """
    nombre_hilo = threading.current_thread().name
    registrar_auditoria(f"INFO: {nombre_hilo} atendiendo a Usuario {id_usuario}.")

    max_reintentos = 3
    intento = 0
    conectado = False
    error_critico = False

    while intento < max_reintentos and conectado == False and error_critico == False:
        conexion = None
        try:
            print(f" {nombre_hilo} (Usuario {id_usuario}): Intento BBDD {intento + 1}...")
            conexion = pool.get_connection()

            if conexion.is_connected():
                mensaje_exito = f"ÉXITO: {nombre_hilo} conectó al Usuario {id_usuario}."
                print(f" {mensaje_exito}")
                registrar_auditoria(mensaje_exito)

                # --- AQUÍ IRÍA EL TRABAJO REAL ---
                time.sleep(2)
                # ---------------------------------

                conectado = True

        except mysql.connector.Error as e:
            registrar_auditoria(f"ALERTA: Error BBDD en {nombre_hilo}: {e}")
            if intento < max_reintentos - 1:
                time.sleep(3)  # Espera antes de reintentar

        except Exception as e:
            registrar_auditoria(f"ERROR CRÍTICO: {nombre_hilo} falló: {e}")
            error_critico = True

        finally:
            # Cerramos la conexión a la BBDD en cada intento para no dejar hilos muertos
            if conexion and conexion.is_connected():
                conexion.close()

        intento += 1

    try:
        conexion_cliente.close()
        mensaje_final = f"CIERRE: {nombre_hilo} liberó la red del Usuario {id_usuario}."
        print(f" {mensaje_final}")
        registrar_auditoria(mensaje_final)
    except Exception as e:
        registrar_auditoria(f"ERROR: No se pudo cerrar el socket del usuario {id_usuario}: {e}")

# =====================================================================
# 3. EL SERVIDOR DE ESCUCHA (Lógica Estructurada + Logging)
# =====================================================================


def iniciar_servidor():
    pool = inicializar_pool()
    servidor_activo = True
    while servidor_activo:
        if pool is not None:
            servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip_dir = "0.0.0.0"  # Hay que cambiar la ip a la que tengamos
            puerto = 9789

            try:
                servidor_socket.bind((ip_dir, puerto))
                servidor_socket.listen(5)

                print(f"\nSERVIDOR ARTEMUS ACTIVO en el puerto {puerto}.")
                print(f"Para conectar desde otro PC usa tu IP local y el puerto {puerto}.")
                registrar_auditoria(f"SISTEMA: Servidor iniciado en {ip_dir}:{puerto}")

                servidor_activo = True
                id_usuario_contador = 1

                while servidor_activo:
                    # El programa se detiene aquí hasta que entra alguien
                    conexion_cliente, direccion_remota = servidor_socket.accept()

                    print(f"\n Conexión  detectada desde: {direccion_remota[0]}")
                    registrar_auditoria(f"RED: Conexión entrante desde {direccion_remota[0]}")

                    hilo = threading.Thread(target=procesar_peticion_usuario, args=(id_usuario_contador, pool , conexion_cliente))
                    hilo.start()
                    id_usuario_contador += 1

            except socket.error as e:
                print(f" Error al abrir el socket: {e}")
            except KeyboardInterrupt:
                servidor_activo = False
                print("\nApagando servidor de red...")
            finally:
                servidor_socket.close()
                registrar_auditoria("SISTEMA: Servidor cerrado.")


# =====================================================================
# EJECUCIÓN DIRECTA
# =====================================================================
iniciar_servidor()
