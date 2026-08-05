import sqlite3
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp, sp

class FarmaNoahApp(MDApp):
    dialog = None

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Dark"

        # Inicializar Base de Datos SQLite
        self.init_db()

        screen = MDScreen()
        top_bar = MDTopAppBar(title="FarmaNoah - Sistema POS & IA", elevation=4, pos_hint={"top": 1})
        screen.add_widget(top_bar)

        nav = MDBottomNavigation(
            panel_color=(0.1, 0.12, 0.15, 1),
            selected_color_background=(0.15, 0.2, 0.25, 1),
            text_color_active=self.theme_cls.primary_color
        )

        # ----------------------------------------------------
        # PESTAÑA 1: CAJA / APERTURA
        # ----------------------------------------------------
        item_caja = MDBottomNavigationItem(name='tab_caja', text='Caja', icon='cash-register')
        box_caja = MDBoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        box_caja.add_widget(MDLabel(text="", size_hint_y=None, height=dp(50)))

        self.txt_monto_inicial = MDTextField(
            hint_text="Monto Inicial para Apertura ($)",
            input_filter="float",
            mode="rectangle"
        )
        box_caja.add_widget(self.txt_monto_inicial)

        btn_apertura = MDRaisedButton(
            text="ABRIR CAJA",
            md_bg_color=(0.2, 0.7, 0.3, 1),
            size_hint=(1, None), height=dp(48),
            on_release=self.abrir_caja
        )
        box_caja.add_widget(btn_apertura)

        self.card_caja_info = MDCard(
            orientation='vertical', padding=dp(16), spacing=dp(8),
            size_hint=(1, None), height=dp(160), elevation=3, radius=[dp(12)]
        )
        self.lbl_estado_caja = MDLabel(text="Estado: Caja Cerrada", font_style="H6")
        self.lbl_monto_actual = MDLabel(text="Fondo Actual: $0.00", font_style="Body1")
        self.card_caja_info.add_widget(self.lbl_estado_caja)
        self.card_caja_info.add_widget(self.lbl_monto_actual)

        box_caja.add_widget(self.card_caja_info)
        box_caja.add_widget(MDLabel())
        item_caja.add_widget(box_caja)

        # ----------------------------------------------------
        # PESTAÑA 2: INVENTARIO (AGREGAR Y LISTAR)
        # ----------------------------------------------------
        item_inv = MDBottomNavigationItem(name='tab_inv', text='Inventario', icon='pill')
        box_inv = MDBoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        box_inv.add_widget(MDLabel(text="", size_hint_y=None, height=dp(50)))

        self.txt_prod_nombre = MDTextField(hint_text="Nombre del Producto", mode="rectangle")
        self.txt_prod_precio = MDTextField(hint_text="Precio ($)", input_filter="float", mode="rectangle")
        self.txt_prod_stock = MDTextField(hint_text="Cantidad Stock", input_filter="int", mode="rectangle")

        box_inv.add_widget(self.txt_prod_nombre)
        box_inv.add_widget(self.txt_prod_precio)
        box_inv.add_widget(self.txt_prod_stock)

        btn_guardar_p = MDRaisedButton(
            text="GUARDAR EN INVENTARIO",
            size_hint=(1, None), height=dp(48),
            on_release=self.guardar_producto
        )
        box_inv.add_widget(btn_guardar_p)

        scroll_inv = MDScrollView()
        self.grid_inv = MDGridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.grid_inv.bind(minimum_height=self.grid_inv.setter('height'))
        scroll_inv.add_widget(self.grid_inv)
        box_inv.add_widget(scroll_inv)

        item_inv.add_widget(box_inv)

        # ----------------------------------------------------
        # PESTAÑA 3: ASISTENTE IA
        # ----------------------------------------------------
        item_ia = MDBottomNavigationItem(name='tab_ia', text='Asistente IA', icon='robot')
        box_ia = MDBoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        box_ia.add_widget(MDLabel(text="", size_hint_y=None, height=dp(50)))

        self.txt_ia_pregunta = MDTextField(hint_text="Consulta stock o recomendaciones...", mode="rectangle")
        box_ia.add_widget(self.txt_ia_pregunta)

        btn_consultar_ia = MDRaisedButton(
            text="CONSULTAR A LA IA",
            icon="send", size_hint=(1, None), height=dp(48),
            on_release=self.consultar_ia
        )
        box_ia.add_widget(btn_consultar_ia)

        self.lbl_ia_respuesta = MDLabel(
            text="Hola, soy Noah IA. ¿En qué te ayudo hoy con tu farmacia?",
            theme_text_color="Secondary",
            font_style="Body1"
        )
        box_ia.add_widget(self.lbl_ia_respuesta)
        box_ia.add_widget(MDLabel())
        item_ia.add_widget(box_ia)

        # Agregar pestañas
        nav.add_widget(item_caja)
        nav.add_widget(item_inv)
        nav.add_widget(item_ia)

        screen.add_widget(nav)
        self.cargar_productos_ui()
        return screen

    # ----------------------------------------------------
    # LÓGICA BASE DE DATOS Y EVENTOS
    # ----------------------------------------------------
    def init_db(self):
        conn = sqlite3.connect('farmanoah.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS productos 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, precio REAL, stock INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS caja 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, monto REAL, estado TEXT)''')
        conn.commit()
        conn.close()

    def abrir_caja(self, instance):
        monto = self.txt_monto_inicial.text.strip()
        if monto:
            conn = sqlite3.connect('farmanoah.db')
            c = conn.cursor()
            c.execute("INSERT INTO caja (monto, estado) VALUES (?, 'ABIERTA')", (float(monto),))
            conn.commit()
            conn.close()
            self.lbl_estado_caja.text = "Estado: Caja ABIERTA"
            self.lbl_monto_actual.text = f"Fondo Actual: ${monto}"
            self.mostrar_alerta("Éxito", "Caja abierta correctamente.")
            self.txt_monto_inicial.text = ""
        else:
            self.mostrar_alerta("Error", "Ingresa un monto inicial válido.")

    def guardar_producto(self, instance):
        nom = self.txt_prod_nombre.text.strip()
        pre = self.txt_prod_precio.text.strip()
        stk = self.txt_prod_stock.text.strip()

        if nom and pre and stk:
            conn = sqlite3.connect('farmanoah.db')
            c = conn.cursor()
            c.execute("INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)",
                      (nom, float(pre), int(stk)))
            conn.commit()
            conn.close()
            self.mostrar_alerta("Éxito", f"Producto '{nom}' guardado en inventario.")
            self.txt_prod_nombre.text = ""
            self.txt_prod_precio.text = ""
            self.txt_prod_stock.text = ""
            self.cargar_productos_ui()
        else:
            self.mostrar_alerta("Error", "Completa todos los campos del producto.")

    def cargar_productos_ui(self):
        self.grid_inv.clear_widgets()
        conn = sqlite3.connect('farmanoah.db')
        c = conn.cursor()
        c.execute("SELECT nombre, precio, stock FROM productos")
        filas = c.fetchall()
        conn.close()

        for f in filas:
            card = MDCard(orientation='vertical', padding=dp(8), size_hint_y=None, height=dp(60), radius=[dp(8)])
            card.add_widget(MDLabel(text=f"{f[0]} - ${f[1]} (Stock: {f[2]})", font_style="Body2"))
            self.grid_inv.add_widget(card)

    def consultar_ia(self, instance):
        pregunta = self.txt_ia_pregunta.text.lower().strip()
        if not pregunta:
            self.lbl_ia_respuesta.text = "Por favor escribe una consulta."
            return

        conn = sqlite3.connect('farmanoah.db')
        c = conn.cursor()
        c.execute("SELECT nombre, stock FROM productos")
        prods = c.fetchall()
        conn.close()

        if "stock" in pregunta or "inventario" in pregunta:
            res = "Estado de inventario:\n" + "\n".join([f"• {p[0]}: {p[1]} unidades" for p in prods]) if prods else "No tienes productos en inventario."
        elif "paracetamol" in pregunta or "dolor" in pregunta:
            res = "Recomendación: El paracetamol es un analgésico y antipirético común para el dolor leve a moderado. Dosis estándar adulta: 500mg-1g cada 6-8 hrs."
        else:
            res = f"Analizando consulta sobre '{pregunta}': Te sugiero verificar el stock registrado en la pestaña de Inventario para proceder con la venta."

        self.lbl_ia_respuesta.text = f"Respuesta Noah IA:\n{res}"

    def mostrar_alerta(self, titulo, texto):
        if not self.dialog:
            self.dialog = MDDialog(title=titulo, text=texto, size_hint=(0.8, None))
        else:
            self.dialog.title = titulo
            self.dialog.text = texto
        self.dialog.open()

if __name__ == '__main__':
    FarmaNoahApp().run()
