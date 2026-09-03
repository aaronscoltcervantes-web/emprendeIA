import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp

DATA_FILE = "data.json"

def inicializar_datos():
    """Inicializa el archivo de datos JSON si no existe en el entorno local."""
    if not os.path.exists(DATA_FILE):
        datos_iniciales = {
            "presupuesto_inicial": 1000.0,
            "saldo_actual": 1000.0,
            "gastos": []
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(datos_iniciales, f, indent=4, ensure_ascii=False)

class GestorSobranteApp(App):
    def build(self):
        self.title = "Control de Dinero Sobrante"
        inicializar_datos()
        self.cargar_datos()

        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Cabecera de saldos
        self.lbl_saldo = Label(
            text=f"Saldo Disponible: {self.saldo_actual:.2f} Bs",
            font_size='22sp',
            size_hint_y=None,
            height=dp(50)
        )
        root.add_widget(self.lbl_saldo)

        # Entrada de categoría
        self.txt_categoria = TextInput(
            hint_text="Categoría (ej. Ocio, Antojos, Salidas)",
            multiline=False,
            size_hint_y=None,
            height=dp(45)
        )
        root.add_widget(self.txt_categoria)

        # Entrada de monto
        self.txt_monto = TextInput(
            hint_text="Monto gastado (Bs)",
            input_filter='float',
            multiline=False,
            size_hint_y=None,
            height=dp(45)
        )
        root.add_widget(self.txt_monto)

        # Botón de registro
        btn_registrar = Button(
            text="Registrar Gasto",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.1, 0.6, 0.4, 1)
        )
        btn_registrar.bind(on_press=self.registrar_gasto)
        root.add_widget(btn_registrar)

        # Mensaje de estado / alertas
        self.lbl_mensaje = Label(text="", font_size='16sp')
        root.add_widget(self.lbl_mensaje)

        return root

    def cargar_datos(self):
        """Carga el saldo y los registros desde el archivo JSON local."""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.presupuesto_inicial = data.get("presupuesto_inicial", 1000.0)
                self.saldo_actual = data.get("saldo_actual", 1000.0)
                self.gastos = data.get("gastos", [])
        else:
            self.presupuesto_inicial = 1000.0
            self.saldo_actual = 1000.0
            self.gastos = []

    def guardar_datos(self):
        """Guarda el estado actual de los datos en el archivo JSON."""
        data = {
            "presupuesto_inicial": self.presupuesto_inicial,
            "saldo_actual": self.saldo_actual,
            "gastos": self.gastos
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def registrar_gasto(self, instance):
        """Procesa y valida el registro de un nuevo gasto contra el excedente."""
        cat = self.txt_categoria.text.strip()
        monto_str = self.txt_monto.text.strip()

        if not cat or not monto_str:
            self.lbl_mensaje.text = "Error: Completa todos los campos."
            return

        try:
            monto = float(monto_str)
        except ValueError:
            self.lbl_mensaje.text = "Error: El monto debe ser un número válido."
            return

        if monto <= 0:
            self.lbl_mensaje.text = "Error: El monto debe ser mayor a cero."
            return

        if monto > self.saldo_actual:
            self.lbl_mensaje.text = "Alerta: ¡El gasto supera tu sobrante disponible!"
            return

        # Actualizar valores
        self.saldo_actual -= monto
        self.gastos.append({"categoria": cat, "monto": monto})
        self.guardar_datos()

        # Actualizar interfaz
        self.lbl_saldo.text = f"Saldo Disponible: {self.saldo_actual:.2f} Bs"
        self.lbl_mensaje.text = f"Gasto de {monto:.2f} Bs registrado en '{cat}'."
        self.txt_categoria.text = ""
        self.txt_monto.text = ""

if __name__ == '__main__':
    GestorSobranteApp().run()
