import os
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView

# Rutas de Archivos
CARPETA_BASE = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '.'
ARCHIVO_DB = os.path.join(CARPETA_BASE, "inventario.txt")
ARCHIVO_CAJA = os.path.join(CARPETA_BASE, "caja.txt")

def cargar_datos():
    lista = []
    if not os.path.exists(ARCHIVO_DB):
        with open(ARCHIVO_DB, "w") as f:
            f.write("1,Paracetamol 500mg,100,1.50,2.50,L1024,12/2027,Genfar\n")
            f.write("2,Ibuprofeno 400mg,8,2.20,4.00,L0825,05/2026,Bago\n")
            f.write("3,Amoxicilina 500mg,50,3.00,5.00,L0924,08/2026,Genfar\n")
    
    if os.path.exists(ARCHIVO_DB):
        with open(ARCHIVO_DB, "r") as f:
            for linea in f:
                if linea.strip():
                    partes = linea.strip().split(",")
                    if len(partes) >= 8:
                        lista.append({
                            "id": int(partes[0]), 
                            "nombre": partes[1], 
                            "stock": int(partes[2]),
                            "precio_compra": float(partes[3]), 
                            "precio_venta": float(partes[4]),
                            "lote": partes[5], 
                            "vencimiento": partes[6],
                            "laboratorio": partes[7]
                        })
    return lista

def guardar_datos(inventario):
    try:
        with open(ARCHIVO_DB, "w") as f:
            for prod in inventario:
                f.write(f"{prod['id']},{prod['nombre']},{prod['stock']},{prod['precio_compra']},{prod['precio_venta']},{prod['lote']},{prod['vencimiento']},{prod['laboratorio']}\n")
    except Exception as e:
        print(f"[ERROR] guardar_datos() falló: {e}")

# Variables Globales de Estado del Negocio
inventario = cargar_datos()
caja_abierta = False
monto_apertura = 0.0
total_recaudado = 0.0
total_costo_vendido = 0.0
ganancia_neta = 0.0
fecha_caja = ""
carrito_ventas = []
historial_ventas_dia = []

# --- PANTALLA DE CAJA / ARQUEO ---
class CajaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        layout.add_widget(Label(text="🗄 CONTROL DE ARQUEO Y APERTURA DE CAJA", font_size=18, size_hint_y=None, height=40))
        
        self.lbl_estado = Label(text="Estado: Caja Cerrada", font_size=14, color=(0.9, 0.2, 0.2, 1), size_hint_y=None, height=30)
        layout.add_widget(self.lbl_estado)
        
        self.input_monto = TextInput(text="0.00", multiline=False, size_hint_y=None, height=40)
        layout.add_widget(Label(text="Fondo Inicial ($):", size_hint_y=None, height=20))
        layout.add_widget(self.input_monto)
        
        self.btn_accion = Button(text="Habilitar Caja Diaria", background_color=(0.1, 0.7, 0.5, 1), size_hint_y=None, height=50)
        self.btn_accion.bind(on_press=self.toggle_caja)
        layout.add_widget(self.btn_accion)
        
        self.lbl_detalles = Label(text="Monto Inicial: $0.00\nVentas Brutas: $0.00\nGanancia Neta: $0.00", font_size=14)
        layout.add_widget(self.lbl_detalles)
        
        self.add_widget(layout)

    def toggle_caja(self, instance):
        global caja_abierta, monto_apertura, fecha_caja, total_recaudado, total_costo_vendido, ganancia_neta, historial_ventas_dia
        if not caja_abierta:
            try:
                monto_apertura = float(self.input_monto.text)
            except ValueError:
                monto_apertura = 0.0
            caja_abierta = True
            fecha_caja = datetime.now().strftime("%d/%m/%Y")
            total_recaudado = 0.0
            total_costo_vendido = 0.0
            ganancia_neta = 0.0
            historial_ventas_dia.clear()
            self.lbl_estado.text = f"Estado: Operando Activamente ({fecha_caja})"
            self.lbl_estado.color = (0.1, 0.8, 0.5, 1)
            self.btn_accion.text = "Realizar Cierre de Turno"
            self.btn_accion.background_color = (0.9, 0.2, 0.2, 1)
        else:
            monto_total = monto_apertura + total_recaudado
            with open(ARCHIVO_CAJA, "a") as f:
                f.write(f"FECHA: {fecha_caja} | Apertura: ${monto_apertura:.2f} | Ventas: ${total_recaudado:.2f} | Ganancia: ${ganancia_neta:.2f} | Total: ${monto_total:.2f}\n")
            caja_abierta = False
            self.lbl_estado.text = "Estado: Caja Cerrada"
            self.lbl_estado.color = (0.9, 0.2, 0.2, 1)
            self.btn_accion.text = "Habilitar Caja Diaria"
            self.btn_accion.background_color = (0.1, 0.7, 0.5, 1)
        self.actualizar_info()

    def actualizar_info(self):
        self.lbl_detalles.text = f"Monto Inicial: ${monto_apertura:.2f}\nVentas Brutas: ${total_recaudado:.2f}\nEfectivo en Caja: ${(monto_apertura + total_recaudado):.2f}\nGanancia Neta: ${ganancia_neta:.2f}"


# --- PANTALLA DE PUNTO DE VENTA ---
class VentasScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text="🛒 PUNTO DE VENTA", font_size=18, size_hint_y=None, height=40))
        
        self.input_id = TextInput(hint_text="ID del Medicamento", multiline=False, size_hint_y=None, height=40)
        self.input_cant = TextInput(hint_text="Cantidad", multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.input_id)
        layout.add_widget(self.input_cant)
        
        btn_add = Button(text="➕ Agregar al Carrito", background_color=(0.2, 0.6, 0.86, 1), size_hint_y=None, height=45)
        btn_add.bind(on_press=self.agregar_carrito)
        layout.add_widget(btn_add)
        
        self.lbl_status = Label(text="", size_hint_y=None, height=30)
        layout.add_widget(self.lbl_status)
        
        self.txt_carrito_box = TextInput(text="", readonly=True, multiline=True)
        layout.add_widget(self.txt_carrito_box)
        
        self.lbl_total = Label(text="Total: $0.00", font_size=16, size_hint_y=None, height=40)
        layout.add_widget(self.lbl_total)
        
        btn_cobrar = Button(text="✔ COBRAR VENTA", background_color=(0.1, 0.7, 0.5, 1), size_hint_y=None, height=50)
        btn_cobrar.bind(on_press=self.cobrar)
        layout.add_widget(btn_cobrar)
        
        self.add_widget(layout)

    def agregar_carrito(self, instance):
        global inventario, carrito_ventas
        if not caja_abierta:
            self.lbl_status.text = "Error: Abra la caja primero."
            return
        try:
            prod_id = int(self.input_id.text)
            cant = int(self.input_cant.text)
        except ValueError:
            self.lbl_status.text = "Error: Ingrese ID y cantidad válidos."
            return
        
        prod = next((p for p in inventario if p["id"] == prod_id), None)
        if not prod:
            self.lbl_status.text = "Error: Producto no encontrado."
            return
        
        if prod["stock"] < cant:
            self.lbl_status.text = "Error: Stock insuficiente."
            return
        
        carrito_ventas.append({
            "id": prod["id"], "nombre": prod["nombre"], "cantidad": cant,
            "precio_compra": prod["precio_compra"], "subtotal": cant * prod["precio_venta"]
        })
        self.lbl_status.text = f"Agregado: {prod['nombre']} x{cant}"
        self.actualizar_vista()

    def actualizar_vista(self):
        texto = f"{'ID':<4} | {'Medicamento':<15} | {'Cant':<4} | {'Total':<6}\n" + "-"*40 + "\n"
        total = 0.0
        for item in carrito_ventas:
            texto += f"{item['id']:<4} | {item['nombre'][:15]:<15} | {item['cantidad']:<4} | ${item['subtotal']:<5.2f}\n"
            total += item["subtotal"]
        self.txt_carrito_box.text = texto
        self.lbl_total.text = f"Total: ${total:.2f}"

    def cobrar(self, instance):
        global total_recaudado, total_costo_vendido, ganancia_neta, historial_ventas_dia, inventario
        if not carrito_ventas:
            self.lbl_status.text = "El carrito está vacío."
            return
        hora = datetime.now().strftime("%H:%M:%S")
        for item in carrito_ventas:
            p = next(x for x in inventario if x["id"] == item["id"])
            p["stock"] -= item["cantidad"]
            total_recaudado += item["subtotal"]
            total_costo_vendido += item["cantidad"] * item["precio_compra"]
            historial_ventas_dia.append({"hora": hora, "nombre": item["nombre"], "cantidad": item["cantidad"], "total": item["subtotal"]})
        
        ganancia_neta = total_recaudado - total_costo_vendido
        guardar_datos(inventario)
        carrito_ventas.clear()
        self.actualizar_vista()
        self.lbl_status.text = "¡Cobro realizado con éxito!"


# --- PANTALLA DE INVENTARIO ---
class InventarioScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="📦 CONTROL DE INVENTARIO", font_size=18, size_hint_y=None, height=40))
        
        self.txt_inv = TextInput(text="", readonly=True, multiline=True)
        layout.add_widget(self.txt_inv)
        
        btn_actualizar = Button(text="🔄 Actualizar Lista", background_color=(0.2, 0.6, 0.86, 1), size_hint_y=None, height=45)
        btn_actualizar.bind(on_press=self.cargar_inventario_texto)
        layout.add_widget(btn_actualizar)
        
        self.add_widget(layout)
        self.cargar_inventario_texto(None)

    def cargar_inventario_texto(self, instance):
        global inventario
        inventario = cargar_datos()
        texto = f"{'ID':<3} | {'Nombre':<15} | {'Stock':<5} | {'Precio':<6} | {'Vence':<7}\n" + "-"*45 + "\n"
        for p in inventario:
            texto += f"{p['id']:<3} | {p['nombre'][:15]:<15} | {p['stock']:<5} | ${p['precio_venta']:<5.2f} | {p['vencimiento']:<7}\n"
        self.txt_inv.text = texto


# --- APLICACIÓN PRINCIPAL KIVY ---
class FarmaNoahApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(CajaScreen(name='caja'))
        sm.add_widget(VentasScreen(name='ventas'))
        sm.add_widget(InventarioScreen(name='inventario'))
        
        # Menú de navegación inferior simple
        layout_principal = BoxLayout(orientation='vertical')
        layout_principal.add_widget(sm)
        
        menu_bar = BoxLayout(size_hint_y=None, height=50, spacing=5, padding=5)
        btn_caja = Button(text="Caja", background_color=(0.2, 0.6, 0.86, 1))
        btn_caja.bind(on_press=lambda x: setattr(sm, 'current', 'caja'))
        btn_ventas = Button(text="Venta", background_color=(0.1, 0.7, 0.5, 1))
        btn_ventas.bind(on_press=lambda x: setattr(sm, 'current', 'ventas'))
        btn_inv = Button(text="Inventario", background_color=(0.5, 0.5, 0.5, 1))
        btn_inv.bind(on_press=lambda x: setattr(sm, 'current', 'inventario'))
        
        menu_bar.add_widget(btn_caja)
        menu_bar.add_widget(btn_ventas)
        menu_bar.add_widget(btn_inv)
        
        layout_principal.add_widget(menu_bar)
        return layout_principal

if __name__ == '__main__':
    FarmaNoahApp().run()
