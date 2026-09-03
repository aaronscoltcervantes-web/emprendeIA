import json
import os
from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.core.audio import SoundLoader

DATA_FILE = "data.json"

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        # Cabecera de saldos
        self.lbl_saldo = Label(
            text="",
            font_size='22sp',
            size_hint_y=None,
            height=dp(38),
            bold=True
        )
        root.add_widget(self.lbl_saldo)

        # Aviso grande y destacado para alertas críticas (Presupuesto bajo o Límite diario excedido)
        self.lbl_alerta_grande = Label(
            text="",
            font_size='16sp',
            bold=True,
            color=(1, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(50),
            halign='center',
            valign='middle'
        )
        self.lbl_alerta_grande.bind(size=self.lbl_alerta_grande.setter('text_size'))
        root.add_widget(self.lbl_alerta_grande)

        # Configuración de Sobrante Total y Límite Diario en una línea
        layout_config = BoxLayout(orientation='horizontal', spacing=dp(6), size_hint_y=None, height=dp(38))
        
        self.txt_presupuesto = TextInput(
            hint_text="Sobrante total",
            input_filter='float',
            multiline=False,
            size_hint_x=0.35
        )
        self.txt_limite_diario = TextInput(
            hint_text="Límite diario",
            input_filter='float',
            multiline=False,
            size_hint_x=0.35
        )
        btn_guardar_config = Button(
            text="Fijar Límites",
            size_hint_x=0.30,
            background_color=(0.2, 0.5, 0.8, 1)
        )
        btn_guardar_config.bind(on_press=self.cambiar_configuracion)
        
        layout_config.add_widget(self.txt_presupuesto)
        layout_config.add_widget(self.txt_limite_diario)
        layout_config.add_widget(btn_guardar_config)
        root.add_widget(layout_config)

        # Entradas de categoría y monto
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

        # Resumen actual en curso
        lbl_act_title = Label(
            text="Gastos del Ciclo Actual",
            font_size='15sp',
            size_hint_y=None,
            height=dp(28),
            bold=True
        )
        root.add_widget(lbl_act_title)

        scroll = ScrollView(size_hint=(1, 1))
        self.layout_actual = GridLayout(cols=1, spacing=dp(4), size_hint_y=None)
        self.layout_actual.bind(minimum_height=self.layout_actual.setter('height'))
        scroll.add_widget(self.layout_actual)
        root.add_widget(scroll)

        # Botones de navegación y cierre de ciclo
        layout_botones = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(40))
        
        btn_ver_historial = Button(
            text="Ver Historial",
            background_color=(0.3, 0.4, 0.6, 1)
        )
        btn_ver_historial.bind(on_press=self.ir_a_historial)
        
        btn_cerrar_ciclo = Button(
            text="Cerrar y Archivar Ciclo",
            background_color=(0.8, 0.3, 0.3, 1)
        )
        btn_cerrar_ciclo.bind(on_press=self.cerrar_y_archivar_ciclo)

        layout_botones.add_widget(btn_ver_historial)
        layout_botones.add_widget(btn_cerrar_ciclo)
        root.add_widget(layout_botones)

        self.add_widget(root)

    def on_enter(self):
        self.actualizar_vista()

    def reproducir_sonido(self, archivo):
        try:
            sonido = SoundLoader.load(archivo)
            if sonido:
                sonido.play()
        except Exception:
            pass

    def actualizar_vista(self):
        self.app.cargar_datos()
        self.txt_presupuesto.text = str(self.app.presupuesto_inicial)
        self.txt_limite_diario.text = str(self.app.limite_diario)
        self.lbl_saldo.text = f"Saldo Disponible: {self.app.saldo_actual:.2f} Bs"
        self.verificar_alertas_y_gastos_diarios()
        self.actualizar_lista_actual()

    def verificar_alertas_y_gastos_diarios(self):
        hoy_str = datetime.now().strftime("%Y-%m-%d")
        gasto_hoy = sum(g["monto"] for g in self.app.gastos if g.get("fecha", "").startswith(hoy_str))
        
        alertas = []
        
        # Validación de gasto diario alto
        if gasto_hoy >= self.app.limite_diario and self.app.limite_diario > 0:
            alertas.append(f"🚨 ¡Límite diario superado! Hoy gastaste {gasto_hoy:.2f} Bs.")
            self.reproducir_sonido("alerta.wav")
        
        # Validación de saldo general bajo o agotado
        if self.app.saldo_actual <= 0:
            alertas.append("⚠️ ¡Te has quedado sin dinero sobrante!")
            self.reproducir_sonido("alerta.wav")
        elif self.app.presupuesto_inicial > 0 and (self.app.saldo_actual / self.app.presupuesto_inicial) * 100 <= 20:
            alertas.append("⚠️ Alerta: Queda menos del 20% de tu sobrante.")

        if alertas:
            self.lbl_alerta_grande.text = "\n".join(alertas)
        else:
            self.lbl_alerta_grande.text = ""

    def cambiar_configuracion(self, instance):
        try:
            nuevo_presupuesto = float(self.txt_presupuesto.text.strip())
            nuevo_limite = float(self.txt_limite_diario.text.strip())
        except ValueError:
            self.lbl_mensaje.text = "Error: Ingresa montos válidos."
            return

        if nuevo_presupuesto < 0 or nuevo_limite < 0:
            self.lbl_mensaje.text = "Error: Los montos no pueden ser negativos."
            return

        total_gastos = sum(g["monto"] for g in self.app.gastos)
        self.app.presupuesto_inicial = nuevo_presupuesto
        self.app.limite_diario = nuevo_limite
        self.app.saldo_actual = self.app.presupuesto_inicial - total_gastos

        if self.app.saldo_actual < 0:
            self.app.saldo_actual = 0
            self.lbl_mensaje.text = "Alerta: El sobrante es menor que tus gastos."
        else:
            self.lbl_mensaje.text = "Límites actualizados correctamente."

        self.app.guardar_datos()
        self.lbl_saldo.text = f"Saldo Disponible: {self.app.saldo_actual:.2f} Bs"
        self.verificar_alertas_y_gastos_diarios()

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

        if monto > self.app.saldo_actual:
            self.lbl_mensaje.text = "Alerta: ¡El gasto supera tu sobrante disponible!"
            return

        self.app.saldo_actual -= monto
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.app.gastos.append({"categoria": cat, "monto": monto, "fecha": fecha_actual})
        self.app.guardar_datos()

        self.reproducir_sonido("exito.wav")
        self.lbl_saldo.text = f"Saldo Disponible: {self.app.saldo_actual:.2f} Bs"
        self.lbl_mensaje.text = f"Gasto registrado: {monto:.2f} Bs en '{cat}'."
        self.txt_categoria.text = ""
        self.txt_monto.text = ""
        self.verificar_alertas_y_gastos_diarios()
        self.actualizar_lista_actual()

    def actualizar_lista_actual(self):
        self.layout_actual.clear_widgets()
        if not self.app.gastos:
            self.layout_actual.add_widget(Label(text="No hay gastos en este ciclo.", size_hint_y=None, height=dp(30), color=(0.6, 0.6, 0.6, 1)))
            return

        resumen_cat = {}
        for g in self.app.gastos:
            resumen_cat[g["categoria"]] = resumen_cat.get(g["categoria"], 0.0) + g["monto"]

        self.layout_actual.add_widget(Label(text="• Totales por Categoría:", size_hint_y=None, height=dp(25), bold=True))
        for cat, total in resumen_cat.items():
            self.layout_actual.add_widget(Label(text=f"   - {cat}: {total:.2f} Bs", size_hint_y=None, height=dp(22)))

        self.layout_actual.add_widget(Label(text="• Últimos Movimientos:", size_hint_y=None, height=dp(28), bold=True))
        for g in reversed(self.app.gastos):
            fecha_str = f" [{g.get('fecha', '')}]" if 'fecha' in g else ""
            self.layout_actual.add_widget(Label(text=f"   [{g['categoria']}]  →  {g['monto']:.2f} Bs{fecha_str}", size_hint_y=None, height=dp(22)))

    def cerrar_y_archivar_ciclo(self, instance):
        ciclo_archivado = {
            "fecha_cierre": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "presupuesto_inicial": self.app.presupuesto_inicial,
            "limite_diario": self.app.limite_diario,
            "saldo_restante": self.app.saldo_actual,
            "gastos": list(self.app.gastos)
        }
        self.app.historial_ciclos.append(ciclo_archivado)
        self.app.gastos = []
        self.app.saldo_actual = self.app.presupuesto_inicial
        self.app.guardar_datos()
        
        self.lbl_mensaje.text = "Ciclo cerrado y archivado correctamente."
        self.actualizar_vista()

    def ir_a_historial(self, instance):
        self.manager.current = 'history'

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        lbl_titulo = Label(
            text="Historial de Ciclos Archivados",
            font_size='20sp',
            size_hint_y=None,
            height=dp(40),
            bold=True
        )
        root.add_widget(lbl_titulo)

        scroll = ScrollView(size_hint=(1, 1))
        self.layout_historial = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.layout_historial.bind(minimum_height=self.layout_historial.setter('height'))
        scroll.add_widget(self.layout_historial)
        root.add_widget(scroll)

        btn_volver = Button(
            text="Volver al Panel Principal",
            size_hint_y=None,
            height=dp(45),
            background_color=(0.2, 0.5, 0.8, 1)
        )
        btn_volver.bind(on_press=self.volver_principal)
        root.add_widget(btn_volver)

        self.add_widget(root)

    def on_enter(self):
        self.actualizar_historial_vista()

    def actualizar_historial_vista(self):
        self.app.cargar_datos()
        self.layout_historial.clear_widgets()

        if not self.app.historial_ciclos:
            self.layout_historial.add_widget(Label(
                text="Aún no hay ciclos archivados.",
                size_hint_y=None,
                height=dp(40),
                color=(0.6, 0.6, 0.6, 1)
            ))
            return

        for i, ciclo in enumerate(reversed(self.app.historial_ciclos)):
            num_gastos = len(ciclo["gastos"])
            altura_bloque = dp(75 + (num_gastos * 22) + 30)
            
            box_ciclo = BoxLayout(orientation='vertical', size_hint_y=None, height=altura_bloque, padding=dp(5), spacing=dp(3))

            lbl_encabezado = Label(
                text=f"🗓 Ciclo #{len(self.app.historial_ciclos) - i} - Fecha: {ciclo['fecha_cierre']}",
                size_hint_y=None,
                height=dp(25),
                bold=True,
                color=(0.2, 0.7, 0.4, 1)
            )
            box_ciclo.add_widget(lbl_encabezado)

            lbl_resumen = Label(
                text=f"   Sobrante: {ciclo['presupuesto_inicial']:.2f} Bs | Límite Diario: {ciclo.get('limite_diario', 0):.2f} Bs | Restante: {ciclo['saldo_restante']:.2f} Bs",
                size_hint_y=None,
                height=dp(22)
            )
            box_ciclo.add_widget(lbl_resumen)

            if ciclo["gastos"]:
                box_ciclo.add_widget(Label(text="   Gastos:", size_hint_y=None, height=dp(20), bold=True))
                for g in ciclo["gastos"]:
                    fecha_g = f" [{g.get('fecha', '')}]" if 'fecha' in g else ""
                    box_ciclo.add_widget(Label(text=f"      • [{g['categoria']}] {g['monto']:.2f} Bs{fecha_g}", size_hint_y=None, height=dp(20)))
            else:
                box_ciclo.add_widget(Label(text="   Sin gastos registrados.", size_hint_y=None, height=dp(20)))

            box_ciclo.add_widget(Label(text="--------------------------------------------------", size_hint_y=None, height=dp(15), color=(0.4, 0.4, 0.4, 1)))
            self.layout_historial.add_widget(box_ciclo)

    def volver_principal(self, instance):
        self.manager.current = 'main'

class GestorSobranteApp(App):
    def build(self):
        self.inicializar_datos()
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(HistoryScreen(name='history'))
        return sm

    def inicializar_datos(self):
        if not os.path.exists(DATA_FILE):
            datos_iniciales = {
                "presupuesto_inicial": 1000.0,
                "limite_diario": 200.0,
                "saldo_actual": 1000.0,
                "gastos": [],
                "historial_ciclos": []
            }
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(datos_iniciales, f, indent=4)
        self.cargar_datos()

    def cargar_datos(self):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.presupuesto_inicial = data.get("presupuesto_inicial", 1000.0)
            self.limite_diario = data.get("limite_diario", 200.0)
            self.saldo_actual = data.get("saldo_actual", 1000.0)
            self.gastos = data.get("gastos", [])
            self.historial_ciclos = data.get("historial_ciclos", [])

    def guardar_datos(self):
        data = {
            "presupuesto_inicial": self.presupuesto_inicial,
            "limite_diario": self.limite_diario,
            "saldo_actual": self.saldo_actual,
            "gastos": self.gastos,
            "historial_ciclos": self.historial_ciclos
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

if __name__ == '__main__':
    GestorSobranteApp().run()
