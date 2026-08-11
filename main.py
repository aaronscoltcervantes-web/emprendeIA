# -*- coding: utf-8 -*-
"""
Sistema de Caja - Negocio Gastronómico (Churrasquería / Broastería / Fast Food)
Mesas y comandas, punto de venta con stock diario de porciones, cobro flexible
(efectivo / QR / mixto), gastos, arqueo de caja y reportes.

Un solo archivo, sin dependencias externas más allá de Kivy.
Guarda todo en 'sistema_caja_gastronomico.json' junto al script.
"""
import json
import os
import math
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
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse, Line
from kivy.metrics import dp, sp
from kivy.animation import Animation

DATA_FILE = "sistema_caja_gastronomico.json"


def cargar_datos():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "caja_abierta": False,
        "monto_apertura": 0.0,
        "hora_apertura": "",
        "apertura_timestamp": "",
        "productos": [
            {"nombre": "Cuadril Broaster", "categoria": "Platos", "precio": 45.0, "stock_dia": 30},
            {"nombre": "Pollo Broaster 1/4", "categoria": "Platos", "precio": 28.0, "stock_dia": 25},
            {"nombre": "Papas Fritas", "categoria": "Guarniciones", "precio": 12.0, "stock_dia": 50},
            {"nombre": "Coca Cola 500ml", "categoria": "Bebidas", "precio": 8.0, "stock_dia": 40},
            {"nombre": "Salsa Extra", "categoria": "Extras", "precio": 3.0, "stock_dia": 100},
        ],
        "comandas": [],
        "historial_ventas": [],
        "historial_gastos": [],
        "contador_ventas": 0,
        "contador_gastos": 0,
        "contador_comandas": 0,
    }


def guardar_datos():
    data = {
        "caja_abierta": GlobalData.caja_abierta,
        "monto_apertura": GlobalData.monto_apertura,
        "hora_apertura": GlobalData.hora_apertura,
        "apertura_timestamp": GlobalData.apertura_timestamp,
        "productos": GlobalData.productos,
        "comandas": GlobalData.comandas,
        "historial_ventas": GlobalData.historial_ventas,
        "historial_gastos": GlobalData.historial_gastos,
        "contador_ventas": GlobalData.contador_ventas,
        "contador_gastos": GlobalData.contador_gastos,
        "contador_comandas": GlobalData.contador_comandas,
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[AVISO] No se pudieron guardar los datos: {e}")


class GlobalData:
    datos = cargar_datos()
    caja_abierta = datos["caja_abierta"]
    monto_apertura = datos["monto_apertura"]
    hora_apertura = datos.get("hora_apertura", "")
    apertura_timestamp = datos.get("apertura_timestamp", "")
    productos = datos["productos"]
    comandas = datos.get("comandas", [])
    historial_ventas = datos["historial_ventas"]
    historial_gastos = datos["historial_gastos"]
    contador_ventas = datos.get("contador_ventas", 0)
    contador_gastos = datos.get("contador_gastos", 0)
    contador_comandas = datos.get("contador_comandas", 0)


def calcular_arqueo_caja():
    """Suma ventas/gastos ocurridos desde que se abrió la caja (por timestamp),
    sin importar si el negocio sigue abierto pasada la medianoche."""
    desde = GlobalData.apertura_timestamp or ""
    ventas_sesion = [v for v in GlobalData.historial_ventas if v.get('timestamp', '') >= desde]
    gastos_sesion = [g for g in GlobalData.historial_gastos if g.get('timestamp', '') >= desde]

    ventas_efectivo = sum(v.get('monto_efectivo', 0.0) for v in ventas_sesion)
    ventas_qr = sum(v.get('monto_qr', 0.0) for v in ventas_sesion)
    ventas_totales = ventas_efectivo + ventas_qr
    gastos_efectivo = sum(g['monto'] for g in gastos_sesion)
    efectivo_teorico = GlobalData.monto_apertura + ventas_efectivo - gastos_efectivo
    ganancia_neta = ventas_totales - gastos_efectivo

    return {
        'ventas_efectivo': ventas_efectivo, 'ventas_qr': ventas_qr,
        'ventas_totales': ventas_totales, 'gastos_efectivo': gastos_efectivo,
        'efectivo_teorico': efectivo_teorico, 'ganancia_neta': ganancia_neta,
    }


def ranking_platos(top_n=10):
    conteo = {}
    for v in GlobalData.historial_ventas:
        for it in v.get('items', []):
            conteo[it['nombre']] = conteo.get(it['nombre'], 0) + it['cantidad']
    return sorted(conteo.items(), key=lambda kv: kv[1], reverse=True)[:top_n]


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
        Line(rounded_rectangle=(x + w * 0.08, y + h * 0.15, w * 0.84, h * 0.6, dp(4)), width=dp(1.8))
        Ellipse(pos=(x + w * 0.38, y + h * 0.32), size=(w * 0.24, w * 0.24))
        Line(points=[x + w * 0.5, y + h * 0.75, x + w * 0.5, y + h * 0.9], width=dp(1.8))

    def _draw_venta(self, x, y, w, h):
        Line(points=[
            x + w * 0.12, y + h * 0.78, x + w * 0.22, y + h * 0.78, x + w * 0.34, y + h * 0.32,
            x + w * 0.82, y + h * 0.32, x + w * 0.74, y + h * 0.6, x + w * 0.30, y + h * 0.6,
        ], width=dp(1.8), joint='round', cap='round')
        Ellipse(pos=(x + w * 0.34, y + h * 0.12), size=(w * 0.12, w * 0.12))
        Ellipse(pos=(x + w * 0.62, y + h * 0.12), size=(w * 0.12, w * 0.12))

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

    def _draw_siguiente(self, x, y, w, h):
        Line(points=[x + w * 0.38, y + h * 0.2, x + w * 0.68, y + h * 0.5, x + w * 0.38, y + h * 0.8],
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

    def _draw_mixto(self, x, y, w, h):
        Line(ellipse=(x + w * 0.14, y + h * 0.14, w * 0.72, h * 0.72), width=dp(1.8))
        Line(points=[x + w * 0.5, y + h * 0.16, x + w * 0.5, y + h * 0.84], width=dp(1.6))

    def _draw_gasto(self, x, y, w, h):
        Line(points=[x + w * 0.2, y + h * 0.75, x + w * 0.5, y + h * 0.25, x + w * 0.8, y + h * 0.75],
             width=dp(2.0), joint='round', cap='round')
        Line(points=[x + w * 0.5, y + h * 0.25, x + w * 0.5, y + h * 0.85], width=dp(2.0))

    def _draw_alerta(self, x, y, w, h):
        Line(points=[x + w * 0.5, y + h * 0.35, x + w * 0.5, y + h * 0.68], width=dp(2.2), cap='round')
        Ellipse(pos=(x + w * 0.5 - dp(1.4), y + h * 0.18), size=(dp(2.8), dp(2.8)))

    def _draw_editar(self, x, y, w, h):
        Line(points=[x + w * 0.22, y + h * 0.22, x + w * 0.72, y + h * 0.72], width=dp(3.0), cap='round')
        Line(points=[x + w * 0.68, y + h * 0.68, x + w * 0.8, y + h * 0.8], width=dp(3.0), cap='round')
        Line(points=[x + w * 0.16, y + h * 0.16, x + w * 0.26, y + h * 0.26], width=dp(3.0), cap='round')

    def _draw_eliminar(self, x, y, w, h):
        Line(rounded_rectangle=(x + w * 0.24, y + h * 0.14, w * 0.52, h * 0.56, dp(2)), width=dp(1.7))
        Line(points=[x + w * 0.16, y + h * 0.7, x + w * 0.84, y + h * 0.7], width=dp(1.7))
        Line(points=[x + w * 0.4, y + h * 0.76, x + w * 0.6, y + h * 0.76], width=dp(2.0))
        Line(points=[x + w * 0.38, y + h * 0.26, x + w * 0.38, y + h * 0.56], width=dp(1.4))
        Line(points=[x + w * 0.5, y + h * 0.26, x + w * 0.5, y + h * 0.56], width=dp(1.4))
        Line(points=[x + w * 0.62, y + h * 0.26, x + w * 0.62, y + h * 0.56], width=dp(1.4))

    def _draw_ticket(self, x, y, w, h):
        Line(rounded_rectangle=(x + w * 0.22, y + h * 0.12, w * 0.56, h * 0.76, dp(3)), width=dp(1.7))
        for i in range(3):
            yy = y + h * 0.3 + i * h * 0.16
            Line(points=[x + w * 0.34, yy, x + w * 0.66, yy], width=dp(1.4))

    def _draw_cerrar(self, x, y, w, h):
        Line(points=[x + w * 0.26, y + h * 0.26, x + w * 0.74, y + h * 0.74], width=dp(2.2), cap='round')
        Line(points=[x + w * 0.74, y + h * 0.26, x + w * 0.26, y + h * 0.74], width=dp(2.2), cap='round')

    def _draw_mesa(self, x, y, w, h):
        Line(rounded_rectangle=(x + w * 0.1, y + h * 0.55, w * 0.8, h * 0.16, dp(2)), width=dp(1.8))
        Line(points=[x + w * 0.2, y + h * 0.55, x + w * 0.2, y + h * 0.14], width=dp(1.8), cap='round')
        Line(points=[x + w * 0.8, y + h * 0.55, x + w * 0.8, y + h * 0.14], width=dp(1.8), cap='round')

    def _draw_plato(self, x, y, w, h):
        Line(ellipse=(x + w * 0.12, y + h * 0.12, w * 0.76, h * 0.76), width=dp(1.8))
        Line(ellipse=(x + w * 0.3, y + h * 0.3, w * 0.4, h * 0.4), width=dp(1.3))

    def _draw_estrella(self, x, y, w, h):
        cx, cy = x + w / 2, y + h / 2
        r = min(w, h) * 0.42
        pts = []
        for i in range(10):
            ang = math.pi / 2 + i * math.pi / 5
            rad = r if i % 2 == 0 else r * 0.42
            pts += [cx + rad * math.cos(ang), cy + rad * math.sin(ang)]
        pts += pts[:2]
        Line(points=pts, width=dp(1.6), joint='round', cap='round', close=True)


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
            self.border = Line(rounded_rectangle=(*self.pos, *self.size, self.radius_val), width=dp(1))
        self.bind(size=self._update_canvas, pos=self._update_canvas)

    def _update_canvas(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        self.border.rounded_rectangle = (instance.x, instance.y, instance.width,
                                          instance.height, self.radius_val)


class RoundedButton(ButtonBehavior, FloatLayout):
    """Botón con fondo redondeado, ícono opcional y animación al presionar."""

    def __init__(self, text='', icon=None, bg_color=None, bg_color_dark=None,
                 text_color=None, font_size=None, icon_size=None, radius=None, **kwargs):
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
            icon_pos_hint = {'center_x': 0.5, 'center_y': 0.5} if not text else {'x': 0.045, 'center_y': 0.5}
            self.icon_widget = Icon(
                kind=icon, color=text_color or Theme.TEXT,
                size_hint=(None, None), size=(icon_size or dp(20), icon_size or dp(20)),
                pos_hint=icon_pos_hint)
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
        self.cursor_color = Theme.PRIMARY
        self.hint_text_color = Theme.TEXT_DIM
        self.foreground_color = Theme.TEXT
        self.background_color = Theme.SURFACE
        self.selection_color = (Theme.PRIMARY[0], Theme.PRIMARY[1], Theme.PRIMARY[2], 0.35)
        self.padding = [dp(14), dp(12), dp(14), dp(12)]


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
        self.icon = Icon(kind='check', color=(1, 1, 1, 1), size_hint=(None, None), size=(dp(16), dp(16)))
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
            fg, icon_kind = Theme.PRIMARY, 'check'
        else:
            fg, icon_kind = Theme.DANGER, 'alerta'
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
# BARRA INFERIOR
# ---------------------------------------------------------------------------
class NavTab(ButtonBehavior, BoxLayout):
    def __init__(self, icon_kind, text, screen_name, sm, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(3), **kwargs)
        self.screen_name = screen_name
        self.sm = sm
        icon_holder = AnchorLayout(size_hint_y=None, height=dp(24))
        self.icon = Icon(kind=icon_kind, color=Theme.TEXT_MUTED, size_hint=(None, None), size=(dp(22), dp(22)))
        icon_holder.add_widget(self.icon)
        self.label = Label(text=text, font_size=sp(11), bold=True, color=Theme.TEXT_MUTED,
                            size_hint_y=None, height=dp(16))
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
            ('mesa', 'Mesas', 'mesas'),
            ('plato', 'Productos', 'productos'),
            ('caja', 'Caja', 'caja'),
            ('resumen', 'Reportes', 'reportes'),
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
# VENTANAS MODALES
# ---------------------------------------------------------------------------
def _popup_kwargs(title, size_hint=(0.87, None)):
    return dict(
        title=title, size_hint=size_hint,
        title_color=Theme.TEXT, title_size=sp(16),
        background_color=(0.08, 0.09, 0.11, 0.98),
        separator_color=Theme.SURFACE_BORDER,
    )


class ConfirmModal(Popup):
    def __init__(self, titulo, mensaje, on_confirmar, texto_confirmar='Confirmar',
                 texto_cancelar='Cancelar', color_confirmar=None, color_confirmar_dark=None,
                 icono_confirmar=None, **kwargs):
        color_confirmar = color_confirmar or Theme.PRIMARY
        color_confirmar_dark = color_confirmar_dark or Theme.PRIMARY_DARK

        content = BoxLayout(orientation='vertical', spacing=dp(18), padding=dp(20))
        lbl = Label(text=mensaje, font_size=sp(14.5), color=Theme.TEXT, halign='center', valign='middle')
        lbl.bind(size=lbl.setter('text_size'))
        content.add_widget(lbl)

        botones = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(12))
        btn_cancelar = RoundedButton(text=texto_cancelar, bg_color=Theme.NEUTRAL,
                                      bg_color_dark=Theme.NEUTRAL_DARK, font_size=sp(14))
        btn_confirmar = RoundedButton(text=texto_confirmar, icon=icono_confirmar,
                                       bg_color=color_confirmar, bg_color_dark=color_confirmar_dark,
                                       font_size=sp(13.5))
        botones.add_widget(btn_cancelar)
        botones.add_widget(btn_confirmar)
        content.add_widget(botones)

        super().__init__(content=content, auto_dismiss=False, height=dp(210), **_popup_kwargs(titulo), **kwargs)

        btn_cancelar.bind(on_release=lambda x: self.dismiss())

        def _confirmar(x):
            self.dismiss()
            on_confirmar()

        btn_confirmar.bind(on_release=_confirmar)


class CantidadNotaModal(Popup):
    """Elegir cantidad y una nota rápida (ej. 'Sin cebolla') antes de agregar a la comanda."""

    def __init__(self, producto, on_confirmar, **kwargs):
        self.producto = producto
        self.cantidad = 1
        self.max_stock = producto['stock_dia']

        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(18))
        lbl_prod = Label(text=producto['nombre'], font_size=sp(15), bold=True, color=Theme.TEXT,
                          size_hint_y=None, height=dp(24))
        content.add_widget(lbl_prod)

        stepper = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(14))
        btn_menos = RoundedButton(text='-', font_size=sp(18), bg_color=Theme.NEUTRAL,
                                   bg_color_dark=Theme.NEUTRAL_DARK, size_hint=(None, None), size=(dp(48), dp(48)))
        self.lbl_cant = Label(text='1', font_size=sp(20), bold=True, color=Theme.TEXT)
        btn_mas = RoundedButton(text='+', font_size=sp(18), bg_color=Theme.NEUTRAL,
                                 bg_color_dark=Theme.NEUTRAL_DARK, size_hint=(None, None), size=(dp(48), dp(48)))
        btn_menos.bind(on_release=lambda x: self._cambiar(-1))
        btn_mas.bind(on_release=lambda x: self._cambiar(1))
        stepper.add_widget(Widget())
        stepper.add_widget(btn_menos)
        stepper.add_widget(self.lbl_cant)
        stepper.add_widget(btn_mas)
        stepper.add_widget(Widget())
        content.add_widget(stepper)

        self.input_nota = RoundedInput(hint_text='Nota (ej. Sin cebolla, Término medio)',
                                        multiline=False, font_size=sp(13), size_hint_y=None, height=dp(48))
        content.add_widget(self.input_nota)

        botones = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(12))
        btn_cancelar = RoundedButton(text='Cancelar', bg_color=Theme.NEUTRAL,
                                      bg_color_dark=Theme.NEUTRAL_DARK, font_size=sp(14))
        btn_agregar = RoundedButton(text='Agregar', icon='plus', font_size=sp(13.5),
                                     bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK)
        botones.add_widget(btn_cancelar)
        botones.add_widget(btn_agregar)
        content.add_widget(botones)

        super().__init__(content=content, auto_dismiss=True, height=dp(330),
                          **_popup_kwargs('¿Cuántas porciones?'), **kwargs)

        btn_cancelar.bind(on_release=lambda x: self.dismiss())

        def _confirmar(x):
            if self.cantidad > 0:
                cant = self.cantidad
                nota = self.input_nota.text.strip()
                self.dismiss()
                on_confirmar(self.producto, cant, nota)

        btn_agregar.bind(on_release=_confirmar)

    def _cambiar(self, delta):
        nueva = max(1, min(self.cantidad + delta, self.max_stock))
        self.cantidad = nueva
        self.lbl_cant.text = str(self.cantidad)


class CatalogoModal(Popup):
    """Catálogo de productos por categoría, para agregar a la comanda actual."""
    CATEGORIAS = ['Platos', 'Bebidas', 'Guarniciones', 'Extras']

    def __init__(self, on_agregar, **kwargs):
        self.on_agregar_cb = on_agregar
        self.categoria_actual = 'Platos'

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(16))

        fila_cat = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
        self.botones_cat = {}
        for cat in self.CATEGORIAS:
            btn = RoundedButton(text=cat, font_size=sp(10.5), radius=dp(8))
            btn.bind(on_release=lambda x, c=cat: self._cambiar_categoria(c))
            self.botones_cat[cat] = btn
            fila_cat.add_widget(btn)
        content.add_widget(fila_cat)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.lista = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.lista.bind(minimum_height=self.lista.setter('height'))
        self.scroll.add_widget(self.lista)
        content.add_widget(self.scroll)

        btn_cerrar = RoundedButton(text='Cerrar', icon='cerrar', font_size=sp(13),
                                    bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK,
                                    size_hint_y=None, height=dp(46))
        content.add_widget(btn_cerrar)

        super().__init__(content=content, auto_dismiss=True, size_hint=(0.92, 0.85),
                          **{k: v for k, v in _popup_kwargs('Agregar Producto').items() if k != 'size_hint'},
                          **kwargs)
        btn_cerrar.bind(on_release=lambda x: self.dismiss())
        self._pintar_categorias()
        self._refrescar_lista()

    def _pintar_categorias(self):
        for c, btn in self.botones_cat.items():
            activo = c == self.categoria_actual
            btn.bg_color = Theme.PRIMARY if activo else Theme.NEUTRAL
            btn.bg_color_dark = Theme.PRIMARY_DARK if activo else Theme.NEUTRAL_DARK
            btn._color.rgba = btn.bg_color

    def _cambiar_categoria(self, cat):
        self.categoria_actual = cat
        self._pintar_categorias()
        self._refrescar_lista()

    def _refrescar_lista(self):
        self.lista.clear_widgets()
        productos_cat = [p for p in GlobalData.productos if p['categoria'] == self.categoria_actual]
        if not productos_cat:
            self.lista.add_widget(Label(text='No hay productos en esta categoría.', font_size=sp(12),
                                         color=Theme.TEXT_DIM, size_hint_y=None, height=dp(36)))
            return
        for p in productos_cat:
            agotado = p['stock_dia'] <= 0
            texto = f"{p['nombre']}  ·  {p['precio']:.2f} Bs"
            texto += "  ·  AGOTADO" if agotado else f"  ·  Quedan {p['stock_dia']}"
            btn = RoundedButton(
                text=texto, icon='alerta' if agotado else 'plato', font_size=sp(12),
                bg_color=Theme.NEUTRAL_DARK if agotado else Theme.SURFACE, bg_color_dark=Theme.NEUTRAL_DARK,
                text_color=Theme.TEXT_DIM if agotado else Theme.TEXT, icon_size=dp(15),
                size_hint_y=None, height=dp(46), radius=Theme.RADIUS_SM,
            )
            if not agotado:
                btn.bind(on_release=lambda x, prod=p: self._elegir_producto(prod))
            self.lista.add_widget(btn)

    def _elegir_producto(self, producto):
        modal = CantidadNotaModal(producto, on_confirmar=self._confirmar_agregar)
        modal.open()

    def _confirmar_agregar(self, producto, cantidad, nota):
        self.on_agregar_cb(producto, cantidad, nota)
        self.dismiss()


class PagoModal(Popup):
    """Cobro flexible: efectivo, QR o mixto (con ambos montos)."""

    def __init__(self, total, on_confirmar, **kwargs):
        self.total = total
        self.metodo = 'EFECTIVO'
        self.on_confirmar_cb = on_confirmar

        content = BoxLayout(orientation='vertical', spacing=dp(14), padding=dp(20))
        lbl_total = Label(text=f'Total a cobrar: {total:.2f} Bs', font_size=sp(17), bold=True,
                           color=Theme.PRIMARY, size_hint_y=None, height=dp(26))
        content.add_widget(lbl_total)

        fila_metodos = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.btn_efectivo = RoundedButton(text='Efectivo', icon='efectivo', font_size=sp(12),
                                           bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK)
        self.btn_qr = RoundedButton(text='QR', icon='qr', font_size=sp(12),
                                     bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK)
        self.btn_mixto = RoundedButton(text='Mixto', icon='mixto', font_size=sp(12),
                                        bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK)
        self.btn_efectivo.bind(on_release=lambda x: self._elegir_metodo('EFECTIVO'))
        self.btn_qr.bind(on_release=lambda x: self._elegir_metodo('QR'))
        self.btn_mixto.bind(on_release=lambda x: self._elegir_metodo('MIXTO'))
        fila_metodos.add_widget(self.btn_efectivo)
        fila_metodos.add_widget(self.btn_qr)
        fila_metodos.add_widget(self.btn_mixto)
        content.add_widget(fila_metodos)

        self.fila_mixto = BoxLayout(size_hint_y=None, height=0, spacing=dp(8), opacity=0)
        self.input_efectivo = RoundedInput(hint_text='Monto efectivo', input_filter='float',
                                            font_size=sp(13), multiline=False)
        self.input_qr = RoundedInput(hint_text='Monto QR', input_filter='float',
                                      font_size=sp(13), multiline=False)
        self.fila_mixto.add_widget(self.input_efectivo)
        self.fila_mixto.add_widget(self.input_qr)
        content.add_widget(self.fila_mixto)

        self.banner = MessageBanner()
        content.add_widget(self.banner)

        botones = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(12))
        btn_cancelar = RoundedButton(text='Cancelar', bg_color=Theme.NEUTRAL,
                                      bg_color_dark=Theme.NEUTRAL_DARK, font_size=sp(14))
        btn_confirmar = RoundedButton(text='Confirmar Cobro', icon='check', font_size=sp(12.5),
                                       bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK)
        botones.add_widget(btn_cancelar)
        botones.add_widget(btn_confirmar)
        content.add_widget(botones)

        super().__init__(content=content, auto_dismiss=False, height=dp(370),
                          **_popup_kwargs('Cobrar Cuenta'), **kwargs)

        btn_cancelar.bind(on_release=lambda x: self.dismiss())
        btn_confirmar.bind(on_release=self._confirmar)
        self._elegir_metodo('EFECTIVO')

    def _elegir_metodo(self, metodo):
        self.metodo = metodo
        for m, btn in [('EFECTIVO', self.btn_efectivo), ('QR', self.btn_qr), ('MIXTO', self.btn_mixto)]:
            activo = m == metodo
            btn.bg_color = Theme.PRIMARY if activo else Theme.NEUTRAL
            btn.bg_color_dark = Theme.PRIMARY_DARK if activo else Theme.NEUTRAL_DARK
            btn._color.rgba = btn.bg_color
        self.fila_mixto.opacity = 1 if metodo == 'MIXTO' else 0
        self.fila_mixto.height = dp(50) if metodo == 'MIXTO' else 0
        self.banner.hide()

    def _confirmar(self, instance):
        if self.metodo == 'EFECTIVO':
            self.dismiss()
            self.on_confirmar_cb('EFECTIVO', self.total, 0.0)
        elif self.metodo == 'QR':
            self.dismiss()
            self.on_confirmar_cb('QR', 0.0, self.total)
        else:
            try:
                monto_ef = float(self.input_efectivo.text) if self.input_efectivo.text else 0.0
                monto_qr = float(self.input_qr.text) if self.input_qr.text else 0.0
            except ValueError:
                self.banner.show('Ingresa montos válidos.', 'error')
                return
            if monto_ef < 0 or monto_qr < 0:
                self.banner.show('Los montos no pueden ser negativos.', 'error')
                return
            if abs((monto_ef + monto_qr) - self.total) > 0.01:
                self.banner.show(f'La suma debe dar {self.total:.2f} Bs.', 'error')
                return
            self.dismiss()
            self.on_confirmar_cb('MIXTO', monto_ef, monto_qr)


class PostPagoModal(Popup):
    """Tras confirmar el pago: ¿se libera la mesa ahora o se mantiene ocupada (ya pagada)?"""

    def __init__(self, metodo, total, on_elegir, **kwargs):
        content = BoxLayout(orientation='vertical', spacing=dp(16), padding=dp(20))

        lbl = Label(text=f'Pago registrado: {total:.2f} Bs ({metodo})', font_size=sp(14.5), bold=True,
                    color=Theme.PRIMARY, size_hint_y=None, height=dp(26), halign='center', valign='middle')
        lbl.bind(size=lbl.setter('text_size'))
        content.add_widget(lbl)

        pregunta = Label(text='¿La mesa se retira o se queda?', font_size=sp(13.5), color=Theme.TEXT,
                          size_hint_y=None, height=dp(22), halign='center', valign='middle')
        pregunta.bind(size=pregunta.setter('text_size'))
        content.add_widget(pregunta)

        btn_liberar = RoundedButton(text='Marcar Pagado y Liberar Mesa', icon='check', font_size=sp(13),
                                     bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK,
                                     size_hint_y=None, height=dp(54))
        btn_mantener = RoundedButton(text='Marcar Pagado pero Mantener Ocupada', icon='mesa', font_size=sp(11.5),
                                      bg_color=Theme.ACCENT_BLUE, bg_color_dark=Theme.ACCENT_BLUE_DARK,
                                      size_hint_y=None, height=dp(54))
        content.add_widget(btn_liberar)
        content.add_widget(btn_mantener)

        super().__init__(content=content, auto_dismiss=False, height=dp(300),
                          **_popup_kwargs('Cobro Confirmado'), **kwargs)

        def _liberar(x):
            self.dismiss()
            on_elegir(True)

        def _mantener(x):
            self.dismiss()
            on_elegir(False)

        btn_liberar.bind(on_release=_liberar)
        btn_mantener.bind(on_release=_mantener)


class TicketModal(Popup):
    """Comprobante de venta para el cliente."""

    def __init__(self, venta, **kwargs):
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(18))
        scroll = ScrollView(size_hint=(1, 1))
        info = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None, padding=(0, dp(4)))
        info.bind(minimum_height=info.setter('height'))

        def linea(texto, size=13, bold=False, color=None, align='left'):
            lbl = Label(text=texto, font_size=sp(size), bold=bold, color=color or Theme.TEXT,
                        halign=align, valign='middle', size_hint_y=None, height=dp(size + 10))
            lbl.bind(size=lbl.setter('text_size'))
            info.add_widget(lbl)

        linea(f"VENTA #{venta['ticket']:04d}", size=16, bold=True, color=Theme.PRIMARY, align='center')
        linea(venta['mesa'], size=13, color=Theme.TEXT_MUTED, align='center')
        linea(f"Fecha: {venta['fecha']}    Hora: {venta['hora']}", size=11.5,
              color=Theme.TEXT_MUTED, align='center')
        info.add_widget(Widget(size_hint_y=None, height=dp(6)))

        for it in venta['items']:
            sub = it['precio'] * it['cantidad']
            texto_item = it['nombre'] + (f"  ({it['nota']})" if it.get('nota') else '')
            linea(texto_item, size=13, bold=True)
            linea(f"  {it['cantidad']} x {it['precio']:.2f} Bs{' ' * 6}{sub:.2f} Bs",
                  size=12, color=Theme.TEXT_MUTED)

        info.add_widget(Widget(size_hint_y=None, height=dp(6)))
        linea(f"TOTAL: {venta['total']:.2f} Bs", size=17, bold=True, color=Theme.PRIMARY, align='center')
        metodo_txt = venta['metodo']
        if metodo_txt == 'MIXTO':
            metodo_txt += f" (Efvo {venta['monto_efectivo']:.2f} / QR {venta['monto_qr']:.2f})"
        linea(f"Pago: {metodo_txt}", size=12.5, color=Theme.TEXT_MUTED, align='center')

        scroll.add_widget(info)
        content.add_widget(scroll)

        content.add_widget(Label(text='¡Gracias por su visita!', font_size=sp(13), italic=True,
                                  color=Theme.TEXT_MUTED, size_hint_y=None, height=dp(24)))

        btn_cerrar = RoundedButton(text='Cerrar', icon='cerrar', font_size=sp(14),
                                    bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK,
                                    size_hint_y=None, height=dp(48))
        content.add_widget(btn_cerrar)

        super().__init__(content=content, auto_dismiss=True, size_hint=(0.9, 0.82),
                          **{k: v for k, v in _popup_kwargs('Comprobante de Venta').items() if k != 'size_hint'},
                          **kwargs)
        btn_cerrar.bind(on_release=lambda x: self.dismiss())


class ComandaTicketModal(Popup):
    """Comanda simplificada para enviar a cocina: sin precios, con notas."""

    def __init__(self, comanda, **kwargs):
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(18))
        scroll = ScrollView(size_hint=(1, 1))
        info = BoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None, padding=(0, dp(4)))
        info.bind(minimum_height=info.setter('height'))

        info.add_widget(Label(text=comanda['nombre'], font_size=sp(18), bold=True, color=Theme.PRIMARY,
                               size_hint_y=None, height=dp(28)))
        info.add_widget(Label(text=f"Hora: {datetime.now().strftime('%H:%M')}", font_size=sp(11.5),
                               color=Theme.TEXT_MUTED, size_hint_y=None, height=dp(18)))
        info.add_widget(Widget(size_hint_y=None, height=dp(8)))

        for it in comanda['items']:
            lbl = Label(text=f"{it['cantidad']} x {it['nombre']}", font_size=sp(15), bold=True,
                        color=Theme.TEXT, halign='left', valign='middle', size_hint_y=None, height=dp(24))
            lbl.bind(size=lbl.setter('text_size'))
            info.add_widget(lbl)
            if it.get('nota'):
                nota_lbl = Label(text=f"   -> {it['nota']}", font_size=sp(12.5), italic=True,
                                  color=Theme.WARNING, halign='left', valign='middle',
                                  size_hint_y=None, height=dp(20))
                nota_lbl.bind(size=nota_lbl.setter('text_size'))
                info.add_widget(nota_lbl)

        scroll.add_widget(info)
        content.add_widget(scroll)

        btn_cerrar = RoundedButton(text='Cerrar', icon='cerrar', font_size=sp(14),
                                    bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK,
                                    size_hint_y=None, height=dp(48))
        content.add_widget(btn_cerrar)

        super().__init__(content=content, auto_dismiss=True, size_hint=(0.88, 0.75),
                          **{k: v for k, v in _popup_kwargs('Comanda para Cocina').items() if k != 'size_hint'},
                          **kwargs)
        btn_cerrar.bind(on_release=lambda x: self.dismiss())


class EditarGastoModal(Popup):
    def __init__(self, gasto, on_guardado, **kwargs):
        self.gasto = gasto
        self.on_guardado_cb = on_guardado

        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(18))
        self.input_categoria = RoundedInput(hint_text='Categoría', multiline=False, font_size=sp(13),
                                             size_hint_y=None, height=dp(48))
        self.input_categoria.text = gasto.get('categoria', '')
        self.input_monto = RoundedInput(hint_text='Monto (Bs)', input_filter='float', multiline=False,
                                         font_size=sp(13), size_hint_y=None, height=dp(48))
        self.input_monto.text = str(gasto.get('monto', 0))
        self.input_descripcion = RoundedInput(hint_text='Descripción', multiline=False, font_size=sp(13),
                                               size_hint_y=None, height=dp(48))
        self.input_descripcion.text = gasto.get('descripcion', '')
        content.add_widget(self.input_categoria)
        content.add_widget(self.input_monto)
        content.add_widget(self.input_descripcion)

        self.banner = MessageBanner()
        content.add_widget(self.banner)

        botones = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(12))
        btn_cancelar = RoundedButton(text='Cancelar', bg_color=Theme.NEUTRAL,
                                      bg_color_dark=Theme.NEUTRAL_DARK, font_size=sp(14))
        btn_guardar = RoundedButton(text='Guardar Cambios', icon='check', font_size=sp(12.5),
                                     bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK)
        botones.add_widget(btn_cancelar)
        botones.add_widget(btn_guardar)
        content.add_widget(botones)

        super().__init__(content=content, auto_dismiss=False, height=dp(340), **_popup_kwargs('Editar Gasto'), **kwargs)

        btn_cancelar.bind(on_release=lambda x: self.dismiss())
        btn_guardar.bind(on_release=self._guardar)

    def _guardar(self, instance):
        try:
            monto = float(self.input_monto.text) if self.input_monto.text else 0.0
            if monto <= 0:
                self.banner.show('El monto debe ser mayor a 0.', 'error')
                return
            self.gasto['categoria'] = self.input_categoria.text.strip() or 'Otros'
            self.gasto['monto'] = monto
            self.gasto['descripcion'] = self.input_descripcion.text.strip()
            guardar_datos()
            self.dismiss()
            self.on_guardado_cb()
        except ValueError:
            self.banner.show('Verifica el monto ingresado.', 'error')


# ---------------------------------------------------------------------------
# PANTALLAS
# ---------------------------------------------------------------------------
class MesasScreen(BaseScreen):
    NUM_MESAS = 6

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_layout.add_widget(make_title('Mesas y Pedidos'))

        self.grid_mesas = GridLayout(cols=3, spacing=dp(8), size_hint_y=None)
        self.grid_mesas.bind(minimum_height=self.grid_mesas.setter('height'))
        self.content_layout.add_widget(self.grid_mesas)

        fila_nuevos = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        btn_llevar = RoundedButton(text='+ Para Llevar', icon='plus', font_size=sp(12),
                                    bg_color=Theme.ACCENT_BLUE, bg_color_dark=Theme.ACCENT_BLUE_DARK)
        btn_llevar.bind(on_release=lambda x: self.nuevo_pedido('Para Llevar'))
        btn_delivery = RoundedButton(text='+ Delivery', icon='plus', font_size=sp(12),
                                      bg_color=Theme.WARNING, bg_color_dark=Theme.WARNING_DARK)
        btn_delivery.bind(on_release=lambda x: self.nuevo_pedido('Delivery'))
        fila_nuevos.add_widget(btn_llevar)
        fila_nuevos.add_widget(btn_delivery)
        self.content_layout.add_widget(fila_nuevos)

        self.content_layout.add_widget(
            Label(text='Para llevar / delivery activos', font_size=sp(12.5), bold=True,
                  color=Theme.TEXT_MUTED, size_hint_y=None, height=dp(20), halign='left', valign='middle')
        )
        self.scroll_otros = ScrollView(size_hint=(1, 1))
        self.lista_otros = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.lista_otros.bind(minimum_height=self.lista_otros.setter('height'))
        self.scroll_otros.add_widget(self.lista_otros)
        self.content_layout.add_widget(self.scroll_otros)

    def on_enter(self):
        self._refrescar()

    def _refrescar(self):
        self.grid_mesas.clear_widgets()
        nombres_mesas = [f'Mesa {i}' for i in range(1, self.NUM_MESAS + 1)]
        for nombre in nombres_mesas:
            comanda = next((c for c in GlobalData.comandas if c['nombre'] == nombre), None)
            bg, bg_dark, txt_color, texto = self._estilo_mesa(nombre, comanda)
            card = RoundedButton(
                text=texto, bg_color=bg, bg_color_dark=bg_dark, text_color=txt_color,
                font_size=sp(12.5), size_hint_y=None, height=dp(64), radius=Theme.RADIUS_SM,
            )
            card.bind(on_release=lambda x, n=nombre: self.abrir_mesa(n))
            self.grid_mesas.add_widget(card)

        self.lista_otros.clear_widgets()
        otros = [c for c in GlobalData.comandas if c['nombre'] not in nombres_mesas]
        if not otros:
            self.lista_otros.add_widget(
                Label(text='No hay pedidos para llevar/delivery activos.', font_size=sp(12),
                      color=Theme.TEXT_DIM, size_hint_y=None, height=dp(32))
            )
        for c in otros:
            if c.get('pagada'):
                texto = f"{c['nombre']}  ·  PAGADO ✓  ·  toca para liberar"
                bg_color, bg_color_dark = Theme.PRIMARY, Theme.PRIMARY_DARK
            else:
                total = sum(it['precio'] * it['cantidad'] for it in c['items'])
                texto = f"{c['nombre']}  ·  {len(c['items'])} items  ·  {total:.2f} Bs"
                bg_color, bg_color_dark = Theme.SURFACE, Theme.NEUTRAL_DARK
            row = RoundedButton(
                text=texto, icon='venta', bg_color=bg_color, bg_color_dark=bg_color_dark,
                text_color=Theme.TEXT, font_size=sp(12), size_hint_y=None, height=dp(46),
                radius=Theme.RADIUS_SM,
            )
            row.bind(on_release=lambda x, n=c['nombre']: self.abrir_mesa(n))
            self.lista_otros.add_widget(row)

    def _estilo_mesa(self, nombre, comanda):
        """Devuelve (bg, bg_dark, text_color, texto) según el estado de la mesa."""
        if comanda is None:
            return Theme.SURFACE, Theme.NEUTRAL_DARK, Theme.TEXT_MUTED, f"{nombre}\nLibre"
        if comanda.get('pagada'):
            return Theme.PRIMARY, Theme.PRIMARY_DARK, Theme.TEXT, f"{nombre}\nPAGADO ✓"
        total = sum(it['precio'] * it['cantidad'] for it in comanda['items'])
        return Theme.WARNING, Theme.WARNING_DARK, Theme.TEXT, f"{nombre}\n{total:.2f} Bs"

    def nuevo_pedido(self, tipo):
        GlobalData.contador_comandas += 1
        nombre = f"{tipo} #{GlobalData.contador_comandas:03d}"
        comanda = {'id': GlobalData.contador_comandas, 'nombre': nombre, 'items': [],
                   'hora_apertura': datetime.now().strftime('%H:%M'), 'pagada': False}
        GlobalData.comandas.append(comanda)
        guardar_datos()
        self.abrir_mesa(nombre)

    def abrir_mesa(self, nombre):
        comanda = next((c for c in GlobalData.comandas if c['nombre'] == nombre), None)
        if comanda and comanda.get('pagada'):
            self._mostrar_modal_liberar(comanda)
            return
        if not comanda:
            GlobalData.contador_comandas += 1
            comanda = {'id': GlobalData.contador_comandas, 'nombre': nombre, 'items': [],
                       'hora_apertura': datetime.now().strftime('%H:%M'), 'pagada': False}
            GlobalData.comandas.append(comanda)
            guardar_datos()
        self.manager.get_screen('comanda').abrir(comanda)
        self.manager.current = 'comanda'

    def _mostrar_modal_liberar(self, comanda):
        ConfirmModal(
            titulo='Cuenta Saldada',
            mensaje=f"\"{comanda['nombre']}\" ya está pagada y sigue ocupada.\n¿Liberar la mesa ahora?",
            texto_confirmar='Liberar Mesa', icono_confirmar='check',
            color_confirmar=Theme.PRIMARY, color_confirmar_dark=Theme.PRIMARY_DARK,
            on_confirmar=lambda: self.liberar_mesa(comanda),
        ).open()

    def liberar_mesa(self, comanda):
        if comanda in GlobalData.comandas:
            GlobalData.comandas.remove(comanda)
        guardar_datos()
        self._refrescar()


class ComandaScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.comanda = None

        self.titulo_lbl = make_title('Comanda')
        self.content_layout.add_widget(self.titulo_lbl)

        self.lbl_info = Label(text='', font_size=sp(12), color=Theme.TEXT_MUTED,
                               size_hint_y=None, height=dp(18), halign='left', valign='middle')
        self.lbl_info.bind(size=self.lbl_info.setter('text_size'))
        self.content_layout.add_widget(self.lbl_info)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.lista_items = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.lista_items.bind(minimum_height=self.lista_items.setter('height'))
        self.scroll.add_widget(self.lista_items)
        self.content_layout.add_widget(self.scroll)

        self.lbl_total = Label(text='Total: 0.00 Bs', font_size=sp(18), bold=True,
                                color=Theme.PRIMARY, size_hint_y=None, height=dp(30))
        self.content_layout.add_widget(self.lbl_total)

        self.banner = MessageBanner()
        self.content_layout.add_widget(self.banner)

        btn_agregar = RoundedButton(text='Agregar Producto', icon='plus', font_size=sp(14),
                                     bg_color=Theme.ACCENT_BLUE, bg_color_dark=Theme.ACCENT_BLUE_DARK,
                                     size_hint_y=None, height=dp(52))
        btn_agregar.bind(on_release=lambda x: self.abrir_catalogo())
        self.content_layout.add_widget(btn_agregar)

        fila_acciones = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        btn_cocina = RoundedButton(text='Enviar a Cocina', icon='ticket', font_size=sp(12),
                                    bg_color=Theme.WARNING, bg_color_dark=Theme.WARNING_DARK)
        btn_cocina.bind(on_release=lambda x: self.enviar_cocina())
        btn_cancelar = RoundedButton(text='Cancelar Mesa', icon='cerrar', font_size=sp(12),
                                      bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK)
        btn_cancelar.bind(on_release=lambda x: self.confirmar_cancelar_mesa())
        fila_acciones.add_widget(btn_cocina)
        fila_acciones.add_widget(btn_cancelar)
        self.content_layout.add_widget(fila_acciones)

        btn_cobrar = RoundedButton(text='Cobrar', icon='efectivo', font_size=sp(16),
                                    bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK,
                                    size_hint_y=None, height=dp(56))
        btn_cobrar.bind(on_release=lambda x: self.iniciar_cobro())
        self.content_layout.add_widget(btn_cobrar)

        btn_volver = RoundedButton(text='Volver a Mesas', icon='back', font_size=sp(13),
                                    bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK,
                                    size_hint_y=None, height=dp(44))
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'mesas'))
        self.content_layout.add_widget(btn_volver)

    def abrir(self, comanda):
        self.comanda = comanda
        self.banner.hide()
        self._refrescar()

    def on_leave(self):
        self.comanda = None

    def _refrescar(self):
        if not self.comanda:
            return
        self.titulo_lbl.text = self.comanda['nombre']
        self.lbl_info.text = f"Abierta a las {self.comanda.get('hora_apertura', '')}"
        self.lista_items.clear_widgets()
        total = 0.0
        for item in self.comanda['items']:
            sub = item['precio'] * item['cantidad']
            total += sub
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(6))
            texto = item['nombre'] + (f"  ({item['nota']})" if item.get('nota') else '')
            info = Label(text=texto, font_size=sp(12.5), color=Theme.TEXT, halign='left', valign='middle',
                         shorten=True, shorten_from='right')
            info.bind(size=info.setter('text_size'))

            btn_menos = RoundedButton(text='-', font_size=sp(16), bg_color=Theme.NEUTRAL,
                                       bg_color_dark=Theme.NEUTRAL_DARK, size_hint=(None, None),
                                       size=(dp(32), dp(32)), radius=dp(8))
            btn_menos.bind(on_release=lambda x, it=item: self.cambiar_cantidad(it, -1))
            lbl_cant = Label(text=str(item['cantidad']), font_size=sp(13), bold=True, color=Theme.TEXT,
                              size_hint=(None, None), size=(dp(24), dp(32)))
            btn_mas = RoundedButton(text='+', font_size=sp(16), bg_color=Theme.NEUTRAL,
                                     bg_color_dark=Theme.NEUTRAL_DARK, size_hint=(None, None),
                                     size=(dp(32), dp(32)), radius=dp(8))
            btn_mas.bind(on_release=lambda x, it=item: self.cambiar_cantidad(it, 1))
            sub_lbl = Label(text=f"{sub:.2f}", font_size=sp(12.5), bold=True, color=Theme.PRIMARY,
                             size_hint=(None, None), size=(dp(56), dp(32)))

            row.add_widget(info)
            row.add_widget(btn_menos)
            row.add_widget(lbl_cant)
            row.add_widget(btn_mas)
            row.add_widget(sub_lbl)
            self.lista_items.add_widget(row)
        self.lbl_total.text = f'Total: {total:.2f} Bs'

    def cambiar_cantidad(self, item, delta):
        producto = next((p for p in GlobalData.productos if p['nombre'] == item['nombre']), None)
        if delta > 0:
            if not producto or producto['stock_dia'] <= 0:
                self.banner.show('No queda stock disponible de este producto.', 'error')
                return
            item['cantidad'] += 1
            producto['stock_dia'] -= 1
        else:
            item['cantidad'] -= 1
            if producto:
                producto['stock_dia'] += 1
            if item['cantidad'] <= 0:
                self.comanda['items'].remove(item)
        guardar_datos()
        self._refrescar()

    def abrir_catalogo(self):
        if not self.comanda:
            return
        CatalogoModal(on_agregar=self.agregar_item).open()

    def agregar_item(self, producto, cantidad, nota):
        cantidad = max(0, min(cantidad, producto['stock_dia']))
        if cantidad <= 0:
            self.banner.show('No queda stock disponible de este producto.', 'error')
            return
        existente = next((it for it in self.comanda['items']
                           if it['nombre'] == producto['nombre'] and it.get('nota', '') == nota), None)
        if existente:
            existente['cantidad'] += cantidad
        else:
            self.comanda['items'].append({'nombre': producto['nombre'], 'precio': producto['precio'],
                                           'cantidad': cantidad, 'nota': nota})
        producto['stock_dia'] -= cantidad
        guardar_datos()
        self._refrescar()

    def enviar_cocina(self):
        if not self.comanda or not self.comanda['items']:
            self.banner.show('No hay productos para enviar a cocina.', 'error')
            return
        ComandaTicketModal(self.comanda).open()

    def confirmar_cancelar_mesa(self):
        if not self.comanda:
            return
        ConfirmModal(
            titulo='Cancelar Mesa',
            mensaje=f"¿Cancelar \"{self.comanda['nombre']}\"?\nSe liberará la mesa y se devolverá el stock reservado.",
            texto_confirmar='Cancelar Mesa', icono_confirmar='cerrar',
            color_confirmar=Theme.DANGER, color_confirmar_dark=Theme.DANGER_DARK,
            on_confirmar=self.cancelar_mesa,
        ).open()

    def cancelar_mesa(self):
        if not self.comanda:
            return
        for item in self.comanda['items']:
            producto = next((p for p in GlobalData.productos if p['nombre'] == item['nombre']), None)
            if producto:
                producto['stock_dia'] += item['cantidad']
        if self.comanda in GlobalData.comandas:
            GlobalData.comandas.remove(self.comanda)
        guardar_datos()
        self.comanda = None
        self.manager.current = 'mesas'

    def iniciar_cobro(self):
        if not GlobalData.caja_abierta:
            self.banner.show('Debes abrir la caja antes de cobrar.', 'error')
            return
        if not self.comanda or not self.comanda['items']:
            self.banner.show('Agrega productos antes de cobrar.', 'error')
            return
        total = sum(it['precio'] * it['cantidad'] for it in self.comanda['items'])
        PagoModal(total=total, on_confirmar=self._elegir_liberacion).open()

    def _elegir_liberacion(self, metodo, monto_efectivo, monto_qr):
        total = monto_efectivo + monto_qr
        PostPagoModal(
            metodo=metodo, total=total,
            on_elegir=lambda liberar: self._procesar_cobro(metodo, monto_efectivo, monto_qr, liberar),
        ).open()

    def _procesar_cobro(self, metodo, monto_efectivo, monto_qr, liberar):
        if not self.comanda:
            return
        total = sum(it['precio'] * it['cantidad'] for it in self.comanda['items'])
        GlobalData.contador_ventas += 1
        ticket_num = GlobalData.contador_ventas
        ahora = datetime.now()
        venta = {
            "ticket": ticket_num, "fecha": ahora.strftime("%d/%m/%Y"), "hora": ahora.strftime("%H:%M:%S"),
            "timestamp": ahora.isoformat(), "mesa": self.comanda['nombre'],
            "items": [dict(it) for it in self.comanda['items']], "total": total, "metodo": metodo,
            "monto_efectivo": monto_efectivo, "monto_qr": monto_qr,
        }
        GlobalData.historial_ventas.append(venta)

        if liberar:
            if self.comanda in GlobalData.comandas:
                GlobalData.comandas.remove(self.comanda)
        else:
            # Queda ocupada y marcada como pagada; se vacía la cuenta ya cobrada
            # para que, si se reabre por error, no se pueda volver a cobrar lo mismo.
            self.comanda['items'] = []
            self.comanda['pagada'] = True
            self.comanda['hora_pago'] = ahora.strftime('%H:%M')
        guardar_datos()

        TicketModal(venta).open()
        self.comanda = None
        self.manager.current = 'mesas'


class ProductosScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_layout.add_widget(make_title('Catálogo de Productos'))

        self.scroll = ScrollView(size_hint=(1, 1))
        self.lista = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.lista.bind(minimum_height=self.lista.setter('height'))
        self.scroll.add_widget(self.lista)
        self.content_layout.add_widget(self.scroll)

        btn_nuevo = RoundedButton(text='Nuevo Producto', icon='plus', font_size=sp(14),
                                   bg_color=Theme.WARNING, bg_color_dark=Theme.WARNING_DARK,
                                   size_hint_y=None, height=dp(50))
        btn_nuevo.bind(on_release=self.ir_a_nuevo)
        self.content_layout.add_widget(btn_nuevo)

    def ir_a_nuevo(self, instance):
        self.manager.get_screen('producto_form').cargar_para_nuevo()
        self.manager.current = 'producto_form'

    def on_enter(self):
        self.lista.clear_widgets()
        for prod in GlobalData.productos:
            agotado = prod['stock_dia'] <= 0
            color_stock = Theme.DANGER if agotado else Theme.PRIMARY

            row = RoundedCard(orientation='vertical', padding=(dp(14), dp(10)), spacing=dp(6),
                               size_hint_y=None, height=dp(88))

            fila_sup = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(32))
            nombre_lbl = Label(text=prod['nombre'], font_size=sp(14), bold=True, color=Theme.TEXT,
                                halign='left', valign='middle', shorten=True, shorten_from='right')
            nombre_lbl.bind(size=nombre_lbl.setter('text_size'))
            btn_editar = RoundedButton(icon='editar', bg_color=Theme.ACCENT_BLUE,
                                        bg_color_dark=Theme.ACCENT_BLUE_DARK, icon_size=dp(15),
                                        size_hint=(None, None), size=(dp(32), dp(32)), radius=dp(9))
            btn_editar.bind(on_release=lambda x, p=prod: self.editar_producto(p))
            btn_eliminar = RoundedButton(icon='eliminar', bg_color=Theme.DANGER,
                                          bg_color_dark=Theme.DANGER_DARK, icon_size=dp(15),
                                          size_hint=(None, None), size=(dp(32), dp(32)), radius=dp(9))
            btn_eliminar.bind(on_release=lambda x, p=prod: self.confirmar_eliminar(p))
            fila_sup.add_widget(nombre_lbl)
            fila_sup.add_widget(btn_editar)
            fila_sup.add_widget(btn_eliminar)
            row.add_widget(fila_sup)

            fila_inf = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(36))
            detalle_lbl = Label(text=f"{prod['categoria']}  ·  {prod['precio']:.2f} Bs",
                                 font_size=sp(12), color=Theme.TEXT_MUTED, halign='left', valign='middle')
            detalle_lbl.bind(size=detalle_lbl.setter('text_size'))
            stock_lbl = Label(text=('AGOTADO' if agotado else f"{prod['stock_dia']} disp."),
                               font_size=sp(12), bold=True, color=color_stock,
                               size_hint_x=None, width=dp(90), halign='right', valign='middle')
            stock_lbl.bind(size=stock_lbl.setter('text_size'))
            fila_inf.add_widget(detalle_lbl)
            fila_inf.add_widget(stock_lbl)
            row.add_widget(fila_inf)

            self.lista.add_widget(row)

    def editar_producto(self, producto):
        self.manager.get_screen('producto_form').cargar_para_editar(producto)
        self.manager.current = 'producto_form'

    def confirmar_eliminar(self, producto):
        ConfirmModal(
            titulo='Eliminar producto',
            mensaje=f"¿Está seguro de eliminar \"{producto['nombre']}\" del catálogo?",
            texto_confirmar='Eliminar', icono_confirmar='eliminar',
            color_confirmar=Theme.DANGER, color_confirmar_dark=Theme.DANGER_DARK,
            on_confirmar=lambda: self.eliminar_producto(producto),
        ).open()

    def eliminar_producto(self, producto):
        if producto in GlobalData.productos:
            GlobalData.productos.remove(producto)
        guardar_datos()
        self.on_enter()


class ProductoFormScreen(BaseScreen):
    CATEGORIAS = ['Platos', 'Bebidas', 'Guarniciones', 'Extras']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.producto_editando = None

        self.titulo_lbl = make_title('Nuevo Producto')
        self.content_layout.add_widget(self.titulo_lbl)

        self.input_nombre = RoundedInput(hint_text='Nombre del producto', multiline=False,
                                          size_hint_y=None, height=dp(52), font_size=sp(14))
        self.content_layout.add_widget(self.input_nombre)

        self.content_layout.add_widget(
            Label(text='Categoría', font_size=sp(12.5), color=Theme.TEXT_MUTED,
                  size_hint_y=None, height=dp(18), halign='left', valign='middle')
        )
        fila_cat = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        self.categoria_actual = 'Platos'
        self.botones_cat = {}
        for cat in self.CATEGORIAS:
            btn = RoundedButton(text=cat, font_size=sp(10.5), radius=dp(8))
            btn.bind(on_release=lambda x, c=cat: self._elegir_categoria(c))
            self.botones_cat[cat] = btn
            fila_cat.add_widget(btn)
        self.content_layout.add_widget(fila_cat)

        fila_precios = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        self.input_precio = RoundedInput(hint_text='Precio de venta (Bs)', input_filter='float',
                                          multiline=False, font_size=sp(13.5))
        self.input_stock = RoundedInput(hint_text='Porciones disponibles hoy', input_filter='int',
                                         multiline=False, font_size=sp(13.5))
        fila_precios.add_widget(self.input_precio)
        fila_precios.add_widget(self.input_stock)
        self.content_layout.add_widget(fila_precios)

        self.banner = MessageBanner()
        self.content_layout.add_widget(self.banner)

        self.btn_guardar = RoundedButton(text='Guardar', icon='check', font_size=sp(15),
                                          bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK,
                                          size_hint_y=None, height=dp(52))
        self.btn_guardar.bind(on_release=self.guardar_producto)
        self.content_layout.add_widget(self.btn_guardar)

        btn_volver = RoundedButton(text='Volver al Catálogo', icon='back', font_size=sp(13),
                                    bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK,
                                    size_hint_y=None, height=dp(46))
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'productos'))
        self.content_layout.add_widget(btn_volver)

        self.content_layout.add_widget(Widget())
        self._pintar_categoria()

    def _elegir_categoria(self, cat):
        self.categoria_actual = cat
        self._pintar_categoria()

    def _pintar_categoria(self):
        for c, btn in self.botones_cat.items():
            activo = c == self.categoria_actual
            btn.bg_color = Theme.PRIMARY if activo else Theme.NEUTRAL
            btn.bg_color_dark = Theme.PRIMARY_DARK if activo else Theme.NEUTRAL_DARK
            btn._color.rgba = btn.bg_color

    def _limpiar(self):
        self.input_nombre.text = ''
        self.input_precio.text = ''
        self.input_stock.text = ''
        self.categoria_actual = 'Platos'
        self._pintar_categoria()
        self.banner.hide()

    def cargar_para_nuevo(self):
        self.producto_editando = None
        self.titulo_lbl.text = 'Nuevo Producto'
        self.btn_guardar.label.text = 'Guardar'
        self._limpiar()

    def cargar_para_editar(self, producto):
        self.producto_editando = producto
        self.titulo_lbl.text = 'Editar Producto'
        self.btn_guardar.label.text = 'Guardar Cambios'
        self.input_nombre.text = producto['nombre']
        self.input_precio.text = str(producto['precio'])
        self.input_stock.text = str(producto['stock_dia'])
        self.categoria_actual = producto.get('categoria', 'Platos')
        self._pintar_categoria()
        self.banner.hide()

    def guardar_producto(self, instance):
        try:
            nombre = self.input_nombre.text.strip()
            precio = float(self.input_precio.text) if self.input_precio.text else 0.0
            stock = int(self.input_stock.text) if self.input_stock.text else 0

            if not nombre:
                self.banner.show('Ingresa un nombre de producto.', 'error')
                return
            if precio < 0 or stock < 0:
                self.banner.show('Los valores no pueden ser negativos.', 'error')
                return

            if self.producto_editando is not None:
                self.producto_editando['nombre'] = nombre
                self.producto_editando['categoria'] = self.categoria_actual
                self.producto_editando['precio'] = precio
                self.producto_editando['stock_dia'] = stock
                guardar_datos()
                self.banner.show('¡Producto actualizado!', 'success')
            else:
                GlobalData.productos.append({'nombre': nombre, 'categoria': self.categoria_actual,
                                              'precio': precio, 'stock_dia': stock})
                guardar_datos()
                self.banner.show('¡Producto agregado!', 'success')
                self._limpiar()
        except ValueError:
            self.banner.show('Verifica los campos numéricos.', 'error')


class CajaScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_layout.add_widget(make_title('Caja del Día'))

        self.input_monto = RoundedInput(hint_text='Monto de apertura (Bs)', multiline=False,
                                         input_filter='float', font_size=sp(15),
                                         size_hint_y=None, height=dp(54))
        self.content_layout.add_widget(self.input_monto)

        self.btn_accion = RoundedButton(text='ABRIR CAJA', icon='caja', font_size=sp(16),
                                         bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK,
                                         size_hint_y=None, height=dp(56))
        self.btn_accion.bind(on_release=self.ejecutar_accion)
        self.content_layout.add_widget(self.btn_accion)

        self.card = RoundedCard(orientation='vertical', padding=dp(18), size_hint_y=None)
        self.scroll = ScrollView(size_hint=(1, 1))
        self.lbl_detalles = Label(text='', font_size=sp(13.5), color=Theme.TEXT, halign='left',
                                   valign='top', size_hint_y=None, markup=True, line_height=1.35)
        self.lbl_detalles.bind(size=self.lbl_detalles.setter('text_size'))
        self.card.add_widget(self.lbl_detalles)
        self.scroll.add_widget(self.card)
        self.content_layout.add_widget(self.scroll)

        self.banner = MessageBanner()
        self.content_layout.add_widget(self.banner)

        fila_acciones = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        btn_gasto = RoundedButton(text='Registrar Gasto', icon='gasto', font_size=sp(12.5),
                                   bg_color=Theme.DANGER, bg_color_dark=Theme.DANGER_DARK)
        btn_gasto.bind(on_release=lambda x: setattr(self.manager, 'current', 'gasto'))
        btn_reportes = RoundedButton(text='Ver Reportes', icon='resumen', font_size=sp(12.5),
                                      bg_color=Theme.ACCENT_BLUE, bg_color_dark=Theme.ACCENT_BLUE_DARK)
        btn_reportes.bind(on_release=lambda x: setattr(self.manager, 'current', 'reportes'))
        fila_acciones.add_widget(btn_gasto)
        fila_acciones.add_widget(btn_reportes)
        self.content_layout.add_widget(fila_acciones)

    def on_enter(self):
        self.banner.hide()
        self.input_monto.text = ''
        if not GlobalData.caja_abierta:
            self.input_monto.hint_text = 'Monto de apertura (Bs)'
            self.btn_accion.label.text = 'ABRIR CAJA'
            self.btn_accion.bg_color = Theme.PRIMARY
            self.btn_accion.bg_color_dark = Theme.PRIMARY_DARK
            self.btn_accion._color.rgba = Theme.PRIMARY
            self.lbl_detalles.text = (f"[color={Theme.TEXT_MUTED_HEX}]Abre la caja para empezar a "
                                       f"registrar ventas y gastos del día.[/color]")
            self.lbl_detalles.texture_update()
            self.card.height = max(dp(80), self.lbl_detalles.texture_size[1] + dp(36))
        else:
            self.input_monto.hint_text = 'Conteo exacto para Cierre (Bs)'
            self.btn_accion.label.text = 'CERRAR CAJA'
            self.btn_accion.bg_color = Theme.DANGER
            self.btn_accion.bg_color_dark = Theme.DANGER_DARK
            self.btn_accion._color.rgba = Theme.DANGER
            self._mostrar_arqueo()

    def _mostrar_arqueo(self):
        a = calcular_arqueo_caja()
        texto = (
            f"[b]Caja abierta desde:[/b] {GlobalData.hora_apertura}\n"
            f"[b]Monto de apertura:[/b] {GlobalData.monto_apertura:.2f} Bs\n\n"
            f"[b][color={Theme.TEXT_MUTED_HEX}]VENTAS[/color][/b]\n"
            f"Efectivo:  {a['ventas_efectivo']:.2f} Bs\n"
            f"QR:  {a['ventas_qr']:.2f} Bs\n"
            f"[b]Total ventas:  {a['ventas_totales']:.2f} Bs[/b]\n\n"
            f"[b][color={Theme.TEXT_MUTED_HEX}]GASTOS[/color][/b]\n"
            f"Gastos en efectivo:  [color={Theme.DANGER_HEX}]{a['gastos_efectivo']:.2f} Bs[/color]\n\n"
            f"[b][color={Theme.TEXT_MUTED_HEX}]EFECTIVO TEÓRICO EN CAJA[/color][/b]\n"
            f"[size={int(sp(19))}]{a['efectivo_teorico']:.2f} Bs[/size]\n\n"
            f"[b][color={Theme.TEXT_MUTED_HEX}]GANANCIA NETA DEL DÍA[/color][/b]\n"
            f"[size={int(sp(20))}][color={Theme.PRIMARY_HEX}][b]{a['ganancia_neta']:.2f} Bs[/b][/color][/size]"
        )
        self.lbl_detalles.text = texto
        self.lbl_detalles.texture_update()
        self.card.height = max(dp(320), self.lbl_detalles.texture_size[1] + dp(36))

    def ejecutar_accion(self, instance):
        try:
            monto = float(self.input_monto.text) if self.input_monto.text else 0.0
            if not GlobalData.caja_abierta:
                GlobalData.caja_abierta = True
                GlobalData.monto_apertura = monto
                ahora = datetime.now()
                GlobalData.apertura_timestamp = ahora.isoformat()
                GlobalData.hora_apertura = ahora.strftime('%d/%m/%Y %H:%M')
                guardar_datos()
                self.on_enter()
                self.banner.show('¡Caja abierta correctamente!', 'success')
            else:
                a = calcular_arqueo_caja()
                diferencia = monto - a['efectivo_teorico']
                GlobalData.caja_abierta = False
                guardar_datos()
                self.on_enter()
                self.banner.show(f'Caja cerrada. Contado: {monto:.2f} Bs (Dif: {diferencia:+.2f} Bs)', 'success')
        except ValueError:
            self.banner.show('Ingresa un valor numérico válido.', 'error')


class GastoScreen(BaseScreen):
    CATEGORIAS_SUGERIDAS = ['Carne', 'Verduras', 'Carbón', 'Personal', 'Otros']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_layout.add_widget(make_title('Registrar Gasto'))

        self.content_layout.add_widget(
            Label(text='Categoría', font_size=sp(12.5), color=Theme.TEXT_MUTED,
                  size_hint_y=None, height=dp(18), halign='left', valign='middle')
        )
        fila_cat = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(5))
        self.categoria_actual = 'Carne'
        self.botones_cat = {}
        for cat in self.CATEGORIAS_SUGERIDAS:
            btn = RoundedButton(text=cat, font_size=sp(10), radius=dp(8))
            btn.bind(on_release=lambda x, c=cat: self._elegir_categoria(c))
            self.botones_cat[cat] = btn
            fila_cat.add_widget(btn)
        self.content_layout.add_widget(fila_cat)

        self.input_descripcion = RoundedInput(hint_text='Descripción (opcional)', multiline=False,
                                               size_hint_y=None, height=dp(52), font_size=sp(14))
        self.input_monto = RoundedInput(hint_text='Monto (Bs)', multiline=False, input_filter='float',
                                         size_hint_y=None, height=dp(52), font_size=sp(14))
        self.content_layout.add_widget(self.input_descripcion)
        self.content_layout.add_widget(self.input_monto)

        self.banner = MessageBanner()
        self.content_layout.add_widget(self.banner)

        btn_reg = RoundedButton(text='Registrar Gasto', icon='gasto', font_size=sp(15),
                                 bg_color=Theme.DANGER, bg_color_dark=Theme.DANGER_DARK,
                                 size_hint_y=None, height=dp(52))
        btn_reg.bind(on_release=self.registrar)
        self.content_layout.add_widget(btn_reg)

        btn_volver = RoundedButton(text='Volver a Caja', icon='back', font_size=sp(13),
                                    bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK,
                                    size_hint_y=None, height=dp(46))
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'caja'))
        self.content_layout.add_widget(btn_volver)

        self.content_layout.add_widget(Widget())
        self._pintar_categoria()

    def _elegir_categoria(self, cat):
        self.categoria_actual = cat
        self._pintar_categoria()

    def _pintar_categoria(self):
        for c, btn in self.botones_cat.items():
            activo = c == self.categoria_actual
            btn.bg_color = Theme.DANGER if activo else Theme.NEUTRAL
            btn.bg_color_dark = Theme.DANGER_DARK if activo else Theme.NEUTRAL_DARK
            btn._color.rgba = btn.bg_color

    def registrar(self, instance):
        try:
            monto = float(self.input_monto.text) if self.input_monto.text else 0.0
            descripcion = self.input_descripcion.text.strip()
            if monto <= 0:
                self.banner.show('El monto debe ser mayor a 0.', 'error')
                return

            GlobalData.contador_gastos += 1
            ahora = datetime.now()
            GlobalData.historial_gastos.append({
                'id': GlobalData.contador_gastos, 'fecha': ahora.strftime('%d/%m/%Y'),
                'hora': ahora.strftime('%H:%M:%S'), 'timestamp': ahora.isoformat(),
                'categoria': self.categoria_actual, 'monto': monto, 'descripcion': descripcion,
            })
            guardar_datos()
            self.banner.show('¡Gasto registrado!', 'success')
            self.input_descripcion.text = ''
            self.input_monto.text = ''
        except ValueError:
            self.banner.show('Verifica el monto ingresado.', 'error')


class ReportesScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_layout.add_widget(make_title('Reportes'))

        fila_tabs = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        self.btn_ranking = RoundedButton(text='Ranking', icon='estrella', font_size=sp(13),
                                          bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK)
        self.btn_historial = RoundedButton(text='Historial', icon='ticket', font_size=sp(13),
                                            bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK)
        self.btn_ranking.bind(on_release=lambda x: self._cambiar_vista('ranking'))
        self.btn_historial.bind(on_release=lambda x: self._cambiar_vista('historial'))
        fila_tabs.add_widget(self.btn_ranking)
        fila_tabs.add_widget(self.btn_historial)
        self.content_layout.add_widget(fila_tabs)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.lista = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.lista.bind(minimum_height=self.lista.setter('height'))
        self.scroll.add_widget(self.lista)
        self.content_layout.add_widget(self.scroll)

        self.vista_actual = 'ranking'

    def _cambiar_vista(self, vista):
        self.vista_actual = vista
        for btn, v in [(self.btn_ranking, 'ranking'), (self.btn_historial, 'historial')]:
            activo = v == vista
            btn.bg_color = Theme.PRIMARY if activo else Theme.NEUTRAL
            btn.bg_color_dark = Theme.PRIMARY_DARK if activo else Theme.NEUTRAL_DARK
            btn._color.rgba = btn.bg_color
        self.on_enter()

    def on_enter(self):
        if self.vista_actual == 'ranking':
            self._mostrar_ranking()
        else:
            self._mostrar_historial()

    def _mostrar_ranking(self):
        self.lista.clear_widgets()
        ranking = ranking_platos()
        if not ranking:
            self.lista.add_widget(Label(text='Todavía no hay ventas registradas.', font_size=sp(13),
                                         color=Theme.TEXT_MUTED, size_hint_y=None, height=dp(40)))
            return
        for i, (nombre, cantidad) in enumerate(ranking, start=1):
            card = RoundedCard(orientation='horizontal', padding=(dp(14), dp(10)), spacing=dp(10),
                                size_hint_y=None, height=dp(50))
            pos_lbl = Label(text=f'#{i}', font_size=sp(15), bold=True, color=Theme.PRIMARY,
                             size_hint_x=None, width=dp(36))
            nombre_lbl = Label(text=nombre, font_size=sp(13.5), color=Theme.TEXT, halign='left',
                                valign='middle', shorten=True, shorten_from='right')
            nombre_lbl.bind(size=nombre_lbl.setter('text_size'))
            cant_lbl = Label(text=f'{cantidad} vendidos', font_size=sp(12), color=Theme.TEXT_MUTED,
                              size_hint_x=None, width=dp(100), halign='right', valign='middle')
            cant_lbl.bind(size=cant_lbl.setter('text_size'))
            card.add_widget(pos_lbl)
            card.add_widget(nombre_lbl)
            card.add_widget(cant_lbl)
            self.lista.add_widget(card)

    def _mostrar_historial(self):
        self.lista.clear_widgets()
        eventos = [('venta', v) for v in GlobalData.historial_ventas]
        eventos += [('gasto', g) for g in GlobalData.historial_gastos]
        eventos.sort(key=lambda e: e[1].get('timestamp', ''), reverse=True)

        if not eventos:
            self.lista.add_widget(Label(text='Todavía no hay movimientos registrados.', font_size=sp(13),
                                         color=Theme.TEXT_MUTED, size_hint_y=None, height=dp(40)))
            return

        for tipo, ev in eventos[:60]:
            card = RoundedCard(orientation='horizontal', padding=(dp(12), dp(8)), spacing=dp(8),
                                size_hint_y=None, height=dp(56))
            info = BoxLayout(orientation='vertical', spacing=dp(2))
            if tipo == 'venta':
                titulo = f"Venta #{ev['ticket']:04d}  ·  {ev['mesa']}"
                sub = f"{ev['fecha']} {ev['hora']}  ·  {ev['metodo']}"
                monto_txt, color_monto = f"+{ev['total']:.2f} Bs", Theme.PRIMARY
            else:
                titulo = f"Gasto: {ev['categoria']}"
                sub = f"{ev['fecha']} {ev['hora']}" + (f"  ·  {ev['descripcion']}" if ev.get('descripcion') else '')
                monto_txt, color_monto = f"-{ev['monto']:.2f} Bs", Theme.DANGER

            titulo_lbl = Label(text=titulo, font_size=sp(13), bold=True, color=Theme.TEXT, halign='left',
                                valign='middle', size_hint_y=None, height=dp(20),
                                shorten=True, shorten_from='right')
            titulo_lbl.bind(size=titulo_lbl.setter('text_size'))
            sub_lbl = Label(text=sub, font_size=sp(11), color=Theme.TEXT_MUTED, halign='left',
                             valign='middle', size_hint_y=None, height=dp(16),
                             shorten=True, shorten_from='right')
            sub_lbl.bind(size=sub_lbl.setter('text_size'))
            info.add_widget(titulo_lbl)
            info.add_widget(sub_lbl)
            card.add_widget(info)

            card.add_widget(Label(text=monto_txt, font_size=sp(13), bold=True, color=color_monto,
                                   size_hint_x=None, width=dp(78)))

            if tipo == 'gasto':
                btn_editar = RoundedButton(icon='editar', bg_color=Theme.ACCENT_BLUE,
                                            bg_color_dark=Theme.ACCENT_BLUE_DARK, icon_size=dp(13),
                                            size_hint=(None, None), size=(dp(28), dp(28)), radius=dp(8))
                btn_editar.bind(on_release=lambda x, g=ev: self.editar_gasto(g))
                card.add_widget(btn_editar)

            btn_del = RoundedButton(icon='eliminar', bg_color=Theme.DANGER, bg_color_dark=Theme.DANGER_DARK,
                                     icon_size=dp(13), size_hint=(None, None), size=(dp(28), dp(28)), radius=dp(8))
            btn_del.bind(on_release=lambda x, t=tipo, e=ev: self.confirmar_cancelar(t, e))
            card.add_widget(btn_del)

            self.lista.add_widget(card)

    def editar_gasto(self, gasto):
        EditarGastoModal(gasto, on_guardado=self.on_enter).open()

    def confirmar_cancelar(self, tipo, ev):
        if tipo == 'venta':
            mensaje = f"¿Cancelar la venta #{ev['ticket']:04d}?\nSe devolverá el stock de los productos."
        else:
            mensaje = f"¿Eliminar este gasto de {ev['monto']:.2f} Bs?"
        ConfirmModal(
            titulo='Cancelar Registro', mensaje=mensaje,
            texto_confirmar='Eliminar', icono_confirmar='eliminar',
            color_confirmar=Theme.DANGER, color_confirmar_dark=Theme.DANGER_DARK,
            on_confirmar=lambda: self._cancelar(tipo, ev),
        ).open()

    def _cancelar(self, tipo, ev):
        if tipo == 'venta':
            if ev in GlobalData.historial_ventas:
                GlobalData.historial_ventas.remove(ev)
            for it in ev.get('items', []):
                producto = next((p for p in GlobalData.productos if p['nombre'] == it['nombre']), None)
                if producto:
                    producto['stock_dia'] += it['cantidad']
        else:
            if ev in GlobalData.historial_gastos:
                GlobalData.historial_gastos.remove(ev)
        guardar_datos()
        self.on_enter()


class MainApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical')
        sm = ScreenManager(transition=FadeTransition(duration=0.15))

        sm.add_widget(MesasScreen(name='mesas'))
        sm.add_widget(ComandaScreen(name='comanda'))
        sm.add_widget(ProductosScreen(name='productos'))
        sm.add_widget(ProductoFormScreen(name='producto_form'))
        sm.add_widget(CajaScreen(name='caja'))
        sm.add_widget(GastoScreen(name='gasto'))
        sm.add_widget(ReportesScreen(name='reportes'))

        nav_bar = BottomNavBar(sm)

        root.add_widget(sm)
        root.add_widget(nav_bar)
        return root


if __name__ == '__main__':
    MainApp().run()
