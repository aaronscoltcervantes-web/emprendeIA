from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class VentasApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.label_titulo = Label(text="Control de Ventas", font_size='24sp')
        layout.add_widget(self.label_titulo)
        
        self.input_producto = TextInput(hint_text="Nombre del producto", multiline=False)
        layout.add_widget(self.input_producto)
        
        self.btn_guardar = Button(text="Guardar Venta", size_hint=(1, 0.3))
        self.btn_guardar.bind(on_press=self.guardar_venta)
        layout.add_widget(self.btn_guardar)
        
        self.label_resultado = Label(text="")
        layout.add_widget(self.label_resultado)
        
        return layout

    def guardar_venta(self, instance):
        producto = self.input_producto.text
        if producto:
            self.label_resultado.text = f"Registrado: {producto}"
            self.input_producto.text = ""

if __name__ == '__main__':
    VentasApp().run()
