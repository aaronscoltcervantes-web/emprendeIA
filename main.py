# -*- coding: utf-8 -*-
"""
Sistema de Negocio - App para emprendedores
UI rediseñada: iconos vectoriales propios (sin depender de fuentes externas),
botones con feedback táctil, tipografía/espaciado más grandes y tarjetas
con borde sutil. La lógica de datos (caja, ventas, inventario) es la misma
que en la versión original.

CORRECCIONES APLICADAS:
  1. RoundedInput: background_color ahora es Theme.SURFACE (oscuro) en lugar
     de transparente, evitando texto invisible sobre fondo blanco en Android.
  2. VentaScreen: carrito ahora muestra botones − y + por producto,
     con método cambiar_cantidad que ajusta stock en tiempo real.
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
# ICONOS: dibujados a mano con canvas
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
        Line(rounded_rectangle=(x + w * 0.1, y + h * 0.28, w * 0.8, h * 0.44, dp(4)), width=dp
