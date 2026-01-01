import json
from pathlib import Path


class AuthRepository:
    """Repositorio para gestionar la autenticación de usuarios con persistencia JSON."""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.data_file = self.base_dir / "json" / "users.json"
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Crea el archivo users.json con datos por defecto si no existe."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            default_users = {
                "admin1": {"password": "admin123", "role": "admin"},
                "admin_super": {"password": "root2025", "role": "admin"},
                "boss_artemus": {"password": "masterkey", "role": "admin"},
                "admin_alpha": {"password": "alpha_pass", "role": "admin"},
                "maint_joe": {"password": "fixitnow", "role": "maintenance"},
                "tech_sarah": {"password": "cables99", "role": "maintenance"},
                "eng_mike": {"password": "wrench77", "role": "maintenance"},
                "client_ana": {"password": "guest001", "role": "user"},
                "visit_tom": {"password": "parkfun2", "role": "user"},
                "user_demo": {"password": "testpass", "role": "user"},
                "user_sofia": {"password": "sofia_pass", "role": "user"},
                "user_pedro": {"password": "pedro_pass", "role": "user"},
                "user_maria": {"password": "maria_pass", "role": "user"},
                "user_luis": {"password": "luis_pass", "role": "user"},
                "user_laura": {"password": "laura_pass", "role": "user"},
                "user_carlos": {"password": "carlos_pass", "role": "user"},
            }
            self._save_users(default_users)

    def _load_users(self):
        """Carga los usuarios del archivo JSON."""
        try:
            return json.loads(self.data_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_users(self, users):
        """Guarda los usuarios en el archivo JSON."""
        self.data_file.write_text(json.dumps(users, indent=4), encoding="utf-8")

    def authenticate(self, username, password):
        """Verifica las credenciales y devuelve el rol si son correctas."""
        users = self._load_users()
        if username in users:
            user_data = users[username]
            if user_data["password"] == password:
                return user_data["role"]
        return None

    def get_all_users(self):
        """Retorna todos los usuarios."""
        return self._load_users()

    def add_user(self, username, password, role):
        """Agrega un nuevo usuario."""
        users = self._load_users()
        if username in users:
            raise ValueError("El usuario ya existe.")
        users[username] = {"password": password, "role": role}
        self._save_users(users)

    def update_user(self, username, password=None, role=None, assigned_sensors=None):
        """Actualiza la contraseña, rol o sensores asignados de un usuario existente."""
        users = self._load_users()
        if username not in users:
            raise ValueError("El usuario no existe.")

        if password:
            users[username]["password"] = password
        if role:
            users[username]["role"] = role
        if assigned_sensors is not None:
            users[username]["assigned_sensors"] = assigned_sensors

        self._save_users(users)

    def delete_user(self, username):
        """Elimina un usuario."""
        users = self._load_users()
        if username in users:
            del users[username]
            self._save_users(users)
