from ArtemusPark.database.DB_Manager import db_manager


class AuthRepository:
    """Repositorio para gestionar la autenticación de usuarios con MariaDB."""

    def authenticate(self, username, password):
        """Verifica las credenciales y devuelve el rol si son correctas."""
        query = """
            SELECT role FROM users 
            WHERE username = %s AND password = %s
        """
        result = db_manager.execute_query(query, (username, password))
        if result:
            return result[0]["role"]
        return None

    def get_all_users(self):
        """Retorna todos los usuarios con sus datos."""
        query = """
            SELECT u.id, u.username, u.role, u.full_name, u.dni, u.phone, u.address,
                   GROUP_CONCAT(DISTINCT s.sensor_id) as assigned_sensors,
                   GROUP_CONCAT(DISTINCT sup.username) as supervisors,
                   GROUP_CONCAT(DISTINCT sub.username) as subordinates
            FROM users u
            LEFT JOIN user_assigned_sensors s ON u.id = s.user_id
            LEFT JOIN user_supervisors us ON u.id = us.user_id
            LEFT JOIN users sup ON us.supervisor_id = sup.id
            LEFT JOIN user_supervisors us2 ON u.id = us2.supervisor_id
            LEFT JOIN users sub ON us2.user_id = sub.id
            GROUP BY u.id
        """
        results = db_manager.execute_query(query)
        users = {}
        for row in results:
            username = row["username"]
            users[username] = {
                "password": "",  # No devolver contraseñas
                "role": row["role"],
                "full_name": row["full_name"],
                "dni": row["dni"],
                "phone": row["phone"],
                "address": row["address"],
            }
            if row["assigned_sensors"]:
                users[username]["assigned_sensors"] = row["assigned_sensors"].split(",")
            if row["supervisors"]:
                users[username]["supervisors"] = row["supervisors"].split(",")
            if row["subordinates"]:
                users[username]["subordinates"] = row["subordinates"].split(",")
        return users

    def get_user_by_username(self, username):
        """Obtiene un usuario específico por su nombre de usuario."""
        query = """
            SELECT u.id, u.username, u.password, u.role, u.full_name, u.dni, u.phone, u.address,
                   GROUP_CONCAT(DISTINCT s.sensor_id) as assigned_sensors,
                   GROUP_CONCAT(DISTINCT s.sensor_type) as sensor_types,
                   GROUP_CONCAT(DISTINCT sup.username) as supervisors,
                   GROUP_CONCAT(DISTINCT sub.username) as subordinates
            FROM users u
            LEFT JOIN user_assigned_sensors s ON u.id = s.user_id
            LEFT JOIN user_supervisors us ON u.id = us.user_id
            LEFT JOIN users sup ON us.supervisor_id = sup.id
            LEFT JOIN user_supervisors us2 ON u.id = us2.supervisor_id
            LEFT JOIN users sub ON us2.user_id = sub.id
            WHERE u.username = %s
            GROUP BY u.id
        """
        result = db_manager.execute_query(query, (username,))
        if not result:
            return None
        
        row = result[0]
        user = {
            "password": row["password"],
            "role": row["role"],
            "full_name": row["full_name"],
            "dni": row["dni"],
            "phone": row["phone"],
            "address": row["address"],
        }
        
        if row["assigned_sensors"]:
            sensors = row["assigned_sensors"].split(",")
            types = row["sensor_types"].split(",") if row["sensor_types"] else []
            user["assigned_sensors"] = sensors
            user["sensor_types"] = types
        if row["supervisors"]:
            user["supervisors"] = row["supervisors"].split(",")
        if row["subordinates"]:
            user["subordinates"] = row["subordinates"].split(",")
        
        return user

    def add_user(
        self, username, password, role, full_name="", dni="", phone="", address=""
    ):
        """Agrega un nuevo usuario con datos personales."""
        query = """
            INSERT INTO users (username, password, role, full_name, dni, phone, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            db_manager.execute_insert(query, (username, password, role, full_name, dni, phone, address))
        except Exception as e:
            if "Duplicate entry" in str(e):
                raise ValueError("El usuario ya existe.")
            raise

    def update_user(
        self,
        username,
        password=None,
        role=None,
        assigned_sensors=None,
        full_name=None,
        dni=None,
        phone=None,
        address=None,
        supervisors=None,
        subordinates=None,
    ):
        """Actualiza datos de un usuario existente."""
        # Obtener ID del usuario
        user_query = "SELECT id FROM users WHERE username = %s"
        user_result = db_manager.execute_query(user_query, (username,))
        if not user_result:
            raise ValueError("El usuario no existe.")
        
        user_id = user_result[0]["id"]
        
        # Actualizar campos básicos
        updates = []
        params = []
        if password is not None:
            updates.append("password = %s")
            params.append(password)
        if role is not None:
            updates.append("role = %s")
            params.append(role)
        if full_name is not None:
            updates.append("full_name = %s")
            params.append(full_name)
        if dni is not None:
            updates.append("dni = %s")
            params.append(dni)
        if phone is not None:
            updates.append("phone = %s")
            params.append(phone)
        if address is not None:
            updates.append("address = %s")
            params.append(address)
        
        if updates:
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            params.append(user_id)
            db_manager.execute_update(query, tuple(params))
        
        # Actualizar sensores asignados
        if assigned_sensors is not None:
            # Eliminar sensores actuales
            db_manager.execute_update(
                "DELETE FROM user_assigned_sensors WHERE user_id = %s", (user_id,)
            )
            # Insertar nuevos sensores
            for sensor_data in assigned_sensors:
                if isinstance(sensor_data, dict):
                    sensor_id = sensor_data.get("sensor_id")
                    sensor_type = sensor_data.get("sensor_type", "unknown")
                else:
                    sensor_id = sensor_data
                    sensor_type = "unknown"
                
                db_manager.execute_insert(
                    """INSERT INTO user_assigned_sensors (user_id, sensor_id, sensor_type)
                       VALUES (%s, %s, %s)""",
                    (user_id, sensor_id, sensor_type)
                )
        
        # Actualizar supervisores
        if supervisors is not None:
            db_manager.execute_update(
                "DELETE FROM user_supervisors WHERE user_id = %s", (user_id,)
            )
            for supervisor_username in supervisors:
                sup_query = "SELECT id FROM users WHERE username = %s"
                sup_result = db_manager.execute_query(sup_query, (supervisor_username,))
                if sup_result:
                    db_manager.execute_insert(
                        "INSERT INTO user_supervisors (user_id, supervisor_id) VALUES (%s, %s)",
                        (user_id, sup_result[0]["id"])
                    )

    def delete_user(self, username):
        """Elimina un usuario y sus relaciones."""
        query = "DELETE FROM users WHERE username = %s"
        db_manager.execute_update(query, (username,))

    def get_users_by_role(self, role):
        """Obtiene todos los usuarios de un rol específico."""
        query = """
            SELECT username, full_name, dni, phone, address
            FROM users WHERE role = %s
        """
        return db_manager.execute_query(query, (role,))

    def get_maintenance_users(self):
        """Obtiene todos los usuarios de mantenimiento con sus sensores."""
        query = """
            SELECT u.username, u.full_name, 
                   GROUP_CONCAT(DISTINCT s.sensor_id) as sensors
            FROM users u
            LEFT JOIN user_assigned_sensors s ON u.id = s.user_id
            WHERE u.role = 'maintenance'
            GROUP BY u.id
        """
        return db_manager.execute_query(query)
