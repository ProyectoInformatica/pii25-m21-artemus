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
        default_users = {
            "admin1": {
                "password": "admin123",
                "role": "admin",
                "full_name": "Adrian Molina",
                "dni": "11111111A",
                "phone": "600111111",
                "address": "Calle Falsa 123",
            },
            "admin_super": {
                "password": "root2025",
                "role": "admin",
                "full_name": "Sonia Ortega",
                "dni": "22222222B",
                "phone": "600222222",
                "address": "Avenida Siempre Viva 45",
            },
            "boss_artemus": {
                "password": "masterkey",
                "role": "admin",
                "full_name": "Javier Torres",
                "dni": "33333333C",
                "phone": "600333333",
                "address": "Plaza Mayor 1",
            },
            "admin_alpha": {
                "password": "alpha_pass",
                "role": "admin",
                "full_name": "Marta Vega",
                "dni": "44444444D",
                "phone": "600444444",
                "address": "Rua Augusta 10",
            },
            "maint_joe": {
                "password": "fixitnow",
                "role": "maintenance",
                "full_name": "Jose Pardo",
                "dni": "55555555E",
                "phone": "600555555",
                "address": "Paseo de la Castellana 50",
            },
            "tech_sarah": {
                "password": "cables99",
                "role": "maintenance",
                "full_name": "Sara Marin",
                "dni": "66666666F",
                "phone": "600666666",
                "address": "Gran Via 20",
            },
            "eng_mike": {
                "password": "wrench77",
                "role": "maintenance",
                "full_name": "Miguel Rios",
                "dni": "77777777G",
                "phone": "600777777",
                "address": "Via Laietana 30",
            },
            "client_ana": {
                "password": "guest001",
                "role": "user",
                "full_name": "Ana Garcia",
                "dni": "88888888H",
                "phone": "600888888",
                "address": "Calle del Arenal 1",
            },
            "visit_tom": {
                "password": "parkfun2",
                "role": "user",
                "full_name": "Tomas Perez",
                "dni": "99999999I",
                "phone": "600999999",
                "address": "Calle Alcala 15",
            },
            "user_demo": {
                "password": "testpass",
                "role": "user",
                "full_name": "Dario Ponce",
                "dni": "10101010J",
                "phone": "600101010",
                "address": "Calle Mayor 5",
            },
            "user_sofia": {
                "password": "sofia_pass",
                "role": "user",
                "full_name": "Sofia Martin",
                "dni": "12121212K",
                "phone": "600121212",
                "address": "Plaza de Espana 3",
            },
            "user_pedro": {
                "password": "pedro_pass",
                "role": "user",
                "full_name": "Pedro Ruiz",
                "dni": "13131313L",
                "phone": "600131313",
                "address": "Paseo del Prado 10",
            },
            "user_maria": {
                "password": "maria_pass",
                "role": "user",
                "full_name": "Maria Gomez",
                "dni": "14141414M",
                "phone": "600141414",
                "address": "Calle Serrano 25",
            },
            "user_luis": {
                "password": "luis_pass",
                "role": "user",
                "full_name": "Luis Hernandez",
                "dni": "15151515N",
                "phone": "600151515",
                "address": "Ronda de Toledo 5",
            },
            "user_laura": {
                "password": "laura_pass",
                "role": "user",
                "full_name": "Laura Diaz",
                "dni": "16161616O",
                "phone": "600161616",
                "address": "Calle de la Paz 7",
            },
            "user_carlos": {
                "password": "carlos_pass",
                "role": "user",
                "full_name": "Carlos Sanchez",
                "dni": "17171717P",
                "phone": "600171717",
                "address": "Avenida de America 12",
            },
        }

        if not self.data_file.exists():
            self._save_users(default_users)
            return

        try:
            current_users = json.loads(self.data_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            current_users = {}

        if not current_users:
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

    def add_user(self, username, password, role, full_name="", dni="", phone="", address=""):
        """Agrega un nuevo usuario con datos personales."""
        users = self._load_users()
        if username in users:
            raise ValueError("El usuario ya existe.")
        
        users[username] = {
            "password": password, 
            "role": role,
            "full_name": full_name,
            "dni": dni,
            "phone": phone,
            "address": address
        }
        self._save_users(users)

    def update_user(self, username, password=None, role=None, assigned_sensors=None, full_name=None, dni=None, phone=None, address=None):
        """Actualiza datos de un usuario existente."""
        users = self._load_users()
        if username not in users:
            raise ValueError("El usuario no existe.")

        if password:
            users[username]["password"] = password
        if role:
            users[username]["role"] = role
        if assigned_sensors is not None:
            users[username]["assigned_sensors"] = assigned_sensors
        
        if full_name is not None:
            users[username]["full_name"] = full_name
        if dni is not None:
            users[username]["dni"] = dni
        if phone is not None:
            users[username]["phone"] = phone
        if address is not None:
            users[username]["address"] = address

        self._save_users(users)

    def delete_user(self, username):
        """Elimina un usuario."""
        users = self._load_users()
        if username in users:
            del users[username]
            self._save_users(users)
