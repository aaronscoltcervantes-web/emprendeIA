import sqlite3
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView

# --- BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect("tienda.db")
    cursor = conn.cursor()
    # Tabla Productos (incluye precio compra y venta)
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        precio_compra REAL NOT NULL,
                        precio_venta REAL NOT NULL,
                        stock INTEGER DEFAULT 0)''')
    # Tabla Ventas (incluye metodo de pago como QR)
    cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT,
                        producto TEXT,
                        cantidad INTEGER,
                        total REAL,
                        ganancia REAL,
                        metodo_pago TEXT)''')
    # Tabla Caja (Apertura y Cierre)
    cursor.execute('''CREATE TABLE IF NOT EXISTS caja (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT,
                        tipo TEXT,
                        monto REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- PANTALLA PRINCIPAL DE NAVEGACIÓN ---
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text="SISTEMA DE CONTROL DE VENTAS", font_size='20sp', bold=True))
        
        btn_caja = Button(text="1. Apertura / Cierre de Caja", size_hint_y=None, height=50)
        btn_caja.bind(on_press=lambda x: setattr(self.manager, 'current', 'caja'))
        layout.add_widget(btn_caja)

        btn_prod = Button(text="2. Agregar Producto (Costo / Venta)", size_hint_y=None, height=50)
        btn_prod.bind(on_press=lambda x: setattr(self.manager, 'current', 'productos'))
        layout.add_widget(btn_prod)

        btn_venta = Button(text="3. Registrar Venta (Efectivo / QR)", size_hint_y=None, height=50)
        btn_venta.bind(on_press=lambda x: setattr(self.manager, 'current', 'ventas'))
        layout.add_widget(btn_venta)

        btn_resumen = Button(text="4. Resumen Diario y Conteo Semanal", size_hint_y=None, height=50)
        btn_resumen.bind(on_press=lambda x: setattr(self.manager, 'current', 'resumen'))
        layout.add_widget(btn_resumen)

        self.add_widget(layout)

# --- 1. APERTURA Y CIERRE DE CAJA ---
class CajaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text="Control de Caja", font_size='18sp'))
        
        self.txt_monto = TextInput(hint_text="Monto en Bs", input_filter='float', multiline=False)
        layout.add_widget(self.txt_monto)
        
        # Corregido bg_color por background_color
        btn_apertura = Button(text="Registrar Apertura de Caja", background_color=(0, 1, 0, 1))
        btn_apertura.bind(on_press=self.aperturar_caja)
        layout.add_widget(btn_apertura)

        btn_volver = Button(text="Volver al Menú Principal")
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        self.add_widget(layout)

   def aperturar_caja(self, instance):
        if self.txt_monto.text:
            monto = float(self.txt_monto.text)
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect("tienda.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO caja (fecha, tipo, monto) VALUES (?, 'Apertura', ?)", (fecha, monto))
            conn.commit()
            conn.close()
            self.txt_monto.text = ""
            Popup(title="Caja", content=Label(text=f"Apertura registrada con {monto} Bs"), size_hint=(0.8, 0.4)).open()

# --- 2. AGREGAR PRODUCTOS (COSTO Y VENTA) ---
class ProductosScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text="Registro de Productos", font_size='18sp'))
        
        self.txt_nombre = TextInput(hint_text="Nombre del producto / prenda / medicina", multiline=False)
        self.txt_compra = TextInput(hint_text="Precio de Compra (Costo)", input_filter='float', multiline=False)
        self.txt_venta = TextInput(hint_text="Precio de Venta (Público)", input_filter='float', multiline=False)
        self.txt_stock = TextInput(hint_text="Cantidad Inicial / Stock", input_filter='int', multiline=False)
        
        layout.add_widget(self.txt_nombre)
        layout.add_widget(self.txt_compra)
        layout.add_widget(self.txt_venta)
        layout.add_widget(self.txt_stock)
        
        btn_guardar = Button(text="Guardar Producto")
        btn_guardar.bind(on_press=self.guardar_producto)
        layout.add_widget(btn_guardar)

        btn_volver = Button(text="Volver al Menú Principal")
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def guardar_producto(self, instance):
        if self.txt_nombre.text and self.txt_compra.text and self.txt_venta.text:
            nombre = self.txt_nombre.text
            compra = float(self.txt_compra.text)
            venta = float(self.txt_venta.text)
            stock = int(self.txt_stock.text) if self.txt_stock.text else 0
            
            conn = sqlite3.connect("tienda.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO productos (nombre, precio_compra, precio_venta, stock) VALUES (?, ?, ?, ?)",
                           (nombre, compra, venta, stock))
            conn.commit()
            conn.close()
            
            self.txt_nombre.text = ""
            self.txt_compra.text = ""
            self.txt_venta.text = ""
            self.txt_stock.text = ""
            Popup(title="Éxito", content=Label(text="Producto registrado correctamente"), size_hint=(0.8, 0.4)).open()

# --- 3. VENTAS (PAGO CON QR O EFECTIVO) ---
class VentasScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text="Registrar Venta", font_size='18sp'))
        
        self.spinner_prod = Spinner(text="Seleccionar Producto", values=())
        layout.add_widget(self.spinner_prod)
        
        self.txt_cantidad = TextInput(hint_text="Cantidad", input_filter='int', multiline=False, text="1")
        layout.add_widget(self.txt_cantidad)

        # Selección de método de pago
        layout.add_widget(Label(text="Método de Pago:"))
        self.spinner_pago = Spinner(text="Efectivo", values=("Efectivo", "QR / Transferencia"))
        layout.add_widget(self.spinner_pago)
        
        btn_vender = Button(text="Completar Venta")
        btn_vender.bind(on_press=self.realizar_venta)
        layout.add_widget(btn_vender)

        btn_volver = Button(text="Volver al Menú Principal")
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def on_pre_enter(self):
        # Cargar productos registrados al entrar a la pantalla
        conn = sqlite3.connect("tienda.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM productos")
        prods = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.spinner_prod.values = prods

    def realizar_venta(self, instance):
        prod_nombre = self.spinner_prod.text
        if prod_nombre != "Seleccionar Producto" and self.txt_cantidad.text:
            cant = int(self.txt_cantidad.text)
            pago = self.spinner_pago.text
            
            conn = sqlite3.connect("tienda.db")
            cursor = conn.cursor()
            cursor.execute("SELECT precio_compra, precio_venta, stock FROM productos WHERE nombre = ?", (prod_nombre,))
            row = cursor.fetchone()
            
            if row:
                compra, venta, stock = row
                total = venta * cant
                ganancia = (venta - compra) * cant
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Registrar Venta
                cursor.execute("INSERT INTO ventas (fecha, producto, cantidad, total, ganancia, metodo_pago) VALUES (?, ?, ?, ?, ?, ?)",
                               (fecha, prod_nombre, cant, total, ganancia, pago))
                # Actualizar Stock
                cursor.execute("UPDATE productos SET stock = stock - ? WHERE nombre = ?", (cant, prod_nombre))
                
                conn.commit()
                conn.close()
                
                Popup(title="Venta Exitosa", content=Label(text=f"Total: {total} Bs\nPago con: {pago}"), size_hint=(0.8, 0.4)).open()

# --- 4. RESUMEN Y CONTEO SEMANAL ---
class ResumenScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.add_widget(self.layout)

    def on_pre_enter(self):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="Resumen Diario & Conteo de Inventario", font_size='18sp'))
        
        # Calcular totales del día
        hoy = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect("tienda.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT SUM(total), SUM(ganancia) FROM ventas WHERE fecha LIKE ?", (f"{hoy}%",))
        res_ventas = cursor.fetchone()
        total_dia = res_ventas[0] if res_ventas[0] else 0.0
        ganancia_dia = res_ventas[1] if res_ventas[1] else 0.0

        # Ventas por QR vs Efectivo
        cursor.execute("SELECT SUM(total) FROM ventas WHERE fecha LIKE ? AND metodo_pago = 'QR / Transferencia'", (f"{hoy}%",))
        total_qr = cursor.fetchone()[0] or 0.0

        self.layout.add_widget(Label(text=f"Ventas Hoy: {total_dia:.2f} Bs | En QR: {total_qr:.2f} Bs"))
        self.layout.add_widget(Label(text=f"Ganancia Neta Hoy: {ganancia_dia:.2f} Bs", color=(0, 1, 0, 1)))
        
        self.layout.add_widget(Label(text="--- Stock Actual para Conteo Semanal ---", bold=True))
        
        # Mostrar Inventario
        cursor.execute("SELECT nombre, stock FROM productos")
        items = cursor.fetchall()
        
        scroll = ScrollView()
        grid = GridLayout(cols=2, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for name, stock in items:
            grid.add_widget(Label(text=name, size_hint_y=None, height=30))
            grid.add_widget(Label(text=f"Stock: {stock}", size_hint_y=None, height=30))
            
        scroll.add_widget(grid)
        self.layout.add_widget(scroll)
        
        conn.close()

        btn_volver = Button(text="Volver al Menú Principal", size_hint_y=None, height=40)
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        self.layout.add_widget(btn_volver)

# --- APLICACIÓN PRINCIPAL ---
class MiAppEmprende(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(CajaScreen(name='caja'))
        sm.add_widget(ProductosScreen(name='productos'))
        sm.add_widget(VentasScreen(name='ventas'))
        sm.add_widget(ResumenScreen(name='resumen'))
        return sm

if __name__ == '__main__':
    MiAppEmprende().run()
