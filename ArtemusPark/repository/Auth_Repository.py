class AuthRepository:
    def __init__(self):
        # En una aplicación real, esto vendría de una base de datos hash
        self._users = {
            # Admins
            "admin1": {"password": "admin123", "role": "admin"},
            "admin_super": {"password": "root2025", "role": "admin"},
            "boss_artemus": {"password": "masterkey", "role": "admin"},
            
            # Maintenance
            "maint_joe": {"password": "fixitnow", "role": "maintenance"},
            "tech_sarah": {"password": "cables99", "role": "maintenance"},
            "eng_mike": {"password": "wrench77", "role": "maintenance"},
            
            # Users
            "client_ana": {"password": "guest001", "role": "user"},
            "visit_tom": {"password": "parkfun2", "role": "user"},
            "user_demo": {"password": "testpass", "role": "user"},
        }

    def authenticate(self, username, password):
        """
        Verifica las credenciales y devuelve el rol si son correctas.
        Retorna None si fallan.
        """
        if username in self._users:
            user_data = self._users[username]
            if user_data["password"] == password:
                return user_data["role"]
        return None
