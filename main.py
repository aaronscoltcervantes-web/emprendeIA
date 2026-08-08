from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

class GlobalState:
    # Estado global de la caja para compartir datos entre pantallas
    caja_abierta = False
    monto_inicial = 0.0
    total_ingresos = 0.0
    total_gastos = 0.0

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        with main_layout.canvas.before:
            Color(0.08, 0.09, 0.12, 1) # Fondo oscuro moderno
            self.rect = RoundedRectangle(size=main_layout.size, pos=main_layout.pos, radius=[0])
        main_layout.bind(size=self._update_rect, pos=self._update_rect)

        # Encabezado con Título y Estado
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(90), spacing=dp(5))
        title = Label(text='SISTEMA DE GESTIÓN DE CAJA', font_size=dp(20), bold=True, color=(1, 1, 1, 1))
        self.lbl_estado = Label(text='Estado: CAJA CERRADA', font_size=dp(14), color=(0.9, 0.3, 0.3, 1), bold=True)
        header.add_widget(title)
        header.add_widget(self.lbl_estado)
        main_layout.add_widget(header)

        # Panel de Opciones en Cuadrícula (Grid)
        grid = GridLayout(cols=1, spacing=dp(12), size_hint_y=None, height=dp(320))

        btn_apertura = self.crear_boton('1. Registrar Apertura de Caja', (0.1, 0.5, 0.2, 1), self.ir_apertura)
        btn_cierre = self.crear_boton('2. Registrar Cierre de Caja', (0.7, 0.2, 0.2, 1), self.ir_cierre)
        btn_movimiento = self.crear_boton('3. Registrar Ingreso / Gasto Extra', (0.2, 0.4, 0.7, 1), self.ir_movimiento)
        btn_resumen = self.crear_boton('4. Resumen del Día', (0.4, 0.4, 0.45, 1), self.ir_resumen)

        grid.add_widget(btn_apertura)
        grid.add_widget(btn_cierre)
        grid.add_widget(btn_movimiento)
        grid.add_widget(btn_resumen)

        main_layout.add_widget(grid)
        main_layout.add_widget(Label()) # Espaciador flexible

        self.add_widget(main_layout)

    def on_enter(self):
        # Actualiza el estado visual al volver al menú principal
        if GlobalState.caja_abierta:
            self.lbl_estado.text = f'Estado: CAJA ABIERTA (Inicial: {GlobalState.monto_inicial:.2f} Bs)'
            self.lbl_estado.color = (0.2, 0.8, 0.3, 1)
        else:
            self.lbl_estado.text = 'Estado: CAJA CERRADA'
            self.lbl_estado.color = (0.9, 0.3, 0.3, 1)

    def crear_boton(self, texto, color_fondo, callback):
        btn = Button(
            text=texto,
            font_size=dp(16),
            bold=True,
            background_normal='',
            background_color=color_fondo,
            size_hint_y=None,
            height=dp(60)
        )
        btn.bind(on_press=callback)
        return btn

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def ir_apertura(self, instance): self.manager.current = 'apertura'
    def ir_cierre(self, instance): self.manager.current = 'cierre'
    def ir_movimiento(self, instance): self.manager.current = 'movimiento'
    def ir_resumen(self, instance): self.manager.current = 'resumen'


class AperturaScreen(Screen):
    def __init__(self, **kwargs):
        super(AperturaScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(15))
        
        with layout.canvas.before:
            Color(0.08, 0.09, 0.12, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Apertura de Caja', font_size=dp(22), bold=True, size_hint_y=None, height=dp(40)))
        layout.add_widget(Label(text='Ingrese el monto inicial en efectivo (Bs):', font_size=dp(15), size_hint_y=None, height=dp(30)))
        
        self.input_monto = TextInput(hint_text='0.00', multiline=False, input_filter='float', font_size=dp(18), size_hint_y=None, height=dp(50))
        layout.add_widget(self.input_monto)

        self.lbl_msg = Label(text='', font_size=dp(15), color=(0.2, 0.8, 0.3, 1), size_hint_y=None, height=dp(40))
        layout.add_widget(self.lbl_msg)

        btn_guardar = Button(text='Confirmar Apertura', background_normal='', background_color=(0.1, 0.5, 0.2, 1), size_hint_y=None, height=dp(50), bold=True)
        btn_guardar.bind(on_press=self.guardar)
        layout.add_widget(btn_guardar)

        btn_volver = Button(text='Volver al Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(50))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        layout.add_widget(Label())
        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def guardar(self, instance):
        try:
            monto = float(self.input_monto.text)
            GlobalState.caja_abierta = True
            GlobalState.monto_inicial = monto
            self.lbl_msg.text = '¡Apertura registrada correctamente!'
        except ValueError:
            self.lbl_msg.text = 'Por favor ingrese un número válido.'


class CierreScreen(Screen):
    def __init__(self, **kwargs):
        super(CierreScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(12))
        
        with layout.canvas.before:
            Color(0.08, 0.09, 0.12, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Cierre de Caja', font_size=dp(22), bold=True, size_hint_y=None, height=dp(40)))

        layout.add_widget(Label(text='Efectivo Contado en Caja (Bs):', font_size=dp(14), size_hint_y=None, height=dp(25)))
        self.input_efectivo = TextInput(hint_text='0.00', multiline=False, input_filter='float', size_hint_y=None, height=dp(45))
        layout.add_widget(self.input_efectivo)

        layout.add_widget(Label(text='Ventas por QR / Transferencia (Bs):', font_size=dp(14), size_hint_y=None, height=dp(25)))
        self.input_qr = TextInput(hint_text='0.00', multiline=False, input_filter='float', size_hint_y=None, height=dp(45))
        layout.add_widget(self.input_qr)

        self.lbl_resultado = Label(text='', font_size=dp(14), color=(0.9, 0.9, 0.2, 1), size_hint_y=None, height=dp(60))
        layout.add_widget(self.lbl_resultado)

        btn_procesar = Button(text='Procesar Cierre de Caja', background_normal='', background_color=(0.7, 0.2, 0.2, 1), size_hint_y=None, height=dp(50), bold=True)
        btn_procesar.bind(on_press=self.procesar)
        layout.add_widget(btn_procesar)

        btn_volver = Button(text='Volver al Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(50))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def procesar(self, instance):
        try:
            efectivo = float(self.input_efectivo.text) if self.input_efectivo.text else 0.0
            qr = float(self.input_qr.text) if self.input_qr.text else 0.0
            total_final = efectivo + qr
            total_esperado = GlobalState.monto_inicial + GlobalState.total_ingresos - GlobalState.total_gastos
            
            GlobalState.caja_abierta = False # Cierra la caja
            self.lbl_resultado.text = f'Inicial: {GlobalState.monto_inicial:.2f} | Contado: {total_final:.2f} Bs\n¡Caja cerrada con éxito!'
        except ValueError:
            self.lbl_resultado.text = 'Ingrese valores numéricos válidos.'


class MovimientoScreen(Screen):
    def __init__(self, **kwargs):
        super(MovimientoScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(15))
        
        with layout.canvas.before:
            Color(0.08, 0.09, 0.12, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Ingresos / Gastos Extras', font_size=dp(22), bold=True, size_hint_y=None, height=dp(40)))
        
        layout.add_widget(Label(text='Monto del Movimiento (Bs):', font_size=dp(14), size_hint_y=None, height=dp(25)))
        self.input_monto = TextInput(hint_text='0.00', multiline=False, input_filter='float', size_hint_y=None, height=dp(45))
        layout.add_widget(self.input_monto)

        self.lbl_msg = Label(text='', font_size=dp(15), color=(0.2, 0.8, 0.3, 1), size_hint_y=None, height=dp(40))
        layout.add_widget(self.lbl_msg)

        btn_ingreso = Button(text='Registrar como Ingreso Extra', background_normal='', background_color=(0.1, 0.5, 0.2, 1), size_hint_y=None, height=dp(45))
        btn_ingreso.bind(on_press=lambda x: self.registrar('ingreso'))
        layout.add_widget(btn_ingreso)

        btn_gasto = Button(text='Registrar como Gasto / Retiro', background_normal='', background_color=(0.8, 0.3, 0.2, 1), size_hint_y=None, height=dp(45))
        btn_gasto.bind(on_press=lambda x: self.registrar('gasto'))
        layout.add_widget(btn_gasto)

        btn_volver = Button(text='Volver al Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(50))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        layout.add_widget(Label())
        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def registrar(self, tipo):
        try:
            monto = float(self.input_monto.text)
            if tipo == 'ingreso':
                GlobalState.total_ingresos += monto
                self.lbl_msg.text = f'Ingreso de {monto} Bs registrado.'
            else:
                GlobalState.total_gastos += monto
                self.lbl_msg.text = f'Gasto de {monto} Bs registrado.'
        except ValueError:
            self.lbl_msg.text = 'Ingrese un monto válido.'


class ResumenScreen(Screen):
    def __init__(self, **kwargs):
        super(ResumenScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(15))
        
        with layout.canvas.before:
            Color(0.08, 0.09, 0.12, 1)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[0])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Resumen del Día', font_size=dp(22), bold=True, size_hint_y=None, height=dp(40)))
        
        self.lbl_detalle = Label(text='', font_size=dp(15), color=(1, 1, 1, 1), halign='left', valign='middle')
        self.lbl_detalle.bind(size=self.lbl_detalle.setter('text_size'))
        layout.add_widget(self.lbl_detalle)

        btn_volver = Button(text='Volver al Menú', background_normal='', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=dp(50))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def on_enter(self):
        estado_txt = "Abierta" if GlobalState.caja_abierta else "Cerrada"
        self.lbl_detalle.text = (
            f"Estado actual: {estado_txt}\n\n"
            f"Monto Inicial: {GlobalState.monto_inicial:.2f} Bs\n"
            f"Ingresos Extras: {GlobalState.total_ingresos:.2f} Bs\n"
            f"Gastos / Retiros: {GlobalState.total_gastos:.2f} Bs\n\n"
            f"Efectivo Teórico en Caja:\n"
            f"{(GlobalState.monto_inicial + GlobalState.total_ingresos - GlobalState.total_gastos):.2f} Bs"
        )

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name='menu'))
        sm.add_widget(AperturaScreen(name='apertura'))
        sm.add_widget(CierreScreen(name='cierre'))
        sm.add_widget(MovimientoScreen(name='movimiento'))
        sm.add_widget(ResumenScreen(name='resumen'))
        return sm

if __name__ == '__main__':
    MyApp().run()
