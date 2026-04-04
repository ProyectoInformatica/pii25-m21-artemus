import flet as ft
import base64
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.repository.Auth_Repository import AuthRepository

class ProfilePage(ft.Container):
    def __init__(self, username):
        super().__init__()
        self.expand = True
        self.bgcolor = AppColors.BG_MAIN
        self.padding = 40
        self.username = username
        self.auth_repo = AuthRepository()
        
        # UI Elements
        self.tf_full_name = ft.TextField(label="Nombre Completo", width=400, color="black")
        self.tf_dni = ft.TextField(label="DNI", width=400, color="black")
        self.tf_phone = ft.TextField(label="Teléfono", width=400, color="black")
        self.tf_street = ft.TextField(label="Calle / Dirección", width=400, color="black")
        self.tf_city = ft.TextField(label="Ciudad", width=400, color="black")
        self.tf_zip = ft.TextField(label="Código Postal", width=400, color="black")
        self.tf_pass = ft.TextField(label="Nueva Contraseña (opcional)", width=400, password=True, can_reveal_password=True, color="black")
        
        self.user_avatar = ft.CircleAvatar(
            radius=50,
            content=ft.Text(self.username[0].upper(), size=30),
            bgcolor=ft.Colors.BLUE_GREY_700,
        )
        
        self.file_picker = ft.FilePicker(on_result=self._on_file_result)
        
        self.content = self._build_ui()

    def did_mount(self):
        if self.page:
            self.page.overlay.append(self.file_picker)
            self.page.update()
        self._load_data()

    def _load_data(self):
        data = self.auth_repo.get_user_by_username(self.username)
        if data:
            self.tf_full_name.value = data.get("full_name", "")
            self.tf_dni.value = data.get("dni", "")
            self.tf_phone.value = data.get("phone", "")
            self.tf_street.value = data.get("address_street", "")
            self.tf_city.value = data.get("address_city", "")
            self.tf_zip.value = data.get("address_zip", "")
            
            profile_pic = self.auth_repo.get_user_profile_picture(self.username)
            if profile_pic:
                b64 = base64.b64encode(profile_pic).decode("utf-8")
                self.user_avatar.content = ft.Image(src_base64=b64, border_radius=50, fit=ft.ImageFit.COVER)
                self.user_avatar.bgcolor = ft.Colors.TRANSPARENT
            
            self.update()

    def _on_file_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            with open(e.files[0].path, "rb") as f:
                img_bytes = f.read()
            
            user_data = self.auth_repo.get_user_by_username(self.username)
            self.auth_repo.update_user(user_data["dni"], profile_picture=img_bytes)
            
            self.page.pubsub.send_all({"topic": "profile_updated", "username": self.username})
            self._load_data()
            self.page.open(ft.SnackBar(ft.Text("Foto de perfil actualizada"), bgcolor="green"))

    def _handle_save(self, e):
        if not self.tf_full_name.value or not self.tf_dni.value or not self.tf_phone.value:
            self.page.open(ft.SnackBar(ft.Text("Nombre, DNI y Teléfono son obligatorios"), bgcolor="red"))
            return
            
        user_data = self.auth_repo.get_user_by_username(self.username)
        update_data = {
            "full_name": self.tf_full_name.value,
            "phone": self.tf_phone.value,
            "address_street": self.tf_street.value,
            "address_city": self.tf_city.value,
            "address_zip": self.tf_zip.value,
        }
        
        if self.tf_pass.value:
            update_data["password"] = self.tf_pass.value
            
        if self.tf_dni.value != user_data["dni"]:
            update_data["new_dni"] = self.tf_dni.value
            
        self.auth_repo.update_user(user_data["dni"], **update_data)
        self.page.pubsub.send_all({"topic": "profile_updated", "username": self.username})
        self.page.open(ft.SnackBar(ft.Text("Perfil actualizado correctamente"), bgcolor="green"))

    def _build_ui(self):
        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Text("Mi Perfil", size=32, weight=ft.FontWeight.BOLD, color="black"),
                ft.Stack([
                    self.user_avatar,
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        bgcolor=ft.Colors.WHITE,
                        icon_color="blue",
                        top=60,
                        right=0,
                        on_click=lambda _: self.file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)
                    )
                ]),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Datos Personales", size=18, weight="bold", color="black"),
                        self.tf_full_name,
                        self.tf_dni,
                        self.tf_phone,
                    ], spacing=10),
                    bgcolor=ft.Colors.WHITE,
                    padding=20,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Dirección", size=18, weight="bold", color="black"),
                        self.tf_street,
                        self.tf_city,
                        self.tf_zip,
                    ], spacing=10),
                    bgcolor=ft.Colors.WHITE,
                    padding=20,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Seguridad", size=18, weight="bold", color="black"),
                        self.tf_pass,
                    ], spacing=10),
                    bgcolor=ft.Colors.WHITE,
                    padding=20,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                ),
                ft.ElevatedButton(
                    "Guardar Cambios",
                    icon=ft.Icons.SAVE,
                    bgcolor="blue",
                    color="white",
                    on_click=self._handle_save,
                    width=200,
                    height=50
                ),
                ft.Container(height=20) # Bottom padding
            ]
        )
