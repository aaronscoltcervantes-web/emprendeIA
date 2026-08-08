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

class GlobalData:
    caja_abierta = False
    monto_inicial = 0.0
    total_ventas_dia = 0.0
    # Inventario inicial de ejemplo: [{'nombre': str, 'stock': int, 'costo': float, 'precio': float}]
    inventario = [
        {"nombre": "Coca Cola 2L", "stock": 15, "costo": 10.0, "precio": 15.0},
        {"nombre": "Galletas Club Social", "stock": 30, "costo": 2.5, "precio": 4.0},
        {"nombre": "Agua Mineral 500ml", "stock": 20, "costo": 3.0, "precio": 5.0}
    ]
    carrito = []

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        with layout.canvas.before:
            Color(0.07, 0.08, 0.11, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        # Header
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), spacing=dp(5))
        header.add_widget(Label(text='SISTEMA COMERCIAL PRO', font_size=dp(22), bold=True, color=(1,1,1,1)))
        self.lbl_estado = Label(text='Estado de Caja: CERRADA', font_size=dp(14), color=(0.9, 0.3, 0.3, 1), bold=True)
        header.add_widget(self.lbl_estado)
        layout.add_widget(header)

        # Menú de Opciones
        grid = GridLayout(cols=1, spacing=dp(12), size_hint_y=None, height=dp(380))
        grid.add_widget(self.crear_Boton('1. Control de Caja (Apertura / Cierre)', (0.15, 0.5, 0.25, 1), lambda x: setattr(self.manager, 'current', 'caja')))
        grid.add_widget(self.crear_Boton('2. Ver Inventario y Stock', (0.2, 0.4, 0.6, 1), lambda x: setattr(self.manager, 'current', 'inventario')))
        grid.add_widget(self.crear_Boton('3. Ingresar Producto / Compras', (0.7, 0.4, 0.1, 1), lambda x: setattr(self.manager, 'current', 'ingreso')))
        grid.add_widget(self.crear_Boton('4. Realizar Venta (Búsqueda Rápida)', (0.8, 0.2, 0.2, 1), lambda x: setattr(self.manager, 'current', 'venta')))
        grid.add_widget(self.crear_Boton('5. Resumen de Ventas y Caja', (0.35, 0.35, 0.4, 1), lambda x: setattr(self.manager, 'current', 'resumen')))
        
        layout.add_widget(grid)
        layout.add_widget(Label())
        self.add_widget(layout)

    def on_enter(self):
        if GlobalData.caja_abierta:
            self.lbl_estado.text = f'Estado de Caja: ABIERTA (Inicial: {GlobalData.monto_inicial:.2f} Bs)'
            self.lbl_estado.color = (0.2, 0.8, 0.3, 1)
        else:
            self.lbl_estado.text = 'Estado de Caja: CERRADA'
            self.lbl_estado.color = (0.9, 0.3, 0.3, 1)

    def crear_Boton(self, texto, color, callback):
        btn = Button(text=texto, font_size=dp(15), bold=True, background_normal='', background_color=color, size_hint_y=None, height=dp(60))
        btn.bind(on_press=callback)
        return btn

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class CajaScreen(Screen):
    def __init__(self, **kwargs):
        super(CajaScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(15))
        
        with layout.canvas.before:
            Color(0.07, 0.08, 0.11, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Módulo de Caja (Apertura / Cierre)', font_size=dp(20), bold=True, size_hint_y=None, height=dp(40)))
        
        self.lbl_info_estado = Label(text='', font_size=dp(15), color=(0.9, 0.9, 0.2, 1), size_hint_y=None, height=dp(30))
        layout.add_widget(self.lbl_info_estado)

        layout.add_widget(Label(text='Monto en Efectivo (Bs):', font_size=dp(14), size_hint_y=None, height=dp(25)))
        self.input_monto = TextInput(hint_text='0.00', multiline=False, input_filter='float', font_size=dp(18), size_hint_y=None, height=dp(45))
        layout.add_widget(self.input_monto)

        self.lbl_msg = Label(text='', font_size=dp(14), color=(0.2, 0.8, 0.3, 1), size_hint_y=None, height=dp(40))
        layout.add_widget(self.lbl_msg)

        self.btn_accion = Button(text='', font_size=dp(16), bold=True, background_normal='', size_hint_y=None, height=dp(50))
        self.btn_accion.bind(on_press=self.ejecutar_accion)
        layout.add_widget(self.btn_accion)

        btn_volver = Button(text='Volver al Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(50))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        layout.add_widget(Label())
        self.add_widget(layout)

    def on_enter(self):
        self.lbl_msg.text = ''
        self.input_monto.text = ''
        if not GlobalData.caja_abierta:
            self.lbl_info_estado.text = 'La caja se encuentra CERRADA. Ingrese el monto para abrir.'
            self.btn_accion.text = 'Registrar Apertura de Caja'
            self.btn_accion.background_color = (0.15, 0.5, 0.25, 1)
        else:
            self.lbl_info_estado.text = f'Caja Abierta. Monto Inicial: {GlobalData.monto_inicial} Bs. Ingrese total para cierre.'
            self.btn_accion.text = 'Registrar Cierre de Caja'
            self.btn_accion.background_color = (0.8, 0.2, 0.2, 1)

    def ejecutar_accion(self, instance):
        try:
            monto = float(self.input_monto.text) if self.input_monto.text else 0.0
            if not GlobalData.caja_abierta:
                GlobalData.caja_abierta = True
                GlobalData.monto_inicial = monto
                self.lbl_msg.text = f'¡Apertura exitosa con {monto:.2f} Bs!'
                self.on_enter()
            else:
                total_en_caja = GlobalData.monto_inicial + GlobalData.total_ventas_dia
                diferencia = monto - total_en_caja
                GlobalData.caja_abierta = False
                self.lbl_msg.text = f'Cierre exitoso. Contado: {monto} Bs. Diferencia: {diferencia:.2f} Bs'
                self.on_enter()
        except ValueError:
            self.lbl_msg.text = 'Ingrese un valor numérico válido.'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class InventarioScreen(Screen):
    def __init__(self, **kwargs):
        super(InventarioScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        with layout.canvas.before:
            Color(0.07, 0.08, 0.11, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Inventario de Productos', font_size=dp(20), bold=True, size_hint_y=None, height=dp(40)))

        self.scroll = ScrollView(size_hint=(1, 1))
        self.lista_layout = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.lista_layout.bind(minimum_height=self.lista_layout.setter('height'))
        self.scroll.add_widget(self.lista_layout)
        layout.add_widget(self.scroll)

        btn_volver = Button(text='Volver al Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(50))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def on_enter(self):
        self.lista_layout.clear_widgets()
        for prod in GlobalData.inventario:
            texto = f"{prod['nombre']} | Stock: {prod['stock']} | Compra: {prod['costo']} Bs | Venta: {prod['precio']} Bs"
            lbl = Label(text=texto, font_size=dp(14), color=(1,1,1,1), size_hint_y=None, height=dp(45))
            self.lista_layout.add_widget(lbl)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class IngresoProductoScreen(Screen):
    def __init__(self, **kwargs):
        super(IngresoProductoScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        with layout.canvas.before:
            Color(0.07, 0.08, 0.11, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Ingreso / Registro de Producto', font_size=dp(20), bold=True, size_hint_y=None, height=dp(40)))

        layout.add_widget(Label(text='Nombre del Producto:', font_size=dp(13), size_hint_y=None, height=dp(20)))
        self.input_nombre = TextInput(hint_text='Ej. Arroz 1kg', multiline=False, size_hint_y=None, height=dp(40))
        layout.add_widget(self.input_nombre)

        layout.add_widget(Label(text='Cantidad a ingresar (Stock):', font_size=dp(13), size_hint_y=None, height=dp(20)))
        self.input_stock = TextInput(hint_text='0', multiline=False, input_filter='int', size_hint_y=None, height=dp(40))
        layout.add_widget(self.input_stock)

        layout.add_widget(Label(text='Costo de Compra (Bs):', font_size=dp(13), size_hint_y=None, height=dp(20)))
        self.input_costo = TextInput(hint_text='0.00', multiline=False, input_filter='float', size_hint_y=None, height=dp(40))
        layout.add_widget(self.input_costo)

        layout.add_widget(Label(text='Costo / Precio de Venta (Bs):', font_size=dp(13), size_hint_y=None, height=dp(20)))
        self.input_precio = TextInput(hint_text='0.00', multiline=False, input_filter='float', size_hint_y=None, height=dp(40))
        layout.add_widget(self.input_precio)

        self.lbl_msg = Label(text='', font_size=dp(14), color=(0.2, 0.8, 0.3, 1), size_hint_y=None, height=dp(30))
        layout.add_widget(self.lbl_msg)

        btn_guardar = Button(text='Guardar Producto', background_normal='', background_color=(0.7, 0.4, 0.1, 1), size_hint_y=None, height=dp(45), bold=True)
        btn_guardar.bind(on_press=self.guardar_producto)
        layout.add_widget(btn_guardar)

        btn_volver = Button(text='Volver al Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(45))
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

            # Verificar si ya existe para sumar stock o agregarlo nuevo
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
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        with layout.canvas.before:
            Color(0.07, 0.08, 0.11, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Punto de Venta (Búsqueda por letra)', font_size=dp(18), bold=True, size_hint_y=None, height=dp(35)))

        # Buscador inteligente en tiempo real
        self.input_buscar = TextInput(hint_text='Escriba una letra o nombre para buscar...', multiline=False, size_hint_y=None, height=dp(45), font_size=dp(16))
        self.input_buscar.bind(text=self.filtrar_productos)
        layout.add_widget(self.input_buscar)

        # Resultados de búsqueda
        self.scroll_res = ScrollView(size_hint=(1, 0.4))
        self.lista_resultados = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.lista_resultados.bind(minimum_height=self.lista_resultados.setter('height'))
        self.scroll_res.add_widget(self.lista_resultados)
        layout.add_widget(self.scroll_res)

        layout.add_widget(Label(text='Productos Seleccionados (Carrito):', font_size=dp(14), bold=True, size_hint_y=None, height=dp(25)))
        
        self.scroll_car = ScrollView(size_hint=(1, 0.3))
        self.lista_carrito = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.lista_carrito.bind(minimum_height=self.lista_carrito.setter('height'))
        self.scroll_car.add_widget(self.lista_carrito)
        layout.add_widget(self.scroll_car)

        self.lbl_total = Label(text='Total Venta: 0.00 Bs', font_size=dp(16), bold=True, color=(0.2, 0.8, 0.3, 1), size_hint_y=None, height=dp(30))
        layout.add_widget(self.lbl_total)

        # Botones inferiores
        botones_layout = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        btn_cobrar = Button(text='Cobrar / Finalizar', background_normal='', background_color=(0.2, 0.7, 0.3, 1), bold=True)
        btn_cobrar.bind(on_press=self.cobrar)
        btn_volver = Button(text='Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        
        botones_layout.add_widget(btn_cobrar)
        botones_layout.add_widget(btn_volver)
        layout.add_widget(botones_layout)

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
                texto_btn = f"{prod['nombre']} - Stock: {prod['stock']} - {prod['precio']} Bs"
                btn = Button(text=texto_btn, size_hint_y=None, height=dp(40), background_normal='', background_color=(0.2, 0.3, 0.4, 1))
                btn.bind(on_press=lambda x, p=prod: self.agregar_al_carrito(p))
                self.lista_resultados.add_widget(btn)

    def agregar_al_carrito(self, producto):
        if producto['stock'] > 0:
            # Buscar si ya está en carrito
            en_carrito = next((item for item in GlobalData.carrito if item['nombre'] == producto['nombre']), None)
            if en_carrito:
                en_carrito['cantidad'] += 1
            else:
                GlobalData.carrito.append({'nombre': producto['nombre'], 'precio': producto['precio'], 'cantidad': 1})
            producto['stock'] -= 1
            self.actualizar_carrito_vista()
            self.filtrar_productos(None, self.input_buscar.text)

    def actualizar_carrito_vista(self):
        self.lista_carrito.clear_widgets()
        total = 0.0
        for item in GlobalData.carrito:
            sub = item['precio'] * item['cantidad']
            total += sub
            lbl = Label(text=f"{item['nombre']} x{item['cantidad']} = {sub:.2f} Bs", font_size=dp(13), size_hint_y=None, height=dp(30), color=(1,1,1,1))
            self.lista_carrito.add_widget(lbl)
        self.lbl_total.text = f'Total Venta: {total:.2f} Bs'

    def cobrar(self, instance):
        if not GlobalData.carrito:
            return
        total_venta = sum(i['precio'] * i['cantidad'] for i in GlobalData.carrito)
        GlobalData.total_ventas_dia += total_venta
        GlobalData.carrito = []
        self.actualizar_carrito_vista()
        self.lbl_total.text = '¡Venta cobrada con éxito! Total: 0.00 Bs'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class ResumenScreen(Screen):
    def __init__(self, **kwargs):
        super(ResumenScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(15))
        
        with layout.canvas.before:
            Color(0.07, 0.08, 0.11, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Resumen General del Día', font_size=dp(20), bold=True, size_hint_y=None, height=dp(40)))
        
        self.lbl_detalles = Label(text='', font_size=dp(15), color=(1,1,1,1), halign='left', valign='middle')
        self.lbl_detalles.bind(size=self.lbl_detalles.setter('text_size'))
        layout.add_widget(self.lbl_detalles)

        btn_volver = Button(text='Volver al Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(50))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def on_enter(self):
        estado_txt = "Abierta" if GlobalData.caja_abierta else "Cerrada"
        self.lbl_detalles.text = (
            f"Estado de Caja: {estado_txt}\n\n"
            f"Monto Inicial en Caja: {GlobalData.monto_inicial:.2f} Bs\n"
            f"Total Ventas del Día: {GlobalData.total_ventas_dia:.2f} Bs\n\n"
            f"Efectivo Total Teórico:\n"
            f"{(GlobalData.monto_inicial + GlobalData.total_ventas_dia):.2f} Bs"
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
        sm.add_widget(ResumenScreen(name='resumen'))
        return sm

if __name__ == '__main__':
    MyApp().run()
