import os
import json
import time
import traceback

from kivy.lang import Builder
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton

# plyer se importa de forma segura: si falla, la app igual arranca
camera = None
try:
    from plyer import camera
except Exception:
    traceback.print_exc()

KV = '''
MDScreen:
    md_bg_color: self.theme_cls.bg_normal

    ScrollView:
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(24)
            spacing: dp(16)
            adaptive_height: True

            MDLabel:
                text: "Registro Promoción Óptica"
                font_style: "H5"
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1]
                bold: True
                theme_text_color: "Primary"

            MDTextField:
                id: client_name
                hint_text: "Nombre Completo del Cliente"
                helper_text: "Obligatorio"
                helper_text_mode: "on_error"
                icon_right: "account"

            MDTextField:
                id: client_carnet
                hint_text: "Número de Carnet de Identidad (CI)"
                helper_text: "Documento de identidad"
                helper_text_mode: "on_error"
                icon_right: "card-account-details"

            MDTextField:
                id: lens_ticket
                hint_text: "Número de Ficha del Lente"
                helper_text: "Número de receta o ficha asignada"
                helper_text_mode: "on_error"
                icon_right: "glasses"

            MDRaisedButton:
                text: "Tomar Foto de la Montura"
                size_hint_x: 1
                on_release: app.take_montura_photo()

            MDRaisedButton:
                text: "Tomar Foto del Carnet"
                size_hint_x: 1
                on_release: app.take_carnet_photo()

            MDRaisedButton:
                text: "Guardar Registro Local"
                size_hint_x: 1
                on_release: app.save_record()

            MDRaisedButton:
                text: "Compartir Último Registro"
                size_hint_x: 1
                md_bg_color: app.theme_cls.accent_color
                on_release: app.share_last_record()
'''


class OpticaApp(MDApp):
    dialog = None
    current_montura_path = ""
    current_carnet_path = ""

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Teal"
        return Builder.load_string(KV)

    def on_start(self):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.CAMERA])
            except Exception:
                traceback.print_exc()
            try:
                # Evita FileUriExposedException al usar la cámara con plyer
                from jnius import autoclass
                autoclass('android.os.StrictMode').disableDeathOnFileUriExposure()
            except Exception:
                traceback.print_exc()

    # ---------- utilidades ----------
    def photo_dir(self):
        """Carpeta donde la app de cámara puede escribir la foto."""
        if platform == 'android':
            try:
                from jnius import autoclass
                act = autoclass('org.kivy.android.PythonActivity').mActivity
                d = act.getExternalFilesDir(None).getAbsolutePath()
                os.makedirs(d, exist_ok=True)
                return d
            except Exception:
                traceback.print_exc()
        return self.user_data_dir

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

    # ---------- fotos ----------
    def take_montura_photo(self):
        if camera is None:
            self.show_dialog("Error", "La cámara no está disponible en este dispositivo.")
            return
        filename = os.path.join(self.photo_dir(), f"montura_{int(time.time())}.jpg")
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
        if camera is None:
            self.show_dialog("Error", "La cámara no está disponible en este dispositivo.")
            return
        filename = os.path.join(self.photo_dir(), f"carnet_{int(time.time())}.jpg")
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

    # ---------- registro ----------
    def save_record(self):
        name = self.root.ids.client_name.text.strip()
        carnet = self.root.ids.client_carnet.text.strip()
        ticket = self.root.ids.lens_ticket.text.strip()

        if not name or not carnet or not ticket:
            self.show_dialog("Atención", "Por favor completa todos los campos (Nombre, Carnet y Ficha).")
            return
        if not self.current_montura_path or not os.path.exists(self.current_montura_path):
            self.show_dialog("Atención", "Es obligatorio tomar la foto de la montura.")
            return
        if not self.current_carnet_path or not os.path.exists(self.current_carnet_path):
            self.show_dialog("Atención", "Es obligatorio tomar la foto del carnet.")
            return

        record = {
            "nombre_cliente": name,
            "numero_carnet": carnet,
            "numero_ficha": ticket,
            "foto_montura": self.current_montura_path,
            "foto_carnet": self.current_carnet_path,
            "fecha_registro": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

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
            self.show_dialog("¡Guardado!", "El registro del cliente se guardó con éxito.")
            self.reset_form()
        except Exception as e:
            self.show_dialog("Error", f"No se pudo guardar el archivo JSON: {e}")

    # ---------- compartir ----------
    def share_text_android(self, text):
        from jnius import autoclass, cast
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        String = autoclass('java.lang.String')
        intent = Intent(Intent.ACTION_SEND)
        intent.setType('text/plain')
        intent.putExtra(Intent.EXTRA_TEXT, cast('java.lang.CharSequence', String(text)))
        chooser = Intent.createChooser(
            intent, cast('java.lang.CharSequence', String('Compartir Registro Óptica'))
        )
        PythonActivity.mActivity.startActivity(chooser)

    def share_last_record(self):
        json_path = os.path.join(self.user_data_dir, "registros_optica.json")
        if not os.path.exists(json_path):
            self.show_dialog("Aviso", "No hay registros guardados todavía.")
            return
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not data:
                self.show_dialog("Aviso", "La lista de registros está vacía.")
                return

            last = data[-1]
            text_to_share = (
                f"REGISTRO PROMOCIÓN ÓPTICA\n\n"
                f"Cliente: {last.get('nombre_cliente')}\n"
                f"Carnet (CI): {last.get('numero_carnet')}\n"
                f"N° Ficha Lente: {last.get('numero_ficha')}\n"
                f"Fecha: {last.get('fecha_registro')}"
            )

            if platform == 'android':
                self.share_text_android(text_to_share)
            else:
                self.show_dialog("Vista previa de compartir", text_to_share)
        except Exception as e:
            self.show_dialog("Error", f"No se pudo compartir: {e}")

    def reset_form(self):
        self.root.ids.client_name.text = ""
        self.root.ids.client_carnet.text = ""
        self.root.ids.lens_ticket.text = ""
        self.current_montura_path = ""
        self.current_carnet_path = ""


if __name__ == "__main__":
    OpticaApp().run()
