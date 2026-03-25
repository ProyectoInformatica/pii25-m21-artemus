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
    "port": 3306,
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
            pool_name="artemus_pool", pool_size=5, pool_reset_session=True, **DB_CONFIG
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
    Gestiona la peticion de un usuario real.
    Conecta a la BBDD, realiza operaciones SQL y cierra la red al terminar.
    """
    nombre_hilo = threading.current_thread().name
    registrar_auditoria(f"INFO: {nombre_hilo} atendiendo a Usuario {id_usuario} (RED REAL).")

    # Variables de estado para control estructurado
    max_reintentos = 3
    intento = 0
    conectado_bbdd = False
    error_critico = False

    # Bucle de reintentos para la base de datos
    while intento < max_reintentos and conectado_bbdd == False and error_critico == False:
        conexion = None
        try:
            # 1. Pedir conexion al Pool
            print(f" Intentando conectar a MariaDB (Intento {intento + 1})...")
            conexion = pool.get_connection()

            if conexion.is_connected():
                registrar_auditoria(f"EXITO: {nombre_hilo} obtuvo conexion del pool para ID {id_usuario}.")

                # =========================================================
                # TRABAJO REAL: OPERACIONES SQL
                # =========================================================
                cursor = conexion.cursor(dictionary=True)

                # Consultamos si el usuario existe en Artemus Park
                sql_check = "SELECT nombre_usuario, id_rol FROM Usuario WHERE usuario = %s"
                cursor.execute(sql_check, (id_usuario,))
                usuario = cursor.fetchone()

                if usuario:
                    msg_log = f"ACCESO: {usuario['nombre_usuario']} (Rol {usuario['id_rol']}) ha entrado."
                    print(f" {msg_log}")
                    registrar_auditoria(f"BBDD: {msg_log}")
                else:
                    registrar_auditoria(f"ALERTA: Usuario {id_usuario} no encontrado en la BBDD.")

                cursor.close()
                # Marcamos exito para salir del bucle de reintentos
                conectado_bbdd = True
                # =========================================================

        except mysql.connector.Error as e:
            msg_err = f"ALERTA: Error de MariaDB en {nombre_hilo}: {e}"
            print(f" {msg_err}")
            registrar_auditoria(msg_err)
            # Si falla, esperamos un poco antes del siguiente intento
            time.sleep(2)

        except Exception as e:
            msg_crit = f"ERROR CRITICO en {nombre_hilo}: {e}"
            print(f" {msg_crit}")
            registrar_auditoria(msg_crit)
            error_critico = True

        finally:
            # Liberamos la conexion de la BBDD al pool en cada intento
            if conexion and conexion.is_connected():
                conexion.close()
                registrar_auditoria(f"POOL: {nombre_hilo} devolvio conexion al pool.")

        intento += 1

    # --- CIERRE DE COMUNICACION ---
    # Una vez terminados los intentos, cerramos la conexion de red con el cliente
    try:
        conexion_cliente.close()
        registrar_auditoria(f"FIN: Conexion de red cerrada para Usuario {id_usuario}.")
    except Exception as e:
        registrar_auditoria(f"ERROR: Fallo al cerrar socket del Usuario {id_usuario}: {e}")


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
                print(
                    f"Para conectar desde otro PC usa tu IP local y el puerto {puerto}."
                )
                registrar_auditoria(f"SISTEMA: Servidor iniciado en {ip_dir}:{puerto}")

                servidor_activo = True
                id_usuario_contador = 1

                while servidor_activo:
                    # El programa se detiene aquí hasta que entra alguien
                    conexion_cliente, direccion_remota = servidor_socket.accept()

                    print(f"\n Conexión  detectada desde: {direccion_remota[0]}")
                    registrar_auditoria(
                        f"RED: Conexión entrante desde {direccion_remota[0]}"
                    )

                    hilo = threading.Thread(
                        target=procesar_peticion_usuario,
                        args=(id_usuario_contador, pool, conexion_cliente),
                    )
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
