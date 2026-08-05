from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDRectangleFlatIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp, sp

class FarmaNoahApp(MDApp):
    def build(self):
        # Configuración del tema visual (Estilo moderno / Dark-Light Tech)
        self.theme_cls.primary_palette = "Teal"      # Color principal tecnológico
        self.theme_cls.accent_palette = "Amber"       # Color secundario
        self.theme_cls.theme_style = "Dark"          # Fondo oscuro elegante

        screen = MDScreen()

        # Barra superior con título
        top_bar = MDTopAppBar(
            title="FarmaNoah - Sistema POS & IA",
            elevation=4,
            pos_hint={"top": 1}
        )
        screen.add_widget(top_bar)

        # Navegación Inferior (Barra flotante con efectos táctiles)
        nav = MDBottomNavigation(
            panel_color=(0.1, 0.12, 0.15, 1),
            selected_color_background=(0.15, 0.2, 0.25, 1),
            text_color_active=self.theme_cls.primary_color
        )

        # ----------------------------------------------------
        # PESTAÑA 1: CAJA / RESUMEN
        # ----------------------------------------------------
        item_caja = MDBottomNavigationItem(
            name='tab_caja',
            text='Caja',
            icon='cash-register'
        )
        box_caja = MDBoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        box_caja.add_widget(MDLabel(text="", size_hint_y=None, height=dp(50))) # Espaciador topbar

        # Tarjeta resumen elegante
        card_resumen = MDCard(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(12),
            size_hint=(1, None),
            height=dp(220),
            elevation=3,
            radius=[dp(16),]
        )
        card_resumen.add_widget(MDLabel(text="Control de Caja", font_style="H6", theme_text_color="Primary"))
        card_resumen.add_widget(MDLabel(text="Monto Inicial: $30.00", font_style="Body1"))
        card_resumen.add_widget(MDLabel(text="Ventas Brutas: $0.00", font_style="Body1"))
        card_resumen.add_widget(MDLabel(text="Efectivo en Caja: $30.00", font_style="Body1", bold=True))
        card_resumen.add_widget(MDLabel(text="Ganancia Neta: $0.00", font_style="Body1", theme_text_color="Custom", text_color=(0.2, 0.8, 0.4, 1)))

        box_caja.add_widget(card_resumen)

        btn_cierre = MDRaisedButton(
            text="REALIZAR CIERRE DE TURNO",
            md_bg_color=(0.8, 0.2, 0.2, 1),
            font_size=sp(16),
            size_hint=(1, None),
            height=dp(50)
        )
        box_caja.add_widget(btn_cierre)
        box_caja.add_widget(MDLabel()) # Relleno flexible
        item_caja.add_widget(box_caja)

        # ----------------------------------------------------
        # PESTAÑA 2: VENTA / PUNTO DE VENTA
        # ----------------------------------------------------
        item_venta = MDBottomNavigationItem(
            name='tab_venta',
            text='Venta',
            icon='cart-outline'
        )
        box_venta = MDBoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        box_venta.add_widget(MDLabel(text="", size_hint_y=None, height=dp(50)))

        txt_buscar = MDTextField(
            hint_text="Buscar o escanear medicamento...",
            icon_right="magnify",
            mode="rectangle"
        )
        box_venta.add_widget(txt_buscar)

        # Lista rápida de productos / carrito
        scroll_venta = MDScrollView()
        grid_venta = MDGridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        grid_venta.bind(minimum_height=grid_venta.setter('height'))

        # Ejemplo de tarjeta de producto con efecto ripple al tocar
        for i in range(1, 4):
            card_p = MDCard(
                orientation='horizontal',
                padding=dp(10),
                size_hint_y=None,
                height=dp(70),
                ripple_behavior=True, # EFECTO AL TOCAR
                radius=[dp(10),]
            )
            card_p.add_widget(MDLabel(text=f"Medicamento Ejemplo {i}\n$15.00", font_style="Body2"))
            card_p.add_widget(MDRaisedButton(text="+ Agregar", size_hint=(None, None), height=dp(36)))
            grid_venta.add_widget(card_p)

        scroll_venta.add_widget(grid_venta)
        box_venta.add_widget(scroll_venta)
        item_venta.add_widget(box_venta)

        # ----------------------------------------------------
        # PESTAÑA 3: INVENTARIO
        # ----------------------------------------------------
        item_inv = MDBottomNavigationItem(
            name='tab_inv',
            text='Inventario',
            icon='pill'
        )
        box_inv = MDBoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        box_inv.add_widget(MDLabel(text="", size_hint_y=None, height=dp(50)))

        btn_add = MDRectangleFlatIconButton(
            icon="plus",
            text="REGISTRAR NUEVO PRODUCTO",
            size_hint=(1, None),
            height=dp(50)
        )
        box_inv.add_widget(btn_add)
        box_inv.add_widget(MDLabel(text="Stock disponible:", font_style="Subtitle1"))
        box_inv.add_widget(MDLabel()) # Relleno
        item_inv.add_widget(box_inv)

        # ----------------------------------------------------
        # PESTAÑA 4: ASISTENTE IA
        # ----------------------------------------------------
        item_ia = MDBottomNavigationItem(
            name='tab_ia',
            text='Asistente IA',
            icon='robot'
        )
        box_ia = MDBoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        box_ia.add_widget(MDLabel(text="", size_hint_y=None, height=dp(50)))

        box_ia.add_widget(MDLabel(text="Consultas Farmacéuticas & Inventario", font_style="H6"))

        txt_ia_chat = MDTextField(
            hint_text="Escribe tu consulta para la IA...",
            multiline=True,
            mode="rectangle"
        )
        box_ia.add_widget(txt_ia_chat)

        btn_consultar = MDRaisedButton(
            text="CONSULTAR A LA IA",
            icon="send",
            size_hint=(1, None),
            height=dp(50)
        )
        box_ia.add_widget(btn_consultar)
        box_ia.add_widget(MDLabel()) # Relleno
        item_ia.add_widget(box_ia)

        # Agregar pestañas al menú
        nav.add_widget(item_caja)
        nav.add_widget(item_venta)
        nav.add_widget(item_inv)
        nav.add_widget(item_ia)

        screen.add_widget(nav)
        return screen

if __name__ == '__main__':
    FarmaNoahApp().run()
