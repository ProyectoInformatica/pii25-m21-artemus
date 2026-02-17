from ArtemusPark.database.DB_Manager import db_manager


class RequestsRepository:
    """Repositorio para gestionar solicitudes con MariaDB."""

    def create_request(self, username, message, request_type="sensor_change"):
        """Crea una nueva solicitud en la base de datos."""
        # Obtener ID del usuario
        user_query = "SELECT id FROM users WHERE username = %s"
        user_result = db_manager.execute_query(user_query, (username,))

        if not user_result:
            raise ValueError(f"Usuario {username} no encontrado")

        user_id = user_result[0]["id"]

        query = """
            INSERT INTO requests (user_id, request_type, message, status)
            VALUES (%s, %s, %s, 'PENDING')
        """
        request_id = db_manager.execute_insert(query, (user_id, request_type, message))
        return request_id

    def get_all_requests(self):
        """Obtiene todas las solicitudes con información del usuario."""
        query = """
            SELECT 
                r.id,
                u.username as user,
                r.request_type as type,
                r.message,
                r.status,
                r.created_at as timestamp
            FROM requests r
            JOIN users u ON r.user_id = u.id
            ORDER BY r.created_at DESC
        """
        return db_manager.execute_query(query)

    def get_requests_by_user(self, username):
        """Obtiene las solicitudes de un usuario específico."""
        query = """
            SELECT 
                r.id,
                u.username as user,
                r.request_type as type,
                r.message,
                r.status,
                r.created_at as timestamp
            FROM requests r
            JOIN users u ON r.user_id = u.id
            WHERE u.username = %s
            ORDER BY r.created_at DESC
        """
        return db_manager.execute_query(query, (username,))

    def get_pending_requests(self):
        """Obtiene solo las solicitudes pendientes."""
        query = """
            SELECT 
                r.id,
                u.username as user,
                r.request_type as type,
                r.message,
                r.status,
                r.created_at as timestamp
            FROM requests r
            JOIN users u ON r.user_id = u.id
            WHERE r.status = 'PENDING'
            ORDER BY r.created_at DESC
        """
        return db_manager.execute_query(query)

    def update_request_status(self, request_id, new_status):
        """Actualiza el estado de una solicitud."""
        query = """
            UPDATE requests 
            SET status = %s 
            WHERE id = %s
        """
        rows_affected = db_manager.execute_update(query, (new_status, request_id))
        return rows_affected > 0

    def delete_request(self, request_id):
        """Elimina una solicitud por su ID."""
        query = "DELETE FROM requests WHERE id = %s"
        rows_affected = db_manager.execute_update(query, (request_id,))
        return rows_affected > 0

    def get_request_by_id(self, request_id):
        """Obtiene una solicitud específica por ID."""
        query = """
            SELECT 
                r.id,
                u.username as user,
                r.request_type as type,
                r.message,
                r.status,
                r.created_at as timestamp
            FROM requests r
            JOIN users u ON r.user_id = u.id
            WHERE r.id = %s
        """
        result = db_manager.execute_query(query, (request_id,))
        return result[0] if result else None
