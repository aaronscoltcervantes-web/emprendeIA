import io
import os
import re
import json
import time
import uuid
import shutil
import threading
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
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel

REQ_CAMERA = 4711
RESULT_OK = -1
PHOTO_SUBDIR = "Pictures/RegistroOptica"
PDF_SUBDIR = "Download/RegistroOptica"

# Página A4 (proporción 595x842 pt) renderizada a 1240x1754 px
PAGE_W, PAGE_H = 1240, 1754

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
                            id: save_btn
                            text: "Guardar Registro Local"
                            size_hint_x: 1
                            on_release: app.save_record()

                        MDRaisedButton:
                            id: cancel_edit_btn
                            text: "Cancelar edición"
                            size_hint: 1, None
                            height: 0
                            opacity: 0
                            disabled: True
                            md_bg_color: 0.5, 0.5, 0.5, 1
                            on_release: app.cancel_edit()

                        MDRaisedButton:
                            text: "Compartir Último Registro (PDF)"
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

                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(8)

                        MDRaisedButton:
                            text: "Nuevo registro"
                            size_hint_x: 1
                            on_release: app.open_form()

                        MDRaisedButton:
                            text: "Todos en PDF"
                            size_hint_x: 1
                            md_bg_color: app.theme_cls.accent_color
                            on_release: app.share_all_pdf()

                    ScrollView:
                        MDBoxLayout:
                            id: list_box
                            orientation: 'vertical'
                            spacing: dp(12)
                            padding: [0, 0, 0, dp(12)]
                            adaptive_height: True
'''


# ======================================================================
# Generación de PDF (sin dependencias extra: Pillow + escritor PDF mínimo)
# ======================================================================
def _load_font(bold, size):
    from PIL import ImageFont
    try:
        from kivy.resources import resource_find
        name = 'data/fonts/Roboto-Bold.ttf' if bold else 'data/fonts/Roboto-Regular.ttf'
        return ImageFont.truetype(resource_find(name), size)
    except Exception:
        return ImageFont.load_default()


def _wrap(draw, text, font, max_w):
    lines, line = [], ""
    for word in str(text).split():
        test = f"{line} {word}".strip()
        if draw.textlength(test, font=font) <= max_w or not line:
            line = test
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def render_record_page(rec):
    """Dibuja un registro completo (datos + fotos) como una página A4 y devuelve bytes JPEG."""
    from PIL import Image as PILImage, ImageDraw, ImageOps

    W, H, M = PAGE_W, PAGE_H, 90
    page = PILImage.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(page)
    f_title = _load_font(True, 56)
    f_label = _load_font(True, 34)
    f_value = _load_font(False, 40)
    f_sec = _load_font(True, 38)
    f_small = _load_font(False, 30)

    d.rectangle([0, 0, W, 150], fill=(48, 63, 159))
    d.text((M, 45), "Registro Promoción Óptica", font=f_title, fill="white")

    y = 200
    col = 460
    fields = [
        ("Cliente", rec.get("nombre_cliente", "")),
        ("Carnet (CI)", rec.get("numero_carnet", "")),
        ("N° de ficha del lente", rec.get("numero_ficha", "")),
        ("Fecha de registro", rec.get("fecha_registro", "")),
    ]
    if rec.get("fecha_edicion"):
        fields.append(("Última edición", rec.get("fecha_edicion", "")))
    for label, value in fields:
        d.text((M, y + 4), f"{label}:", font=f_label, fill=(90, 90, 90))
        lines = _wrap(d, value, f_value, W - M - (M + col))
        for i, ln in enumerate(lines):
            d.text((M + col, y + i * 52), ln, font=f_value, fill=(20, 20, 20))
        y += max(1, len(lines)) * 52 + 14

    y += 20
    avail = H - M - y
    box_w = W - 2 * M
    box_h = int(min(640, (avail - 2 * 56 - 40) // 2))

    for title, key in (("Foto de la montura", "foto_montura"), ("Foto del carnet", "foto_carnet")):
        d.text((M, y), title, font=f_sec, fill=(48, 63, 159))
        y += 56
        path = rec.get(key, "")
        d.rectangle([M, y, M + box_w, y + box_h], outline=(190, 190, 190), width=2)
        if path and os.path.exists(path):
            try:
                img = PILImage.open(path)
                img = ImageOps.exif_transpose(img).convert("RGB")
                img = ImageOps.contain(img, (box_w - 8, box_h - 8))
                px = M + (box_w - img.width) // 2
                py = y + (box_h - img.height) // 2
                page.paste(img, (px, py))
            except Exception:
                d.text((M + 20, y + 20), "(no se pudo cargar la imagen)", font=f_small, fill=(150, 0, 0))
        else:
            d.text((M + 20, y + 20), "(sin imagen)", font=f_small, fill=(150, 0, 0))
        y += box_h + 40

    buf = io.BytesIO()
    page.save(buf, "JPEG", quality=85)
    return buf.getvalue()


def write_pdf(jpeg_pages, out_path):
    """Escribe un PDF mínimo con una imagen JPEG por página (A4)."""
    n = len(jpeg_pages)
    offsets = {}
    with open(out_path, "wb") as f:
        def start(num):
            offsets[num] = f.tell()
            f.write(f"{num} 0 obj\n".encode())

        f.write(b"%PDF-1.4\n")
        start(1)
        f.write(b"<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        kids = " ".join(f"{3 + 3 * i} 0 R" for i in range(n))
        start(2)
        f.write(f"<< /Type /Pages /Kids [{kids}] /Count {n} >>\nendobj\n".encode())

        for i, data in enumerate(jpeg_pages):
            pn = 3 + 3 * i
            start(pn)
            f.write((
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                f"/Resources << /XObject << /Im0 {pn + 2} 0 R >> >> "
                f"/Contents {pn + 1} 0 R >>\nendobj\n"
            ).encode())
            content = b"q 595 0 0 842 0 0 cm /Im0 Do Q"
            start(pn + 1)
            f.write(f"<< /Length {len(content)} >>\nstream\n".encode())
            f.write(content)
            f.write(b"\nendstream\nendobj\n")
            start(pn + 2)
            f.write((
                f"<< /Type /XObject /Subtype /Image /Width {PAGE_W} /Height {PAGE_H} "
                f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode "
                f"/Length {len(data)} >>\nstream\n"
            ).encode())
            f.write(data)
            f.write(b"\nendstream\nendobj\n")

        xref = f.tell()
        total = 3 + 3 * n
        f.write(f"xref\n0 {total}\n".encode())
        f.write(b"0000000000 65535 f \n")
        for k in range(1, total):
            f.write(f"{offsets[k]:010d} 00000 n \n".encode())
        f.write((
            f"trailer\n<< /Size {total} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n"
        ).encode())


class TapImage(ButtonBehavior, Image):
    """Imagen que se puede tocar para verla en grande."""
    pass


class OpticaApp(MDApp):
    dialog = None
    current_montura_path = ""
    current_carnet_path = ""
    editing_id = None
    _saved_paths = set()
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
        # Imprescindible en Android: evita que la app se reinicie al abrir la cámara.
        return True

    def on_resume(self):
        pass

    def on_key(self, window, key, *args):
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
        self.root.ids.toolbar.title = "Editar registro" if self.editing_id else "Registro Óptica"

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
                data = json.load(f)
        except Exception:
            return []
        changed = False
        for r in data:
            if not r.get("id"):
                r["id"] = uuid.uuid4().hex
                changed = True
        if changed:
            self.save_records(data)
        return data

    def save_records(self, data):
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def find_record(self, rec_id):
        for r in self.load_records():
            if r.get("id") == rec_id:
                return r
        return None

    @staticmethod
    def thumb_of(path):
        base, ext = os.path.splitext(path)
        return f"{base}_thumb{ext}"

    def remove_photo_files(self, path):
        if not path:
            return
        for p in (path, self.thumb_of(path)):
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                traceback.print_exc()

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

        # Si se repite una foto aún no guardada, borrar la anterior
        old = self.current_montura_path if kind == "montura" else self.current_carnet_path
        if old and old not in self._saved_paths and old != dest:
            self.remove_photo_files(old)

        preview = self.thumb_of(dest) if os.path.exists(self.thumb_of(dest)) else dest
        if kind == "montura":
            self.current_montura_path = dest
            self.root.ids.montura_preview.source = preview
        else:
            self.current_carnet_path = dest
            self.root.ids.carnet_preview.source = preview
        self.show_dialog("Éxito", "Foto capturada correctamente.")

    # ------------------------------------------------------------------
    # Registro: guardar / editar / eliminar
    # ------------------------------------------------------------------
    def save_record(self):
        ids = self.root.ids
        name = ids.client_name.text.strip()
        carnet = ids.client_carnet.text.strip()
        ticket = ids.lens_ticket.text.strip()

        if not name or not carnet or not ticket:
            self.show_dialog("Atención", "Por favor completa todos los campos (Nombre, Carnet y Ficha).")
            return
        if not self.current_montura_path or not os.path.exists(self.current_montura_path):
            self.show_dialog("Atención", "Es obligatorio tomar la foto de la montura.")
            return
        if not self.current_carnet_path or not os.path.exists(self.current_carnet_path):
            self.show_dialog("Atención", "Es obligatorio tomar la foto del carnet.")
            return

        data = self.load_records()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        target = None
        if self.editing_id:
            for r in data:
                if r.get("id") == self.editing_id:
                    target = r
                    break

        try:
            if target is not None:
                old_m, old_c = target.get("foto_montura"), target.get("foto_carnet")
                target.update({
                    "nombre_cliente": name,
                    "numero_carnet": carnet,
                    "numero_ficha": ticket,
                    "foto_montura": self.current_montura_path,
                    "foto_carnet": self.current_carnet_path,
                    "fecha_edicion": now,
                })
                self.save_records(data)
                if old_m and old_m != self.current_montura_path:
                    self.remove_photo_files(old_m)
                if old_c and old_c != self.current_carnet_path:
                    self.remove_photo_files(old_c)
                msg = "Los cambios del cliente se guardaron con éxito."
            else:
                data.append({
                    "id": uuid.uuid4().hex,
                    "nombre_cliente": name,
                    "numero_carnet": carnet,
                    "numero_ficha": ticket,
                    "foto_montura": self.current_montura_path,
                    "foto_carnet": self.current_carnet_path,
                    "fecha_registro": now,
                })
                self.save_records(data)
                msg = "El registro del cliente se guardó con éxito."

            self.exit_edit_mode()
            self.reset_form()
            self.open_form()
            self.show_dialog("¡Guardado!", msg)
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

    def _set_edit_ui(self, editing):
        ids = self.root.ids
        ids.save_btn.text = "Guardar cambios" if editing else "Guardar Registro Local"
        btn = ids.cancel_edit_btn
        btn.height = dp(36) if editing else 0
        btn.opacity = 1 if editing else 0
        btn.disabled = not editing

    def exit_edit_mode(self):
        self.editing_id = None
        self._saved_paths = set()
        self._set_edit_ui(False)

    def _discard_unsaved(self):
        """Borra fotos tomadas en el formulario que no pertenecen a un registro guardado."""
        for p in (self.current_montura_path, self.current_carnet_path):
            if p and p not in self._saved_paths:
                self.remove_photo_files(p)

    def start_edit(self, rec_id):
        rec = self.find_record(rec_id)
        if not rec:
            self.show_dialog("Error", "No se encontró el registro.")
            return
        self._discard_unsaved()
        ids = self.root.ids
        self.editing_id = rec_id
        self._saved_paths = {rec.get("foto_montura", ""), rec.get("foto_carnet", "")}
        ids.client_name.text = rec.get("nombre_cliente", "")
        ids.client_carnet.text = rec.get("numero_carnet", "")
        ids.lens_ticket.text = rec.get("numero_ficha", "")
        self.current_montura_path = rec.get("foto_montura", "")
        self.current_carnet_path = rec.get("foto_carnet", "")
        for key, widget in (("foto_montura", ids.montura_preview), ("foto_carnet", ids.carnet_preview)):
            full = rec.get(key, "")
            thumb = self.thumb_of(full) if full else ""
            widget.source = thumb if os.path.exists(thumb) else (full if os.path.exists(full) else "")
        self._set_edit_ui(True)
        self.open_form()

    def cancel_edit(self):
        self._discard_unsaved()
        self.exit_edit_mode()
        self.reset_form()
        self.open_form()

    def confirm_delete(self, rec_id):
        rec = self.find_record(rec_id)
        if not rec:
            return
        dlg = MDDialog(
            title="Eliminar registro",
            text=f"¿Eliminar el registro de {rec.get('nombre_cliente', '')}? "
                 f"Se borrarán también sus fotos. Esta acción no se puede deshacer.",
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: dlg.dismiss()),
                MDRaisedButton(
                    text="ELIMINAR",
                    md_bg_color=(0.8, 0.2, 0.2, 1),
                    on_release=lambda x: (dlg.dismiss(), self.delete_record(rec_id)),
                ),
            ],
        )
        dlg.open()

    def delete_record(self, rec_id):
        data = self.load_records()
        keep, removed = [], None
        for r in data:
            if r.get("id") == rec_id:
                removed = r
            else:
                keep.append(r)
        if removed is None:
            return
        try:
            self.save_records(keep)
        except Exception as e:
            self.show_dialog("Error", f"No se pudo eliminar: {e}")
            return
        self.remove_photo_files(removed.get("foto_montura", ""))
        self.remove_photo_files(removed.get("foto_carnet", ""))
        if self.editing_id == rec_id:
            self.exit_edit_mode()
            self.reset_form()
        self.refresh_list()

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
        rid = rec["id"]
        card = MDCard(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(4),
            size_hint_y=None,
            height=dp(390),
            elevation=2,
        )
        fecha = str(rec.get("fecha_registro", ""))
        if rec.get("fecha_edicion"):
            fecha += f"  (editado {rec['fecha_edicion']})"
        lines = [
            f"[b]{escape_markup(str(rec.get('nombre_cliente', '')))}[/b]",
            f"CI: {escape_markup(str(rec.get('numero_carnet', '')))}",
            f"Ficha: {escape_markup(str(rec.get('numero_ficha', '')))}",
            f"Fecha: {escape_markup(fecha)}",
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

        buttons = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(44))
        buttons.add_widget(MDRaisedButton(
            text="PDF", size_hint_x=1,
            on_release=lambda x, r=rid: self.share_record_pdf(r),
        ))
        buttons.add_widget(MDRaisedButton(
            text="Editar", size_hint_x=1,
            on_release=lambda x, r=rid: self.start_edit(r),
        ))
        buttons.add_widget(MDRaisedButton(
            text="Eliminar", size_hint_x=1, md_bg_color=(0.8, 0.2, 0.2, 1),
            on_release=lambda x, r=rid: self.confirm_delete(r),
        ))
        card.add_widget(buttons)
        return card

    def show_full_image(self, path):
        if not path or not os.path.exists(path):
            return
        view = ModalView(size_hint=(0.95, 0.9), background_color=(0, 0, 0, 0.9))
        view.add_widget(TapImage(source=path, on_release=lambda w: view.dismiss()))
        view.open()

    # ------------------------------------------------------------------
    # Compartir en PDF
    # ------------------------------------------------------------------
    @staticmethod
    def _safe_name(text):
        return re.sub(r'[^\w-]+', '_', str(text)).strip('_')[:30] or "registro"

    def share_last_record(self):
        data = self.load_records()
        if not data:
            self.show_dialog("Aviso", "No hay registros guardados todavía.")
            return
        last = data[-1]
        base = f"registro_{self._safe_name(last.get('nombre_cliente'))}_{int(time.time())}"
        self._start_pdf_share([last], base)

    def share_record_pdf(self, rec_id):
        rec = self.find_record(rec_id)
        if not rec:
            self.show_dialog("Error", "No se encontró el registro.")
            return
        base = f"registro_{self._safe_name(rec.get('nombre_cliente'))}_{int(time.time())}"
        self._start_pdf_share([rec], base)

    def share_all_pdf(self):
        data = self.load_records()
        if not data:
            self.show_dialog("Aviso", "No hay registros guardados todavía.")
            return
        base = f"registros_optica_{time.strftime('%Y%m%d_%H%M')}"
        self._start_pdf_share(data, base)

    def _start_pdf_share(self, records, base_name):
        self.show_dialog("Generando PDF", "Espera un momento...")
        pdf_name = f"{base_name}.pdf"
        path = os.path.join(self.user_data_dir, pdf_name)

        def work():
            try:
                pages = [render_record_page(r) for r in records]
                write_pdf(pages, path)
                Clock.schedule_once(lambda dt: self._after_pdf(path, pdf_name), 0)
            except Exception as e:
                traceback.print_exc()
                err = str(e)
                Clock.schedule_once(
                    lambda dt: self.show_dialog("Error", f"No se pudo crear el PDF: {err}"), 0)

        threading.Thread(target=work, daemon=True).start()

    def _after_pdf(self, path, pdf_name):
        if platform == 'android':
            try:
                self.share_pdf_android(path, pdf_name)
                if self.dialog:
                    self.dialog.dismiss()
            except Exception as e:
                traceback.print_exc()
                self.show_dialog("Error", f"No se pudo compartir el PDF: {e}")
        else:
            self.show_dialog("PDF generado", f"Guardado en:\n{path}")

    def share_pdf_android(self, path, pdf_name):
        """Copia el PDF a Descargas (MediaStore) y lo comparte por Intent."""
        from jnius import autoclass, cast
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        String = autoclass('java.lang.String')
        ContentValues = autoclass('android.content.ContentValues')
        Downloads = autoclass('android.provider.MediaStore$Downloads')
        FileUtils = autoclass('android.os.FileUtils')
        FileInputStream = autoclass('java.io.FileInputStream')

        activity = PythonActivity.mActivity
        resolver = activity.getContentResolver()

        values = ContentValues()
        values.put("_display_name", pdf_name)
        values.put("mime_type", "application/pdf")
        values.put("relative_path", PDF_SUBDIR)
        uri = resolver.insert(Downloads.EXTERNAL_CONTENT_URI, values)
        if uri is None:
            raise RuntimeError("No se pudo crear el archivo PDF en Descargas.")

        ins = FileInputStream(path)
        outs = resolver.openOutputStream(uri)
        FileUtils.copy(ins, outs)
        ins.close()
        outs.close()

        intent = Intent(Intent.ACTION_SEND)
        intent.setType("application/pdf")
        intent.putExtra(Intent.EXTRA_STREAM, cast('android.os.Parcelable', uri))
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        chooser = Intent.createChooser(
            intent, cast('java.lang.CharSequence', String('Compartir registro (PDF)'))
        )
        chooser.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        activity.startActivity(chooser)


if __name__ == "__main__":
    OpticaApp().run()
