# -*- coding: utf-8 -*-
"""
Sistema de Negocio - App para emprendedores
UI rediseñada: iconos vectoriales propios (sin depender de fuentes externas),
botones con feedback táctil, tipografía/espaciado más grandes y tarjetas
con borde sutil. La lógica de datos (caja, ventas, inventario) es la misma
que en la versión original.
"""
import json
import os
from datetime import datetime

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse, Line
from kivy.metrics import dp, sp
from kivy.animation import Animation

DATA_FILE = "sistema_negocio_data.json"


def cargar_datos():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "caja_abierta": False,
        "monto_inicial": 0.0,
        "total_ventas_efectivo": 0.0,
        "total_ventas_qr": 0.0,
        "total_ganancias": 0.0,
        "inventario": [
            {"nombre": "Coca Cola 2L", "stock": 15, "costo": 10.0, "precio": 15.0},
            {"nombre": "Galletas Club Social", "stock": 3, "costo": 2.5, "precio": 4.0},
            {"nombre": "Agua Mineral 500ml", "stock": 2, "costo": 3.0, "precio": 5.0}
        ],
        "historial_ventas": [],
        "gastos_caja": []
    }


def guardar_datos():
    data = {
        "caja_abierta": GlobalData.caja_abierta,
        "monto_inicial": GlobalData.monto_inicial,
        "total_ventas_efectivo": GlobalData.total_ventas_efectivo,
        "total_ventas_qr": GlobalData.total_ventas_qr,
        "total_ganancias": GlobalData.total_ganancias,
        "inventario": GlobalData.inventario,
        "historial_ventas": GlobalData.historial_ventas,
        "gastos_caja": GlobalData.gastos_caja
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        # Evita que un problema de escritura tumbe la app; queda en el log.
        print(f"[AVISO] No se pudieron guardar los datos: {e}")


class GlobalData:
    datos = cargar_datos()
    caja_abierta = datos["caja_abierta"]
    monto_inicial = datos["monto_inicial"]
    total_ventas_efectivo = datos["total_ventas_efectivo"]
    total_ventas_qr = datos["total_ventas_qr"]
    total_ganancias = datos["total_ganancias"]
    inventario = datos["inventario"]
    historial_ventas = datos["historial_ventas"]
    gastos_caja = datos["gastos_caja"]
    carrito = []


# ---------------------------------------------------------------------------
# TEMA: paleta, tipografía y espaciado centralizados
# ---------------------------------------------------------------------------
class Theme:
    BG = (0.05, 0.06, 0.08, 1)
    SURFACE = (0.11, 0.12, 0.15, 1)
    SURFACE_BORDER = (1, 1, 1, 0.06)

    PRIMARY = (0.20, 0.75, 0.42, 1)
    PRIMARY_DARK = (0.14, 0.55, 0.31, 1)
    PRIMARY_HEX = "33BF6B"

    ACCENT_BLUE = (0.25, 0.48, 0.90, 1)
    ACCENT_BLUE_DARK = (0.18, 0.36, 0.70, 1)

    DANGER = (0.85, 0.28, 0.28, 1)
    DANGER_DARK = (0.65, 0.20, 0.20, 1)
    DANGER_HEX = "D94747"

    WARNING = (0.80, 0.52, 0.16, 1)
    WARNING_DARK = (0.60, 0.38, 0.10, 1)

    NEUTRAL = (0.22, 0.24, 0.28, 1)
    NEUTRAL_DARK = (0.16, 0.17, 0.20, 1)

    TEXT = (0.96, 0.97, 0.98, 1)
    TEXT_MUTED = (0.62, 0.65, 0.70, 1)
    TEXT_MUTED_HEX = "9EA6B2"
    TEXT_DIM = (0.42, 0.45, 0.50, 1)

    NAV_BG = (0.08, 0.09, 0.11, 1)

    RADIUS = dp(16)
    RADIUS_SM = dp(10)
    PAD = dp(18)
    GAP = dp(14)


def make_title(text):
    lbl = Label(text=text, font_size=sp(22), bold=True, color=Theme.TEXT,
                size_hint_y=None, height=dp(36), halign='left', valign='middle')
    lbl.bind(size=lbl.setter('text_size'))
    return lbl


# ---------------------------------------------------------------------------
# ICONOS: dibujados a mano con canvas, no dependen de ninguna fuente/asset
# ---------------------------------------------------------------------------
class Icon(Widget):
    def __init__(self, kind='dot', color=(1, 1, 1, 1), **kwargs):
        kwargs.setdefault('size_hint', (None, None))
        super().__init__(**kwargs)
        self.kind = kind
        self.icon_color = color
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size
        if w <= 0 or h <= 0:
            return
        with self.canvas:
            Color(*self.icon_color)
            draw = getattr(self, f'_draw_{self.kind}', self._draw_dot)
            draw(x, y, w, h)

    def _draw_dot(self, x, y, w, h):
        Ellipse(pos=(x + w * 0.3, y + h * 0.3), size=(w * 0.4, h * 0.4))

    def _draw_caja(self, x, y, w, h):
        Line(rounded_rectangle=(x + w * 0.08, y + h * 0.15, w * 0.84, h * 0.6, dp(4)),
             width=dp(1.8))
        Ellipse(pos=(x + w * 0.38, y + h * 0.32), size=(w * 0.24, w * 0.24))
        Line(points=[x + w * 0.5, y + h * 0.75, x + w * 0.5, y + h * 0.9], width=dp(1.8))

    def _draw_venta(self, x, y, w, h):
        Line(points=[
            x + w * 0.12, y + h * 0.78,
            x + w * 0.22, y + h * 0.78,
            x + w * 0.34, y + h * 0.32,
            x + w * 0.82, y + h * 0.32,
            x + w * 0.74, y + h * 0.6,
            x + w * 0.30, y + h * 0.6,
        ], width=dp(1.8), joint='round', cap='round')
        Ellipse(pos=(x + w * 0.34, y + h * 0.12), size=(w * 0.12, w * 0.12))
        Ellipse(pos=(x + w * 0.62, y + h * 0.12), size=(w * 0.12, w * 0.12))

    def _draw_inventario(self, x, y, w, h):
        Line(rounded_rectangle=(x + w * 0.14, y + h * 0.15, w * 0.72, h * 0.62, dp(3)),
             width=dp(1.8))
        Line(points=[x + w * 0.14, y + h * 0.46, x + w * 0.86, y + h * 0.46], width=dp(1.6))
        Line(points=[x + w * 0.5, y + h * 0.15, x + w * 0.5, y + h * 0.46], width=dp(1.6))

    def _draw_resumen(self, x, y, w, h):
        Rectangle(pos=(x + w * 0.18, y + h * 0.2), size=(w * 0.14, h * 0.3))
        Rectangle(pos=(x + w * 0.42, y + h * 0.2), size=(w * 0.14, h * 0.5))
        Rectangle(pos=(x + w * 0.66, y + h * 0.2), size=(w * 0.14, h * 0.65))

    def _draw_plus(self, x, y, w, h):
        t = min(w, h) * 0.16
        Rectangle(pos=(x + w / 2 - t / 2, y + h * 0.18), size=(t, h * 0.64))
        Rectangle(pos=(x + w * 0.18, y + h / 2 - t / 2), size=(w * 0.64, t))

    def _draw_back(self, x, y, w, h):
        Line(points=[x + w * 0.62, y + h * 0.2, x + w * 0.32, y + h * 0.5, x + w * 0.62, y + h * 0.8],
             width=dp(2.0), joint='round', cap='round')

    def _draw_check(self, x, y, w, h):
        Line(points=[x + w * 0.18, y + h * 0.5, x + w * 0.42, y + h * 0.24, x + w * 0.84, y + h * 0.72],
             width=dp(2.0), joint='round', cap='round')

    def _draw_efectivo(self, x, y, w, h):
        Line(rounded_rectangle=(x + w * 0.1, y + h * 0.28, w * 0.8, h * 0.44, dp(4)), width=dp(1.8))
        Ellipse(pos=(x + w * 0.38, y + h * 0.38), size=(w * 0.24, w * 0.24))

    def _draw_qr(self, x, y, w, h):
        s = w * 0.16
        for cx, cy in [(0.14, 0.14), (0.14, 0.5), (0.14, 0.7), (0.5, 0.14),
                       (0.7, 0.14), (0.5, 0.5), (0.7, 0.62), (0.62, 0.7)]:
            Rectangle(pos=(x + w * cx, y + h * cy), size=(s, s))

    def _draw_gasto(self, x, y, w, h):
        Line(points=[x + w * 0.2, y + h * 0.75, x + w * 0.5, y + h * 0.25, x + w * 0.8, y + h * 0.75],
             width=dp(2.0), joint='round', cap='round')
        Line(points=[x + w * 0.5, y + h * 0.25, x + w * 0.5, y + h * 0.85], width=dp(2.0))

    def _draw_alerta(self, x, y, w, h):
        Line(points=[x + w * 0.5, y + h * 0.35, x + w * 0.5, y + h * 0.68],
             width=dp(2.2), cap='round')
        Ellipse(pos=(x + w * 0.5 - dp(1.4), y + h * 0.18), size=(dp(2.8), dp(2.8)))


# ---------------------------------------------------------------------------
# WIDGETS BASE reutilizables
# ---------------------------------------------------------------------------
class RoundedCard(BoxLayout):
    def __init__(self, bg_color=None, radius=None, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color or Theme.SURFACE
        self.radius_val = radius if radius is not None else Theme.RADIUS
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[self.radius_val])
            Color(*Theme.SURFACE_BORDER)
            self.border = Line(rounded_rectangle=(*self.pos, *self.size, self.radius_val),
                                width=dp(1))
        self.bind(size=self._update_canvas, pos=self._update_canvas)

    def _update_canvas(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        self.border.rounded_rectangle = (instance.x, instance.y, instance.width,
                                          instance.height, self.radius_val)


class RoundedButton(ButtonBehavior, FloatLayout):
    """Botón con fondo redondeado, ícono opcional y animación al presionar."""

    def __init__(self, text='', icon=None, bg_color=None, bg_color_dark=None,
                 text_color=None, font_size=None, icon_size=None,
                 radius=None, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color or Theme.PRIMARY
        self.bg_color_dark = bg_color_dark or Theme.PRIMARY_DARK
        self._radius = radius if radius is not None else Theme.RADIUS_SM
        with self.canvas.before:
            self._color = Color(*self.bg_color)
            self._rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[self._radius])
        self.bind(pos=self._update_rect, size=self._update_rect)

        self.label = Label(
            text=text, font_size=font_size or sp(15), bold=True,
            color=text_color or Theme.TEXT,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(1, 1), halign='center', valign='middle',
        )
        self.label.bind(size=lambda i, v: setattr(i, 'text_size', v))
        self.add_widget(self.label)

        if icon:
            self.icon_widget = Icon(
                kind=icon, color=text_color or Theme.TEXT,
                size_hint=(None, None), size=(icon_size or dp(20), icon_size or dp(20)),
                pos_hint={'x': 0.045, 'center_y': 0.5})
            self.add_widget(self.icon_widget)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def on_press(self):
        Animation.cancel_all(self._color)
        Animation(rgba=self.bg_color_dark, duration=0.08).start(self._color)

    def on_release(self):
        Animation.cancel_all(self._color)
        Animation(rgba=self.bg_color, duration=0.12).start(self._color)


class RoundedInput(TextInput):
    def __init__(self, radius=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_disabled = ''
        self.background_color = (0, 0, 0, 0)
        self.cursor_color = Theme.PRIMARY
        self.hint_text_color = Theme.TEXT_DIM
        self.foreground_color = Theme.TEXT
        self.padding = [dp(16), dp(14), dp(16), dp(14)]
        self._radius = radius if radius is not None else Theme.RADIUS_SM
        with self.canvas.before:
            Color(*Theme.SURFACE)
            self._bg = RoundedRectangle(size=self.size, pos=self.pos, radius=[self._radius])
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size


class MessageBanner(BoxLayout):
    """Mensaje de feedback (éxito / error) con ícono y fondo de color suave."""

    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', spacing=dp(8),
                          size_hint_y=None, height=0, padding=(dp(12), 0), **kwargs)
        self.opacity = 0
        with self.canvas.before:
            self._color = Color(0, 0, 0, 0)
            self._rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.icon = Icon(kind='check', color=(1, 1, 1, 1), size_hint=(None, None),
                          size=(dp(16), dp(16)))
        self.label = Label(text='', font_size=sp(13), bold=True, color=(1, 1, 1, 1),
                            halign='left', valign='middle', size_hint=(1, 1))
        self.label.bind(size=lambda i, v: setattr(i, 'text_size', v))
        self.add_widget(self.icon)
        self.add_widget(self.label)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def show(self, text, kind='success'):
        if kind == 'success':
            fg = Theme.PRIMARY
            icon_kind = 'check'
        else:
            fg = Theme.DANGER
            icon_kind = 'alerta'
        self.icon.kind = icon_kind
        self.icon.icon_color = fg
        self.icon._redraw()
        self.label.text = text
        self.label.color = fg
        self._color.rgba = (fg[0], fg[1], fg[2], 0.14)
        self.height = dp(40)
        self.opacity = 1

    def hide(self):
        self.label.text = ''
        self.height = 0
        self.opacity = 0


class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical')
        with self.main_layout.canvas.before:
            Color(*Theme.BG)
            self.rect = RoundedRectangle(size=self.main_layout.size, pos=self.main_layout.pos, radius=[0])
        self.main_layout.bind(size=self._update_rect, pos=self._update_rect)
        self.content_layout = BoxLayout(orientation='vertical', padding=Theme.PAD, spacing=Theme.GAP)
        self.main_layout.add_widget(self.content_layout)
        self.add_widget(self.main_layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


# ---------------------------------------------------------------------------
# BARRA INFERIOR con pestaña activa resaltada
# ---------------------------------------------------------------------------
class NavTab(ButtonBehavior, BoxLayout):
    def __init__(self, icon_kind, text, screen_name, sm, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(3), **kwargs)
        self.screen_name = screen_name
        self.sm = sm
        icon_holder = AnchorLayout(size_hint_y=None, height=dp(24))
        self.icon = Icon(kind=icon_kind, color=Theme.TEXT_MUTED,
                          size_hint=(None, None), size=(dp(22), dp(22)))
        icon_holder.add_widget(self.icon)
        self.label = Label(text=text, font_size=sp(11), bold=True,
                            color=Theme.TEXT_MUTED, size_hint_y=None, height=dp(16))
        self.add_widget(icon_holder)
        self.add_widget(self.label)
        self.bind(on_press=self._go)

    def _go(self, *args):
        self.sm.current = self.screen_name

    def set_active(self, active):
        color = Theme.PRIMARY if active else Theme.TEXT_MUTED
        self.icon.icon_color = color
        self.icon._redraw()
        self.label.color = color


class BottomNavBar(BoxLayout):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(72)
        self.sm = screen_manager

        with self.canvas.before:
            Color(*Theme.NAV_BG)
            self._bg = RoundedRectangle(size=self.size, pos=self.pos, radius=[0])
        self.bind(pos=self._update_rect, size=self._update_rect)

        items = [
            ('caja', 'Caja', 'caja'),
            ('venta', 'Venta', 'venta'),
            ('inventario', 'Inventario', 'inventario'),
            ('resumen', 'Resumen', 'resumen'),
        ]
        self.tabs = []
        for icon_kind, label, screen_name in items:
            tab = NavTab(icon_kind, label, screen_name, self.sm)
            self.tabs.append(tab)
            self.add_widget(tab)

        self.sm.bind(current=self._on_screen_change)
        self._on_screen_change(self.sm, self.sm.current)

    def _update_rect(self, instance, value):
        self._bg.pos = instance.pos
        self._bg.size = instance.size

    def _on_screen_change(self, instance, value):
        for tab in self.tabs:
            tab.set_active(tab.screen_name == value)


# ---------------------------------------------------------------------------
# PANTALLAS
# ---------------------------------------------------------------------------
class CajaScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_layout.add_widget(make_title('Control de Caja'))

        self.input_monto = RoundedInput(
            hint_text='Monto Inicial para Apertura (Bs)',
            multiline=False, input_filter='float', font_size=sp(15),
            size_hint_y=None, height=dp(54),
        )
        self.content_layout.add_widget(self.input_monto)

        self.btn_accion = RoundedButton(
            text='ABRIR CAJA', icon='caja', font_size=sp(16),
            bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK,
            size_hint_y=None, height=dp(56),
        )
        self.btn_accion.bind(on_release=self.ejecutar_accion)
        self.content_layout.add_widget(self.btn_accion)

        self.card_estado = RoundedCard(orientation='vertical', padding=dp(18), spacing=dp(10),
                                        size_hint_y=None, height=dp(140))

        fila_estado = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(22))
        self.dot_estado = Icon(kind='dot', color=Theme.TEXT_MUTED, size_hint=(None, None),
                                size=(dp(14), dp(14)), pos_hint={'center_y': 0.5})
        self.lbl_estado = Label(text='Estado: Caja Cerrada', font_size=sp(16), bold=True,
                                 color=Theme.TEXT, halign='left', valign='middle')
        self.lbl_estado.bind(size=self.lbl_estado.setter('text_size'))
        fila_estado.add_widget(self.dot_estado)
        fila_estado.add_widget(self.lbl_estado)
        self.card_estado.add_widget(fila_estado)

        self.lbl_fondo = Label(text='Fondo Actual: 0.00 Bs', font_size=sp(14),
                                color=Theme.TEXT_MUTED, halign='left', valign='middle')
        self.lbl_fondo.bind(size=self.lbl_fondo.setter('text_size'))
        self.card_estado.add_widget(self.lbl_fondo)

        self.content_layout.add_widget(self.card_estado)

        self.banner = MessageBanner()
        self.content_layout.add_widget(self.banner)

        self.content_layout.add_widget(Widget())

    def on_enter(self):
        self.banner.hide()
        self.input_monto.text = ''
        if not GlobalData.caja_abierta:
            self.lbl_estado.text = 'Estado: Caja Cerrada'
            self.lbl_fondo.text = 'Fondo Actual: 0.00 Bs'
            self.input_monto.hint_text = 'Monto Inicial para Apertura (Bs)'
            self.btn_accion.text = 'ABRIR CAJA'
            self.btn_accion.label.text = 'ABRIR CAJA'
            self.btn_accion.bg_color = Theme.PRIMARY
            self.btn_accion.bg_color_dark = Theme.PRIMARY_DARK
            self.btn_accion._color.rgba = Theme.PRIMARY
            self.dot_estado.icon_color = Theme.TEXT_MUTED
        else:
            total_gastos = sum(g['monto'] for g in GlobalData.gastos_caja)
            efectivo_esperado = GlobalData.monto_inicial + GlobalData.total_ventas_efectivo - total_gastos
            self.lbl_estado.text = 'Estado: Caja Abierta'
            self.lbl_fondo.text = f'Efectivo en Caja: {efectivo_esperado:.2f} Bs'
            self.input_monto.hint_text = 'Conteo exacto para Cierre (Bs)'
            self.btn_accion.label.text = 'CERRAR CAJA'
            self.btn_accion.bg_color = Theme.DANGER
            self.btn_accion.bg_color_dark = Theme.DANGER_DARK
            self.btn_accion._color.rgba = Theme.DANGER
            self.dot_estado.icon_color = Theme.PRIMARY
        self.dot_estado._redraw()

    def ejecutar_accion(self, instance):
        try:
            monto = float(self.input_monto.text) if self.input_monto.text else 0.0
            if not GlobalData.caja_abierta:
                GlobalData.caja_abierta = True
                GlobalData.monto_inicial = monto
                GlobalData.total_ventas_efectivo = 0.0
                GlobalData.total_ventas_qr = 0.0
                GlobalData.total_ganancias = 0.0
                GlobalData.historial_ventas = []
                GlobalData.gastos_caja = []
                guardar_datos()
                self.on_enter()
                self.banner.show('¡Caja abierta correctamente!', 'success')
            else:
                total_gastos = sum(g['monto'] for g in GlobalData.gastos_caja)
                efectivo_esperado = GlobalData.monto_inicial + GlobalData.total_ventas_efectivo - total_gastos
                diferencia = monto - efectivo_esperado
                GlobalData.caja_abierta = False
                guardar_datos()
                dif_txt = f" (Dif: {diferencia:+.2f} Bs)"
                self.on_enter()
                self.banner.show(f'Cierre exitoso. Contado: {monto}{dif_txt}', 'success')
        except ValueError:
            self.banner.show('Ingrese un valor numérico válido.', 'error')


class VentaScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_layout.add_widget(make_title('Punto de Venta Rápido'))

        self.input_buscar = RoundedInput(
            hint_text='Buscar producto...', multiline=False,
            font_size=sp(14), size_hint_y=None, height=dp(50),
        )
        self.input_buscar.bind(text=self.filtrar_productos)
        self.content_layout.add_widget(self.input_buscar)

        self.scroll_res = ScrollView(size_hint=(1, 0.26))
        self.lista_resultados = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.lista_resultados.bind(minimum_height=self.lista_resultados.setter('height'))
        self.scroll_res.add_widget(self.lista_resultados)
        self.content_layout.add_widget(self.scroll_res)

        self.content_layout.add_widget(
            Label(text='Carrito de Compras', font_size=sp(14), bold=True,
                  size_hint_y=None, height=dp(22), color=Theme.TEXT_MUTED,
                  halign='left', valign='middle')
        )

        self.scroll_car = ScrollView(size_hint=(1, 0.28))
        self.lista_carrito = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.lista_carrito.bind(minimum_height=self.lista_carrito.setter('height'))
        self.scroll_car.add_widget(self.lista_carrito)
        self.content_layout.add_widget(self.scroll_car)

        self.lbl_total = Label(text='Total: 0.00 Bs', font_size=sp(18), bold=True,
                                color=Theme.PRIMARY, size_hint_y=None, height=dp(30))
        self.content_layout.add_widget(self.lbl_total)

        botones_pago = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10))
        btn_efectivo = RoundedButton(text='Cobrar Efectivo', icon='efectivo', font_size=sp(14),
                                      bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK)
        btn_efectivo.bind(on_release=lambda x: self.cobrar('efectivo'))

        btn_qr = RoundedButton(text='Cobrar QR', icon='qr', font_size=sp(14),
                                bg_color=Theme.ACCENT_BLUE, bg_color_dark=Theme.ACCENT_BLUE_DARK)
        btn_qr.bind(on_release=lambda x: self.cobrar('qr'))

        botones_pago.add_widget(btn_efectivo)
        botones_pago.add_widget(btn_qr)
        self.content_layout.add_widget(botones_pago)

    def on_enter(self):
        GlobalData.carrito = []
        self.actualizar_carrito_vista()
        self.input_buscar.text = ''
        self.filtrar_productos(None, '')

    def filtrar_productos(self, instance, valor):
        self.lista_resultados.clear_widgets()
        filtro = valor.lower()
        for prod in GlobalData.inventario:
            if filtro in prod['nombre'].lower():
                alerta = "  ¡STOCK BAJO!" if prod['stock'] <= 5 else ""
                texto = f"{prod['nombre']}  ·  Stock {prod['stock']}  ·  {prod['precio']} Bs{alerta}"
                btn = RoundedButton(
                    text=texto, icon='plus', font_size=sp(12.5),
                    bg_color=Theme.SURFACE, bg_color_dark=Theme.NEUTRAL_DARK,
                    text_color=Theme.TEXT, icon_size=dp(16),
                    size_hint_y=None, height=dp(46), radius=Theme.RADIUS_SM,
                )
                btn.bind(on_release=lambda x, p=prod: self.agregar_al_carrito(p))
                self.lista_resultados.add_widget(btn)

    def agregar_al_carrito(self, producto):
        if producto['stock'] > 0:
            en_carrito = next((item for item in GlobalData.carrito if item['nombre'] == producto['nombre']), None)
            if en_carrito:
                en_carrito['cantidad'] += 1
            else:
                GlobalData.carrito.append({'nombre': producto['nombre'], 'precio': producto['precio'],
                                            'costo': producto['costo'], 'cantidad': 1})
            producto['stock'] -= 1
            guardar_datos()
            self.actualizar_carrito_vista()
            self.filtrar_productos(None, self.input_buscar.text)

    def actualizar_carrito_vista(self):
        self.lista_carrito.clear_widgets()
        total = 0.0
        for item in GlobalData.carrito:
            sub = item['precio'] * item['cantidad']
            total += sub
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(28))
            left = Label(text=f"{item['nombre']}  x{item['cantidad']}", font_size=sp(13),
                         color=Theme.TEXT, halign='left', valign='middle')
            left.bind(size=left.setter('text_size'))
            right = Label(text=f"{sub:.2f} Bs", font_size=sp(13), bold=True,
                          color=Theme.PRIMARY, halign='right', valign='middle',
                          size_hint_x=None, width=dp(90))
            right.bind(size=right.setter('text_size'))
            row.add_widget(left)
            row.add_widget(right)
            self.lista_carrito.add_widget(row)
        self.lbl_total.text = f'Total: {total:.2f} Bs'

    def cobrar(self, metodo):
        if not GlobalData.carrito or not GlobalData.caja_abierta:
            return
        total_venta = sum(i['precio'] * i['cantidad'] for i in GlobalData.carrito)
        ganancia_venta = sum((i['precio'] - i['costo']) * i['cantidad'] for i in GlobalData.carrito)
        detalle = ", ".join([f"{i['nombre']} x{i['cantidad']}" for i in GlobalData.carrito])

        if metodo == 'efectivo':
            GlobalData.total_ventas_efectivo += total_venta
        else:
            GlobalData.total_ventas_qr += total_venta
        GlobalData.total_ganancias += ganancia_venta

        GlobalData.historial_ventas.append({
            "hora": datetime.now().strftime("%H:%M:%S"),
            "metodo": metodo.upper(),
            "total": total_venta,
            "productos": detalle
        })
        GlobalData.carrito = []
        guardar_datos()
        self.actualizar_carrito_vista()


class InventarioScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_layout.add_widget(make_title('Inventario y Stock'))

        self.scroll = ScrollView(size_hint=(1, 1))
        self.lista_layout = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.lista_layout.bind(minimum_height=self.lista_layout.setter('height'))
        self.scroll.add_widget(self.lista_layout)
        self.content_layout.add_widget(self.scroll)

        btn_agregar = RoundedButton(text='Nuevo Producto / Stock', icon='plus', font_size=sp(14),
                                     bg_color=Theme.WARNING, bg_color_dark=Theme.WARNING_DARK,
                                     size_hint_y=None, height=dp(50))
        btn_agregar.bind(on_release=lambda x: setattr(self.manager, 'current', 'ingreso'))
        self.content_layout.add_widget(btn_agregar)

    def on_enter(self):
        self.lista_layout.clear_widgets()
        for prod in GlobalData.inventario:
            bajo = prod['stock'] <= 5
            badge_color = Theme.DANGER if bajo else Theme.PRIMARY

            row = RoundedCard(orientation='horizontal', padding=(dp(14), dp(10)),
                               spacing=dp(10), size_hint_y=None, height=dp(66))

            info = BoxLayout(orientation='vertical', spacing=dp(3))
            nombre_lbl = Label(text=prod['nombre'], font_size=sp(14.5), bold=True,
                                color=Theme.TEXT, halign='left', valign='middle',
                                size_hint_y=None, height=dp(20))
            nombre_lbl.bind(size=nombre_lbl.setter('text_size'))
            precio_lbl = Label(text=f"Compra {prod['costo']:.2f} Bs  ·  Venta {prod['precio']:.2f} Bs",
                                font_size=sp(12), color=Theme.TEXT_MUTED,
                                halign='left', valign='middle', size_hint_y=None, height=dp(18))
            precio_lbl.bind(size=precio_lbl.setter('text_size'))
            info.add_widget(nombre_lbl)
            info.add_widget(precio_lbl)
            row.add_widget(info)

            badge = BoxLayout(orientation='vertical', size_hint=(None, None),
                               size=(dp(66), dp(46)))
            with badge.canvas.before:
                Color(badge_color[0], badge_color[1], badge_color[2], 0.16)
                badge_rect = RoundedRectangle(size=badge.size, pos=badge.pos, radius=[dp(10)])
            badge.bind(
                pos=lambda inst, val, r=badge_rect: setattr(r, 'pos', val),
                size=lambda inst, val, r=badge_rect: setattr(r, 'size', val),
            )
            stock_lbl = Label(text=str(prod['stock']), font_size=sp(17), bold=True,
                               color=badge_color, size_hint_y=None, height=dp(24))
            cap_lbl = Label(text='bajo' if bajo else 'stock', font_size=sp(9.5),
                             color=badge_color, size_hint_y=None, height=dp(14))
            badge.add_widget(stock_lbl)
            badge.add_widget(cap_lbl)
            row.add_widget(badge)

            self.lista_layout.add_widget(row)


class IngresoProductoScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_layout.add_widget(make_title('Registrar / Actualizar Producto'))

        self.input_nombre = RoundedInput(hint_text='Nombre del producto', multiline=False,
                                          size_hint_y=None, height=dp(52), font_size=sp(14))
        self.input_stock = RoundedInput(hint_text='Cantidad (Stock)', multiline=False,
                                         input_filter='int', size_hint_y=None, height=dp(52),
                                         font_size=sp(14))
        self.input_costo = RoundedInput(hint_text='Costo de compra (Bs)', multiline=False,
                                         input_filter='float', size_hint_y=None, height=dp(52),
                                         font_size=sp(14))
        self.input_precio = RoundedInput(hint_text='Precio de venta (Bs)', multiline=False,
                                          input_filter='float', size_hint_y=None, height=dp(52),
                                          font_size=sp(14))

        self.content_layout.add_widget(self.input_nombre)
        self.content_layout.add_widget(self.input_stock)
        self.content_layout.add_widget(self.input_costo)
        self.content_layout.add_widget(self.input_precio)

        self.banner = MessageBanner()
        self.content_layout.add_widget(self.banner)

        btn_guardar = RoundedButton(text='Guardar', icon='check', font_size=sp(15),
                                     bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK,
                                     size_hint_y=None, height=dp(52))
        btn_guardar.bind(on_release=self.guardar_producto)
        self.content_layout.add_widget(btn_guardar)

        btn_volver = RoundedButton(text='Volver al Inventario', icon='back', font_size=sp(13),
                                    bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK,
                                    size_hint_y=None, height=dp(46))
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventario'))
        self.content_layout.add_widget(btn_volver)

        self.content_layout.add_widget(Widget())

    def guardar_producto(self, instance):
        try:
            nombre = self.input_nombre.text.strip()
            stock = int(self.input_stock.text)
            costo = float(self.input_costo.text)
            precio = float(self.input_precio.text)
            if not nombre:
                return

            encontrado = False
            for p in GlobalData.inventario:
                if p['nombre'].lower() == nombre.lower():
                    p['stock'] += stock
                    p['costo'] = costo
                    p['precio'] = precio
                    encontrado = True
                    break
            if not encontrado:
                GlobalData.inventario.append({"nombre": nombre, "stock": stock, "costo": costo, "precio": precio})

            guardar_datos()
            self.banner.show('¡Guardado con éxito!', 'success')
            self.input_nombre.text = ''
            self.input_stock.text = ''
            self.input_costo.text = ''
            self.input_precio.text = ''
        except ValueError:
            self.banner.show('Verifique los campos numéricos.', 'error')


class ResumenScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_layout.add_widget(make_title('Resumen y Caja Chica'))

        self.card = RoundedCard(orientation='vertical', padding=dp(18), size_hint_y=None)
        self.scroll = ScrollView(size_hint=(1, 1))

        self.lbl_detalles = Label(text='', font_size=sp(14), color=Theme.TEXT,
                                   halign='left', valign='top', size_hint_y=None,
                                   markup=True, line_height=1.35)
        self.lbl_detalles.bind(size=self.lbl_detalles.setter('text_size'))
        self.card.add_widget(self.lbl_detalles)
        self.scroll.add_widget(self.card)
        self.content_layout.add_widget(self.scroll)

        btn_gasto = RoundedButton(text='Registrar Gasto / Retiro', icon='gasto', font_size=sp(14),
                                   bg_color=Theme.DANGER, bg_color_dark=Theme.DANGER_DARK,
                                   size_hint_y=None, height=dp(52))
        btn_gasto.bind(on_release=lambda x: setattr(self.manager, 'current', 'gasto'))
        self.content_layout.add_widget(btn_gasto)

    def on_enter(self):
        estado_txt = "Abierta" if GlobalData.caja_abierta else "Cerrada"
        estado_color = Theme.PRIMARY_HEX if GlobalData.caja_abierta else Theme.TEXT_MUTED_HEX
        total_gastos = sum(g['monto'] for g in GlobalData.gastos_caja)
        efectivo_en_caja = GlobalData.monto_inicial + GlobalData.total_ventas_efectivo - total_gastos
        total_ventas = GlobalData.total_ventas_efectivo + GlobalData.total_ventas_qr

        self.lbl_detalles.text = (
            f"[b]Estado:[/b] [color={estado_color}]{estado_txt}[/color]\n\n"
            f"[b][color={Theme.TEXT_MUTED_HEX}]EFECTIVO FÍSICO[/color][/b]\n"
            f"Inicial:  {GlobalData.monto_inicial:.2f} Bs\n"
            f"Ventas efectivo:  {GlobalData.total_ventas_efectivo:.2f} Bs\n"
            f"Retiros / gastos:  [color={Theme.DANGER_HEX}]-{total_gastos:.2f} Bs[/color]\n"
            f"[b]Total en caja:  {efectivo_en_caja:.2f} Bs[/b]\n\n"
            f"[b][color={Theme.TEXT_MUTED_HEX}]VENTAS DIGITALES[/color][/b]\n"
            f"QR / Transferencia:  {GlobalData.total_ventas_qr:.2f} Bs\n"
            f"[b]Total general:  {total_ventas:.2f} Bs[/b]\n\n"
            f"[b][color={Theme.TEXT_MUTED_HEX}]GANANCIAS NETAS[/color][/b]\n"
            f"[size={int(sp(21))}][color={Theme.PRIMARY_HEX}][b]{GlobalData.total_ganancias:.2f} Bs[/b][/color][/size]"
        )
        self.lbl_detalles.texture_update()
        content_h = max(dp(320), self.lbl_detalles.texture_size[1] + dp(10))
        self.lbl_detalles.height = content_h
        self.card.height = content_h + dp(36)


class GastoScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_layout.add_widget(make_title('Registrar Gasto / Retiro'))

        self.input_motivo = RoundedInput(hint_text='Motivo (ej. Cambio, Delivery)', multiline=False,
                                          size_hint_y=None, height=dp(52), font_size=sp(14))
        self.input_monto = RoundedInput(hint_text='Monto (Bs)', multiline=False, input_filter='float',
                                         size_hint_y=None, height=dp(52), font_size=sp(14))

        self.content_layout.add_widget(self.input_motivo)
        self.content_layout.add_widget(self.input_monto)

        self.banner = MessageBanner()
        self.content_layout.add_widget(self.banner)

        btn_reg = RoundedButton(text='Registrar Retiro', icon='gasto', font_size=sp(15),
                                 bg_color=Theme.DANGER, bg_color_dark=Theme.DANGER_DARK,
                                 size_hint_y=None, height=dp(52))
        btn_reg.bind(on_release=self.registrar)
        self.content_layout.add_widget(btn_reg)

        btn_volver = RoundedButton(text='Volver al Resumen', icon='back', font_size=sp(13),
                                    bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK,
                                    size_hint_y=None, height=dp(46))
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'resumen'))
        self.content_layout.add_widget(btn_volver)

        self.content_layout.add_widget(Widget())

    def registrar(self, instance):
        try:
            motivo = self.input_motivo.text.strip()
            monto = float(self.input_monto.text) if self.input_monto.text else 0.0
            if not motivo or monto <= 0:
                return

            GlobalData.gastos_caja.append({"motivo": motivo, "monto": monto})
            guardar_datos()
            self.banner.show('¡Gasto registrado con éxito!', 'success')
            self.input_motivo.text = ''
            self.input_monto.text = ''
        except ValueError:
            self.banner.show('Verifique los datos.', 'error')


class MainApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical')
        sm = ScreenManager(transition=FadeTransition(duration=0.15))

        sm.add_widget(CajaScreen(name='caja'))
        sm.add_widget(VentaScreen(name='venta'))
        sm.add_widget(InventarioScreen(name='inventario'))
        sm.add_widget(IngresoProductoScreen(name='ingreso'))
        sm.add_widget(ResumenScreen(name='resumen'))
        sm.add_widget(GastoScreen(name='gasto'))

        nav_bar = BottomNavBar(sm)

        root.add_widget(sm)
        root.add_widget(nav_bar)
        return root


if __name__ == '__main__':
    MainApp().run()
