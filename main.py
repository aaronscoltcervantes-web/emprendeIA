-- 1. Tabla de Productos
CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    precio_compra REAL NOT NULL,
    precio_venta REAL NOT NULL
);

-- Datos de prueba
INSERT INTO productos (nombre, precio_compra, precio_venta) VALUES 
('Paracetamol 500mg', 5.00, 10.00),
('Ibuprofeno 400mg', 7.00, 15.00),
('Panadol Antigripal', 8.00, 12.00);

-- 2. Tabla de Ventas (Con opción de pago QR o Efectivo)
CREATE TABLE ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT DEFAULT (datetime('now', 'localtime')),
    total_venta REAL NOT NULL,
    total_ganancia REAL NOT NULL,
    metodo_pago TEXT NOT NULL CHECK(metodo_pago IN ('Efectivo', 'QR')) DEFAULT 'Efectivo'
);

-- 3. Tabla de Detalle de Ventas
CREATE TABLE detalle_ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_venta INTEGER,
    id_producto INTEGER,
    cantidad INTEGER NOT NULL,
    precio_compra_momento REAL NOT NULL,
    precio_venta_momento REAL NOT NULL,
    ganancia_linea REAL NOT NULL,
    FOREIGN KEY (id_venta) REFERENCES ventas(id),
    FOREIGN KEY (id_producto) REFERENCES productos(id)
);
