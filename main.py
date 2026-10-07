import os
import json
import time
import shutil
import traceback

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.utils import platform, escape_markup
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel

REQ_CAMERA = 4711
RESULT_OK = -1
PHOTO_SUBDIR = "Pictures/RegistroOptica"

KV = '''
MDScreen:
    md_bg_color: self.theme_cls.bg_normal

    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            id: toolbar
            title: "Registro Óptica"
            right_action_items: [["format-list-bulleted", lambda x: app.open_list()]]

        MDScreenManager:
            id: sm

            # ---------------- FORMULARIO ----------------
            MDScreen:
                name: "form"

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
                            on_release: app.take_photo("montura")

                        MDRaisedButton:
                            text: "Tomar Foto del Carnet"
                            size_hint_x: 1
                            on_release: app.take_photo("carnet")

                        MDBoxLayout:
                            spacing: dp(8)
                            size_hint_y: None
                            height: dp(120)

                            Image:
                                id: montura_preview

                            Image:
                                id: carnet_preview

                        MDRaisedButton:
                            text: "Guardar Registro Local"
                            size_hint_x: 1
                            on_release: app.save_record()

                        MDRaisedButton:
                            text: "Compartir Último Registro"
                            size_hint_x: 1
                            md_bg_color: app.theme_cls.accent_color
                            on_release: app.share_last_record()

            # ---------------- LISTA DE CLIENTES ----------------
            MDScreen:
                name: "list"

                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(12)
                    spacing: dp(8)

                    MDRaisedButton:
                        text: "Nuevo registro"
                        size_hint_x: 1
                        on_release: app.open_form()

                    ScrollView:
                        MDBoxLayout:
                            id: list_box
                            orientation: 'vertical'
                            spacing: dp(12)
                            padding: [0, 0, 0, dp(12)]
                            adaptive_height: True
'''


class TapImage(ButtonBehavior, Image):
    """Imagen que se puede tocar para verla en grande."""
    pass


class OpticaApp(MDApp):
    dialog = None
    current_montura_path = ""
    current_carnet_path = ""
    _pending = None

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Teal"
        return Builder.load_string(KV)

    def on_start(self):
        Window.bind(on_keyboard=self.on_key)

    def on_pause(self):
        # IMPRESCINDIBLE en Android: sin esto la app se reinicia/congela
        # al abrir la cámara externa.
        return True

    def on_resume(self):
        pass

    def on_key(self, window, key, *args):
        # Botón "atrás" de Android: desde la lista vuelve al formulario
        if key == 27 and self.root.ids.sm.current == "list":
            self.open_form()
            return True
        return False

    # ------------------------------------------------------------------
    # Navegación
    # ------------------------------------------------------------------
    def open_list(self):
        self.root.ids.sm.current = "list"
        self.root.ids.toolbar.title = "Clientes guardados"
        self.refresh_list()

    def open_form(self):
        self.root.ids.sm.current = "form"
        self.root.ids.toolbar.title = "Registro Óptica"

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
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

    @property
    def json_path(self):
        return os.path.join(self.user_data_dir, "registros_optica.json")

    def load_records(self):
        if not os.path.exists(self.json_path):
            return []
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def thumb_of(path):
        base, ext = os.path.splitext(path)
        return f"{base}_thumb{ext}"

    @staticmethod
    def process_image(path):
        """Corrige la rotación EXIF, reduce el tamaño y crea una miniatura."""
        try:
            from PIL import Image as PILImage, ImageOps
            img = PILImage.open(path)
            img = ImageOps.exif_transpose(img).convert("RGB")
            img.thumbnail((1600, 1600))
            img.save(path, "JPEG", quality=85)
            thumb = OpticaApp.thumb_of(path)
            img.thumbnail((400, 400))
            img.save(thumb, "JPEG", quality=80)
        except Exception:
            traceback.print_exc()

    # ------------------------------------------------------------------
    # Cámara (Intent nativo + MediaStore, sin plyer ni permisos)
    # ------------------------------------------------------------------
    def take_photo(self, kind):
        if platform != 'android':
            self.show_dialog("Aviso", "La cámara solo funciona en Android.")
            return
        try:
            from jnius import autoclass, cast
            from android import activity as android_activity

            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            MediaStore = autoclass('android.provider.MediaStore')
            ImagesMedia = autoclass('android.provider.MediaStore$Images$Media')
            ContentValues = autoclass('android.content.ContentValues')

            activity = PythonActivity.mActivity
            resolver = activity.getContentResolver()

            name = f"{kind}_{int(time.time())}.jpg"
            values = ContentValues()
            values.put("_display_name", name)
            values.put("mime_type", "image/jpeg")
            values.put("relative_path", PHOTO_SUBDIR)

            uri = resolver.insert(ImagesMedia.EXTERNAL_CONTENT_URI, values)
            if uri is None:
                raise RuntimeError("No se pudo crear el archivo de la foto.")

            self._pending = {"kind": kind, "uri": uri, "name": name}

            android_activity.unbind(on_activity_result=self._on_activity_result)
            android_activity.bind(on_activity_result=self._on_activity_result)

            intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            intent.putExtra(MediaStore.EXTRA_OUTPUT, cast('android.os.Parcelable', uri))
            intent.addFlags(
                Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                | Intent.FLAG_GRANT_READ_URI_PERMISSION
            )
            activity.startActivityForResult(intent, REQ_CAMERA)
        except Exception as e:
            traceback.print_exc()
            self._pending = None
            self.show_dialog("Error", f"No se pudo abrir la cámara: {e}")

    def _on_activity_result(self, request_code, result_code, intent):
        if request_code != REQ_CAMERA:
            return
        # Pasar al hilo principal de Kivy
        Clock.schedule_once(lambda dt: self._finish_photo(result_code), 0)

    def _finish_photo(self, result_code):
        pending, self._pending = self._pending, None
        try:
            from android import activity as android_activity
            android_activity.unbind(on_activity_result=self._on_activity_result)
        except Exception:
            pass
        if not pending:
            return

        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        resolver = PythonActivity.mActivity.getContentResolver()
        uri = pending["uri"]
        kind = pending["kind"]
        dest = os.path.join(self.user_data_dir, pending["name"])

        if result_code != RESULT_OK:
            try:
                resolver.delete(uri, None, None)
            except Exception:
                pass
            self.show_dialog("Aviso", "Captura cancelada.")
            return

        copied = False
        try:
            FileUtils = autoclass('android.os.FileUtils')
            FileOutputStream = autoclass('java.io.FileOutputStream')
            ins = resolver.openInputStream(uri)
            outs = FileOutputStream(dest)
            FileUtils.copy(ins, outs)
            ins.close()
            outs.close()
            copied = os.path.exists(dest) and os.path.getsize(dest) > 0
        except Exception:
            traceback.print_exc()

        if not copied:
            # Plan B: copiar por ruta directa
            try:
                Environment = autoclass('android.os.Environment')
                root = Environment.getExternalStorageDirectory().getAbsolutePath()
                src = os.path.join(root, PHOTO_SUBDIR, pending["name"])
                shutil.copy(src, dest)
                copied = os.path.exists(dest) and os.path.getsize(dest) > 0
            except Exception:
                traceback.print_exc()

        # Quitar la foto de la galería (privacidad, sobre todo el carnet)
        try:
            resolver.delete(uri, None, None)
        except Exception:
            pass

        if not copied:
            self.show_dialog("Error", "No se pudo guardar la foto. Intenta de nuevo.")
            return

        self.process_image(dest)

        preview = self.thumb_of(dest) if os.path.exists(self.thumb_of(dest)) else dest
        if kind == "montura":
            self.current_montura_path = dest
            self.root.ids.montura_preview.source = preview
        else:
            self.current_carnet_path = dest
            self.root.ids.carnet_preview.source = preview
        self.show_dialog("Éxito", "Foto capturada correctamente.")

    # ------------------------------------------------------------------
    # Registro
    # ------------------------------------------------------------------
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

        data = self.load_records()
        data.append(record)

        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.show_dialog("¡Guardado!", "El registro del cliente se guardó con éxito.")
            self.reset_form()
        except Exception as e:
            self.show_dialog("Error", f"No se pudo guardar el archivo JSON: {e}")

    def reset_form(self):
        ids = self.root.ids
        ids.client_name.text = ""
        ids.client_carnet.text = ""
        ids.lens_ticket.text = ""
        ids.montura_preview.source = ""
        ids.carnet_preview.source = ""
        self.current_montura_path = ""
        self.current_carnet_path = ""

    # ------------------------------------------------------------------
    # Lista de clientes guardados
    # ------------------------------------------------------------------
    def refresh_list(self):
        box = self.root.ids.list_box
        box.clear_widgets()
        records = self.load_records()
        if not records:
            box.add_widget(MDLabel(
                text="Todavía no hay registros guardados.",
                halign="center", size_hint_y=None, height=dp(60),
            ))
            return
        for rec in reversed(records):
            box.add_widget(self.make_card(rec))

    def make_card(self, rec):
        card = MDCard(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(4),
            size_hint_y=None,
            height=dp(330),
            elevation=2,
        )
        lines = [
            f"[b]{escape_markup(str(rec.get('nombre_cliente', '')))}[/b]",
            f"CI: {escape_markup(str(rec.get('numero_carnet', '')))}",
            f"Ficha: {escape_markup(str(rec.get('numero_ficha', '')))}",
            f"Fecha: {escape_markup(str(rec.get('fecha_registro', '')))}",
        ]
        for line in lines:
            card.add_widget(MDLabel(
                text=line, markup=True, size_hint_y=None, height=dp(24),
            ))

        row = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(180))
        for title, key in (("Montura", "foto_montura"), ("Carnet", "foto_carnet")):
            full = rec.get(key, "")
            thumb = self.thumb_of(full) if full else ""
            src = thumb if os.path.exists(thumb) else full
            col = MDBoxLayout(orientation="vertical")
            if src and os.path.exists(src):
                img = TapImage(source=src)
                img.bind(on_release=lambda w, p=full: self.show_full_image(p))
                col.add_widget(img)
            else:
                col.add_widget(MDLabel(text="Sin imagen", halign="center"))
            col.add_widget(MDLabel(
                text=title, halign="center", size_hint_y=None, height=dp(20),
            ))
            row.add_widget(col)
        card.add_widget(row)
        return card

    def show_full_image(self, path):
        if not path or not os.path.exists(path):
            return
        view = ModalView(size_hint=(0.95, 0.9), background_color=(0, 0, 0, 0.9))
        view.add_widget(TapImage(source=path, on_release=lambda w: view.dismiss()))
        view.open()

    # ------------------------------------------------------------------
    # Compartir
    # ------------------------------------------------------------------
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
        data = self.load_records()
        if not data:
            self.show_dialog("Aviso", "No hay registros guardados todavía.")
            return
        try:
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


if __name__ == "__main__":
    OpticaApp().run()
