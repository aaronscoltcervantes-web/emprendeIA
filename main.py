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
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse, Line
from kivy.metrics import dp, sp
from kivy.animation import Animation

try:
    import qrcode
    QRCODE_DISPONIBLE = True
except ImportError:
    QRCODE_DISPONIBLE = False

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
        "gastos_caja": [],
        "contador_ventas": 0,
        "historial_gastos": [],
        "historial_compras": [],
        "fardos": [],
        "contador_fardos": 0
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
        "gastos_caja": GlobalData.gastos_caja,
        "contador_ventas": GlobalData.contador_ventas,
        "historial_gastos": GlobalData.historial_gastos,
        "historial_compras": GlobalData.historial_compras,
        "fardos": GlobalData.fardos,
        "contador_fardos": GlobalData.contador_fardos
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
    contador_ventas = datos.get("contador_ventas", 0)
    historial_gastos = datos.get("historial_gastos", [])
    historial_compras = datos.get("historial_compras", [])
    fardos = datos.get("fardos", [])
    contador_fardos = datos.get("contador_fardos", 0)
    carrito = []


MESES_NOMBRE = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def _parse_fecha(fecha_str):
    """Convierte 'dd/mm/YYYY' a (dia, mes, anio). Devuelve None si no se puede leer."""
    try:
        dia, mes, anio = fecha_str.split('/')
        return int(dia), int(mes), int(anio)
    except Exception:
        return None


def _en_mes(fecha_str, anio, mes):
    p = _parse_fecha(fecha_str)
    return p is not None and p[2] == anio and p[1] == mes


def meses_disponibles():
    """(anio, mes) con al menos un registro, de más reciente a más antiguo.
    Siempre incluye el mes actual aunque todavía no tenga movimientos."""
    claves = set()
    ahora = datetime.now()
    claves.add((ahora.year, ahora.month))
    for lista in (GlobalData.historial_ventas, GlobalData.historial_gastos, GlobalData.historial_compras):
        for reg in lista:
            p = _parse_fecha(reg.get('fecha', ''))
            if p:
                _, mes, anio = p
                claves.add((anio, mes))
    return sorted(claves, key=lambda t: (t[0], t[1]), reverse=True)


def calcular_resumen_mensual(anio, mes):
    ventas_mes = [v for v in GlobalData.historial_ventas if _en_mes(v.get('fecha', ''), anio, mes)]
    gastos_mes = [g for g in GlobalData.historial_gastos if _en_mes(g.get('fecha', ''), anio, mes)]
    compras_mes = [c for c in GlobalData.historial_compras if _en_mes(c.get('fecha', ''), anio, mes)]

    total_ventas_dinero = sum(v['total'] for v in ventas_mes)
    ventas_efectivo = sum(v['total'] for v in ventas_mes if v.get('metodo') == 'EFECTIVO')
    ventas_qr = sum(v['total'] for v in ventas_mes if v.get('metodo') == 'QR')
    ganancia_mes = sum(v.get('ganancia', 0.0) for v in ventas_mes)
    total_gastos = sum(g['monto'] for g in gastos_mes)
    total_compras = sum(c.get('costo_total', 0.0) for c in compras_mes)

    cantidad_productos_vendidos = 0
    conteo_por_producto = {}
    conteo_por_dia = {}
    for v in ventas_mes:
        for it in v.get('productos', []):
            cantidad_productos_vendidos += it['cantidad']
            conteo_por_producto[it['nombre']] = conteo_por_producto.get(it['nombre'], 0) + it['cantidad']
        conteo_por_dia[v['fecha']] = conteo_por_dia.get(v['fecha'], 0.0) + v['total']

    producto_mas_vendido = max(conteo_por_producto.items(), key=lambda kv: kv[1])[0] if conteo_por_producto else '-'
    dia_mayor_venta = max(conteo_por_dia.items(), key=lambda kv: kv[1]) if conteo_por_dia else ('-', 0.0)
    productos_restantes = sum(p['stock'] for p in GlobalData.inventario)

    fardos_mes = [f for f in GlobalData.fardos if _en_mes(f.get('fecha', ''), anio, mes)]

    return {
        "anio": anio, "mes": mes,
        "cantidad_ventas": len(ventas_mes),
        "total_ventas_dinero": total_ventas_dinero,
        "ventas_efectivo": ventas_efectivo,
        "ventas_qr": ventas_qr,
        "total_compras": total_compras,
        "total_gastos": total_gastos,
        "ganancia_mes": ganancia_mes,
        "cantidad_productos_vendidos": cantidad_productos_vendidos,
        "productos_restantes": productos_restantes,
        "producto_mas_vendido": producto_mas_vendido,
        "dia_mayor_venta": dia_mayor_venta[0],
        "dia_mayor_venta_monto": dia_mayor_venta[1],
        "fardos_mes": fardos_mes,
    }


def calcular_recuperado_fardo(fardo_id):
    """Suma cuánto se ha vendido (a precio de venta) de productos que vinieron
    de un fardo específico, revisando todo el historial de ventas."""
    recuperado = 0.0
    unidades_vendidas = 0
    for v in GlobalData.historial_ventas:
        for it in v.get('productos', []):
            if it.get('origen_fardo') == fardo_id:
                recuperado += it['precio'] * it['cantidad']
                unidades_vendidas += it['cantidad']
    return recuperado, unidades_vendidas


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

    def _draw_editar(self, x, y, w, h):
        Line(points=[x + w * 0.22, y + h * 0.22, x + w * 0.72, y + h * 0.72],
             width=dp(3.0), cap='round')
        Line(points=[x + w * 0.68, y + h * 0.68, x + w * 0.8, y + h * 0.8],
             width=dp(3.0), cap='round')
        Line(points=[x + w * 0.16, y + h * 0.16, x + w * 0.26, y + h * 0.26],
             width=dp(3.0), cap='round')

    def _draw_eliminar(self, x, y, w, h):
        Line(rounded_rectangle=(x + w * 0.24, y + h * 0.14, w * 0.52, h * 0.56, dp(2)),
             width=dp(1.7))
        Line(points=[x + w * 0.16, y + h * 0.7, x + w * 0.84, y + h * 0.7], width=dp(1.7))
        Line(points=[x + w * 0.4, y + h * 0.76, x + w * 0.6, y + h * 0.76], width=dp(2.0))
        Line(points=[x + w * 0.38, y + h * 0.26, x + w * 0.38, y + h * 0.56], width=dp(1.4))
        Line(points=[x + w * 0.5, y + h * 0.26, x + w * 0.5, y + h * 0.56], width=dp(1.4))
        Line(points=[x + w * 0.62, y + h * 0.26, x + w * 0.62, y + h * 0.56], width=dp(1.4))

    def _draw_ticket(self, x, y, w, h):
        Line(rounded_rectangle=(x + w * 0.22, y + h * 0.12, w * 0.56, h * 0.76, dp(3)),
             width=dp(1.7))
        for i in range(3):
            yy = y + h * 0.3 + i * h * 0.16
            Line(points=[x + w * 0.34, yy, x + w * 0.66, yy], width=dp(1.4))

    def _draw_cerrar(self, x, y, w, h):
        Line(points=[x + w * 0.26, y + h * 0.26, x + w * 0.74, y + h * 0.74],
             width=dp(2.2), cap='round')
        Line(points=[x + w * 0.74, y + h * 0.26, x + w * 0.26, y + h * 0.74],
             width=dp(2.2), cap='round')

    def _draw_fardo(self, x, y, w, h):
        Line(rounded_rectangle=(x + w * 0.16, y + h * 0.2, w * 0.68, h * 0.56, dp(5)),
             width=dp(1.8))
        Line(points=[x + w * 0.16, y + h * 0.48, x + w * 0.84, y + h * 0.48], width=dp(1.6))
        Line(points=[x + w * 0.5, y + h * 0.76, x + w * 0.36, y + h * 0.9], width=dp(1.6), cap='round')
        Line(points=[x + w * 0.5, y + h * 0.76, x + w * 0.64, y + h * 0.9], width=dp(1.6), cap='round')

    def _draw_calendario(self, x, y, w, h):
        Line(rounded_rectangle=(x + w * 0.16, y + h * 0.12, w * 0.68, h * 0.68, dp(3)),
             width=dp(1.7))
        Line(points=[x + w * 0.16, y + h * 0.58, x + w * 0.84, y + h * 0.58], width=dp(1.5))
        Line(points=[x + w * 0.32, y + h * 0.8, x + w * 0.32, y + h * 0.92], width=dp(1.8), cap='round')
        Line(points=[x + w * 0.68, y + h * 0.8, x + w * 0.68, y + h * 0.92], width=dp(1.8), cap='round')

    def _draw_siguiente(self, x, y, w, h):
        Line(points=[x + w * 0.38, y + h * 0.2, x + w * 0.68, y + h * 0.5, x + w * 0.38, y + h * 0.8],
             width=dp(2.0), joint='round', cap='round')


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
        self.padding = [dp(16), dp(14), dp(16), dp(14)]


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


# ---------------------------------------------------------------------------
# CÓDIGO QR REAL (usa la librería 'qrcode' si está disponible; si no,
# muestra un aviso en vez de dibujar un cuadrado falso)
# ---------------------------------------------------------------------------
class QRWidget(Widget):
    def __init__(self, data='', **kwargs):
        super().__init__(**kwargs)
        self._matrix = None
        if QRCODE_DISPONIBLE:
            try:
                qr = qrcode.QRCode(border=1, error_correction=qrcode.constants.ERROR_CORRECT_M)
                qr.add_data(data)
                qr.make(fit=True)
                self._matrix = qr.get_matrix()
            except Exception as e:
                print(f"[AVISO] No se pudo generar el QR: {e}")
                self._matrix = None
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size
        if w <= 0 or h <= 0:
            return
        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(pos=(x, y), size=(w, h))
            if self._matrix:
                n = len(self._matrix)
                cell = min(w, h) / n
                off_x = x + (w - cell * n) / 2
                off_y = y + (h - cell * n) / 2
                Color(0, 0, 0, 1)
                for row_i, row in enumerate(self._matrix):
                    for col_i, val in enumerate(row):
                        if val:
                            Rectangle(pos=(off_x + col_i * cell, off_y + (n - row_i - 1) * cell),
                                      size=(cell, cell))


# ---------------------------------------------------------------------------
# VENTANAS MODALES (Popup de Kivy, estilizadas con el tema oscuro de la app)
# ---------------------------------------------------------------------------
def _popup_kwargs(title, extra_height=0, size_hint=(0.87, None)):
    return dict(
        title=title, size_hint=size_hint,
        title_color=Theme.TEXT, title_size=sp(16),
        background_color=(0.08, 0.09, 0.11, 0.98),
        separator_color=Theme.SURFACE_BORDER,
    )


class ConfirmModal(Popup):
    """Modal genérico de confirmación (Cancelar / Acción) con mensaje libre."""

    def __init__(self, titulo, mensaje, on_confirmar, texto_confirmar='Confirmar',
                 texto_cancelar='Cancelar', color_confirmar=None, color_confirmar_dark=None,
                 icono_confirmar=None, **kwargs):
        color_confirmar = color_confirmar or Theme.PRIMARY
        color_confirmar_dark = color_confirmar_dark or Theme.PRIMARY_DARK

        content = BoxLayout(orientation='vertical', spacing=dp(18), padding=dp(20))
        lbl = Label(text=mensaje, font_size=sp(14.5), color=Theme.TEXT,
                    halign='center', valign='middle')
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

        super().__init__(content=content, auto_dismiss=False, height=dp(210),
                          **_popup_kwargs(titulo), **kwargs)

        btn_cancelar.bind(on_release=lambda x: self.dismiss())

        def _confirmar(x):
            self.dismiss()
            on_confirmar()

        btn_confirmar.bind(on_release=_confirmar)


class CantidadModal(Popup):
    """Selector de cantidad antes de agregar un producto al carrito."""

    def __init__(self, producto, on_agregar, **kwargs):
        self.producto = producto
        self.cantidad = 1
        self.max_stock = producto['stock']

        content = BoxLayout(orientation='vertical', spacing=dp(14), padding=dp(20))

        lbl_prod = Label(text=producto['nombre'], font_size=sp(16), bold=True,
                          color=Theme.TEXT, size_hint_y=None, height=dp(26))
        content.add_widget(lbl_prod)

        self.lbl_stock = Label(text=f"Stock disponible: {self.max_stock}", font_size=sp(12.5),
                                color=Theme.TEXT_MUTED, size_hint_y=None, height=dp(18))
        content.add_widget(self.lbl_stock)

        stepper = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(16))
        btn_menos = RoundedButton(text='-', font_size=sp(20), bg_color=Theme.NEUTRAL,
                                   bg_color_dark=Theme.NEUTRAL_DARK,
                                   size_hint=(None, None), size=(dp(54), dp(54)))
        self.lbl_cant = Label(text='1', font_size=sp(22), bold=True, color=Theme.TEXT)
        btn_mas = RoundedButton(text='+', font_size=sp(20), bg_color=Theme.NEUTRAL,
                                 bg_color_dark=Theme.NEUTRAL_DARK,
                                 size_hint=(None, None), size=(dp(54), dp(54)))
        btn_menos.bind(on_release=lambda x: self._cambiar(-1))
        btn_mas.bind(on_release=lambda x: self._cambiar(1))
        stepper.add_widget(Widget())
        stepper.add_widget(btn_menos)
        stepper.add_widget(self.lbl_cant)
        stepper.add_widget(btn_mas)
        stepper.add_widget(Widget())
        content.add_widget(stepper)

        botones = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(12))
        btn_cancelar = RoundedButton(text='Cancelar', bg_color=Theme.NEUTRAL,
                                      bg_color_dark=Theme.NEUTRAL_DARK, font_size=sp(14))
        btn_agregar = RoundedButton(text='Agregar al carrito', icon='plus', font_size=sp(12.5),
                                     bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK)
        botones.add_widget(btn_cancelar)
        botones.add_widget(btn_agregar)
        content.add_widget(botones)

        super().__init__(content=content, auto_dismiss=True, height=dp(320),
                          **_popup_kwargs('¿Cuántas unidades desea vender?'), **kwargs)

        btn_cancelar.bind(on_release=lambda x: self.dismiss())

        def _confirmar(x):
            if self.cantidad > 0:
                cantidad = self.cantidad
                self.dismiss()
                on_agregar(cantidad)

        btn_agregar.bind(on_release=_confirmar)

    def _cambiar(self, delta):
        nueva = self.cantidad + delta
        nueva = max(1, min(nueva, self.max_stock))
        self.cantidad = nueva
        self.lbl_cant.text = str(self.cantidad)


class ConfirmVentaModal(Popup):
    """Confirmación final antes de registrar una venta (efectivo o QR)."""

    def __init__(self, items, total, metodo, on_confirmar, **kwargs):
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(20))

        scroll = ScrollView(size_hint=(1, 1))
        lista = BoxLayout(orientation='vertical', spacing=dp(3), size_hint_y=None)
        lista.bind(minimum_height=lista.setter('height'))
        for it in items:
            lbl = Label(text=f"{it['nombre']}  x{it['cantidad']}", font_size=sp(13.5),
                        color=Theme.TEXT, halign='left', valign='middle',
                        size_hint_y=None, height=dp(22))
            lbl.bind(size=lbl.setter('text_size'))
            lista.add_widget(lbl)
        scroll.add_widget(lista)
        content.add_widget(scroll)

        lbl_total = Label(text=f"Total: {total:.2f} Bs", font_size=sp(18), bold=True,
                           color=Theme.PRIMARY, size_hint_y=None, height=dp(28))
        content.add_widget(lbl_total)

        lbl_metodo = Label(text=f"Método de pago: {metodo.upper()}", font_size=sp(13),
                            color=Theme.TEXT_MUTED, size_hint_y=None, height=dp(20))
        content.add_widget(lbl_metodo)

        lbl_pregunta = Label(text='¿Está seguro de realizar la venta?', font_size=sp(13.5),
                              color=Theme.TEXT, size_hint_y=None, height=dp(24))
        content.add_widget(lbl_pregunta)

        botones = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(12))
        btn_cancelar = RoundedButton(text='Cancelar', bg_color=Theme.NEUTRAL,
                                      bg_color_dark=Theme.NEUTRAL_DARK, font_size=sp(14))
        btn_confirmar = RoundedButton(text='Confirmar venta', icon='check', font_size=sp(12.5),
                                       bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK)
        botones.add_widget(btn_cancelar)
        botones.add_widget(btn_confirmar)
        content.add_widget(botones)

        super().__init__(content=content, auto_dismiss=False, size_hint=(0.9, 0.7),
                          **{k: v for k, v in _popup_kwargs('Confirmar Venta').items() if k != 'size_hint'},
                          **kwargs)

        btn_cancelar.bind(on_release=lambda x: self.dismiss())

        def _confirmar(x):
            self.dismiss()
            on_confirmar()

        btn_confirmar.bind(on_release=_confirmar)


class TicketModal(Popup):
    """Comprobante de venta, con QR real si el pago fue por QR."""

    def __init__(self, ticket_num, fecha, hora, productos, total, metodo, **kwargs):
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(18))

        scroll = ScrollView(size_hint=(1, 1))
        info = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None, padding=(0, dp(4)))
        info.bind(minimum_height=info.setter('height'))

        def linea(texto, size=13, bold=False, color=None, align='left', italic=False):
            lbl = Label(text=texto, font_size=sp(size), bold=bold, italic=italic,
                        color=color or Theme.TEXT, halign=align, valign='middle',
                        size_hint_y=None, height=dp(size + 10))
            lbl.bind(size=lbl.setter('text_size'))
            info.add_widget(lbl)

        linea(f"VENTA #{ticket_num:04d}", size=16, bold=True, color=Theme.PRIMARY, align='center')
        linea(f"Fecha: {fecha}    Hora: {hora}", size=11.5, color=Theme.TEXT_MUTED, align='center')
        info.add_widget(Widget(size_hint_y=None, height=dp(6)))

        for p in productos:
            sub = p['precio'] * p['cantidad']
            linea(p['nombre'], size=13, bold=True)
            linea(f"  {p['cantidad']} x {p['precio']:.2f} Bs"
                  f"{' ' * 6}{sub:.2f} Bs", size=12, color=Theme.TEXT_MUTED)

        info.add_widget(Widget(size_hint_y=None, height=dp(6)))
        linea(f"TOTAL: {total:.2f} Bs", size=17, bold=True, color=Theme.PRIMARY, align='center')
        linea(f"Pago: {metodo.upper()}", size=13, color=Theme.TEXT_MUTED, align='center')

        scroll.add_widget(info)
        content.add_widget(scroll)

        if metodo == 'qr':
            qr_holder = AnchorLayout(size_hint_y=None, height=dp(180))
            if QRCODE_DISPONIBLE:
                qr_data = f"NEGOCIO|VENTA#{ticket_num}|TOTAL:{total:.2f}|FECHA:{fecha}|PAGO:QR"
                qr_holder.add_widget(QRWidget(data=qr_data, size=(dp(160), dp(160)),
                                               size_hint=(None, None)))
            else:
                aviso = Label(text='Código QR no disponible.\nAgrega "qrcode" a requirements\n'
                                    'en buildozer.spec para activarlo.',
                               font_size=sp(11.5), color=Theme.TEXT_MUTED,
                               halign='center', valign='middle')
                aviso.bind(size=aviso.setter('text_size'))
                qr_holder.add_widget(aviso)
            content.add_widget(qr_holder)

        linea_gracias = Label(text='¡Gracias por su compra!', font_size=sp(13), italic=True,
                               color=Theme.TEXT_MUTED, size_hint_y=None, height=dp(24))
        content.add_widget(linea_gracias)

        botones = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        btn_guardar = RoundedButton(text='Guardar', icon='ticket', font_size=sp(13),
                                     bg_color=Theme.ACCENT_BLUE, bg_color_dark=Theme.ACCENT_BLUE_DARK)
        btn_cerrar = RoundedButton(text='Cerrar', icon='cerrar', font_size=sp(13),
                                    bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK)
        botones.add_widget(btn_guardar)
        botones.add_widget(btn_cerrar)
        content.add_widget(botones)

        super().__init__(content=content, auto_dismiss=True, size_hint=(0.9, 0.85),
                          **{k: v for k, v in _popup_kwargs('Comprobante de Venta').items() if k != 'size_hint'},
                          **kwargs)

        self._datos_txt = (ticket_num, fecha, hora, productos, total, metodo)
        btn_cerrar.bind(on_release=lambda x: self.dismiss())
        btn_guardar.bind(on_release=self._guardar_txt)

    def _guardar_txt(self, instance):
        ticket_num, fecha, hora, productos, total, metodo = self._datos_txt
        try:
            nombre_archivo = f"ticket_{ticket_num:04d}.txt"
            lineas = [f"VENTA #{ticket_num:04d}", f"Fecha: {fecha}  Hora: {hora}", "-" * 32]
            for p in productos:
                sub = p['precio'] * p['cantidad']
                lineas.append(f"{p['nombre']}  {p['cantidad']} x {p['precio']:.2f} Bs = {sub:.2f} Bs")
            lineas += ["-" * 32, f"TOTAL: {total:.2f} Bs", f"Pago: {metodo.upper()}",
                       "¡Gracias por su compra!"]
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                f.write("\n".join(lineas))
            self.title = 'Comprobante de Venta (guardado ✓)'
        except Exception as e:
            print(f"[AVISO] No se pudo guardar el ticket: {e}")
            self.title = 'Comprobante de Venta (no se pudo guardar)'


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

        self.banner = MessageBanner()
        self.content_layout.add_widget(self.banner)

        botones_pago = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10))
        btn_efectivo = RoundedButton(text='Cobrar Efectivo', icon='efectivo', font_size=sp(14),
                                      bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK)
        btn_efectivo.bind(on_release=lambda x: self.iniciar_cobro('efectivo'))

        btn_qr = RoundedButton(text='Cobrar QR', icon='qr', font_size=sp(14),
                                bg_color=Theme.ACCENT_BLUE, bg_color_dark=Theme.ACCENT_BLUE_DARK)
        btn_qr.bind(on_release=lambda x: self.iniciar_cobro('qr'))

        botones_pago.add_widget(btn_efectivo)
        botones_pago.add_widget(btn_qr)
        self.content_layout.add_widget(botones_pago)

    def on_enter(self):
        self.banner.hide()
        self.actualizar_carrito_vista()
        self.input_buscar.text = ''
        self.filtrar_productos(None, '')

    def on_leave(self):
        self._devolver_stock_carrito()

    def _devolver_stock_carrito(self):
        """Si se sale de la pantalla sin confirmar la venta, las unidades
        reservadas del carrito regresan al inventario."""
        if not GlobalData.carrito:
            return
        for item in GlobalData.carrito:
            producto = next((p for p in GlobalData.inventario if p['nombre'] == item['nombre']), None)
            if producto:
                producto['stock'] += item['cantidad']
        GlobalData.carrito = []
        guardar_datos()

    def filtrar_productos(self, instance, valor):
        self.lista_resultados.clear_widgets()
        filtro = valor.lower()
        cantidades_en_carrito = {item['nombre']: item['cantidad'] for item in GlobalData.carrito}
        for prod in GlobalData.inventario:
            if filtro in prod['nombre'].lower():
                ya = cantidades_en_carrito.get(prod['nombre'], 0)
                if prod['stock'] <= 0:
                    texto = f"{prod['nombre']}  ·  Sin stock"
                    if ya:
                        texto += f"  ·  {ya} en el carrito"
                    btn = RoundedButton(
                        text=texto, icon='alerta', font_size=sp(12),
                        bg_color=Theme.NEUTRAL_DARK, bg_color_dark=Theme.NEUTRAL_DARK,
                        text_color=Theme.TEXT_DIM, icon_size=dp(15),
                        size_hint_y=None, height=dp(44), radius=Theme.RADIUS_SM,
                    )
                else:
                    alerta = "  ¡STOCK BAJO!" if prod['stock'] <= 5 else ""
                    extra = f"  ·  {ya} en el carrito" if ya else ""
                    texto = f"{prod['nombre']}  ·  Stock {prod['stock']}  ·  {prod['precio']} Bs{alerta}{extra}"
                    btn = RoundedButton(
                        text=texto, icon='plus', font_size=sp(12.5),
                        bg_color=Theme.SURFACE, bg_color_dark=Theme.NEUTRAL_DARK,
                        text_color=Theme.TEXT, icon_size=dp(16),
                        size_hint_y=None, height=dp(46), radius=Theme.RADIUS_SM,
                    )
                    btn.bind(on_release=lambda x, p=prod: self.abrir_modal_cantidad(p))
                self.lista_resultados.add_widget(btn)

    def abrir_modal_cantidad(self, producto):
        if producto['stock'] <= 0:
            return
        modal = CantidadModal(producto, on_agregar=lambda cant: self.agregar_al_carrito(producto, cant))
        modal.open()

    def agregar_al_carrito(self, producto, cantidad):
        cantidad = max(0, min(cantidad, producto['stock']))
        if cantidad <= 0:
            return
        en_carrito = next((item for item in GlobalData.carrito if item['nombre'] == producto['nombre']), None)
        if en_carrito:
            en_carrito['cantidad'] += cantidad
        else:
            GlobalData.carrito.append({'nombre': producto['nombre'], 'precio': producto['precio'],
                                        'costo': producto['costo'], 'cantidad': cantidad,
                                        'origen_fardo': producto.get('origen_fardo')})
        producto['stock'] -= cantidad
        guardar_datos()
        self.actualizar_carrito_vista()
        self.filtrar_productos(None, self.input_buscar.text)

    def cambiar_cantidad(self, item, delta):
        producto = next((p for p in GlobalData.inventario if p['nombre'] == item['nombre']), None)
        if delta > 0:
            if not producto or producto['stock'] <= 0:
                return  # no queda stock disponible
            item['cantidad'] += 1
            producto['stock'] -= 1
        else:
            item['cantidad'] -= 1
            if producto:
                producto['stock'] += 1
            if item['cantidad'] <= 0:
                GlobalData.carrito.remove(item)
        guardar_datos()
        self.actualizar_carrito_vista()
        self.filtrar_productos(None, self.input_buscar.text)

    def actualizar_carrito_vista(self):
        self.lista_carrito.clear_widgets()
        total = 0.0
        for item in GlobalData.carrito:
            sub = item['precio'] * item['cantidad']
            total += sub
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(6))

            left = Label(text=item['nombre'], font_size=sp(13), color=Theme.TEXT,
                         halign='left', valign='middle')
            left.bind(size=left.setter('text_size'))

            btn_menos = RoundedButton(text='-', font_size=sp(18), bg_color=Theme.NEUTRAL,
                                       bg_color_dark=Theme.NEUTRAL_DARK, radius=dp(8),
                                       size_hint=(None, None), size=(dp(36), dp(36)))
            btn_menos.bind(on_release=lambda x, it=item: self.cambiar_cantidad(it, -1))

            lbl_cant = Label(text=str(item['cantidad']), font_size=sp(14), bold=True,
                              color=Theme.TEXT, size_hint=(None, None), size=(dp(28), dp(36)),
                              halign='center', valign='middle')
            lbl_cant.bind(size=lbl_cant.setter('text_size'))

            btn_mas = RoundedButton(text='+', font_size=sp(18), bg_color=Theme.NEUTRAL,
                                     bg_color_dark=Theme.NEUTRAL_DARK, radius=dp(8),
                                     size_hint=(None, None), size=(dp(36), dp(36)))
            btn_mas.bind(on_release=lambda x, it=item: self.cambiar_cantidad(it, 1))

            right = Label(text=f"{sub:.2f} Bs", font_size=sp(13), bold=True,
                          color=Theme.PRIMARY, halign='right', valign='middle',
                          size_hint_x=None, width=dp(80))
            right.bind(size=right.setter('text_size'))

            row.add_widget(left)
            row.add_widget(btn_menos)
            row.add_widget(lbl_cant)
            row.add_widget(btn_mas)
            row.add_widget(right)
            self.lista_carrito.add_widget(row)
        self.lbl_total.text = f'Total: {total:.2f} Bs'

    def iniciar_cobro(self, metodo):
        if not GlobalData.caja_abierta:
            self.banner.show('La caja debe estar abierta para vender.', 'error')
            return
        if not GlobalData.carrito:
            self.banner.show('El carrito está vacío.', 'error')
            return
        total_venta = sum(i['precio'] * i['cantidad'] for i in GlobalData.carrito)
        items = [dict(i) for i in GlobalData.carrito]
        modal = ConfirmVentaModal(
            items=items, total=total_venta, metodo=metodo,
            on_confirmar=lambda: self._procesar_venta(metodo),
        )
        modal.open()

    def _procesar_venta(self, metodo):
        if not GlobalData.carrito:
            return
        total_venta = sum(i['precio'] * i['cantidad'] for i in GlobalData.carrito)
        ganancia_venta = sum((i['precio'] - i['costo']) * i['cantidad'] for i in GlobalData.carrito)
        productos_venta = [dict(nombre=i['nombre'], cantidad=i['cantidad'], precio=i['precio'],
                                 origen_fardo=i.get('origen_fardo'))
                            for i in GlobalData.carrito]

        if metodo == 'efectivo':
            GlobalData.total_ventas_efectivo += total_venta
        else:
            GlobalData.total_ventas_qr += total_venta
        GlobalData.total_ganancias += ganancia_venta

        GlobalData.contador_ventas += 1
        ticket_num = GlobalData.contador_ventas
        ahora = datetime.now()
        fecha_txt = ahora.strftime("%d/%m/%Y")
        hora_txt = ahora.strftime("%H:%M:%S")

        GlobalData.historial_ventas.append({
            "ticket": ticket_num,
            "fecha": fecha_txt,
            "hora": hora_txt,
            "metodo": metodo.upper(),
            "total": total_venta,
            "ganancia": ganancia_venta,
            "productos": productos_venta,
        })
        GlobalData.carrito = []
        guardar_datos()
        self.actualizar_carrito_vista()
        self.filtrar_productos(None, self.input_buscar.text)

        ticket_modal = TicketModal(ticket_num=ticket_num, fecha=fecha_txt, hora=hora_txt,
                                    productos=productos_venta, total=total_venta, metodo=metodo)
        ticket_modal.open()


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
        btn_agregar.bind(on_release=self.ir_a_nuevo_producto)
        self.content_layout.add_widget(btn_agregar)

        fila_fardo = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        btn_fardo = RoundedButton(text='Comprar por Fardo', icon='fardo', font_size=sp(12.5),
                                   bg_color=Theme.ACCENT_BLUE, bg_color_dark=Theme.ACCENT_BLUE_DARK)
        btn_fardo.bind(on_release=lambda x: setattr(self.manager, 'current', 'fardo'))
        btn_ver_fardos = RoundedButton(text='Ver Fardos', icon='ticket', font_size=sp(12.5),
                                        bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK)
        btn_ver_fardos.bind(on_release=lambda x: setattr(self.manager, 'current', 'fardos_lista'))
        fila_fardo.add_widget(btn_fardo)
        fila_fardo.add_widget(btn_ver_fardos)
        self.content_layout.add_widget(fila_fardo)

    def ir_a_nuevo_producto(self, instance):
        self.manager.get_screen('ingreso').cargar_para_nuevo()
        self.manager.current = 'ingreso'

    def on_enter(self):
        self.lista_layout.clear_widgets()
        for prod in GlobalData.inventario:
            bajo = prod['stock'] <= 5
            badge_color = Theme.DANGER if bajo else Theme.PRIMARY

            row = RoundedCard(orientation='vertical', padding=(dp(14), dp(10)),
                               spacing=dp(6), size_hint_y=None, height=dp(90))

            fila_sup = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(34))
            nombre_lbl = Label(text=prod['nombre'], font_size=sp(14.5), bold=True,
                                color=Theme.TEXT, halign='left', valign='middle',
                                shorten=True, shorten_from='right')
            nombre_lbl.bind(size=nombre_lbl.setter('text_size'))
            btn_editar = RoundedButton(icon='editar', bg_color=Theme.ACCENT_BLUE,
                                        bg_color_dark=Theme.ACCENT_BLUE_DARK, icon_size=dp(16),
                                        size_hint=(None, None), size=(dp(34), dp(34)), radius=dp(9))
            btn_editar.bind(on_release=lambda x, p=prod: self.editar_producto(p))
            btn_eliminar = RoundedButton(icon='eliminar', bg_color=Theme.DANGER,
                                          bg_color_dark=Theme.DANGER_DARK, icon_size=dp(16),
                                          size_hint=(None, None), size=(dp(34), dp(34)), radius=dp(9))
            btn_eliminar.bind(on_release=lambda x, p=prod: self.confirmar_eliminar(p))
            fila_sup.add_widget(nombre_lbl)
            fila_sup.add_widget(btn_editar)
            fila_sup.add_widget(btn_eliminar)
            row.add_widget(fila_sup)

            fila_inf = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
            detalle_extra = " · ".join(v for v in [prod.get('categoria', ''), prod.get('marca', ''),
                                                     prod.get('talla', '')] if v)
            texto_precio = f"Compra {prod['costo']:.2f} Bs  ·  Venta {prod['precio']:.2f} Bs"
            if detalle_extra:
                texto_precio += f"  ·  {detalle_extra}"
            precio_lbl = Label(text=texto_precio,
                                font_size=sp(11.5), color=Theme.TEXT_MUTED,
                                halign='left', valign='middle', shorten=True, shorten_from='right')
            precio_lbl.bind(size=precio_lbl.setter('text_size'))
            fila_inf.add_widget(precio_lbl)

            badge = BoxLayout(orientation='vertical', size_hint=(None, None),
                               size=(dp(64), dp(40)))
            with badge.canvas.before:
                Color(badge_color[0], badge_color[1], badge_color[2], 0.16)
                badge_rect = RoundedRectangle(size=badge.size, pos=badge.pos, radius=[dp(10)])
            badge.bind(
                pos=lambda inst, val, r=badge_rect: setattr(r, 'pos', val),
                size=lambda inst, val, r=badge_rect: setattr(r, 'size', val),
            )
            stock_lbl = Label(text=str(prod['stock']), font_size=sp(16), bold=True,
                               color=badge_color, size_hint_y=None, height=dp(22))
            cap_lbl = Label(text='bajo' if bajo else 'stock', font_size=sp(9),
                             color=badge_color, size_hint_y=None, height=dp(13))
            badge.add_widget(stock_lbl)
            badge.add_widget(cap_lbl)
            fila_inf.add_widget(badge)
            row.add_widget(fila_inf)

            self.lista_layout.add_widget(row)

    def editar_producto(self, producto):
        self.manager.get_screen('ingreso').cargar_para_editar(producto)
        self.manager.current = 'ingreso'

    def confirmar_eliminar(self, producto):
        modal = ConfirmModal(
            titulo='Eliminar producto',
            mensaje=f"¿Está seguro de eliminar \"{producto['nombre']}\"?\nEsta acción no se puede deshacer.",
            texto_confirmar='Eliminar', icono_confirmar='eliminar',
            color_confirmar=Theme.DANGER, color_confirmar_dark=Theme.DANGER_DARK,
            on_confirmar=lambda: self.eliminar_producto(producto),
        )
        modal.open()

    def eliminar_producto(self, producto):
        if producto in GlobalData.inventario:
            GlobalData.inventario.remove(producto)
        # Si el producto estaba reservado en un carrito de venta activo, se retira también.
        GlobalData.carrito = [i for i in GlobalData.carrito if i['nombre'] != producto['nombre']]
        guardar_datos()
        self.on_enter()


class FardoScreen(BaseScreen):
    """Registrar la compra de un fardo/yute y clasificar sus prendas."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prendas_clasificadas = []

        self.content_layout.add_widget(make_title('Comprar por Fardo'))

        fila_costo = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        self.input_costo_total = RoundedInput(hint_text='Costo total del fardo (Bs)',
                                               input_filter='float', font_size=sp(13.5), multiline=False)
        self.input_cantidad_total = RoundedInput(hint_text='Cantidad total de prendas',
                                                  input_filter='int', font_size=sp(13.5), multiline=False)
        self.input_costo_total.bind(text=self._actualizar_promedio)
        self.input_cantidad_total.bind(text=self._actualizar_promedio)
        fila_costo.add_widget(self.input_costo_total)
        fila_costo.add_widget(self.input_cantidad_total)
        self.content_layout.add_widget(fila_costo)

        self.lbl_promedio = Label(text='Costo promedio por prenda: —', font_size=sp(13), bold=True,
                                   color=Theme.PRIMARY, size_hint_y=None, height=dp(22),
                                   halign='left', valign='middle')
        self.lbl_promedio.bind(size=self.lbl_promedio.setter('text_size'))
        self.content_layout.add_widget(self.lbl_promedio)

        self.lbl_progreso = Label(text='Clasificado: 0 / 0 prendas', font_size=sp(12),
                                   color=Theme.TEXT_MUTED, size_hint_y=None, height=dp(18),
                                   halign='left', valign='middle')
        self.lbl_progreso.bind(size=self.lbl_progreso.setter('text_size'))
        self.content_layout.add_widget(self.lbl_progreso)

        self.scroll_prendas = ScrollView(size_hint=(1, 0.26))
        self.lista_prendas = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.lista_prendas.bind(minimum_height=self.lista_prendas.setter('height'))
        self.scroll_prendas.add_widget(self.lista_prendas)
        self.content_layout.add_widget(self.scroll_prendas)

        self.content_layout.add_widget(
            Label(text='Clasificar prenda', font_size=sp(13), bold=True, color=Theme.TEXT_MUTED,
                  size_hint_y=None, height=dp(20), halign='left', valign='middle')
        )
        fila1 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.input_p_nombre = RoundedInput(hint_text='Nombre (ej. Polera)', font_size=sp(12.5), multiline=False)
        self.input_p_categoria = RoundedInput(hint_text='Categoría', font_size=sp(12.5), multiline=False)
        fila1.add_widget(self.input_p_nombre)
        fila1.add_widget(self.input_p_categoria)
        self.content_layout.add_widget(fila1)

        fila2 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.input_p_talla = RoundedInput(hint_text='Talla', font_size=sp(12.5), multiline=False)
        self.input_p_marca = RoundedInput(hint_text='Marca', font_size=sp(12.5), multiline=False)
        fila2.add_widget(self.input_p_talla)
        fila2.add_widget(self.input_p_marca)
        self.content_layout.add_widget(fila2)

        fila3 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.input_p_cantidad = RoundedInput(hint_text='Cantidad', input_filter='int',
                                              font_size=sp(12.5), multiline=False)
        self.input_p_costo = RoundedInput(hint_text='Costo unit. (Bs)', input_filter='float',
                                           font_size=sp(12.5), multiline=False)
        self.input_p_precio = RoundedInput(hint_text='Precio venta (Bs)', input_filter='float',
                                            font_size=sp(12.5), multiline=False)
        fila3.add_widget(self.input_p_cantidad)
        fila3.add_widget(self.input_p_costo)
        fila3.add_widget(self.input_p_precio)
        self.content_layout.add_widget(fila3)

        self.banner = MessageBanner()
        self.content_layout.add_widget(self.banner)

        btn_agregar_prenda = RoundedButton(text='Agregar prenda a la lista', icon='plus', font_size=sp(13),
                                            bg_color=Theme.ACCENT_BLUE, bg_color_dark=Theme.ACCENT_BLUE_DARK,
                                            size_hint_y=None, height=dp(48))
        btn_agregar_prenda.bind(on_release=self.agregar_prenda_clasificada)
        self.content_layout.add_widget(btn_agregar_prenda)

        fila_final = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        btn_cancelar = RoundedButton(text='Cancelar', icon='cerrar', font_size=sp(13),
                                      bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK)
        btn_cancelar.bind(on_release=lambda x: self.cancelar_fardo())
        btn_finalizar = RoundedButton(text='Finalizar Fardo', icon='check', font_size=sp(12.5),
                                       bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK)
        btn_finalizar.bind(on_release=self.finalizar_fardo)
        fila_final.add_widget(btn_cancelar)
        fila_final.add_widget(btn_finalizar)
        self.content_layout.add_widget(fila_final)

    def on_enter(self):
        self._reiniciar_formulario()

    def _reiniciar_formulario(self):
        self.prendas_clasificadas = []
        self.input_costo_total.text = ''
        self.input_cantidad_total.text = ''
        self._limpiar_mini_form()
        self._actualizar_promedio(None, '')
        self._actualizar_lista_prendas()
        self.banner.hide()

    def _limpiar_mini_form(self):
        self.input_p_nombre.text = ''
        self.input_p_categoria.text = ''
        self.input_p_talla.text = ''
        self.input_p_marca.text = ''
        self.input_p_cantidad.text = ''
        self.input_p_costo.text = ''
        self.input_p_precio.text = ''

    def _promedio_actual(self):
        try:
            costo_total = float(self.input_costo_total.text) if self.input_costo_total.text else 0.0
            cantidad_total = int(self.input_cantidad_total.text) if self.input_cantidad_total.text else 0
            if cantidad_total > 0:
                return costo_total / cantidad_total
        except ValueError:
            pass
        return 0.0

    def _actualizar_promedio(self, instance, valor):
        promedio = self._promedio_actual()
        if promedio > 0:
            self.lbl_promedio.text = f'Costo promedio por prenda: {promedio:.2f} Bs'
        else:
            self.lbl_promedio.text = 'Costo promedio por prenda: —'
        self._actualizar_lista_prendas()

    def agregar_prenda_clasificada(self, instance):
        try:
            nombre = self.input_p_nombre.text.strip()
            cantidad = int(self.input_p_cantidad.text) if self.input_p_cantidad.text else 0
            promedio = self._promedio_actual()
            costo = float(self.input_p_costo.text) if self.input_p_costo.text else promedio
            precio = float(self.input_p_precio.text) if self.input_p_precio.text else 0.0
            categoria = self.input_p_categoria.text.strip()
            marca = self.input_p_marca.text.strip()
            talla = self.input_p_talla.text.strip()

            if not nombre:
                self.banner.show('Ingresa el nombre de la prenda.', 'error')
                return
            if cantidad <= 0:
                self.banner.show('La cantidad debe ser mayor a 0.', 'error')
                return
            if costo < 0 or precio < 0:
                self.banner.show('Los valores no pueden ser negativos.', 'error')
                return

            cantidad_total_fardo = int(self.input_cantidad_total.text) if self.input_cantidad_total.text else 0
            ya_clasificado = sum(p['cantidad'] for p in self.prendas_clasificadas)
            if cantidad_total_fardo > 0 and (ya_clasificado + cantidad) > cantidad_total_fardo:
                restante = cantidad_total_fardo - ya_clasificado
                self.banner.show(f'Solo quedan {restante} prendas por clasificar en este fardo.', 'error')
                return

            self.prendas_clasificadas.append({
                'nombre': nombre, 'categoria': categoria, 'marca': marca, 'talla': talla,
                'cantidad': cantidad, 'costo': costo, 'precio': precio,
            })
            self._limpiar_mini_form()
            self._actualizar_lista_prendas()
            self.banner.show(f'"{nombre}" agregado a la clasificación.', 'success')
        except ValueError:
            self.banner.show('Verifica los campos numéricos.', 'error')

    def quitar_prenda_clasificada(self, prenda):
        if prenda in self.prendas_clasificadas:
            self.prendas_clasificadas.remove(prenda)
        self._actualizar_lista_prendas()

    def _actualizar_lista_prendas(self):
        self.lista_prendas.clear_widgets()
        total_clasificado = 0
        for p in self.prendas_clasificadas:
            total_clasificado += p['cantidad']
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30), spacing=dp(6))
            extra = " · ".join(v for v in [p['categoria'], p['talla'], p['marca']] if v)
            detalle = f"{p['nombre']} ({extra})" if extra else p['nombre']
            lbl = Label(text=f"{detalle}  x{p['cantidad']}  ·  {p['costo']:.2f}/{p['precio']:.2f} Bs",
                        font_size=sp(11), color=Theme.TEXT, halign='left', valign='middle',
                        shorten=True, shorten_from='right')
            lbl.bind(size=lbl.setter('text_size'))
            btn_del = RoundedButton(icon='eliminar', bg_color=Theme.DANGER, bg_color_dark=Theme.DANGER_DARK,
                                     icon_size=dp(13), size_hint=(None, None), size=(dp(26), dp(26)),
                                     radius=dp(7))
            btn_del.bind(on_release=lambda x, pr=p: self.quitar_prenda_clasificada(pr))
            row.add_widget(lbl)
            row.add_widget(btn_del)
            self.lista_prendas.add_widget(row)

        try:
            cantidad_total_fardo = int(self.input_cantidad_total.text) if self.input_cantidad_total.text else 0
        except ValueError:
            cantidad_total_fardo = 0
        self.lbl_progreso.text = f'Clasificado: {total_clasificado} / {cantidad_total_fardo or "?"} prendas'

    def cancelar_fardo(self):
        self._reiniciar_formulario()
        self.manager.current = 'inventario'

    def finalizar_fardo(self, instance):
        try:
            costo_total = float(self.input_costo_total.text) if self.input_costo_total.text else 0.0
            cantidad_total = int(self.input_cantidad_total.text) if self.input_cantidad_total.text else 0
        except ValueError:
            self.banner.show('Revisa el costo y la cantidad del fardo.', 'error')
            return

        if costo_total <= 0 or cantidad_total <= 0:
            self.banner.show('Ingresa el costo total y la cantidad de prendas del fardo.', 'error')
            return
        if not self.prendas_clasificadas:
            self.banner.show('Clasifica al menos una prenda antes de finalizar.', 'error')
            return

        GlobalData.contador_fardos += 1
        fardo_id = GlobalData.contador_fardos
        fecha_txt = datetime.now().strftime("%d/%m/%Y")

        for p in self.prendas_clasificadas:
            existente = next((prod for prod in GlobalData.inventario
                               if prod['nombre'].lower() == p['nombre'].lower()
                               and prod.get('talla', '') == p['talla']
                               and prod.get('marca', '') == p['marca']), None)
            if existente:
                existente['stock'] += p['cantidad']
                existente['costo'] = p['costo']
                existente['precio'] = p['precio']
                existente['origen_fardo'] = fardo_id
            else:
                GlobalData.inventario.append({
                    'nombre': p['nombre'], 'stock': p['cantidad'], 'costo': p['costo'],
                    'precio': p['precio'], 'categoria': p['categoria'], 'marca': p['marca'],
                    'talla': p['talla'], 'origen_fardo': fardo_id,
                })

        GlobalData.fardos.append({
            'id': fardo_id, 'fecha': fecha_txt, 'costo_total': costo_total,
            'cantidad_total': cantidad_total,
            'prendas': [dict(p) for p in self.prendas_clasificadas],
        })
        GlobalData.historial_compras.append({
            'fecha': fecha_txt, 'tipo': 'fardo',
            'descripcion': f'Fardo #{fardo_id:03d}',
            'costo_total': costo_total, 'cantidad_items': cantidad_total,
        })
        guardar_datos()
        self._reiniciar_formulario()
        self.banner.show(f'¡Fardo #{fardo_id:03d} registrado! Ya está en tu inventario.', 'success')
        self.manager.current = 'inventario'


class FardosListScreen(BaseScreen):
    """Lista de fardos comprados con su inversión, recuperación y beneficio."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_layout.add_widget(make_title('Mis Fardos'))

        self.scroll = ScrollView(size_hint=(1, 1))
        self.lista = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.lista.bind(minimum_height=self.lista.setter('height'))
        self.scroll.add_widget(self.lista)
        self.content_layout.add_widget(self.scroll)

        btn_volver = RoundedButton(text='Volver al Inventario', icon='back', font_size=sp(13),
                                    bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK,
                                    size_hint_y=None, height=dp(46))
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventario'))
        self.content_layout.add_widget(btn_volver)

    def on_enter(self):
        self.lista.clear_widgets()
        if not GlobalData.fardos:
            lbl = Label(text='Todavía no registraste ningún fardo.\nUsa "Comprar por Fardo" desde Inventario.',
                        font_size=sp(13), color=Theme.TEXT_MUTED, halign='center', valign='middle',
                        size_hint_y=None, height=dp(60))
            lbl.bind(size=lbl.setter('text_size'))
            self.lista.add_widget(lbl)
            return

        for f in sorted(GlobalData.fardos, key=lambda x: x['id'], reverse=True):
            recuperado, unidades_vendidas = calcular_recuperado_fardo(f['id'])
            beneficio = recuperado - f['costo_total']
            color_beneficio = Theme.PRIMARY if beneficio >= 0 else Theme.DANGER

            card = RoundedCard(orientation='vertical', padding=dp(14), spacing=dp(4),
                                size_hint_y=None, height=dp(122))
            titulo = Label(text=f"Fardo #{f['id']:03d}  ·  {f['fecha']}", font_size=sp(14), bold=True,
                            color=Theme.TEXT, size_hint_y=None, height=dp(20),
                            halign='left', valign='middle')
            titulo.bind(size=titulo.setter('text_size'))
            l1 = Label(text=f"Invertido: {f['costo_total']:.2f} Bs  ·  {f['cantidad_total']} prendas",
                       font_size=sp(12), color=Theme.TEXT_MUTED, size_hint_y=None, height=dp(18),
                       halign='left', valign='middle')
            l1.bind(size=l1.setter('text_size'))
            l2 = Label(text=f"Recuperado: {recuperado:.2f} Bs  ·  Vendidas: {unidades_vendidas} prendas",
                       font_size=sp(12), color=Theme.TEXT_MUTED, size_hint_y=None, height=dp(18),
                       halign='left', valign='middle')
            l2.bind(size=l2.setter('text_size'))
            l3 = Label(text=f"Beneficio: {beneficio:+.2f} Bs", font_size=sp(14), bold=True,
                       color=color_beneficio, size_hint_y=None, height=dp(22),
                       halign='left', valign='middle')
            l3.bind(size=l3.setter('text_size'))
            card.add_widget(titulo)
            card.add_widget(l1)
            card.add_widget(l2)
            card.add_widget(l3)
            self.lista.add_widget(card)


class IngresoProductoScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.producto_editando = None  # None = modo "nuevo producto"; dict = editando ese producto

        self.titulo_lbl = make_title('Nuevo Producto')
        self.content_layout.add_widget(self.titulo_lbl)

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

        fila_extra = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        self.input_categoria = RoundedInput(hint_text='Categoría (opcional)', multiline=False,
                                             font_size=sp(13))
        self.input_marca = RoundedInput(hint_text='Marca (opcional)', multiline=False, font_size=sp(13))
        self.input_talla = RoundedInput(hint_text='Talla (opcional)', multiline=False, font_size=sp(13))
        fila_extra.add_widget(self.input_categoria)
        fila_extra.add_widget(self.input_marca)
        fila_extra.add_widget(self.input_talla)
        self.content_layout.add_widget(fila_extra)

        self.banner = MessageBanner()
        self.content_layout.add_widget(self.banner)

        self.btn_guardar = RoundedButton(text='Guardar', icon='check', font_size=sp(15),
                                          bg_color=Theme.PRIMARY, bg_color_dark=Theme.PRIMARY_DARK,
                                          size_hint_y=None, height=dp(52))
        self.btn_guardar.bind(on_release=self.guardar_producto)
        self.content_layout.add_widget(self.btn_guardar)

        btn_volver = RoundedButton(text='Volver al Inventario', icon='back', font_size=sp(13),
                                    bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK,
                                    size_hint_y=None, height=dp(46))
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'inventario'))
        self.content_layout.add_widget(btn_volver)

        self.content_layout.add_widget(Widget())

    def _limpiar_campos(self):
        self.input_nombre.text = ''
        self.input_stock.text = ''
        self.input_costo.text = ''
        self.input_precio.text = ''
        self.input_categoria.text = ''
        self.input_marca.text = ''
        self.input_talla.text = ''
        self.banner.hide()

    def cargar_para_nuevo(self):
        self.producto_editando = None
        self.titulo_lbl.text = 'Nuevo Producto'
        self.btn_guardar.label.text = 'Guardar'
        self._limpiar_campos()

    def cargar_para_editar(self, producto):
        self.producto_editando = producto
        self.titulo_lbl.text = 'Editar Producto'
        self.btn_guardar.label.text = 'Guardar Cambios'
        self.input_nombre.text = producto['nombre']
        self.input_stock.text = str(producto['stock'])
        self.input_costo.text = str(producto['costo'])
        self.input_precio.text = str(producto['precio'])
        self.input_categoria.text = producto.get('categoria', '')
        self.input_marca.text = producto.get('marca', '')
        self.input_talla.text = producto.get('talla', '')
        self.banner.hide()

    def guardar_producto(self, instance):
        try:
            nombre = self.input_nombre.text.strip()
            stock = int(self.input_stock.text) if self.input_stock.text else 0
            costo = float(self.input_costo.text) if self.input_costo.text else 0.0
            precio = float(self.input_precio.text) if self.input_precio.text else 0.0
            categoria = self.input_categoria.text.strip()
            marca = self.input_marca.text.strip()
            talla = self.input_talla.text.strip()

            if not nombre:
                self.banner.show('Ingresa un nombre de producto.', 'error')
                return
            if stock < 0 or costo < 0 or precio < 0:
                self.banner.show('Los valores no pueden ser negativos.', 'error')
                return

            if self.producto_editando is not None:
                # Modo edición: reemplaza los datos tal cual (no suma stock, no registra compra).
                self.producto_editando['nombre'] = nombre
                self.producto_editando['stock'] = stock
                self.producto_editando['costo'] = costo
                self.producto_editando['precio'] = precio
                self.producto_editando['categoria'] = categoria
                self.producto_editando['marca'] = marca
                self.producto_editando['talla'] = talla
                guardar_datos()
                self.banner.show('¡Producto actualizado!', 'success')
            else:
                # Modo nuevo: si el nombre ya existe, suma el stock (comportamiento previo).
                encontrado = False
                for p in GlobalData.inventario:
                    if p['nombre'].lower() == nombre.lower():
                        p['stock'] += stock
                        p['costo'] = costo
                        p['precio'] = precio
                        if categoria:
                            p['categoria'] = categoria
                        if marca:
                            p['marca'] = marca
                        if talla:
                            p['talla'] = talla
                        encontrado = True
                        break
                if not encontrado:
                    GlobalData.inventario.append({
                        "nombre": nombre, "stock": stock, "costo": costo, "precio": precio,
                        "categoria": categoria, "marca": marca, "talla": talla,
                        "origen_fardo": None,
                    })
                if stock > 0:
                    GlobalData.historial_compras.append({
                        "fecha": datetime.now().strftime("%d/%m/%Y"),
                        "tipo": "individual",
                        "descripcion": nombre,
                        "costo_total": costo * stock,
                        "cantidad_items": stock,
                    })
                guardar_datos()
                self.banner.show('¡Guardado con éxito!', 'success')
                self._limpiar_campos()
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

        btn_mensual = RoundedButton(text='Ver Resumen Mensual', icon='calendario', font_size=sp(13.5),
                                     bg_color=Theme.ACCENT_BLUE, bg_color_dark=Theme.ACCENT_BLUE_DARK,
                                     size_hint_y=None, height=dp(48))
        btn_mensual.bind(on_release=lambda x: setattr(self.manager, 'current', 'resumen_mensual'))
        self.content_layout.add_widget(btn_mensual)

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


class ResumenMensualScreen(BaseScreen):
    """Resumen histórico por mes: ventas, gastos, compras, ganancias y fardos."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_layout.add_widget(make_title('Resumen Mensual'))

        selector = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        btn_prev = RoundedButton(icon='back', bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK,
                                  size_hint=(None, None), size=(dp(46), dp(46)))
        btn_prev.bind(on_release=lambda x: self.cambiar_mes(1))  # +1 índice = mes anterior (lista es desc.)
        self.lbl_mes = Label(text='—', font_size=sp(16), bold=True, color=Theme.TEXT,
                              halign='center', valign='middle')
        self.lbl_mes.bind(size=self.lbl_mes.setter('text_size'))
        btn_next = RoundedButton(icon='siguiente', bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK,
                                  size_hint=(None, None), size=(dp(46), dp(46)))
        btn_next.bind(on_release=lambda x: self.cambiar_mes(-1))  # -1 índice = mes más reciente
        selector.add_widget(btn_prev)
        selector.add_widget(self.lbl_mes)
        selector.add_widget(btn_next)
        self.content_layout.add_widget(selector)

        self.card = RoundedCard(orientation='vertical', padding=dp(18), size_hint_y=None)
        self.scroll = ScrollView(size_hint=(1, 1))
        self.lbl_detalles = Label(text='', font_size=sp(13.5), color=Theme.TEXT, halign='left',
                                   valign='top', size_hint_y=None, markup=True, line_height=1.35)
        self.lbl_detalles.bind(size=self.lbl_detalles.setter('text_size'))
        self.card.add_widget(self.lbl_detalles)
        self.scroll.add_widget(self.card)
        self.content_layout.add_widget(self.scroll)

        btn_volver = RoundedButton(text='Volver al Resumen', icon='back', font_size=sp(13),
                                    bg_color=Theme.NEUTRAL, bg_color_dark=Theme.NEUTRAL_DARK,
                                    size_hint_y=None, height=dp(46))
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'resumen'))
        self.content_layout.add_widget(btn_volver)

        self._lista_meses = []
        self._indice_mes = 0

    def on_enter(self):
        self._lista_meses = meses_disponibles()
        if not self._lista_meses:
            ahora = datetime.now()
            self._lista_meses = [(ahora.year, ahora.month)]
        self._indice_mes = 0
        self._mostrar_mes_actual()

    def cambiar_mes(self, delta):
        nuevo = self._indice_mes + delta
        if 0 <= nuevo < len(self._lista_meses):
            self._indice_mes = nuevo
            self._mostrar_mes_actual()

    def _mostrar_mes_actual(self):
        anio, mes = self._lista_meses[self._indice_mes]
        self.lbl_mes.text = f'{MESES_NOMBRE[mes]} {anio}'
        r = calcular_resumen_mensual(anio, mes)

        dia_txt = r['dia_mayor_venta']
        if r['dia_mayor_venta_monto']:
            dia_txt += f"  ({r['dia_mayor_venta_monto']:.2f} Bs)"

        texto = (
            f"[b]Ventas del mes:[/b] {r['cantidad_ventas']}\n"
            f"[b]Productos vendidos:[/b] {r['cantidad_productos_vendidos']}\n\n"
            f"[b][color={Theme.TEXT_MUTED_HEX}]DINERO[/color][/b]\n"
            f"Total ingresado:  {r['total_ventas_dinero']:.2f} Bs\n"
            f"Ventas efectivo:  {r['ventas_efectivo']:.2f} Bs\n"
            f"Ventas QR:  {r['ventas_qr']:.2f} Bs\n"
            f"Invertido en compras:  [color={Theme.DANGER_HEX}]{r['total_compras']:.2f} Bs[/color]\n"
            f"Gastos registrados:  [color={Theme.DANGER_HEX}]{r['total_gastos']:.2f} Bs[/color]\n\n"
            f"[b][color={Theme.TEXT_MUTED_HEX}]GANANCIA ESTIMADA[/color][/b]\n"
            f"[size={int(sp(19))}][color={Theme.PRIMARY_HEX}][b]{r['ganancia_mes']:.2f} Bs[/b][/color][/size]\n\n"
            f"[b][color={Theme.TEXT_MUTED_HEX}]INVENTARIO[/color][/b]\n"
            f"Productos restantes (stock actual):  {r['productos_restantes']}\n\n"
            f"[b][color={Theme.TEXT_MUTED_HEX}]DESTACADOS DEL MES[/color][/b]\n"
            f"Producto más vendido:  {r['producto_mas_vendido']}\n"
            f"Día con más ventas:  {dia_txt}"
        )

        if r['fardos_mes']:
            texto += f"\n\n[b][color={Theme.TEXT_MUTED_HEX}]FARDOS COMPRADOS ESTE MES[/color][/b]"
            for f in r['fardos_mes']:
                recuperado, _ = calcular_recuperado_fardo(f['id'])
                texto += (f"\nFardo #{f['id']:03d}:  {f['costo_total']:.2f} Bs invertidos  ·  "
                          f"{recuperado:.2f} Bs recuperados")

        self.lbl_detalles.text = texto
        self.lbl_detalles.texture_update()
        content_h = max(dp(380), self.lbl_detalles.texture_size[1] + dp(10))
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
            GlobalData.historial_gastos.append({
                "fecha": datetime.now().strftime("%d/%m/%Y"),
                "motivo": motivo,
                "monto": monto,
            })
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
        sm.add_widget(FardoScreen(name='fardo'))
        sm.add_widget(FardosListScreen(name='fardos_lista'))
        sm.add_widget(ResumenScreen(name='resumen'))
        sm.add_widget(ResumenMensualScreen(name='resumen_mensual'))
        sm.add_widget(GastoScreen(name='gasto'))

        nav_bar = BottomNavBar(sm)

        root.add_widget(sm)
        root.add_widget(nav_bar)
        return root


if __name__ == '__main__':
    MainApp().run()
