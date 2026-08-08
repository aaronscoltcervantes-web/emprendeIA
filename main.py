import json
import os
from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

DATA_FILE = "sistema_negocio_data.json"

def cargar_datos():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
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
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

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

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        with layout.canvas.before:
            Color(0.07, 0.08, 0.11, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        # Header
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(75), spacing=dp(3))
        header.add_widget(Label(text='SISTEMA COMERCIAL PRO', font_size=dp(20), bold=True, color=(1,1,1,1)))
        self.lbl_estado = Label(text='Estado de Caja: CERRADA', font_size=dp(13), color=(0.9, 0.3, 0.3, 1), bold=True)
        header.add_widget(self.lbl_estado)
        layout.add_widget(header)

        # Menú de Opciones en ScrollView para que quepa todo perfecto
        scroll_menu = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        grid.add_widget(self.crear_Boton('1. Control de Caja (Apertura / Cierre)', (0.15, 0.5, 0.25, 1), lambda x: setattr(self.manager, 'current', 'caja')))
        grid.add_widget(self.crear_Boton('2. Ver Inventario y Stock', (0.2, 0.4, 0.6, 1), lambda x: setattr(self.manager, 'current', 'inventario')))
        grid.add_widget(self.crear_Boton('3. Ingresar Producto / Compras', (0.7, 0.4, 0.1, 1), lambda x: setattr(self.manager, 'current', 'ingreso')))
        grid.add_widget(self.crear_Boton('4. Realizar Venta (POS Rápido)', (0.8, 0.2, 0.2, 1), lambda x: setattr(self.manager, 'current', 'venta')))
        grid.add_widget(self.crear_Boton('5. Registrar Gasto / Retiro de Caja', (0.6, 0.2, 0.6, 1), lambda x: setattr(self.manager, 'current', 'gasto')))
        grid.add_widget(self.crear_Boton('6. Historial de Ventas', (0.3, 0.5, 0.5, 1), lambda x: setattr(self.manager, 'current', 'historial')))
        grid.add_widget(self.crear_Boton('7. Resumen Financiero y Ganancias', (0.35, 0.35, 0.4, 1), lambda x: setattr(self.manager, 'current', 'resumen')))

        scroll_menu.add_widget(grid)
        layout.add_widget(scroll_menu)
        self.add_widget(layout)

    def on_enter(self):
        if GlobalData.caja_abierta:
            total_gastos = sum(g['monto'] for g in GlobalData.gastos_caja)
            efectivo_en_caja = GlobalData.monto_inicial + GlobalData.total_ventas_efectivo - total_gastos
            self.lbl_estado.text = f'Caja ABIERTA | Efectivo físico: {efectivo_en_caja:.2f} Bs'
            self.lbl_estado.color = (0.2, 0.8, 0.3, 1)
        else:
            self.lbl_estado.text = 'Estado de Caja: CERRADA'
            self.lbl_estado.color = (0.9, 0.3, 0.3, 1)

    def crear_Boton(self, texto, color, callback):
        btn = Button(text=texto, font_size=dp(14), bold=True, background_normal='', background_color=color, size_hint_y=None, height=dp(50))
        btn.bind(on_press=callback)
        return btn

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class CajaScreen(Screen):
    def __init__(self, **kwargs):
        super(CajaScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        
        with layout.canvas.before:
            Color(0.07, 0.08, 0.11, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Módulo de Apertura y Cierre de Caja', font_size=dp(18), bold=True, size_hint_y=None, height=dp(35)))
        
        self.lbl_info_estado = Label(text='', font_size=dp(13), color=(0.9, 0.9, 0.2, 1), size_hint_y=None, height=dp(55), halign='center', valign='middle')
        self.lbl_info_estado.bind(size=self.lbl_info_estado.setter('text_size'))
        layout.add_widget(self.lbl_info_estado)

        self.lbl_prompt = Label(text='Monto:', font_size=dp(13), size_hint_y=None, height=dp(20))
        layout.add_widget(self.lbl_prompt)

        self.input_monto = TextInput(hint_text='0.00', multiline=False, input_filter='float', font_size=dp(16), size_hint_y=None, height=dp(42))
        layout.add_widget(self.input_monto)

        self.lbl_msg = Label(text='', font_size=dp(13), color=(0.2, 0.8, 0.3, 1), size_hint_y=None, height=dp(55), halign='center')
        self.lbl_msg.bind(size=self.lbl_msg.setter('text_size'))
        layout.add_widget(self.lbl_msg)

        self.btn_accion = Button(text='', font_size=dp(15), bold=True, background_normal='', size_hint_y=None, height=dp(45))
        self.btn_accion.bind(on_press=self.ejecutar_accion)
        layout.add_widget(self.btn_accion)

        btn_volver = Button(text='Volver al Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(42))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        layout.add_widget(Label())
        self.add_widget(layout)

    def on_enter(self):
        self.lbl_msg.text = ''
        self.input_monto.text = ''
        if not GlobalData.caja_abierta:
            self.lbl_info_estado.text = 'La caja está CERRADA. Ingrese el dinero en efectivo con el que inicia el día.'
            self.lbl_prompt.text = 'Monto Inicial en Efectivo (Bs):'
            self.btn_accion.text = 'Registrar Apertura de Caja'
            self.btn_accion.background_color = (0.15, 0.5, 0.25, 1)
        else:
            total_gastos = sum(g['monto'] for g in GlobalData.gastos_caja)
            efectivo_esperado = GlobalData.monto_inicial + GlobalData.total_ventas_efectivo - total_gastos
            self.lbl_info_estado.text = f'Caja Abierta.\nEfectivo esperado: {efectivo_esperado:.2f} Bs (Inicial: {GlobalData.monto_inicial} + Ventas Efectivo: {GlobalData.total_ventas_efectivo} - Gastos: {total_gastos})'
            self.lbl_prompt.text = 'Conteo exacto del efectivo físico contado (Bs):'
            self.btn_accion.text = 'Registrar Cierre de Caja'
            self.btn_accion.background_color = (0.8, 0.2, 0.2, 1)

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
                self.lbl_msg.text = f'¡Apertura registrada con éxito con {monto:.2f} Bs!'
                self.on_enter()
            else:
                total_gastos = sum(g['monto'] for g in GlobalData.gastos_caja)
                efectivo_esperado = GlobalData.monto_inicial + GlobalData.total_ventas_efectivo - total_gastos
                diferencia = monto - efectivo_esperado
                GlobalData.caja_abierta = False
                guardar_datos()
                
                estado_dif = "Cuadre exacto (Sin diferencia)"
                if diferencia > 0:
                    estado_dif = f"Sobrante de +{diferencia:.2f} Bs"
                elif diferencia < 0:
                    estado_dif = f"Faltante de {diferencia:.2f} Bs"

                self.lbl_msg.text = f'Cierre exitoso.\nContado: {monto} Bs | Esperado: {efectivo_esperado:.2f} Bs\nResultado: {estado_dif}'
        except ValueError:
            self.lbl_msg.text = 'Ingrese un valor numérico válido.'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class InventarioScreen(Screen):
    def __init__(self, **kwargs):
        super(InventarioScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        with layout.canvas.before:
            Color(0.07, 0.08, 0.11, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Inventario y Control de Stock', font_size=dp(18), bold=True, size_hint_y=None, height=dp(35)))

        self.scroll = ScrollView(size_hint=(1, 1))
        self.lista_layout = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.lista_layout.bind(minimum_height=self.lista_layout.setter('height'))
        self.scroll.add_widget(self.lista_layout)
        layout.add_widget(self.scroll)

        btn_volver = Button(text='Volver al Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(45))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def on_enter(self):
        self.lista_layout.clear_widgets()
        for prod in GlobalData.inventario:
            alerta = " [¡STOCK BAJO!]" if prod['stock'] <= 5 else ""
            color_texto = (1, 0.4, 0.4, 1) if prod['stock'] <= 5 else (1, 1, 1, 1)
            texto = f"{prod['nombre']} | Stock: {prod['stock']}{alerta}\nCompra: {prod['costo']} Bs | Venta: {prod['precio']} Bs"
            lbl = Label(text=texto, font_size=dp(13), color=color_texto, size_hint_y=None, height=dp(50), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            self.lista_layout.add_widget(lbl)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class IngresoProductoScreen(Screen):
    def __init__(self, **kwargs):
        super(IngresoProductoScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))
        
        with layout.canvas.before:
            Color(0.07, 0.08, 0.11, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Ingreso de Producto / Compras', font_size=dp(18), bold=True, size_hint_y=None, height=dp(35)))

        layout.add_widget(Label(text='Nombre del Producto:', font_size=dp(12), size_hint_y=None, height=dp(18)))
        self.input_nombre = TextInput(hint_text='Ej. Arroz 1kg', multiline=False, size_hint_y=None, height=dp(38))
        layout.add_widget(self.input_nombre)

        layout.add_widget(Label(text='Cantidad a ingresar (Stock):', font_size=dp(12), size_hint_y=None, height=dp(18)))
        self.input_stock = TextInput(hint_text='0', multiline=False, input_filter='int', size_hint_y=None, height=dp(38))
        layout.add_widget(self.input_stock)

        layout.add_widget(Label(text='Costo de Compra (Bs):', font_size=dp(12), size_hint_y=None, height=dp(18)))
        self.input_costo = TextInput(hint_text='0.00', multiline=False, input_filter='float', size_hint_y=None, height=dp(38))
        layout.add_widget(self.input_costo)

        layout.add_widget(Label(text='Precio de Venta (Bs):', font_size=dp(12), size_hint_y=None, height=dp(18)))
        self.input_precio = TextInput(hint_text='0.00', multiline=False, input_filter='float', size_hint_y=None, height=dp(38))
        layout.add_widget(self.input_precio)

        self.lbl_msg = Label(text='', font_size=dp(13), color=(0.2, 0.8, 0.3, 1), size_hint_y=None, height=dp(25))
        layout.add_widget(self.lbl_msg)

        btn_guardar = Button(text='Guardar Producto', background_normal='', background_color=(0.7, 0.4, 0.1, 1), size_hint_y=None, height=dp(42), bold=True)
        btn_guardar.bind(on_press=self.guardar_producto)
        layout.add_widget(btn_guardar)

        btn_volver = Button(text='Volver al Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(42))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def guardar_producto(self, instance):
        try:
            nombre = self.input_nombre.text.strip()
            stock = int(self.input_stock.text)
            costo = float(self.input_costo.text)
            precio = float(self.input_precio.text)
            
            if not nombre:
                self.lbl_msg.text = 'El nombre no puede estar vacío.'
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
            self.lbl_msg.text = '¡Producto registrado con éxito!'
            self.input_nombre.text = ''
            self.input_stock.text = ''
            self.input_costo.text = ''
            self.input_precio.text = ''
        except ValueError:
            self.lbl_msg.text = 'Revise los campos numéricos.'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class VentaScreen(Screen):
    def __init__(self, **kwargs):
        super(VentaScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(6))
        
        with layout.canvas.before:
            Color(0.07, 0.08, 0.11, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Punto de Venta (Búsqueda Rápida)', font_size=dp(16), bold=True, size_hint_y=None, height=dp(30)))

        self.input_buscar = TextInput(hint_text='Escriba una letra para buscar producto...', multiline=False, size_hint_y=None, height=dp(38), font_size=dp(14))
        self.input_buscar.bind(text=self.filtrar_productos)
        layout.add_widget(self.input_buscar)

        self.scroll_res = ScrollView(size_hint=(1, 0.32))
        self.lista_resultados = GridLayout(cols=1, spacing=dp(3), size_hint_y=None)
        self.lista_resultados.bind(minimum_height=self.lista_resultados.setter('height'))
        self.scroll_res.add_widget(self.lista_resultados)
        layout.add_widget(self.scroll_res)

        layout.add_widget(Label(text='Carrito de Compras:', font_size=dp(12), bold=True, size_hint_y=None, height=dp(20)))
        
        self.scroll_car = ScrollView(size_hint=(1, 0.28))
        self.lista_carrito = GridLayout(cols=1, spacing=dp(3), size_hint_y=None)
        self.lista_carrito.bind(minimum_height=self.lista_carrito.setter('height'))
        self.scroll_car.add_widget(self.lista_carrito)
        layout.add_widget(self.scroll_car)

        self.lbl_total = Label(text='Total Venta: 0.00 Bs', font_size=dp(14), bold=True, color=(0.2, 0.8, 0.3, 1), size_hint_y=None, height=dp(25))
        layout.add_widget(self.lbl_total)

        botones_pago = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        btn_efectivo = Button(text='Cobrar Efectivo', background_normal='', background_color=(0.15, 0.5, 0.25, 1), bold=True)
        btn_efectivo.bind(on_press=lambda x: self.cobrar('efectivo'))
        
        btn_qr = Button(text='Cobrar QR / Transf.', background_normal='', background_color=(0.2, 0.4, 0.7, 1), bold=True)
        btn_qr.bind(on_press=lambda x: self.cobrar('qr'))
        
        botones_pago.add_widget(btn_efectivo)
        botones_pago.add_widget(btn_qr)
        layout.add_widget(botones_pago)

        btn_volver = Button(text='Volver al Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(38))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        self.add_widget(layout)

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
                alerta = " [STOCK BAJO]" if prod['stock'] <= 5 else ""
                texto_btn = f"{prod['nombre']} | Stock: {prod['stock']}{alerta} | {prod['precio']} Bs"
                btn = Button(text=texto_btn, size_hint_y=None, height=dp(35), background_normal='', background_color=(0.2, 0.3, 0.4, 1))
                btn.bind(on_press=lambda x, p=prod: self.agregar_al_carrito(p))
                self.lista_resultados.add_widget(btn)

    def agregar_al_carrito(self, producto):
        if producto['stock'] > 0:
            en_carrito = next((item for item in GlobalData.carrito if item['nombre'] == producto['nombre']), None)
            if en_carrito:
                en_carrito['cantidad'] += 1
            else:
                GlobalData.carrito.append({
                    'nombre': producto['nombre'], 
                    'precio': producto['precio'], 
                    'costo': producto['costo'], 
                    'cantidad': 1
                })
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
            lbl = Label(text=f"{item['nombre']} x{item['cantidad']} = {sub:.2f} Bs", font_size=dp(12), size_hint_y=None, height=dp(24), color=(1,1,1,1))
            self.lista_carrito.add_widget(lbl)
        self.lbl_total.text = f'Total Venta: {total:.2f} Bs'

    def cobrar(self, metodo):
        if not GlobalData.carrito:
            return
        
        if not GlobalData.caja_abierta:
            self.lbl_total.text = '¡Error: La caja está cerrada!'
            return

        total_venta = 0.0
        ganancia_venta = 0.0
        detalle_productos = []

        for item in GlobalData.carrito:
            sub_venta = item['precio'] * item['cantidad']
            sub_costo = item['costo'] * item['cantidad']
            total_venta += sub_venta
            ganancia_venta += (sub_venta - sub_costo)
            detalle_productos.append(f"{item['nombre']} x{item['cantidad']}")

        if metodo == 'efectivo':
            GlobalData.total_ventas_efectivo += total_venta
        else:
            GlobalData.total_ventas_qr += total_venta

        GlobalData.total_ganancias += ganancia_venta

        # Registrar en historial
        hora_actual = datetime.now().strftime("%H:%M:%S")
        GlobalData.historial_ventas.append({
            "hora": hora_actual,
            "metodo": metodo.upper(),
            "total": total_venta,
            "productos": ", ".join(detalle_productos)
        })

        GlobalData.carrito = []
        guardar_datos()
        self.actualizar_carrito_vista()
        self.lbl_total.text = f'¡Cobrado ({metodo.upper()})! Total: {total_venta:.2f} Bs'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class GastoScreen(Screen):
    def __init__(self, **kwargs):
        super(GastoScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        
        with layout.canvas.before:
            Color(0.07, 0.08, 0.11, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Registro de Gasto / Retiro de Caja', font_size=dp(18), bold=True, size_hint_y=None, height=dp(35)))

        layout.add_widget(Label(text='Motivo del Gasto:', font_size=dp(13), size_hint_y=None, height=dp(20)))
        self.input_motivo = TextInput(hint_text='Ej. Compra de cambio / Pago delivery', multiline=False, size_hint_y=None, height=dp(40))
        layout.add_widget(self.input_motivo)

        layout.add_widget(Label(text='Monto retirado (Bs):', font_size=dp(13), size_hint_y=None, height=dp(20)))
        self.input_monto = TextInput(hint_text='0.00', multiline=False, input_filter='float', size_hint_y=None, height=dp(40))
        layout.add_widget(self.input_monto)

        self.lbl_msg = Label(text='', font_size=dp(13), color=(0.2, 0.8, 0.3, 1), size_hint_y=None, height=dp(30))
        layout.add_widget(self.lbl_msg)

        btn_registrar = Button(text='Registrar Retiro', background_normal='', background_color=(0.8, 0.3, 0.2, 1), size_hint_y=None, height=dp(45), bold=True)
        btn_registrar.bind(on_press=self.registrar_gasto)
        layout.add_widget(btn_registrar)

        btn_volver = Button(text='Volver al Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(42))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        layout.add_widget(Label())
        self.add_widget(layout)

    def registrar_gasto(self, instance):
        try:
            motivo = self.input_motivo.text.strip()
            monto = float(self.input_monto.text) if self.input_monto.text else 0.0
            
            if not motivo or monto <= 0:
                self.lbl_msg.text = 'Ingrese un motivo y un monto válido.'
                return

            GlobalData.gastos_caja.append({"motivo": motivo, "monto": monto})
            guardar_datos()
            self.lbl_msg.text = f'Gasto de {monto:.2f} Bs registrado con éxito.'
            self.input_motivo.text = ''
            self.input_monto.text = ''
        except ValueError:
            self.lbl_msg.text = 'Revise los campos numéricos.'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class HistorialScreen(Screen):
    def __init__(self, **kwargs):
        super(HistorialScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        with layout.canvas.before:
            Color(0.07, 0.08, 0.11, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Historial de Ventas del Día', font_size=dp(18), bold=True, size_hint_y=None, height=dp(35)))

        self.scroll = ScrollView(size_hint=(1, 1))
        self.lista_layout = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.lista_layout.bind(minimum_height=self.lista_layout.setter('height'))
        self.scroll.add_widget(self.lista_layout)
        layout.add_widget(self.scroll)

        btn_volver = Button(text='Volver al Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(45))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def on_enter(self):
        self.lista_layout.clear_widgets()
        if not GlobalData.historial_ventas:
            lbl = Label(text='No hay ventas registradas aún.', font_size=dp(13), color=(0.7,0.7,0.7,1), size_hint_y=None, height=dp(40))
            self.lista_layout.add_widget(lbl)
            return

        for venta in reversed(GlobalData.historial_ventas):
            texto = f"[{venta['hora']}] ({venta['metodo']}) - Total: {venta['total']:.2f} Bs\nProd: {venta['productos']}"
            lbl = Label(text=texto, font_size=dp(12), color=(1,1,1,1), size_hint_y=None, height=dp(50), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            self.lista_layout.add_widget(lbl)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class ResumenScreen(Screen):
    def __init__(self, **kwargs):
        super(ResumenScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        
        with layout.canvas.before:
            Color(0.07, 0.08, 0.11, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Resumen Financiero y Ganancias', font_size=dp(18), bold=True, size_hint_y=None, height=dp(35)))
        
        self.lbl_detalles = Label(text='', font_size=dp(13), color=(1,1,1,1), halign='left', valign='middle')
        self.lbl_detalles.bind(size=self.lbl_detalles.setter('text_size'))
        layout.add_widget(self.lbl_detalles)

        btn_volver = Button(text='Volver al Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(45))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def on_enter(self):
        estado_txt = "Abierta" if GlobalData.caja_abierta else "Cerrada"
        total_gastos = sum(g['monto'] for g in GlobalData.gastos_caja)
        efectivo_en_caja = GlobalData.monto_inicial + GlobalData.total_ventas_efectivo - total_gastos
        total_ventas_generales = GlobalData.total_ventas_efectivo + GlobalData.total_ventas_qr
        
        self.lbl_detalles.text = (
            f"Estado de Caja: {estado_txt}\n\n"
            f"--- CONTROL DE CAJA FÍSICA ---\n"
            f"Monto Inicial: {GlobalData.monto_inicial:.2f} Bs\n"
            f"Ventas en Efectivo: {GlobalData.total_ventas_efectivo:.2f} Bs\n"
            f"Retiros / Gastos menores: -{total_gastos:.2f} Bs\n"
            f"Dinero Físico en Caja: {efectivo_en_caja:.2f} Bs\n\n"
            f"--- VENTAS DIGITALES ---\n"
            f"Ventas por QR / Transf.: {GlobalData.total_ventas_qr:.2f} Bs\n"
            f"Total Ventas Generales: {total_ventas_generales:.2f} Bs\n\n"
            f"--- GANANCIAS NETAS ---\n"
            f"Ganancia Total del Día: {GlobalData.total_ganancias:.2f} Bs"
        )

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name='menu'))
        sm.add_widget(CajaScreen(name='caja'))
        sm.add_widget(InventarioScreen(name='inventario'))
        sm.add_widget(IngresoProductoScreen(name='ingreso'))
        sm.add_widget(VentaScreen(name='venta'))
        sm.add_widget(GastoScreen(name='gasto'))
        sm.add_widget(HistorialScreen(name='historial'))
        sm.add_widget(ResumenScreen(name='resumen'))
        return sm

if __name__ == '__main__':
    MyApp().run()
