-- 1. Tabla de Productos
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio_compra DECIMAL(10, 2) NOT NULL, -- Costo
    precio_venta DECIMAL(10, 2) NOT NULL   -- Precio al público
);

-- Datos de prueba
INSERT INTO productos (nombre, precio_compra, precio_venta) VALUES 
('Paracetamol 500mg', 5.00, 10.00),
('Ibuprofeno 400mg', 7.00, 15.00),
('Panadol Antigripal', 8.00, 12.00);

-- 2. Tabla de Ventas (Encabezado)
CREATE TABLE ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_venta DECIMAL(10, 2) NOT NULL,
    total_ganancia DECIMAL(10, 2) NOT NULL
);

-- 3. Tabla de Detalle de Ventas
CREATE TABLE detalle_ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT,
    id_producto INT,
    cantidad INT NOT NULL,
    precio_compra_momento DECIMAL(10, 2) NOT NULL,
    precio_venta_momento DECIMAL(10, 2) NOT NULL,
    ganancia_linea DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_venta) REFERENCES ventas(id),
    FOREIGN KEY (id_producto) REFERENCES productos(id)
);
