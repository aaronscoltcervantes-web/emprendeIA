import os
import json
import time
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivy.utils import platform
from plyer import camera

# Solicitar permisos en Android al iniciar
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.CAMERA, 
        Permission.WRITE_EXTERNAL_STORAGE, 
        Permission.READ_EXTERNAL_STORAGE
    ])

KV = '''
MDScreen:
    md_bg_color: self.theme_cls.background_palette

    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(20)
        adaptive_height: True
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

        # Título de la App
        MDLabel:
            text: "Registro Promoción Óptica"
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            bold: True
            theme_text_color: "Primary"

        # Campo de Texto para el Nombre
        MDTextField:
            id: client_name
            hint_text: "Nombre Completo del Cliente"
            helper_text: "Obligatorio para el registro"
            helper_text_mode: "on_error"
            icon_right: "account"
            required: True
            font_size: "18sp"

        # Botón Foto Montura
        MDRaisedButton:
            text: "Tomar Foto de la Montura"
            icon: "camera"
            size_hint_x: 1
            on_release: app.take_montura_photo()
            md_bg_color: self.theme_cls.primary_color

        # Botón Foto Carnet
        MDRaisedButton:
            text: "Tomar Foto del Carnet"
            icon: "card-account-details"
            size_hint_x: 1
            on_release: app.take_carnet_photo()
            md_bg_color: self.theme_cls.primary_color

        # Botón Guardar Registro
        MDRaisedButton:
            text: "Guardar Registro Local"
            icon: "content-save"
            size_hint_x: 1
            on_release: app.save_record()
            md_bg_color: app.theme_cls.accent_color
'''

class OpticaApp(MDApp):
    dialog = None

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Teal"
        
        # Rutas temporales para las imágenes
        self.current_montura_path = ""
        self.current_carnet_path = ""
        
        return Builder.load_string(KV)

    def show_dialog(self, title, text):
        if not self.dialog:
            self.dialog = MDDialog(
                title=title,
                text=text,
                buttons=[
                    MDRaisedButton(
                        text="ACEPTAR",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ],
            )
        else:
            self.dialog.title = title
            self.dialog.text = text
        self.dialog.open()

    def take_montura_photo(self):
        filename = os.path.join(self.user_data_dir, f"montura_{int(time.time())}.jpg")
        self.current_montura_path = filename
        try:
            camera.take_picture(filename=filename, on_complete=self.montura_callback)
        except Exception as e:
            self.show_dialog("Error", f"No se pudo iniciar la cámara: {e}")

    def montura_callback(self, filename):
        if filename and os.path.exists(filename):
            self.show_dialog("Éxito", "Foto de la montura capturada correctamente.")
        else:
            self.current_montura_path = ""
            self.show_dialog("Aviso", "Captura de montura cancelada o fallida.")

    def take_carnet_photo(self):
        filename = os.path.join(self.user_data_dir, f"carnet_{int(time.time())}.jpg")
        self.current_carnet_path = filename
        try:
            camera.take_picture(filename=filename, on_complete=self.carnet_callback)
        except Exception as e:
            self.show_dialog("Error", f"No se pudo iniciar la cámara: {e}")

    def carnet_callback(self, filename):
        if filename and os.path.exists(filename):
            self.show_dialog("Éxito", "Foto del carnet capturada correctamente.")
        else:
            self.current_carnet_path = ""
            self.show_dialog("Aviso", "Captura de carnet cancelada o fallida.")

    def save_record(self):
        name = self.root.ids.client_name.text.strip()
        
        # Validaciones de campos y fotos
        if not name:
            self.show_dialog("Atención", "Por favor ingresa el nombre completo del cliente.")
            return
        if not self.current_montura_path or not os.path.exists(self.current_montura_path):
            self.show_dialog("Atención", "Es obligatorio tomar la foto de la montura.")
            return
        if not self.current_carnet_path or not os.path.exists(self.current_carnet_path):
            self.show_dialog("Atención", "Es obligatorio tomar la foto del carnet de identidad.")
            return

        # Estructura del registro
        record = {
            "nombre_cliente": name,
            "foto_montura": self.current_montura_path,
            "foto_carnet": self.current_carnet_path,
            "fecha_registro": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Ruta del archivo JSON local
        json_path = os.path.join(self.user_data_dir, "registros_optica.json")
        
        data = []
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = []

        data.append(record)

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            self.show_dialog("¡Registro Guardado!", f"Los datos y rutas se almacenaron localmente en:\n{json_path}")
            self.reset_form()
        except Exception as e:
            self.show_dialog("Error", f"No se pudo guardar el archivo JSON: {e}")

    def reset_form(self):
        self.root.ids.client_name.text = ""
        self.current_montura_path = ""
        self.current_carnet_path = ""

if __name__ == "__main__":
    OpticaApp().run()
