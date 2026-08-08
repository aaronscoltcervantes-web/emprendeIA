from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        
        # Layout principal con fondo personalizado
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        
        with layout.canvas.before:
            Color(0.1, 0.1, 0.15, 1) # Fondo oscuro elegante
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=self._update_rect, pos=self._update_rect)

        # Título
        title = Label(
            text='Sistema de Caja\nControl Financiero', 
            font_size=dp(24), 
            halign='center', 
            valign='middle',
            bold=True
        )
        title.bind(size=title.setter('text_size'))
        layout.add_widget(title)

        # Botones de navegación
        btn_apertura = Button(
            text='Registrar Apertura de Caja', 
            background_color=(0.1, 0.6, 0.2, 1),
            font_size=dp(16)
        )
        btn_apertura.bind(on_press=self.ir_apertura)
        layout.add_widget(btn_apertura)

        btn_cierre = Button(
            text='Registrar Cierre de Caja', 
            background_color=(0.8, 0.2, 0.2, 1),
            font_size=dp(16)
        )
        btn_cierre.bind(on_press=self.ir_cierre)
        layout.add_widget(btn_cierre)

        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def ir_apertura(self, instance):
        self.manager.current = 'apertura'

    def ir_cierre(self, instance):
        self.manager.current = 'cierre'


class AperturaScreen(Screen):
    def __init__(self, **kwargs):
        super(AperturaScreen, self).__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(15))
        
        with layout.canvas.before:
            Color(0.12, 0.12, 0.18, 1)
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Apertura de Caja', font_size=dp(22), bold=True, size_hint_y=None, height=dp(50)))

        layout.add_widget(Label(text='Monto Inicial en Bs:', font_size=dp(16), size_hint_y=None, height=dp(30)))
        
        self.input_monto = TextInput(
            text='', 
            hint_text='Ej. 500.00', 
            multiline=False, 
            input_filter='float',
            font_size=dp(18),
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(self.input_monto)

        self.lbl_resultado = Label(text='', font_size=dp(16), color=(0.2, 0.8, 0.3, 1))
        layout.add_widget(self.lbl_resultado)

        btn_guardar = Button(
            text='Guardar Apertura', 
            background_color=(0.1, 0.6, 0.2, 1),
            size_hint_y=None,
            height=dp(50)
        )
        btn_guardar.bind(on_press=self.guardar_apertura)
        layout.add_widget(btn_guardar)

        btn_volver = Button(
            text='Volver al Menú', 
            background_color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(50)
        )
        btn_volver.bind(on_press=self.volver_menu)
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def guardar_apertura(self, instance):
        monto = self.input_monto.text
        if monto:
            self.lbl_resultado.text = f'¡Apertura registrada con éxito: {monto} Bs!'
        else:
            self.lbl_resultado.text = 'Por favor ingrese un monto válido.'

    def volver_menu(self, instance):
        self.lbl_resultado.text = ''
        self.input_monto.text = ''
        self.manager.current = 'menu'


class CierreScreen(Screen):
    def __init__(self, **kwargs):
        super(CierreScreen, self).__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(12))
        
        with layout.canvas.before:
            Color(0.12, 0.12, 0.18, 1)
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=self._update_rect, pos=self._update_rect)

        layout.add_widget(Label(text='Cierre de Caja', font_size=dp(22), bold=True, size_hint_y=None, height=dp(40)))

        layout.add_widget(Label(text='Efectivo Total Contado (Bs):', font_size=dp(15), size_hint_y=None, height=dp(25)))
        self.input_efectivo = TextInput(hint_text='0.00', multiline=False, input_filter='float', size_hint_y=None, height=dp(45))
        layout.add_widget(self.input_efectivo)

        layout.add_widget(Label(text='Ventas por QR / Transferencia (Bs):', font_size=dp(15), size_hint_y=None, height=dp(25)))
        self.input_qr = TextInput(hint_text='0.00', multiline=False, input_filter='float', size_hint_y=None, height=dp(45))
        layout.add_widget(self.input_qr)

        self.lbl_resumen = Label(text='', font_size=dp(15), color=(0.9, 0.9, 0.2, 1), size_hint_y=None, height=dp(40))
        layout.add_widget(self.lbl_resumen)

        btn_procesar = Button(
            text='Calcular y Registrar Cierre', 
            background_color=(0.8, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(50)
        )
        btn_procesar.bind(on_press=self.procesar_cierre)
        layout.add_widget(btn_procesar)

        btn_volver = Button(
            text='Volver al Menú', 
            background_color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(50)
        )
        btn_volver.bind(on_press=self.volver_menu)
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def procesar_cierre(self, instance):
        try:
            efectivo = float(self.input_efectivo.text) if self.input_efectivo.text else 0.0
            qr = float(self.input_qr.text) if self.input_qr.text else 0.0
            total = efectivo + qr
            self.lbl_resumen.text = f'Total General en Caja: {total:.2f} Bs (Efectivo: {efectivo} | QR: {qr})'
        except ValueError:
            self.lbl_resumen.text = 'Ingrese valores numéricos válidos.'

    def volver_menu(self, instance):
        self.lbl_resumen.text = ''
        self.input_efectivo.text = ''
        self.input_qr.text = ''
        self.manager.current = 'menu'


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(AperturaScreen(name='apertura'))
        sm.add_widget(CierreScreen(name='cierre'))
        return sm

if __name__ == '__main__':
    MyApp().run()
