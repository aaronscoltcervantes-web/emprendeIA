import sqlite3
import sys
from datetime import datetime
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineListItem
from kivy.metrics import dp

class MultiPosApp(MDApp):
    dialog = None
    carrito = []  # [(id, nombre, precio_venta, cantidad, subtotal, costo)]
    total_venta = 0.0
    metodo_pago = "EFECTIVO"
    producto_seleccionado = None

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Dark"
        self.init_db()

        root_layout = MDBoxLayout(orientation='vertical')

        # Barra Superior con botón para salir
        top_bar = MDTopAppBar(
            title="POS Multirrubro & IA",
            elevation=4,
            right_action_items=[["power", lambda x: self.salir_app()]]
        )
        root_layout.add_widget(top_bar)

        nav = MDBottomNavigation(
            panel_color=(0.1, 0.12, 0.15, 1),
            selected_color_background=(0.15, 0.2, 0.25, 1),
            text_color_active=self.theme_cls.primary_color
        )

        # ----------------------------------------------------
        # PESTAÑA 1: VENTA (CON AUTOCOMPLETAR Y PAGO QR)
        # ----------------------------------------------------
        item_venta = MDBottomNavigationItem(name='tab_venta', text='Venta', icon='cart')
        box_venta = MDBoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))

        # Campo de búsqueda con autocompletar
        self.txt_buscar_prod = MDTextField(
            hint_text="Buscar producto (Escribe para sugerencias)",
            mode="rectangle"
        )
        self.txt_buscar_prod.bind(text=self.filtrar_sugerencias)
        box_venta.add_widget(self.txt_buscar_prod)

        # Contenedor para sugerencias de búsqueda
        self.scroll_sugerencias = MDScrollView(size_hint_y=None, height=dp(100))
        self.list_sugerencias = MDList()
        self.scroll_sugerencias.add_widget(self.list_sugerencias)
        box_venta.add_widget(self.scroll_sugerencias)

        self.txt_cant_prod = MDTextField(hint_text="Cantidad", input_filter="int", mode="rectangle", text="1")
        box_venta.add_widget(self.txt_cant_prod)

        btn_add_car = MDRaisedButton(
            text="+ AGREGAR AL CARRITO", size_hint=(1, None), height=dp(40),
            on_release=self.agregar_al_carrito
        )
        box_venta.add_widget(btn_add_car)

        self.lbl_total = MDLabel(
            text="Total a Pagar: $0.00", font_style="H6",
            theme_text_color="Custom", text_color=(0.2, 0.8, 0.4, 1),
            size_hint_y=None, height=dp(35)
        )
        box_venta.add_widget(self.lbl_total)

        # Selección Método de Pago (Efectivo / QR)
        box_metodos = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        self.btn_metodo_efectivo = MDRaisedButton(text="Efectivo", on_release=lambda x: self.set_metodo_pago("EFECTIVO"))
        self.btn_metodo_qr = MDRaisedButton(text="Pago QR", md_bg_color=(0.4, 0.4, 0.4, 1), on_release=lambda x: self.set_metodo_pago("QR"))
        box_metodos.add_widget(self.btn_metodo_efectivo)
        box_metodos.add_widget(self.btn_metodo_qr)
        box_venta.add_widget(box_metodos)

        self.txt_pago_cliente = MDTextField(hint_text="Monto recibido del cliente ($)", input_filter="float", mode="rectangle")
        box_venta.add_widget(self.txt_pago_cliente)

        btn_procesar = MDRaisedButton(
            text="PROCESAR VENTA Y TICKET", md_bg_color=(0.1, 0.5, 0.8, 1),
            size_hint=(1, None), height=dp(45), on_release=self.procesar_venta
        )
        box_venta.add_widget(btn_procesar)
        item_venta.add_widget(box_venta)

        # ----------------------------------------------------
        # PESTAÑA 2: INVENTARIO (PRECIO COSTO Y VENTA)
        # ----------------------------------------------------
        item_inv = MDBottomNavigationItem(name='tab_inv', text='Inventario', icon='package-variant-closed')
        box_inv = MDBoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))

        self.txt_prod_nombre = MDTextField(hint_text="Nombre del Producto", mode="rectangle")
        self.txt_prod_costo = MDTextField(hint_text="Precio Compra / Costo ($)", input_filter="float", mode="rectangle")
        self.txt_prod_precio = MDTextField(hint_text="Precio Venta ($)", input_filter="float", mode="rectangle")
        self.txt_prod_stock = MDTextField(hint_text="Cantidad Stock", input_filter="int", mode="rectangle")

        box_inv.add_widget(self.txt_prod_nombre)
        box_inv.add_widget(self.txt_prod_costo)
        box_inv.add_widget(self.txt_prod_precio)
        box_inv.add_widget(self.txt_prod_stock)

        btn_guardar_p = MDRaisedButton(
            text="GUARDAR PRODUCTO", size_hint=(1, None), height=dp(42),
            on_release=self.guardar_producto
        )
        box_inv.add_widget(btn_guardar_p)

        scroll_inv = MDScrollView()
        self.grid_inv = MDGridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.grid_inv.bind(minimum_height=self.grid_inv.setter('height'))
        scroll_inv.add_widget(self.grid_inv)
        box_inv.add_widget(scroll_inv)
        item_inv.add_widget(box_inv)

        # ----------------------------------------------------
        # PESTAÑA 3: RESUMEN Y REPORTES DE VENTAS
        # ----------------------------------------------------
        item_resumen = MDBottomNavigationItem(name='tab_resumen', text='Resumen', icon='chart-bar')
        box_resumen = MDBoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))

        btn_actualizar_resumen = MDRaisedButton(
            text="REFRESCAR RESUMEN DEL DÍA", size_hint=(1, None), height=dp(40),
            on_release=self.actualizar_resumen_ventas
        )
        box_resumen.add_widget(btn_actualizar_resumen)

        self.card_resumen = MDCard(
            orientation='vertical', padding=dp(16), spacing=dp(10),
            size_hint=(1, None), height=dp(180), elevation=3, radius=[dp(12)]
        )
        self.lbl_resumen_total = MDLabel(text="Ventas Totales: $0.00", font_style="H6")
        self.lbl_resumen_ganancia = MDLabel(text="Ganancia Estimada: $0.00", font_style="Body1", theme_text_color="Custom", text_color=(0.2, 0.8, 0.4, 1))
        self.lbl_resumen_trans = MDLabel(text="Transacciones: 0", font_style="Body1")

        self.card_resumen.add_widget(self.lbl_resumen_total)
        self.card_resumen.add_widget(self.lbl_resumen_ganancia)
        self.card_resumen.add_widget(self.lbl_resumen_trans)

        box_resumen.add_widget(self.card_resumen)
        box_resumen.add_widget(MDLabel())
        item_resumen.add_widget(box_resumen)

        # ----------------------------------------------------
        # PESTAÑA 4: ASISTENTE IA
        # ----------------------------------------------------
        item_ia = MDBottomNavigationItem(name='tab_ia', text='Asistente IA', icon='robot')
        box_ia = MDBoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))

        self.txt_ia_pregunta = MDTextField(hint_text="Pregunta sobre stock o recomendaciones...", mode="rectangle")
        box_ia.add_widget(self.txt_ia_pregunta)

        btn_consultar_ia = MDRaisedButton(
            text="CONSULTAR A LA IA", icon="send", size_hint=(1, None), height=dp(45),
            on_release=self.consultar_ia
        )
        box_ia.add_widget(btn_consultar_ia)

        self.lbl_ia_respuesta = MDLabel(
            text="Hola, soy tu Asistente de Negocio POS IA. ¿En qué te ayudo hoy?",
            theme_text_color="Secondary", font_style="Body1"
        )
        box_ia.add_widget(self.lbl_ia_respuesta)
        box_ia.add_widget(MDLabel())
        item_ia.add_widget(box_ia)

        # Ensamblar navegacion
        nav.add_widget(item_venta)
        nav.add_widget(item_inv)
        nav.add_widget(item_resumen)
        nav.add_widget(item_ia)

        root_layout.add_widget(nav)
        self.cargar_productos_ui()
        self.actualizar_resumen_ventas()

        return root_layout

    # ----------------------------------------------------
    # BASE DE DATOS Y LÓGICA DE NEGOCIO
    # ----------------------------------------------------
    def init_db(self):
        conn = sqlite3.connect('pos_multi.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS productos 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, costo REAL, precio REAL, stock INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS ventas 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, total REAL, ganancia REAL, metodo TEXT)''')
        conn.commit()
        conn.close()

    def guardar_producto(self, instance):
        nom = self.txt_prod_nombre.text.strip()
        cos = self.txt_prod_costo.text.strip()
        pre = self.txt_prod_precio.text.strip()
        stk = self.txt_prod_stock.text.strip()

        if nom and cos and pre and stk:
            conn = sqlite3.connect('pos_multi.db')
            c = conn.cursor()
            c.execute("INSERT INTO productos (nombre, costo, precio, stock) VALUES (?, ?, ?, ?)",
                      (nom, float(cos), float(pre), int(stk)))
            conn.commit()
            conn.close()
            self.mostrar_alerta("Éxito", f"Producto '{nom}' registrado correctamente.")
            self.txt_prod_nombre.text = ""
            self.txt_prod_costo.text = ""
            self.txt_prod_precio.text = ""
            self.txt_prod_stock.text = ""
            self.cargar_productos_ui()
        else:
            self.mostrar_alerta("Error", "Completa todos los datos (costo, precio, stock y nombre).")

    def cargar_productos_ui(self):
        self.grid_inv.clear_widgets()
        conn = sqlite3.connect('pos_multi.db')
        c = conn.cursor()
        c.execute("SELECT nombre, costo, precio, stock FROM productos")
        filas = c.fetchall()
        conn.close()

        for f in filas:
            card = MDCard(orientation='vertical', padding=dp(8), size_hint_y=None, height=dp(60), radius=[dp(8)])
            card.add_widget(MDLabel(text=f"{f[0]} | Costo: ${f[1]:.2f} -> Venta: ${f[2]:.2f} (Stock: {f[3]})", font_style="Body2"))
            self.grid_inv.add_widget(card)

    def filtrar_sugerencias(self, instance, text):
        self.list_sugerencias.clear_widgets()
        if not text.strip():
            return
        
        conn = sqlite3.connect('pos_multi.db')
        c = conn.cursor()
        c.execute("SELECT id, nombre, precio, stock, costo FROM productos WHERE LOWER(nombre) LIKE ? LIMIT 5", (f"%{text.lower()}%",))
        coincidencias = c.fetchall()
        conn.close()

        for prod in coincidencias:
            item = OneLineListItem(
                text=f"{prod[1]} - ${prod[2]:.2f} (Stock: {prod[3]})",
                on_release=lambda x, p=prod: self.seleccionar_producto_sugerido(p)
            )
            self.list_sugerencias.add_widget(item)

    def seleccionar_producto_sugerido(self, producto):
        self.producto_seleccionado = producto  # (id, nombre, precio, stock, costo)
        self.txt_buscar_prod.text = producto[1]
        self.list_sugerencias.clear_widgets()

    def agregar_al_carrito(self, instance):
        cant_str = self.txt_cant_prod.text.strip()
        if not self.producto_seleccionado or not cant_str:
            self.mostrar_alerta("Error", "Selecciona un producto de la lista e ingresa una cantidad.")
            return

        cant = int(cant_str)
        p = self.producto_seleccionado

        if p[3] >= cant:
            subtotal = p[2] * cant
            # Guardamos: (id, nombre, precio_venta, cantidad, subtotal, costo_unitario)
            self.carrito.append((p[0], p[1], p[2], cant, subtotal, p[4]))
            self.total_venta += subtotal
            self.lbl_total.text = f"Total a Pagar: ${self.total_venta:.2f}"
            self.mostrar_alerta("Carrito", f"Agregado: {p[1]} x{cant}")
            self.txt_buscar_prod.text = ""
            self.producto_seleccionado = None
            self.txt_cant_prod.text = "1"
        else:
            self.mostrar_alerta("Stock Insuficiente", f"Solo quedan {p[3]} unidades disponibles.")

    def set_metodo_pago(self, metodo):
        self.metodo_pago = metodo
        if metodo == "QR":
            self.btn_metodo_qr.md_bg_color = (0.2, 0.7, 0.3, 1)
            self.btn_metodo_efectivo.md_bg_color = (0.4, 0.4, 0.4, 1)
            self.txt_pago_cliente.text = str(self.total_venta)
            self.txt_pago_cliente.disabled = True
        else:
            self.btn_metodo_efectivo.md_bg_color = (0.2, 0.7, 0.3, 1)
            self.btn_metodo_qr.md_bg_color = (0.4, 0.4, 0.4, 1)
            self.txt_pago_cliente.text = ""
            self.txt_pago_cliente.disabled = False

    def procesar_venta(self, instance):
        if not self.carrito:
            self.mostrar_alerta("Error", "El carrito está vacío.")
            return

        pago_str = self.txt_pago_cliente.text.strip()
        if not pago_str:
            self.mostrar_alerta("Error", "Ingresa el monto recibido.")
            return

        pago = float(pago_str)
        if pago < self.total_venta:
            self.mostrar_alerta("Pago Insuficiente", f"El monto recibido es menor al total.")
            return

        cambio = pago - self.total_venta
        ganancia_total = sum((item[2] - item[5]) * item[3] for item in self.carrito)

        # Actualizar stock y registrar venta
        conn = sqlite3.connect('pos_multi.db')
        c = conn.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for item in self.carrito:
            c.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (item[3], item[0]))

        c.execute("INSERT INTO ventas (fecha, total, ganancia, metodo) VALUES (?, ?, ?, ?)",
                  (fecha_actual, self.total_venta, ganancia_total, self.metodo_pago))

        conn.commit()
        conn.close()

        # Ticket
        ticket = f"--- TICKET DE VENTA ---\nMetodo: {self.metodo_pago}\nFecha: {fecha_actual}\n"
        for item in self.carrito:
            ticket += f"{item[1]} x{item[3]} = ${item[4]:.2f}\n"
        ticket += f"------------------------\nTotal: ${self.total_venta:.2f}\nPago: ${pago:.2f}\nCambio: ${cambio:.2f}\n------------------------\n¡Gracias por su compra!"

        self.mostrar_alerta("VENTA COMPLETADA", ticket)

        # Limpiar
        self.carrito = []
        self.total_venta = 0.0
        self.lbl_total.text = "Total a Pagar: $0.00"
        self.txt_pago_cliente.text = ""
        self.cargar_productos_ui()
        self.actualizar_resumen_ventas()

    def actualizar_resumen_ventas(self, instance=None):
        conn = sqlite3.connect('pos_multi.db')
        c = conn.cursor()
        fecha_hoy = datetime.now().strftime("%Y-%m-%d") + "%"
        c.execute("SELECT SUM(total), SUM(ganancia), COUNT(id) FROM ventas WHERE fecha LIKE ?", (fecha_hoy,))
        res = c.fetchone()
        conn.close()

        total = res[0] if res[0] else 0.0
        ganancia = res[1] if res[1] else 0.0
        cant = res[2] if res[2] else 0

        self.lbl_resumen_total.text = f"Ventas Totales Hoy: ${total:.2f}"
        self.lbl_resumen_ganancia.text = f"Ganancia Estimada: ${ganancia:.2f}"
        self.lbl_resumen_trans.text = f"Nº de Transacciones: {cant}"

    def consultar_ia(self, instance):
        pregunta = self.txt_ia_pregunta.text.lower().strip()
        if not pregunta:
            self.lbl_ia_respuesta.text = "Ingresa tu consulta sobre productos o inventario."
            return

        conn = sqlite3.connect('pos_multi.db')
        c = conn.cursor()
        c.execute("SELECT nombre, stock, precio FROM productos")
        prods = c.fetchall()
        conn.close()

        if "stock" in pregunta or "inventario" in pregunta:
            res = "Inventario registrado:\n" + "\n".join([f"• {p[0]}: {p[1]} unidades (${p[2]:.2f})" for p in prods]) if prods else "Sin productos registrados."
        else:
            res = f"Consulta recibida. Revisa existencias en la pestaña Inventario."

        self.lbl_ia_respuesta.text = f"Respuesta IA:\n{res}"

    def salir_app(self):
        MDApp.get_running_app().stop()
        sys.exit()

    def cerrar_dialogo(self, instance):
        if self.dialog:
            self.dialog.dismiss()

    def mostrar_alerta(self, titulo, texto):
        self.dialog = MDDialog(
            title=titulo,
            text=texto,
            buttons=[MDFlatButton(text="OK", on_release=self.cerrar_dialogo)]
        )
        self.dialog.open()

if __name__ == '__main__':
    MultiPosApp().run()
