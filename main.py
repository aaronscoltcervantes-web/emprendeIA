import customtkinter as ctk
import os
from datetime import datetime, timedelta

# Configuración del Tema Visual y Colores Personalizados
ctk.set_appearance_mode("dark")

# Paleta de colores vibrantes para FarmaNoah
COLOR_PRIMARIO = "#1abc9c"      # Verde esmeralda (Identidad FarmaNoah)
COLOR_SECUNDARIO = "#3498db"    # Azul eléctrico (Acciones del sistema)
COLOR_BOTON_HOVER = "#16a085"
COLOR_PELIGRO = "#e74c3c"        # Rojo coral (Eliminar / Cancelar / Cerrar)
COLOR_ALERTA = "#e67e22"         # Naranja (Stocks críticos / Advertencias)

app = ctk.CTk()
app.title("FarmaNoah - SISTEMA DE CONTROL DE FARMACIA v2.0")
app.geometry("1050x720")

# IMPORTANTE: se usa la carpeta donde está este script (no la carpeta
# desde la que lo ejecutes) para que SIEMPRE lea y escriba el MISMO
# archivo, sin importar si lo corres desde VS Code, doble clic, o un .exe
# generado en una carpeta "dist" distinta.
CARPETA_BASE = os.path.dirname(os.path.abspath(__file__))
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

def guardar_datos():
    try:
        with open(ARCHIVO_DB, "w") as f:
            for prod in inventario:
                f.write(f"{prod['id']},{prod['nombre']},{prod['stock']},{prod['precio_compra']},{prod['precio_venta']},{prod['lote']},{prod['vencimiento']},{prod['laboratorio']}\n")
        print(f"[OK] guardar_datos(): {len(inventario)} productos escritos en {os.path.abspath(ARCHIVO_DB)}")
    except Exception as e:
        print(f"[ERROR] guardar_datos() falló: {e}")

inventario = cargar_datos()
print(f"[INFO] Inventario cargado al iniciar: {len(inventario)} productos desde {os.path.abspath(ARCHIVO_DB)}")

# Variables de Control de Caja
caja_abierta = False
monto_apertura = 0.0
total_recaudado = 0.0
total_costo_vendido = 0.0
ganancia_neta = 0.0
fecha_caja = ""

# Listas de control de operaciones
carrito_ventas = []
historial_ventas_dia = []
entradas_registro = {}

# Variables globales para interfaz
entry_buscar = None
entry_id = None
entry_cant = None
frame_sugerencias = None
lbl_status = None
lbl_status_del = None
entry_del_id = None
txt_carrito = None
lbl_total_carrito = None
lbl_status_reg = None  # <-- IMPORTANTE: inicializada aquí para evitar errores de referencia

def buscar_y_sugerir(*args):
    if not entry_buscar or not frame_sugerencias: return
    for widget in frame_sugerencias.winfo_children():
        widget.destroy()
        
    texto_buscado = entry_buscar.get().lower().strip()
    if not texto_buscado:
        frame_sugerencias.pack_forget()
        return

    coincidencias = []
    for prod in inventario:
        if texto_buscado in prod["nombre"].lower() or texto_buscado in prod["laboratorio"].lower():
            coincidencias.append(prod)
            
    if coincidencias:
        frame_sugerencias.pack(pady=5, fill="x", padx=40)
        for prod in coincidencias[:4]:
            texto_boton = f"💊 {prod['nombre']} [{prod['laboratorio']}] - Stock: {prod['stock']} - ${prod['precio_venta']:.2f}"
            btn_opcion = ctk.CTkButton(
                frame_sugerencias, 
                text=texto_boton, 
                anchor="w",
                fg_color="#2c3e50",
                hover_color="#34495e",
                height=35,
                command=lambda p=prod: seleccionar_sugerencia(p)
            )
            btn_opcion.pack(fill="x", pady=2, padx=5)
    else:
        frame_sugerencias.pack(pady=5, fill="x", padx=40)
        lbl_vacio = ctk.CTkLabel(frame_sugerencias, text="No se encontraron coincidencias", text_color=COLOR_PELIGRO, font=("Arial", 12, "italic"))
        lbl_vacio.pack(pady=5)

def seleccionar_sugerencia(producto):
    entry_id.delete(0, 'end')
    entry_id.insert(0, str(producto["id"]))
    entry_buscar.delete(0, 'end')
    frame_sugerencias.pack_forget()
    entry_cant.focus()
    lbl_status.configure(text=f"Seleccionado: {producto['nombre']}", text_color=COLOR_SECUNDARIO)

def agregar_al_carrito():
    if not caja_abierta:
        lbl_status.configure(text="Error: Abra la caja primero.", text_color=COLOR_PELIGRO)
        return
    try:
        id_ingresado = int(entry_id.get())
        cant_ingresada = int(entry_cant.get())
    except ValueError:
        lbl_status.configure(text="Error: Seleccione producto e ingrese cantidad.", text_color=COLOR_PELIGRO)
        return

    producto = next((p for p in inventario if p["id"] == id_ingresado), None)
    if not producto:
        lbl_status.configure(text="Error: No encontrado.", text_color=COLOR_PELIGRO)
        return

    cant_en_carrito = sum(item["cantidad"] for item in carrito_ventas if item["id"] == id_ingresado)
    if (cant_ingresada + cant_en_carrito) > producto["stock"]:
        lbl_status.configure(text="Error: Stock insuficiente.", text_color=COLOR_PELIGRO)
        return

    carrito_ventas.append({
        "id": producto["id"],
        "nombre": producto["nombre"],
        "cantidad": cant_ingresada,
        "precio_venta": producto["precio_venta"],
        "precio_compra": producto["precio_compra"],
        "subtotal": cant_ingresada * producto["precio_venta"]
    })
    
    lbl_status.configure(text=f"Agregado: {producto['nombre']} x{cant_ingresada}", text_color=COLOR_PRIMARIO)
    entry_id.delete(0, 'end')
    entry_cant.delete(0, 'end')
    actualizar_vista_carrito()

def actualizar_vista_carrito():
    if not txt_carrito: return
    txt_carrito.configure(state="normal")
    txt_carrito.delete("1.0", "end")
    
    cabecera = f"{'ID':<4} | {'Medicamento':<18} | {'Cant':<4} | {'Total':<8}\n"
    txt_carrito.insert("insert", cabecera + "-"*42 + "\n")
    
    total = 0.0
    for item in carrito_ventas:
        nom_corto = item['nombre'][:18]
        linea = f"{item['id']:<4} | {nom_corto:<18} | {item['cantidad']:<4} | ${item['subtotal']:<7.2f}\n"
        txt_carrito.insert("insert", linea)
        total += item["subtotal"]
        
    txt_carrito.configure(state="disabled")
    lbl_total_carrito.configure(text=f"Total de la Venta: $ {total:.2f}")

def limpiar_carrito():
    carrito_ventas.clear()
    actualizar_vista_carrito()
    lbl_status.configure(text="Carrito vaciado.", text_color=COLOR_PELIGRO)

def ejecutar_cobro_multiple():
    global total_recaudado, total_costo_vendido, ganancia_neta, historial_ventas_dia
    if not carrito_ventas:
        lbl_status.configure(text="El carrito está vacío.", text_color=COLOR_PELIGRO)
        return

    hora_actual = datetime.now().strftime("%H:%M:%S")

    for item in carrito_ventas:
        producto = next(p for p in inventario if p["id"] == item["id"])
        producto["stock"] -= item["cantidad"]
        total_recaudado += item["subtotal"]
        total_costo_vendido += item["cantidad"] * item["precio_compra"]
        
        historial_ventas_dia.append({
            "hora": hora_actual,
            "nombre": item["nombre"],
            "cantidad": item["cantidad"],
            "total": item["subtotal"]
        })
        
    ganancia_neta = total_recaudado - total_costo_vendido
    guardar_datos()
    carrito_ventas.clear()
    actualizar_vista_carrito()
    lbl_status.configure(text="¡Cobrado con éxito! Registro en caja.", text_color=COLOR_PRIMARIO)

def ejecutar_registro_medicamento():
    """
    NOTA DE LA CORRECCIÓN:
    - Se agregó 'global lbl_status_reg' por seguridad (buena práctica, evita
      errores de scope si la estructura del código cambia en el futuro).
    - Se capturan TODAS las excepciones (Exception), no solo ValueError, y se
      MUESTRAN en pantalla y en consola. Antes, cualquier error que no fuera
      ValueError (por ejemplo, si un campo no existía o estaba mal escrito)
      hacía que el programa fallara SIN avisar nada, dando la sensación de
      "no se registra y no pasa nada".
    - Se imprime en consola cada paso clave, para que puedas ver en la
      terminal de VS Code exactamente qué está pasando al hacer clic.
    """
    global lbl_status_reg

    print("[DEBUG] Botón 'Guardar en Inventario' presionado.")

    if not caja_abierta:
        print("[DEBUG] Caja cerrada, no se puede registrar.")
        lbl_status_reg.configure(text="Error: Abra la caja primero.", text_color=COLOR_PELIGRO)
        return

    try:
        nombre = entradas_registro["entry_nom"].get().strip()
        stock_txt = entradas_registro["entry_stk"].get().strip()
        pc_txt = entradas_registro["entry_pc"].get().strip()
        pv_txt = entradas_registro["entry_pv"].get().strip()
        lote = entradas_registro["entry_lot"].get().strip()
        vence = entradas_registro["entry_venc"].get().strip()
        lab = entradas_registro["entry_lab"].get().strip()

        print(f"[DEBUG] Datos leídos -> nombre={nombre!r}, stock={stock_txt!r}, "
              f"p_compra={pc_txt!r}, p_venta={pv_txt!r}, lote={lote!r}, "
              f"vence={vence!r}, lab={lab!r}")

        if not nombre or not lote or not vence or not lab:
            print("[DEBUG] Falló validación: hay campos de texto vacíos.")
            lbl_status_reg.configure(text="Campos obligatorios.", text_color=COLOR_PELIGRO)
            return

        if not stock_txt or not pc_txt or not pv_txt:
            print("[DEBUG] Falló validación: hay campos numéricos vacíos.")
            lbl_status_reg.configure(text="Complete Cantidad, Costo y Precio de Venta.", text_color=COLOR_PELIGRO)
            return

        stock = int(stock_txt)
        p_compra = float(pc_txt)
        p_venta = float(pv_txt)

        # Validar formato MM/AAAA estrictamente
        datetime.strptime(vence, "%m/%Y")

    except ValueError as e:
        print(f"[DEBUG] ValueError al validar datos: {e}")
        lbl_status_reg.configure(text="Datos o formato Vence (MM/AAAA) inválido.", text_color=COLOR_PELIGRO)
        return
    except Exception as e:
        # Cualquier otro error inesperado: ahora SÍ se ve en pantalla y en consola
        print(f"[ERROR] Excepción inesperada en ejecutar_registro_medicamento: {e}")
        lbl_status_reg.configure(text=f"Error inesperado: {e}", text_color=COLOR_PELIGRO)
        return

    nuevo_id = max([prod["id"] for prod in inventario], default=0) + 1
    inventario.append({
        "id": nuevo_id, "nombre": nombre, "stock": stock, 
        "precio_compra": p_compra, "precio_venta": p_venta, 
        "lote": lote, "vencimiento": vence, "laboratorio": lab
    })

    print(f"[DEBUG] Producto agregado en memoria. Total productos en inventario: {len(inventario)}")

    guardar_datos()
    
    lbl_status_reg.configure(text=f"Guardado ID: {nuevo_id} ({lab})", text_color=COLOR_PRIMARIO)
    for key in entradas_registro:
        entradas_registro[key].delete(0, 'end')

def ejecutar_eliminacion_medicamento():
    try:
        id_a_borrar = int(entry_del_id.get())
    except ValueError:
        lbl_status_del.configure(text="Error: Ingrese ID.", text_color=COLOR_PELIGRO)
        return

    global inventario
    producto_encontrado = False
    for prod in inventario:
        if prod["id"] == id_a_borrar:
            inventario.remove(prod)
            producto_encontrado = True
            break

    if producto_encontrado:
        guardar_datos()
        lbl_status_del.configure(text=f"ID {id_a_borrar} eliminado.", text_color=COLOR_PRIMARIO)
        entry_del_id.delete(0, 'end')
        mostrar_inventario()
    else:
        lbl_status_del.configure(text="ID no encontrado.", text_color=COLOR_PELIGRO)

def procesar_apertura_caja():
    global caja_abierta, monto_apertura, fecha_caja, total_recaudado, total_costo_vendido, ganancia_neta, historial_ventas_dia
    try:
        monto_apertura = float(entry_monto_ap.get())
    except ValueError:
        lbl_status_caja.configure(text="Monto inicial inválido.", text_color=COLOR_PELIGRO)
        return
    
    caja_abierta = True
    fecha_caja = datetime.now().strftime("%d/%m/%Y")
    total_recaudado = 0.0
    total_costo_vendido = 0.0
    ganancia_neta = 0.0
    historial_ventas_dia.clear()
    
    print(f"[DEBUG] Caja abierta. caja_abierta={caja_abierta}, fecha={fecha_caja}")
    mostrar_reportes()

def procesar_cierre_caja():
    global caja_abierta, monto_apertura, total_recaudado, total_costo_vendido, ganancia_neta
    if not caja_abierta:
        return
        
    monto_total_en_caja = monto_apertura + total_recaudado
    
    with open(ARCHIVO_CAJA, "a") as f:
        f.write(f"FECHA: {fecha_caja} | Apertura: ${monto_apertura:.2f} | Ventas Brutas: ${total_recaudado:.2f} | Costo Inversion: ${total_costo_vendido:.2f} | Ganancia Neta: ${ganancia_neta:.2f} | Total Caja: ${monto_total_en_caja:.2f}\n")
        
    caja_abierta = False
    monto_apertura = 0.0
    total_recaudado = 0.0
    total_costo_vendido = 0.0
    ganancia_neta = 0.0
    mostrar_reportes()

def calcular_acumulado_mensual():
    total_ganado = 0.0
    cierres_contados = 0
    if os.path.exists(ARCHIVO_CAJA):
        with open(ARCHIVO_CAJA, "r") as f:
            for linea in f:
                if "Ganancia Neta:" in linea:
                    try:
                        parte_ganancia = linea.split("Ganancia Neta: $")[1].split(" |")[0]
                        total_ganado += float(parte_ganancia)
                        cierres_contados += 1
                    except Exception:
                        pass
    return total_ganado, cierres_contados

def limpiar_zona_central():
    for widget in zona_central.winfo_children():
        widget.destroy()

def mostrar_ventas():
    global entry_id, entry_cant, entry_buscar, frame_sugerencias, lbl_status, txt_carrito, lbl_total_carrito
    limpiar_zona_central()
    
    if not caja_abierta:
        ctk.CTkLabel(zona_central, text="⚠️ ACCESO RESTRINGIDO\n\nAbra la caja en el menú 'Reporte de Caja' para habilitar las ventas.", font=("Arial", 16, "bold"), text_color=COLOR_PELIGRO).pack(pady=100)
        return

    ctk.CTkLabel(zona_central, text="🛒 PUNTO DE VENTA (MULTIPLE PRODUCTO)", font=("Arial", 20, "bold"), text_color=COLOR_PRIMARIO).pack(pady=10)
    
    f_pantalla = ctk.CTkFrame(zona_central, fg_color="transparent")
    f_pantalla.pack(fill="both", expand=True, padx=10, pady=5)
    
    f_izquierda = ctk.CTkFrame(f_pantalla, width=400)
    f_izquierda.pack(side="left", fill="both", expand=True, padx=5)
    
    ctk.CTkLabel(f_izquierda, text="Buscador Predictivo de Medicamentos:", font=("Arial", 12, "bold")).pack(pady=5)
    entry_buscar = ctk.CTkEntry(f_izquierda, width=320, placeholder_text="Escriba el nombre comercial o laboratorio...")
    entry_buscar.pack(pady=2)
    entry_buscar.bind("<KeyRelease>", buscar_y_sugerir)
    
    frame_sugerencias = ctk.CTkFrame(f_izquierda, fg_color="#1a252f", border_width=1, border_color="#34495e")
    
    f_datos_seleccion = ctk.CTkFrame(f_izquierda, fg_color="transparent")
    f_datos_seleccion.pack(pady=10)
    
    ctk.CTkLabel(f_datos_seleccion, text="ID:").grid(row=0, column=0, padx=5, pady=2)
    entry_id = ctk.CTkEntry(f_datos_seleccion, width=60)
    entry_id.grid(row=0, column=1, padx=5, pady=2)
    
    ctk.CTkLabel(f_datos_seleccion, text="Cantidad:").grid(row=0, column=2, padx=5, pady=2)
    entry_cant = ctk.CTkEntry(f_datos_seleccion, width=80)
    entry_cant.grid(row=0, column=3, padx=5, pady=2)
    
    ctk.CTkButton(f_izquierda, text="➕ Agregar al Carrito", fg_color=COLOR_SECUNDARIO, hover_color="#2980b9", font=("Arial", 12, "bold"), command=agregar_al_carrito).pack(pady=10)
    
    lbl_status = ctk.CTkLabel(f_izquierda, text="Esperando entrada del vendedor...", font=("Arial", 12, "italic"))
    lbl_status.pack(pady=5)

    f_derecha = ctk.CTkFrame(f_pantalla)
    f_derecha.pack(side="right", fill="both", expand=True, padx=5)
    
    ctk.CTkLabel(f_derecha, text="Lista de Medicamentos a Cobrar", font=("Arial", 14, "bold")).pack(pady=5)
    
    f_botones_caja = ctk.CTkFrame(f_derecha, fg_color="transparent")
    f_botones_caja.pack(pady=5)
    ctk.CTkButton(f_botones_caja, text="❌ Cancelar Lista", fg_color=COLOR_PELIGRO, hover_color="#c0392b", width=120, command=limpiar_carrito).grid(row=0, column=0, padx=5)
    ctk.CTkButton(f_botones_caja, text="✔ EMITIR Y COBRAR", fg_color=COLOR_PRIMARIO, hover_color=COLOR_BOTON_HOVER, width=160, font=("Arial", 12, "bold"), command=ejecutar_cobro_multiple).grid(row=0, column=1, padx=5)
    
    lbl_total_carrito = ctk.CTkLabel(f_derecha, text="Total de la Venta: $ 0.00", font=("Arial", 16, "bold"), text_color=COLOR_PRIMARIO)
    lbl_total_carrito.pack(pady=5)
    
    txt_carrito = ctk.CTkTextbox(f_derecha, font=("Courier New", 11), height=250)
    txt_carrito.pack(fill="both", expand=True, padx=10, pady=5)
    
    actualizar_vista_carrito()

def recargar_inventario_y_mostrar():
    global inventario
    inventario = cargar_datos()
    print(f"[DEBUG] Inventario recargado manualmente desde disco: {len(inventario)} productos.")
    mostrar_inventario()

def mostrar_inventario():
    global entry_del_id, lbl_status_del
    limpiar_zona_central()
    
    ctk.CTkLabel(zona_central, text="📦 CONTROL DE INVENTARIO GENERAL", font=("Arial", 20, "bold"), text_color=COLOR_SECUNDARIO).pack(pady=15)
    
    ctk.CTkLabel(zona_central, text=f"Archivo: {ARCHIVO_DB}", font=("Arial", 10), text_color="#888888").pack(pady=(0,5))
    
    frame_acciones = ctk.CTkFrame(zona_central)
    frame_acciones.pack(pady=5, padx=20, fill="x")
    
    ctk.CTkLabel(frame_acciones, text="Eliminar ID:").grid(row=0, column=0, padx=10, pady=10)
    entry_del_id = ctk.CTkEntry(frame_acciones, width=100)
    entry_del_id.grid(row=0, column=1, padx=10, pady=10)
    
    ctk.CTkButton(frame_acciones, text="Remover del Sistema", fg_color=COLOR_PELIGRO, hover_color="#c0392b", command=ejecutar_eliminacion_medicamento).grid(row=0, column=2, padx=10, pady=10)
    ctk.CTkButton(frame_acciones, text="🔄 Recargar desde Disco", fg_color=COLOR_SECUNDARIO, hover_color="#2980b9", command=lambda: recargar_inventario_y_mostrar()).grid(row=0, column=3, padx=10, pady=10)
    lbl_status_del = ctk.CTkLabel(frame_acciones, text="", font=("Arial", 11, "italic"))
    lbl_status_del.grid(row=0, column=4, padx=15, pady=10)
    
    txt_box = ctk.CTkTextbox(zona_central, font=("Courier New", 11), width=750, height=350)
    txt_box.pack(pady=10, padx=20, fill="both", expand=True)
    
    cabecera = f"{'ID':<4} | {'Medicamento':<20} | {'Laboratorio':<12} | {'Stock':<6} | {'P.Venta':<7} | {'Vence':<8} | {'Alerta Estado':<15}\n"
    txt_box.insert("insert", cabecera + "-"*90 + "\n")
    
    hoy = datetime.now()
    
    for p in inventario:
        alerta_tipo = "OK"
        if p['stock'] < 10:
            alerta_tipo = "STOCK CRÍTICO"
            
        try:
            fecha_venc = datetime.strptime(p['vencimiento'], "%m/%Y")
            dias_restantes = (fecha_venc - hoy).days
            
            if dias_restantes <= 0:
                alerta_tipo = "¡PRODUCTO VENCIDO!"
            elif dias_restantes <= 30:
                alerta_tipo = "PRÓX. A VENCER (1M)"
        except Exception:
            pass
            
        linea = f"{p['id']:<4} | {p['nombre']:<20} | {p['laboratorio']:<12} | {p['stock']:<6} | ${p['precio_venta']:<6.2f} | {p['vencimiento']:<8} | {alerta_tipo}\n"
        txt_box.insert("insert", linea)
        
        if "VENC" in alerta_tipo or "PRÓX" in alerta_tipo or "CRÍTICO" in alerta_tipo:
            txt_box.tag_add("critico", "insert - 1 lines", "insert")
            txt_box.tag_config("critico", foreground=COLOR_PELIGRO)
            
    txt_box.configure(state="disabled")

def mostrar_compras():
    global lbl_status_reg
    limpiar_zona_central()
    
    if not caja_abierta:
        ctk.CTkLabel(zona_central, text="⚠️ ACCESO RESTRINGIDO\n\nAbra la caja primero para poder añadir nuevos lotes de compra.", font=("Arial", 16, "bold"), text_color=COLOR_PELIGRO).pack(pady=100)
        return

    ctk.CTkLabel(zona_central, text="📥 ENTRADA DE MERCANCÍA (REGISTRAR COMPRA)", font=("Arial", 20, "bold"), text_color=COLOR_PRIMARIO).pack(pady=15)
    
    frame = ctk.CTkFrame(zona_central)
    frame.pack(pady=10, padx=20)
    
    campos = [
        ("Nombre Comercial:", "entry_nom"), ("Laboratorio / Marca:", "entry_lab"), ("Cantidad Inicial:", "entry_stk"), 
        ("Costo Compra ($):", "entry_pc"), ("Precio Venta ($):", "entry_pv"), 
        ("Número Lote:", "entry_lot"), ("Expiración (MM/AAAA):", "entry_venc")
    ]
    
    entradas_registro.clear()
    for idx, (t, v) in enumerate(campos):
        ctk.CTkLabel(frame, text=t).grid(row=idx, column=0, padx=10, pady=5, sticky="e")
        entradas_registro[v] = ctk.CTkEntry(frame, width=250)
        entradas_registro[v].grid(row=idx, column=1, padx=10, pady=5)
        
    ctk.CTkButton(zona_central, text="Guardar en Inventario", fg_color=COLOR_PRIMARIO, hover_color=COLOR_BOTON_HOVER, font=("Arial", 12, "bold"), command=ejecutar_registro_medicamento).pack(pady=15)
    lbl_status_reg = ctk.CTkLabel(zona_central, text="")
    lbl_status_reg.pack()

def mostrar_historial_ventas_dia():
    limpiar_zona_central()
    
    ctk.CTkLabel(zona_central, text="📋 HISTORIAL CRONOLÓGICO DE VENTAS DEL TURNO", font=("Arial", 20, "bold"), text_color=COLOR_SECUNDARIO).pack(pady=15)
    
    txt_historial = ctk.CTkTextbox(zona_central, font=("Courier New", 12), width=750, height=450)
    txt_historial.pack(pady=10, padx=20, fill="both", expand=True)
    
    cabecera = f"{'Hora Exacta':<12} | {'Medicamento Vendido':<30} | {'Cantidad':<10} | {'Monto Cobrado':<12}\n"
    txt_historial.insert("insert", cabecera + "="*70 + "\n")
    
    if not historial_ventas_dia:
        txt_historial.insert("insert", "\n No se han registrado movimientos comerciales en este periodo.\n")
    else:
        # Muestra los datos de venta organizados desde el más reciente
        historial_ordenado = sorted(historial_ventas_dia, key=lambda x: x['hora'], reverse=True)
        for v in historial_ordenado:
            linea = f"{v['hora']:<12} | {v['nombre']:<30} | {v['cantidad']:<10} | $ {v['total']:<.2f}\n"
            txt_historial.insert("insert", linea)
            
    txt_historial.configure(state="disabled")

def mostrar_balance_semanal():
    limpiar_zona_central()
    
    ctk.CTkLabel(zona_central, text="📊 INFORMES FINANCIEROS REALES (ÚLTIMOS 7 DÍAS)", font=("Arial", 20, "bold"), text_color=COLOR_PRIMARIO).pack(pady=15)
    
    txt_balance = ctk.CTkTextbox(zona_central, font=("Courier New", 12), width=750, height=300)
    txt_balance.pack(pady=10, padx=20, fill="both", expand=True)
    
    cabecera = f"{'Fecha':<12} | {'Ventas Brutas':<15} | {'Costo Inversión':<18} | {'Ganancia Neta Real':<18}\n"
    txt_balance.insert("insert", cabecera + "="*72 + "\n")
    
    total_ventas_semana = 0.0
    total_costo_semana = 0.0
    total_ganancia_semana = 0.0
    dias_evaluados = 0
    
    hoy = datetime.now()
    fechas_ultimos_7_dias = [(hoy - timedelta(days=i)).strftime("%d/%m/%Y") for i in range(7)]
    
    if os.path.exists(ARCHIVO_CAJA):
        with open(ARCHIVO_CAJA, "r") as f:
            for linea in f:
                if "FECHA:" in linea:
                    try:
                        fecha_str = linea.split("FECHA: ")[1].split(" |")[0]
                        if fecha_str in fechas_ultimos_7_dias:
                            v_brutas = float(linea.split("Ventas Brutas: $")[1].split(" |")[0])
                            c_inversion = 0.0
                            if "Costo Inversion: $" in linea:
                                c_inversion = float(linea.split("Costo Inversion: $")[1].split(" |")[0])
                            else:
                                c_inversion = v_brutas * 0.6
                                
                            g_neta = float(linea.split("Ganancia Neta: $")[1].split(" |")[0])
                            
                            linea_tabla = f"{fecha_str:<12} | ${v_brutas:<14.2f} | ${c_inversion:<17.2f} | ${g_neta:<17.2f}\n"
                            txt_balance.insert("insert", linea_tabla)
                            
                            total_ventas_semana += v_brutas
                            total_costo_semana += c_inversion
                            total_ganancia_semana += g_neta
                            dias_evaluados += 1
                    except Exception:
                        pass
                        
    if dias_evaluados == 0:
        txt_balance.insert("insert", "\n Ningún registro contable archivado en la última semana.\n")
    
    txt_balance.configure(state="disabled")
    
    f_totales_sem = ctk.CTkFrame(zona_central, border_width=2, border_color=COLOR_PRIMARIO)
    f_totales_sem.pack(pady=15, padx=20, fill="x")
    
    ctk.CTkLabel(f_totales_sem, text=f"📈 RESULTADO TOTAL ACUMULADO DE LA SEMANA", font=("Arial", 13, "bold"), text_color=COLOR_SECUNDARIO).pack(pady=5)
    f_columnas = ctk.CTkFrame(f_totales_sem, fg_color="transparent")
    f_columnas.pack(pady=5, fill="x")
    
    ctk.CTkLabel(f_columnas, text=f"Ventas: ${total_ventas_semana:.2f}", font=("Arial", 13)).pack(side="left", expand=True, padx=10)
    ctk.CTkLabel(f_columnas, text=f"Inversión Base: ${total_costo_semana:.2f}", font=("Arial", 13), text_color=COLOR_ALERTA).pack(side="left", expand=True, padx=10)
    ctk.CTkLabel(f_columnas, text=f"GANANCIA NETA REAL: ${total_ganancia_semana:.2f}", font=("Arial", 14, "bold"), text_color=COLOR_PRIMARIO).pack(side="left", expand=True, padx=10)

def mostrar_reportes():
    global entry_monto_ap, lbl_status_caja
    limpiar_zona_central()
    
    ctk.CTkLabel(zona_central, text="🗄 CONTROL DE ARQUEO Y APERTURA DE CAJA", font=("Arial", 20, "bold"), text_color=COLOR_SECUNDARIO).pack(pady=10)
    
    frame_gestion = ctk.CTkFrame(zona_central)
    frame_gestion.pack(pady=5, padx=20, fill="x")
    
    if not caja_abierta:
        ctk.CTkLabel(frame_gestion, text="Fondo Inicial ($):").grid(row=0, column=0, padx=10, pady=15)
        entry_monto_ap = ctk.CTkEntry(frame_gestion, width=120)
        entry_monto_ap.grid(row=0, column=1, padx=10, pady=15)
        entry_monto_ap.insert(0, "0.00")
        
        ctk.CTkButton(frame_gestion, text="Habilitar Caja Diaria", fg_color=COLOR_PRIMARIO, hover_color=COLOR_BOTON_HOVER, command=procesar_apertura_caja).grid(row=0, column=2, padx=10, pady=15)
    else:
        ctk.CTkLabel(frame_gestion, text=f"Caja Abierta: {fecha_caja} | Base: ${monto_apertura:.2f}", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=20, pady=15)
        ctk.CTkButton(frame_gestion, text="Realizar Cierre de Turno", fg_color=COLOR_PELIGRO, hover_color="#c0392b", command=procesar_cierre_caja).grid(row=0, column=1, padx=20, pady=15)

    if not caja_abierta:
        lbl_status_caja = ctk.CTkLabel(zona_central, text="Estado: No Operando (Caja Cerrada)", font=("Arial", 13, "italic"), text_color=COLOR_PELIGRO)
    else:
        lbl_status_caja = ctk.CTkLabel(zona_central, text=f"Estado: Operando Activamente ({fecha_caja})", font=("Arial", 13, "italic"), text_color=COLOR_PRIMARIO)
    lbl_status_caja.pack(pady=2)
    
    f_valores = ctk.CTkFrame(zona_central)
    f_valores.pack(pady=5)
    
    ctk.CTkLabel(f_valores, text=f"Monto Inicial de Apertura: $ {monto_apertura:.2f}", font=("Arial", 13)).pack(pady=2, padx=20)
    ctk.CTkLabel(f_valores, text=f"Ventas Brutas del Turno actual: $ {total_recaudado:.2f}", font=("Arial", 13)).pack(pady=2, padx=20)
    ctk.CTkLabel(f_valores, text=f"Efectivo Estimado en Caja: $ {(monto_apertura + total_recaudado):.2f}", font=("Arial", 13, "bold"), text_color=COLOR_SECUNDARIO).pack(pady=2, padx=20)
    
    f_ganancia = ctk.CTkFrame(zona_central, fg_color=COLOR_PRIMARIO if caja_abierta else "#7f8c8d")
    f_ganancia.pack(pady=5)
    ctk.CTkLabel(f_ganancia, text=f"GANANCIA MARGINAL DEL DÍA: $ {ganancia_neta:.2f}", font=("Arial", 14, "bold"), text_color="white").pack(pady=10, padx=20)

    f_mensual = ctk.CTkFrame(zona_central, border_width=2, border_color=COLOR_SECUNDARIO)
    f_mensual.pack(pady=15, padx=20, fill="x")
    
    acumulado, dias = calcular_acumulado_mensual()
    ctk.CTkLabel(f_mensual, text="📊 BALANCE ACUMULADO DEL MES (HISTÓRICO)", font=("Arial", 14, "bold"), text_color=COLOR_SECUNDARIO).pack(pady=5)
    ctk.CTkLabel(f_mensual, text=f"Cierres de caja totales en archivo: {dias}", font=("Arial", 13)).pack(pady=2)
    ctk.CTkLabel(f_mensual, text=f"GANANCIA HISTÓRICA COMBINADA: $ {acumulado:.2f}", font=("Arial", 16, "bold"), text_color=COLOR_PRIMARIO).pack(pady=8)

# =====================================================================
# CONFIGURACIÓN DE LA INTERFAZ PRINCIPAL - IDENTIDAD DE MARCA FARMANOAH
# =====================================================================

menu_lateral = ctk.CTkFrame(app, width=200, corner_radius=0)
menu_lateral.pack(side="left", fill="y")

# Título corporativo personalizado
lbl_titulo_menu = ctk.CTkLabel(menu_lateral, text="🏥 FarmaNoah", font=("Arial", 22, "bold"), text_color=COLOR_PRIMARIO)
lbl_titulo_menu.pack(pady=25, padx=10)

btn_ventas = ctk.CTkButton(menu_lateral, text="🛒 Punto de Venta", fg_color="#2c3e50", hover_color="#34495e", command=mostrar_ventas)
btn_ventas.pack(pady=8, padx=15, fill="x")

btn_historial = ctk.CTkButton(menu_lateral, text="📋 Historial de Hoy", fg_color="#2c3e50", hover_color="#34495e", command=mostrar_historial_ventas_dia)
btn_historial.pack(pady=8, padx=15, fill="x")

btn_balance = ctk.CTkButton(menu_lateral, text="📊 Balance Semanal", fg_color=COLOR_PRIMARIO, hover_color=COLOR_BOTON_HOVER, text_color="black", font=("Arial", 12, "bold"), command=mostrar_balance_semanal)
btn_balance.pack(pady=8, padx=15, fill="x")

btn_inventario = ctk.CTkButton(menu_lateral, text="📦 Ver Inventario", fg_color="#2c3e50", hover_color="#34495e", command=mostrar_inventario)
btn_inventario.pack(pady=8, padx=15, fill="x")

btn_compras = ctk.CTkButton(menu_lateral, text="📥 Registrar Compra", fg_color="#2c3e50", hover_color="#34495e", command=mostrar_compras)
btn_compras.pack(pady=8, padx=15, fill="x")

btn_reportes = ctk.CTkButton(menu_lateral, text="🗄 Reporte / Caja", fg_color=COLOR_SECUNDARIO, hover_color="#2980b9", font=("Arial", 12, "bold"), command=mostrar_reportes)
btn_reportes.pack(pady=15, padx=15, fill="x")

zona_central = ctk.CTkFrame(app, fg_color="transparent")
zona_central.pack(side="right", fill="both", expand=True, padx=10)

# Iniciar mostrando el panel de control de caja al encender
mostrar_reportes()

app.mainloop()
