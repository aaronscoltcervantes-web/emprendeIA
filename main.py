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
from kivy.graphics import Color, RoundedRectangle, Line
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

class RoundedCard(BoxLayout):
    def __init__(self, bg_color=(0.12, 0.13, 0.16, 1), radius=[dp(12)], **kwargs):
        super(RoundedCard, self).__init__(**kwargs)
        self.bg_color = bg_color
        self.radius_val = radius
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=self.radius_val)
        self.bind(size=self._update_canvas, pos=self._update_canvas)

    def _update_canvas(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class BottomNavBar(BoxLayout):
    def __init__(self, screen_manager, **kwargs):
        super(BottomNavBar, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(65)
        self.sm = screen_manager
        
        with self.canvas.before:
            Color(0.09, 0.10, 0.13, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[0])
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.add_nav_button('Caja', 'caja')
        self.add_nav_button('Venta', 'venta')
        self.add_nav_button('Inventario', 'inventario')
        self.add_nav_button('Resumen', 'resumen')

    def add_nav_button(self, text, screen_name):
        btn = Button(
            text=text,
            font_size=dp(12),
            bold=True,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(0.7, 0.7, 0.8, 1)
        )
        btn.bind(on_press=lambda x: setattr(self.sm, 'current', screen_name))
        self.add_widget(btn)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super(BaseScreen, self).__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical')
        with self.main_layout.canvas.before:
            Color(0.06, 0.07, 0.09, 1)
            self.rect = RoundedRectangle(size=self.main_layout.size, pos=self.main_layout.pos, radius=[0])
        self.main_layout.bind(size=self._update_rect, pos=self._update_rect)
        self.content_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12))
        self.main_layout.add_widget(self.content_layout)
        self.add_widget(self.main_layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class CajaScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(CajaScreen, self).__init__(**kwargs)
        
        self.content_layout.add_widget(Label(text='Control de Caja', font_size=dp(18), bold=True, size_hint_y=None, height=dp(30), color=(1,1,1,1)))

        # Input Card Estilo Imagen
        self.input_monto = TextInput(
            hint_text='Monto Inicial para Apertura (Bs)', 
            multiline=False, 
            input_filter='float', 
            font_size=dp(14), 
            size_hint_y=None, 
            height=dp(50),
            background_color=(0.12, 0.13, 0.16, 1),
            foreground_color=(1,1,1,1),
            cursor_color=(1,1,1,1),
            padding=[dp(15), dp(15)]
        )
        self.content_layout.add_widget(self.input_monto)

        self.btn_accion = Button(
            text='ABRIR CAJA', 
            font_size=dp(15), 
            bold=True, 
            background_normal='', 
            background_color=(0.18, 0.7, 0.35, 1), 
            size_hint_y=None, 
            height=dp(50)
        )
        self.btn_accion.bind(on_press=self.ejecutar_accion)
        self.content_layout.add_widget(self.btn_accion)

        # Tarjeta de Estado (Idéntica a la imagen de referencia)
        self.card_estado = RoundedCard(orientation='vertical', padding=dp(15), spacing=dp(8), size_hint_y=None, height=dp(130), bg_color=(0.12, 0.13, 0.16, 1))
        self.lbl_estado = Label(text='Estado: Caja Cerrada', font_size=dp(15), bold=True, color=(1,1,1,1), halign='left', valgin='middle')
        self.lbl_estado.bind(size=self.lbl_estado.setter('text_size'))
        self.card_estado.add_widget(self.lbl_estado)

        self.lbl_fondo = Label(text='Fondo Actual: 0.00 Bs', font_size=dp(14), color=(0.8, 0.8, 0.8, 1), halign='left', valgin='middle')
        self.lbl_fondo.bind(size=self.lbl_fondo.setter('text_size'))
        self.card_estado.add_widget(self.lbl_fondo)
        
        self.content_layout.add_widget(self.card_estado)

        self.lbl_msg = Label(text='', font_size=dp(13), color=(0.2, 0.8, 0.3, 1), size_hint_y=None, height=dp(30))
        self.content_layout.add_widget(self.lbl_msg)
        
        self.content_layout.add_widget(Label())

    def on_enter(self):
        self.lbl_msg.text = ''
        self.input_monto.text = ''
        if not GlobalData.caja_abierta:
            self.lbl_estado.text = 'Estado: Caja Cerrada'
            self.lbl_fondo.text = 'Fondo Actual: 0.00 Bs'
            self.input_monto.hint_text = 'Monto Inicial para Apertura (Bs)'
            self.btn_accion.text = 'ABRIR CAJA'
            self.btn_accion.background_color = (0.18, 0.7, 0.35, 1)
        else:
            total_gastos = sum(g['monto'] for g in GlobalData.gastos_caja)
            efectivo_esperado = GlobalData.monto_inicial + GlobalData.total_ventas_efectivo - total_gastos
            self.lbl_estado.text = 'Estado: Caja Abierta'
            self.lbl_fondo.text = f'Efectivo en Caja: {efectivo_esperado:.2f} Bs'
            self.input_monto.hint_text = 'Conteo exacto para Cierre (Bs)'
            self.btn_accion.text = 'CERRAR CAJA'
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
                self.lbl_msg.text = '¡Caja abierta correctamente!'
                self.on_enter()
            else:
                total_gastos = sum(g['monto'] for g in GlobalData.gastos_caja)
                efectivo_esperado = GlobalData.monto_inicial + GlobalData.total_ventas_efectivo - total_gastos
                diferencia = monto - efectivo_esperado
                GlobalData.caja_abierta = False
                guardar_datos()
                dif_txt = f" (Dif: {diferencia:+.2f} Bs)"
                self.lbl_msg.text = f'Cierre exitoso. Contado: {monto}{dif_txt}'
                self.on_enter()
        except ValueError:
            self.lbl_msg.text = 'Ingrese un valor numérico válido.'

class VentaScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(VentaScreen, self).__init__(**kwargs)
        self.content_layout.add_widget(Label(text='Punto de Venta Rápido', font_size=dp(18), bold=True, size_hint_y=None, height=dp(30), color=(1,1,1,1)))

        self.input_buscar = TextInput(hint_text='Buscar producto...', multiline=False, size_hint_y=None, height=dp(40), font_size=dp(13))
        self.input_buscar.bind(text=self.filtrar_productos)
        self.content_layout.add_widget(self.input_buscar)

        self.scroll_res = ScrollView(size_hint=(1, 0.25))
        self.lista_resultados = GridLayout(cols=1, spacing=dp(4), size_hint_y=None)
        self.lista_resultados.bind(minimum_height=self.lista_resultados.setter('height'))
        self.scroll_res.add_widget(self.lista_resultados)
        self.content_layout.add_widget(self.scroll_res)

        self.content_layout.add_widget(Label(text='Carrito de Compras:', font_size=dp(13), bold=True, size_hint_y=None, height=dp(20), color=(1,1,1,1)))
        
        self.scroll_car = ScrollView(size_hint=(1, 0.28))
        self.lista_carrito = GridLayout(cols=1, spacing=dp(4), size_hint_y=None)
        self.lista_carrito.bind(minimum_height=self.lista_carrito.setter('height'))
        self.scroll_car.add_widget(self.lista_carrito)
        self.content_layout.add_widget(self.scroll_car)

        self.lbl_total = Label(text='Total: 0.00 Bs', font_size=dp(15), bold=True, color=(0.2, 0.8, 0.3, 1), size_hint_y=None, height=dp(25))
        self.content_layout.add_widget(self.lbl_total)

        botones_pago = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
        btn_efectivo = Button(text='Cobrar Efectivo', background_normal='', background_color=(0.18, 0.7, 0.35, 1), bold=True)
        btn_efectivo.bind(on_press=lambda x: self.cobrar('efectivo'))
        
        btn_qr = Button(text='Cobrar QR', background_normal='', background_color=(0.2, 0.4, 0.7, 1), bold=True)
        btn_qr.bind(on_press=lambda x: self.cobrar('qr'))
        
        botones_pago.add_widget(btn_efectivo)
        botones_pago.add_widget(btn_qr)
        self.content_layout.add_widget(botones_pago)

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
                btn = Button(text=f"{prod['nombre']} | Stock: {prod['stock']}{alerta} | {prod['precio']} Bs", size_hint_y=None, height=dp(35), background_normal='', background_color=(0.2, 0.25, 0.35, 1))
                btn.bind(on_press=lambda x, p=prod: self.agregar_al_carrito(p))
                self.lista_resultados.add_widget(btn)

    def agregar_al_carrito(self, producto):
        if producto['stock'] > 0:
            en_carrito = next((item for item in GlobalData.carrito if item['nombre'] == producto['nombre']), None)
            if en_carrito:
                en_carrito['cantidad'] += 1
            else:
                GlobalData.carrito.append({'nombre': producto['nombre'], 'precio': producto['precio'], 'costo': producto['costo'], 'cantidad': 1})
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
        self.lbl_total.text = f'Total: {total:.2f} Bs'

    def cobrar(self, metodo):
        if not GlobalData.carrito or not GlobalData.caja_abierta:
            return
        total_venta = sum(i['precio'] * i['cantidad'] for i in GlobalData.carrito)
        ganancia_venta = sum((i['precio'] - i['costo']) * i['cantidad'] for i in GlobalData.carrito)
        detalle = ", ".join([f"{i['nombre']} x{i['cantidad']}" for i in GlobalData.carrito])

        if metodo == 'efectivo':
            GlobalData.total_ventas_efectivo += total_venta
        else:
            GlobalData.total_ventas_qr += total_venta
        GlobalData.total_ganancias += ganancia_venta

        GlobalData.historial_ventas.append({
            "hora": datetime.now().strftime("%H:%M:%S"),
            "metodo": metodo.upper(),
            "total": total_venta,
            "productos": detalle
        })
        GlobalData.carrito = []
        guardar_datos()
        self.actualizar_carrito_vista()
        self.lbl_total.text = f'¡Cobrado con éxito!'

class InventarioScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(InventarioScreen, self).__init__(**kwargs)
        self.content_layout.add_widget(Label(text='Inventario y Stock', font_size=dp(18), bold=True, size_hint_y=None, height=dp(30), color=(1,1,1,1)))

        self.scroll = ScrollView(size_hint=(1, 1))
        self.lista_layout = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.lista_layout.bind(minimum_height=self.lista_layout.setter('height'))
        self.scroll.add_widget(self.lista_layout)
        self.content_layout.add_widget(self.scroll)

        btn_agregar = Button(text='+ Nuevo Producto / Stock', background_normal='', background_color=(0.7, 0.4, 0.1, 1), size_hint_y=None, height=dp(42), bold=True)
        btn_agregar.bind(on_press=lambda x: setattr(self.manager, 'current', 'ingreso'))
        self.content_layout.add_widget(btn_agregar)

    def on_enter(self):
        self.lista_layout.clear_widgets()
        for prod in GlobalData.inventario:
            alerta = " [¡STOCK BAJO!]" if prod['stock'] <= 5 else ""
            color_texto = (1, 0.4, 0.4, 1) if prod['stock'] <= 5 else (1, 1, 1, 1)
            texto = f"{prod['nombre']} | Stock: {prod['stock']}{alerta}\nCompra: {prod['costo']} Bs | Venta: {prod['precio']} Bs"
            lbl = Label(text=texto, font_size=dp(12), color=color_texto, size_hint_y=None, height=dp(45), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            self.lista_layout.add_widget(lbl)

class IngresoProductoScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(IngresoProductoScreen, self).__init__(**kwargs)
        self.content_layout.add_widget(Label(text='Registrar / Actualizar Producto', font_size=dp(18), bold=True, size_hint_y=None, height=dp(30), color=(1,1,1,1)))

        self.input_nombre = TextInput(hint_text='Nombre del producto', multiline=False, size_hint_y=None, height=dp(40))
        self.input_stock = TextInput(hint_text='Cantidad (Stock)', multiline=False, input_filter='int', size_hint_y=None, height=dp(40))
        self.input_costo = TextInput(hint_text='Costo de compra (Bs)', multiline=False, input_filter='float', size_hint_y=None, height=dp(40))
        self.input_precio = TextInput(hint_text='Precio de venta (Bs)', multiline=False, input_filter='float', size_hint_y=None, height=dp(40))

        self.content_layout.add_widget(self.input_nombre)
        self.content_layout.add_widget(self.input_stock)
        self.content_layout.add_widget(self.input_costo)
        self.content_layout.add_widget(self.input_precio)

        self.lbl_msg = Label(text='', font_size=dp(13), color=(0.2, 0.8, 0.3, 1), size_hint_y=None, height=dp(25))
        self.content_layout.add_widget(self.lbl_msg)

        btn_guardar = Button(text='Guardar', background_normal='', background_color=(0.18, 0.7, 0.35, 1), size_hint_y=None, height=dp(45), bold=True)
        btn_guardar.bind(on_press=self.guardar_producto)
        self.content_layout.add_widget(btn_guardar)

        btn_volver = Button(text='Volver al Inventario', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(40))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'inventario'))
        self.content_layout.add_widget(btn_volver)

    def guardar_producto(self, instance):
        try:
            nombre = self.input_nombre.text.strip()
            stock = int(self.input_stock.text)
            costo = float(self.input_costo.text)
            precio = float(self.input_precio.text)
            if not nombre: return
            
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
            self.lbl_msg.text = '¡Guardado con éxito!'
            self.input_nombre.text = ''
            self.input_stock.text = ''
            self.input_costo.text = ''
            self.input_precio.text = ''
        except ValueError:
            self.lbl_msg.text = 'Verifique los campos numéricos.'

class ResumenScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(ResumenScreen, self).__init__(**kwargs)
        self.content_layout.add_widget(Label(text='Resumen y Caja Chica', font_size=dp(18), bold=True, size_hint_y=None, height=dp(30), color=(1,1,1,1)))

        self.scroll = ScrollView(size_hint=(1, 1))
        self.lbl_detalles = Label(text='', font_size=dp(13), color=(1,1,1,1), halign='left', valgin='top', size_hint_y=None)
        self.lbl_detalles.bind(size=self.lbl_detalles.setter('text_size'))
        self.scroll.add_widget(self.lbl_detalles)
        self.content_layout.add_widget(self.scroll)

        btn_gasto = Button(text='Registrar Gasto / Retiro', background_normal='', background_color=(0.8, 0.3, 0.2, 1), size_hint_y=None, height=dp(42), bold=True)
        btn_gasto.bind(on_press=lambda x: setattr(self.manager, 'current', 'gasto'))
        self.content_layout.add_widget(btn_gasto)

    def on_enter(self):
        estado_txt = "Abierta" if GlobalData.caja_abierta else "Cerrada"
        total_gastos = sum(g['monto'] for g in GlobalData.gastos_caja)
        efectivo_en_caja = GlobalData.monto_inicial + GlobalData.total_ventas_efectivo - total_gastos
        total_ventas = GlobalData.total_ventas_efectivo + GlobalData.total_ventas_qr

        self.lbl_detalles.text = (
            f"Estado: {estado_txt}\n\n"
            f"[EFECTIVO FÍSICO]\n"
            f"• Inicial: {GlobalData.monto_inicial:.2f} Bs\n"
            f"• Ventas Efectivo: {GlobalData.total_ventas_efectivo:.2f} Bs\n"
            f"• Retiros / Gastos: -{total_gastos:.2f} Bs\n"
            f"• Total en Caja: {efectivo_en_caja:.2f} Bs\n\n"
            f"[VENTAS DIGITALES]\n"
            f"• QR / Transferencia: {GlobalData.total_ventas_qr:.2f} Bs\n"
            f"• Total General: {total_ventas:.2f} Bs\n\n"
            f"[GANANCIAS NETAS]\n"
            f"• Ganancia del día: {GlobalData.total_ganancias:.2f} Bs"
        )
        self.lbl_detalles.height = max(dp(300), self.lbl_detalles.texture_size[1])

class GastoScreen(BaseScreen):
    def __init__(self, **kwargs):
        super(GastoScreen, self).__init__(**kwargs)
        self.content_layout.add_widget(Label(text='Registrar Gasto / Retiro', font_size=dp(18), bold=True, size_hint_y=None, height=dp(30), color=(1,1,1,1)))

        self.input_motivo = TextInput(hint_text='Motivo (ej. Cambio, Delivery)', multiline=False, size_hint_y=None, height=dp(45))
        self.input_monto = TextInput(hint_text='Monto (Bs)', multiline=False, input_filter='float', size_hint_y=None, height=dp(45))
        
        self.content_layout.add_widget(self.input_motivo)
        self.content_layout.add_widget(self.input_monto)

        self.lbl_msg = Label(text='', font_size=dp(13), color=(0.2, 0.8, 0.3, 1), size_hint_y=None, height=dp(30))
        self.content_layout.add_widget(self.lbl_msg)

        btn_reg = Button(text='Registrar Retiro', background_normal='', background_color=(0.8, 0.3, 0.2, 1), size_hint_y=None, height=dp(45), bold=True)
        btn_reg.bind(on_press=self.registrar)
        self.content_layout.add_widget(btn_reg)

        btn_volver = Button(text='Volver al Resumen', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(40))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'resumen'))
        self.content_layout.add_widget(btn_volver)
        
        self.content_layout.add_widget(Label())

    def registrar(self, instance):
        try:
            motivo = self.input_motivo.text.strip()
            monto = float(self.input_monto.text) if self.input_monto.text else 0.0
            if not motivo or monto <= 0: return
            
            GlobalData.gastos_caja.append({"motivo": motivo, "monto": monto})
            guardar_datos()
            self.lbl_msg.text = '¡Gasto registrado con éxito!'
            self.input_motivo.text = ''
            self.input_monto.text = ''
        except ValueError:
            self.lbl_msg.text = 'Verifique los datos.'

class MainApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical')
        sm = ScreenManager()
        
        sm.add_widget(CajaScreen(name='caja'))
        sm.add_widget(VentaScreen(name='venta'))
        sm.add_widget(InventarioScreen(name='inventario'))
        sm.add_widget(IngresoProductoScreen(name='ingreso'))
        sm.add_widget(ResumenScreen(name='resumen'))
        sm.add_widget(GastoScreen(name='gasto'))

        nav_bar = BottomNavBar(sm)
        
        root.add_widget(sm)
        root.add_widget(nav_bar)
        return root

if __name__ == '__main__':
    MainApp().run()
