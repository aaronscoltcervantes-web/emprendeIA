import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp

DATA_FILE = "data.json"

class GestorSobranteApp(App):
    def build(self):
        self.inicializar_datos()
        
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        # Cabecera de saldos
        self.lbl_saldo = Label(
            text=f"Saldo Disponible: {self.saldo_actual:.2f} Bs",
            font_size='20sp',
            size_hint_y=None,
            height=dp(35),
            bold=True
        )
        root.add_widget(self.lbl_saldo)

        # Aviso de presupuesto bajo
        self.lbl_alerta = Label(
            text="",
            font_size='13sp',
            color=(1, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(25)
        )
        root.add_widget(self.lbl_alerta)

        # Sección para editar el presupuesto inicial / sobrante libre
        layout_presupuesto = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(38))
        self.txt_presupuesto = TextInput(
            text=str(self.presupuesto_inicial),
            hint_text="Sobrante total",
            input_filter='float',
            multiline=False,
            size_hint_x=0.65
        )
        btn_actualizar_presupuesto = Button(
            text="Fijar Sobrante",
            size_hint_x=0.35,
            background_color=(0.2, 0.5, 0.8, 1)
        )
        btn_actualizar_presupuesto.bind(on_press=self.cambiar_presupuesto)
        layout_presupuesto.add_widget(self.txt_presupuesto)
        layout_presupuesto.add_widget(btn_actualizar_presupuesto)
        root.add_widget(layout_presupuesto)

        # Entradas de categoría y monto en una sola línea compacta
        layout_inputs = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(38))
        self.txt_categoria = TextInput(
            hint_text="Categoría (ej. Antojos)",
            multiline=False,
            size_hint_x=0.45
        )
        self.txt_monto = TextInput(
            hint_text="Monto (Bs)",
            input_filter='float',
            multiline=False,
            size_hint_x=0.30
        )
        btn_registrar = Button(
            text="Registrar",
            size_hint_x=0.25,
            background_color=(0.1, 0.6, 0.4, 1)
        )
        btn_registrar.bind(on_press=self.registrar_gasto)
        layout_inputs.add_widget(self.txt_categoria)
        layout_inputs.add_widget(self.txt_monto)
        layout_inputs.add_widget(btn_registrar)
        root.add_widget(layout_inputs)

        # Mensaje de estado
        self.lbl_mensaje = Label(text="", font_size='13sp', size_hint_y=None, height=dp(25))
        root.add_widget(self.lbl_mensaje)

        # Historial desplazable con resumen por categorías
        lbl_historial_titulo = Label(
            text="Historial y Resumen de Gastos",
            font_size='15sp',
            size_hint_y=None,
            height=dp(28),
            bold=True
        )
        root.add_widget(lbl_historial_titulo)

        scroll = ScrollView(size_hint=(1, 1))
        self.layout_historial = GridLayout(cols=1, spacing=dp(4), size_hint_y=None)
        self.layout_historial.bind(minimum_height=self.layout_historial.setter('height'))
        scroll.add_widget(self.layout_historial)
        root.add_widget(scroll)

        # Botón para reiniciar ciclo o periodo
        btn_reiniciar = Button(
            text="Iniciar Nuevo Ciclo (Reset)",
            size_hint_y=None,
            height=dp(40),
            background_color=(0.8, 0.3, 0.3, 1)
        )
        btn_reiniciar.bind(on_press=self.reiniciar_ciclo)
        root.add_widget(btn_reiniciar)

        self.actualizar_interfaz_historial()
        self.verificar_alerta()
        return root

    def inicializar_datos(self):
        if not os.path.exists(DATA_FILE):
            datos_iniciales = {
                "presupuesto_inicial": 1000.0,
                "saldo_actual": 1000.0,
                "gastos": []
            }
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(datos_iniciales, f, indent=4)
        
        self.cargar_datos()

    def cargar_datos(self):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.presupuesto_inicial = data.get("presupuesto_inicial", 1000.0)
            self.saldo_actual = data.get("saldo_actual", 1000.0)
            self.gastos = data.get("gastos", [])

    def guardar_datos(self):
        data = {
            "presupuesto_inicial": self.presupuesto_inicial,
            "saldo_actual": self.saldo_actual,
            "gastos": self.gastos
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def cambiar_presupuesto(self, instance):
        val_str = self.txt_presupuesto.text.strip()
        try:
            nuevo_presupuesto = float(val_str)
        except ValueError:
            self.lbl_mensaje.text = "Error: Ingresa un monto válido."
            return

        if nuevo_presupuesto < 0:
            self.lbl_mensaje.text = "Error: El monto no puede ser negativo."
            return

        total_gastos = sum(g["monto"] for g in self.gastos)
        self.presupuesto_inicial = nuevo_presupuesto
        self.saldo_actual = self.presupuesto_inicial - total_gastos

        if self.saldo_actual < 0:
            self.saldo_actual = 0
            self.lbl_mensaje.text = "Alerta: El nuevo sobrante es menor que tus gastos."
        else:
            self.lbl_mensaje.text = f"Sobrante actualizado a {self.presupuesto_inicial:.2f} Bs."

        self.guardar_datos()
        self.lbl_saldo.text = f"Saldo Disponible: {self.saldo_actual:.2f} Bs"
        self.verificar_alerta()

    def verificar_alerta(self):
        if self.presupuesto_inicial > 0:
            porcentaje_restante = (self.saldo_actual / self.presupuesto_inicial) * 100
            if self.saldo_actual <= 0:
                self.lbl_alerta.text = "¡Atención! Te has quedado sin dinero sobrante."
            elif porcentaje_restante <= 20 or self.saldo_actual <= 100:
                self.lbl_alerta.text = "⚠️ Alerta: Te queda poco presupuesto (menos del 20%)."
            else:
                self.lbl_alerta.text = ""
        else:
            self.lbl_alerta.text = ""

    def registrar_gasto(self, instance):
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

        self.saldo_actual -= monto
        self.gastos.append({"categoria": cat, "monto": monto})
        self.guardar_datos()

        self.lbl_saldo.text = f"Saldo Disponible: {self.saldo_actual:.2f} Bs"
        self.lbl_mensaje.text = f"Gasto registrado: {monto:.2f} Bs en '{cat}'."
        self.txt_categoria.text = ""
        self.txt_monto.text = ""
        self.verificar_alerta()
        self.actualizar_interfaz_historial()

    def reiniciar_ciclo(self, instance):
        self.gastos = []
        self.saldo_actual = self.presupuesto_inicial
        self.guardar_datos()
        
        self.lbl_saldo.text = f"Saldo Disponible: {self.saldo_actual:.2f} Bs"
        self.lbl_mensaje.text = "Ciclo reiniciado correctamente."
        self.verificar_alerta()
        self.actualizar_interfaz_historial()

    def actualizar_interfaz_historial(self):
        self.layout_historial.clear_widgets()
        
        if not self.gastos:
            lbl = Label(
                text="No hay gastos registrados en este ciclo.", 
                size_hint_y=None, 
                height=dp(30), 
                color=(0.6, 0.6, 0.6, 1)
            )
            self.layout_historial.add_widget(lbl)
            return

        # Resumen por categoría
        resumen_cat = {}
        for g in self.gastos:
            cat = g["categoria"]
            monto = g["monto"]
            resumen_cat[cat] = resumen_cat.get(cat, 0.0) + monto

        lbl_res_title = Label(text="• Totales por Categoría:", size_hint_y=None, height=dp(25), bold=True)
        self.layout_historial.add_widget(lbl_res_title)

        for cat, total in resumen_cat.items():
            lbl_cat = Label(text=f"   - {cat}: {total:.2f} Bs", size_hint_y=None, height=dp(22))
            self.layout_historial.add_widget(lbl_cat)

        lbl_det_title = Label(text="• Últimos Movimientos:", size_hint_y=None, height=dp(28), bold=True)
        self.layout_historial.add_widget(lbl_det_title)

        for g in reversed(self.gastos):
            lbl_gasto = Label(text=f"   [{g['categoria']}]  →  {g['monto']:.2f} Bs", size_hint_y=None, height=dp(22))
            self.layout_historial.add_widget(lbl_gasto)

if __name__ == '__main__':
    GestorSobranteApp().run()
