-- ============================================================
-- COOPGANCE S.A. — Schema completo para Supabase
-- Sistema Web Integral de Produccion de Leche Pasteurizada
-- ============================================================
-- INSTRUCCIONES:
-- 1. Ir a Supabase Dashboard → SQL Editor
-- 2. Pegar todo este archivo y ejecutar (Run)
-- ============================================================

-- Limpiar tablas existentes (orden por dependencias)
DROP TABLE IF EXISTS bitacora CASCADE;
DROP TABLE IF EXISTS alertas CASCADE;
DROP TABLE IF EXISTS distribucion CASCADE;
DROP TABLE IF EXISTS inventario CASCADE;
DROP TABLE IF EXISTS produccion CASCADE;
DROP TABLE IF EXISTS analisis_calidad CASCADE;
DROP TABLE IF EXISTS lotes CASCADE;
DROP TABLE IF EXISTS productores CASCADE;
DROP TABLE IF EXISTS centros_acopio CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

-- ============================================================
-- TABLAS
-- ============================================================

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    usuario TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('admin','gerente','operario','calidad','logistica','recepcion','distribucion')),
    estado TEXT NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo','Inactivo')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE centros_acopio (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    ubicacion TEXT,
    capacidad_litros INTEGER DEFAULT 10000,
    estado TEXT NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo','Inactivo')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE productores (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    telefono TEXT,
    direccion TEXT,
    departamento TEXT,
    estado TEXT NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo','Inactivo')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE lotes (
    id SERIAL PRIMARY KEY,
    codigo_lote TEXT NOT NULL UNIQUE,
    fecha_registro TIMESTAMPTZ DEFAULT NOW(),
    volumen_litros NUMERIC(10,2) NOT NULL,
    estado_lote TEXT NOT NULL DEFAULT 'Pendiente de análisis'
        CHECK (estado_lote IN ('Pendiente de análisis','Aprobado','Rechazado','Procesado','Distribuido')),
    productor_id INTEGER NOT NULL REFERENCES productores(id),
    centro_id INTEGER NOT NULL REFERENCES centros_acopio(id),
    responsable_recepcion TEXT,
    observaciones TEXT
);

CREATE TABLE analisis_calidad (
    id SERIAL PRIMARY KEY,
    lote_id INTEGER NOT NULL REFERENCES lotes(id),
    temperatura NUMERIC(5,2) NOT NULL,
    olor TEXT NOT NULL,
    color TEXT NOT NULL,
    acidez NUMERIC(6,4) NOT NULL,
    densidad NUMERIC(7,4) NOT NULL,
    prueba_alcohol TEXT NOT NULL CHECK (prueba_alcohol IN ('Negativa','Positiva')),
    resultado TEXT NOT NULL CHECK (resultado IN ('Aprobado','Rechazado')),
    fecha_analisis TIMESTAMPTZ DEFAULT NOW(),
    responsable_calidad TEXT,
    observaciones TEXT
);

CREATE TABLE produccion (
    id SERIAL PRIMARY KEY,
    lote_id INTEGER NOT NULL REFERENCES lotes(id),
    temperatura_proceso NUMERIC(5,2) NOT NULL,
    tiempo_proceso INTEGER NOT NULL,
    fecha_produccion TIMESTAMPTZ DEFAULT NOW(),
    estado TEXT NOT NULL DEFAULT 'En proceso' CHECK (estado IN ('En proceso','Completado','Error')),
    responsable_produccion TEXT,
    observaciones TEXT
);

CREATE TABLE inventario (
    id SERIAL PRIMARY KEY,
    producto TEXT NOT NULL,
    presentacion TEXT NOT NULL DEFAULT '1L' CHECK (presentacion IN ('250ml','500ml','1L','2L')),
    cantidad INTEGER NOT NULL DEFAULT 0,
    fecha_registro TIMESTAMPTZ DEFAULT NOW(),
    origen TEXT,
    lote_id INTEGER REFERENCES lotes(id),
    ubicacion TEXT,
    estado TEXT NOT NULL DEFAULT 'En almacén' CHECK (estado IN ('En almacén','En despacho','Agotado','Reservado'))
);

CREATE TABLE distribucion (
    id SERIAL PRIMARY KEY,
    cliente TEXT NOT NULL,
    producto TEXT NOT NULL,
    presentacion TEXT,
    cantidad INTEGER NOT NULL,
    fecha_salida TIMESTAMPTZ DEFAULT NOW(),
    responsable TEXT NOT NULL,
    inventario_id INTEGER REFERENCES inventario(id),
    origen_lote TEXT,
    estado TEXT NOT NULL DEFAULT 'Entregado' CHECK (estado IN ('Entregado','En ruta','Pendiente','Cancelado'))
);

CREATE TABLE alertas (
    id SERIAL PRIMARY KEY,
    lote_id INTEGER REFERENCES lotes(id),
    tipo_alerta TEXT NOT NULL CHECK (tipo_alerta IN ('Lote rechazado','Inventario bajo','Mantenimiento','Proceso','Distribución','Sistema')),
    descripcion TEXT NOT NULL,
    fecha_alerta TIMESTAMPTZ DEFAULT NOW(),
    estado TEXT NOT NULL DEFAULT 'Activa' CHECK (estado IN ('Activa','Resuelta','En revisión'))
);

CREATE TABLE bitacora (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    accion TEXT,
    descripcion TEXT,
    fecha_hora TIMESTAMPTZ DEFAULT NOW(),
    ip_address TEXT
);

-- ============================================================
-- INDICES para mejorar rendimiento en Power BI
-- ============================================================
CREATE INDEX idx_lotes_estado ON lotes(estado_lote);
CREATE INDEX idx_lotes_fecha ON lotes(fecha_registro);
CREATE INDEX idx_lotes_productor ON lotes(productor_id);
CREATE INDEX idx_lotes_centro ON lotes(centro_id);
CREATE INDEX idx_calidad_lote ON analisis_calidad(lote_id);
CREATE INDEX idx_calidad_resultado ON analisis_calidad(resultado);
CREATE INDEX idx_produccion_lote ON produccion(lote_id);
CREATE INDEX idx_inventario_estado ON inventario(estado);
CREATE INDEX idx_distribucion_fecha ON distribucion(fecha_salida);
CREATE INDEX idx_alertas_estado ON alertas(estado);

-- ============================================================
-- DATOS INICIALES
-- ============================================================

INSERT INTO usuarios (nombre, usuario, password, rol, estado) VALUES
('JorgeVargas', 'admin1', 'admin', 'admin', 'Activo'),
('Carlos Mendoza', 'admin', 'admin123', 'admin', 'Activo'),
('Maria Elena Perez', 'gerente', 'gerente123', 'gerente', 'Activo'),
('Jorge Ramirez', 'operario1', 'op123', 'operario', 'Activo'),
('Ana Lucia Torres', 'calidad1', 'cal123', 'calidad', 'Activo'),
('Roberto Castillo', 'logistica1', 'log123', 'logistica', 'Activo'),
('Sofia Hernandez', 'recepcion1', 'rec123', 'recepcion', 'Activo'),
('Luis Garcia', 'distribucion1', 'dist123', 'distribucion', 'Activo'),
('Patricia Lopez', 'calidad2', 'cal456', 'calidad', 'Activo'),
('Diego Morales', 'operario2', 'op456', 'operario', 'Activo'),
('Carmen Fuentes', 'recepcion2', 'rec456', 'recepcion', 'Activo');

INSERT INTO centros_acopio (nombre, ubicacion, capacidad_litros, estado) VALUES
('Centro de Acopio Norte', 'Huehuetenango, Guatemala', 10000, 'Activo'),
('Centro de Acopio Sur', 'Escuintla, Guatemala', 10000, 'Activo'),
('Centro de Acopio Oriente', 'Zacapa, Guatemala', 10000, 'Activo'),
('Centro de Acopio Occidente', 'San Marcos, Guatemala', 10000, 'Activo');

INSERT INTO productores (nombre, telefono, direccion, departamento, estado) VALUES
('Finca San Jose', '5520-1001', 'Huehuetenango km 260', 'Huehuetenango', 'Activo'),
('Ganaderia El Rosario', '5520-1002', 'Quetzaltenango, Salcaja', 'Quetzaltenango', 'Activo'),
('Rancho Los Pinos', '5520-1003', 'Escuintla, Masagua', 'Escuintla', 'Activo'),
('Finca La Esperanza', '5520-1004', 'Santa Rosa, Cuilapa', 'Santa Rosa', 'Activo'),
('Ganaderia Oriente S.A.', '5520-1005', 'Zacapa, Cabanas', 'Zacapa', 'Activo'),
('Rancho El Progreso', '5520-1006', 'Chiquimula, San Jacinto', 'Chiquimula', 'Activo'),
('Finca Las Margaritas', '5520-1007', 'San Marcos, Malacatan', 'San Marcos', 'Activo'),
('Hacienda San Pedro', '5520-1008', 'Solola, San Lucas Toliman', 'Solola', 'Activo'),
('Ganaderia Los Altos', '5520-1009', 'Quetzaltenango, Genova', 'Quetzaltenango', 'Activo'),
('Finca Santa Cecilia', '5520-1010', 'Jalapa, Monjas', 'Jalapa', 'Activo'),
('Rancho El Valle', '5520-1011', 'Escuintla, San Vicente Pacaya', 'Escuintla', 'Activo'),
('Finca Don Carlos', '5520-1012', 'Zacapa, Gualan', 'Zacapa', 'Activo');

-- Lotes Enero-Junio 2025
INSERT INTO lotes (codigo_lote, fecha_registro, volumen_litros, estado_lote, productor_id, centro_id, responsable_recepcion) VALUES
('LP-2025-0001','2025-01-05',3200,'Procesado',1,1,'Sofia Hernandez'),
('LP-2025-0002','2025-01-08',2850,'Procesado',3,2,'Carmen Fuentes'),
('LP-2025-0003','2025-01-10',3100,'Procesado',5,3,'Sofia Hernandez'),
('LP-2025-0004','2025-01-14',2600,'Procesado',7,4,'Carmen Fuentes'),
('LP-2025-0005','2025-01-18',3400,'Procesado',2,1,'Sofia Hernandez'),
('LP-2025-0006','2025-02-03',3050,'Procesado',4,2,'Carmen Fuentes'),
('LP-2025-0007','2025-02-07',2900,'Procesado',6,3,'Sofia Hernandez'),
('LP-2025-0008','2025-02-12',3300,'Procesado',8,4,'Carmen Fuentes'),
('LP-2025-0009','2025-02-17',2750,'Procesado',9,1,'Sofia Hernandez'),
('LP-2025-0010','2025-02-22',3150,'Procesado',10,2,'Carmen Fuentes'),
('LP-2025-0011','2025-03-04',3400,'Procesado',1,1,'Sofia Hernandez'),
('LP-2025-0012','2025-03-08',3250,'Procesado',11,2,'Carmen Fuentes'),
('LP-2025-0013','2025-03-13',2980,'Procesado',12,3,'Sofia Hernandez'),
('LP-2025-0014','2025-03-18',3100,'Procesado',7,4,'Carmen Fuentes'),
('LP-2025-0015','2025-03-25',3600,'Procesado',2,1,'Sofia Hernandez'),
('LP-2025-0016','2025-04-02',3200,'Procesado',3,2,'Carmen Fuentes'),
('LP-2025-0017','2025-04-07',3050,'Procesado',5,3,'Sofia Hernandez'),
('LP-2025-0018','2025-04-12',2850,'Rechazado',6,3,'Sofia Hernandez'),
('LP-2025-0019','2025-04-16',3400,'Procesado',8,4,'Carmen Fuentes'),
('LP-2025-0020','2025-04-21',3100,'Procesado',9,1,'Sofia Hernandez'),
('LP-2025-0021','2025-05-05',3500,'Procesado',10,2,'Carmen Fuentes'),
('LP-2025-0022','2025-05-09',2900,'Procesado',11,3,'Sofia Hernandez'),
('LP-2025-0023','2025-05-14',3300,'Procesado',12,4,'Carmen Fuentes'),
('LP-2025-0024','2025-05-19',3150,'Procesado',1,1,'Sofia Hernandez'),
('LP-2025-0025','2025-05-24',2800,'Rechazado',4,2,'Carmen Fuentes'),
('LP-2025-0026','2025-06-03',3600,'Procesado',2,1,'Sofia Hernandez'),
('LP-2025-0027','2025-06-09',3200,'Procesado',5,3,'Sofia Hernandez'),
('LP-2025-0028','2025-06-13',3050,'Procesado',7,4,'Carmen Fuentes'),
('LP-2025-0029','2025-06-18',3400,'Procesado',9,1,'Sofia Hernandez'),
('LP-2025-0030','2025-06-25',3100,'Pendiente de análisis',3,2,'Carmen Fuentes');

INSERT INTO analisis_calidad (lote_id,temperatura,olor,color,acidez,densidad,prueba_alcohol,resultado,fecha_analisis,responsable_calidad) VALUES
(1,4.2,'Normal','Blanco uniforme',0.16,1.030,'Negativa','Aprobado','2025-01-05','Ana Lucia Torres'),
(2,3.8,'Normal','Blanco uniforme',0.17,1.031,'Negativa','Aprobado','2025-01-08','Patricia Lopez'),
(3,4.5,'Normal','Blanco uniforme',0.16,1.029,'Negativa','Aprobado','2025-01-10','Ana Lucia Torres'),
(4,4.0,'Normal','Blanco uniforme',0.17,1.030,'Negativa','Aprobado','2025-01-14','Patricia Lopez'),
(5,3.9,'Normal','Blanco uniforme',0.15,1.032,'Negativa','Aprobado','2025-01-18','Ana Lucia Torres'),
(6,4.1,'Normal','Blanco uniforme',0.16,1.031,'Negativa','Aprobado','2025-02-03','Ana Lucia Torres'),
(7,4.3,'Normal','Blanco uniforme',0.17,1.030,'Negativa','Aprobado','2025-02-07','Patricia Lopez'),
(8,3.7,'Normal','Blanco uniforme',0.15,1.033,'Negativa','Aprobado','2025-02-12','Ana Lucia Torres'),
(9,4.6,'Normal','Blanco uniforme',0.18,1.029,'Negativa','Aprobado','2025-02-17','Patricia Lopez'),
(10,4.0,'Normal','Blanco uniforme',0.16,1.031,'Negativa','Aprobado','2025-02-22','Ana Lucia Torres'),
(11,3.8,'Normal','Blanco uniforme',0.15,1.032,'Negativa','Aprobado','2025-03-04','Patricia Lopez'),
(12,4.2,'Normal','Blanco uniforme',0.16,1.030,'Negativa','Aprobado','2025-03-08','Ana Lucia Torres'),
(13,4.5,'Normal','Blanco uniforme',0.17,1.031,'Negativa','Aprobado','2025-03-13','Patricia Lopez'),
(14,4.0,'Normal','Blanco uniforme',0.16,1.030,'Negativa','Aprobado','2025-03-18','Ana Lucia Torres'),
(15,3.9,'Normal','Blanco uniforme',0.15,1.033,'Negativa','Aprobado','2025-03-25','Patricia Lopez'),
(16,4.1,'Normal','Blanco uniforme',0.16,1.031,'Negativa','Aprobado','2025-04-02','Ana Lucia Torres'),
(17,4.3,'Normal','Blanco uniforme',0.17,1.030,'Negativa','Aprobado','2025-04-07','Patricia Lopez'),
(18,7.2,'Anormal','Alterado',0.28,1.027,'Positiva','Rechazado','2025-04-12','Ana Lucia Torres'),
(19,4.0,'Normal','Blanco uniforme',0.16,1.032,'Negativa','Aprobado','2025-04-16','Patricia Lopez'),
(20,3.8,'Normal','Blanco uniforme',0.15,1.031,'Negativa','Aprobado','2025-04-21','Ana Lucia Torres'),
(21,4.2,'Normal','Blanco uniforme',0.16,1.030,'Negativa','Aprobado','2025-05-05','Patricia Lopez'),
(22,4.4,'Normal','Blanco uniforme',0.17,1.031,'Negativa','Aprobado','2025-05-09','Ana Lucia Torres'),
(23,3.9,'Normal','Blanco uniforme',0.15,1.032,'Negativa','Aprobado','2025-05-14','Patricia Lopez'),
(24,4.1,'Normal','Blanco uniforme',0.16,1.030,'Negativa','Aprobado','2025-05-19','Ana Lucia Torres'),
(25,8.1,'Anormal','Alterado',0.31,1.026,'Positiva','Rechazado','2025-05-24','Patricia Lopez'),
(26,3.8,'Normal','Blanco uniforme',0.15,1.033,'Negativa','Aprobado','2025-06-03','Ana Lucia Torres'),
(27,4.2,'Normal','Blanco uniforme',0.16,1.031,'Negativa','Aprobado','2025-06-09','Patricia Lopez'),
(28,4.5,'Normal','Blanco uniforme',0.17,1.030,'Negativa','Aprobado','2025-06-13','Ana Lucia Torres'),
(29,4.0,'Normal','Blanco uniforme',0.16,1.032,'Negativa','Aprobado','2025-06-18','Patricia Lopez');

INSERT INTO produccion (lote_id,temperatura_proceso,tiempo_proceso,fecha_produccion,estado,responsable_produccion) VALUES
(1,72.5,15,'2025-01-06','Completado','Jorge Ramirez'),
(2,72.3,15,'2025-01-09','Completado','Diego Morales'),
(3,72.6,15,'2025-01-11','Completado','Jorge Ramirez'),
(4,72.4,15,'2025-01-15','Completado','Diego Morales'),
(5,72.5,15,'2025-01-19','Completado','Jorge Ramirez'),
(6,72.3,15,'2025-02-04','Completado','Jorge Ramirez'),
(7,72.6,15,'2025-02-08','Completado','Diego Morales'),
(8,72.4,15,'2025-02-13','Completado','Jorge Ramirez'),
(9,72.5,15,'2025-02-18','Completado','Diego Morales'),
(10,72.3,15,'2025-02-23','Completado','Jorge Ramirez'),
(11,72.6,15,'2025-03-05','Completado','Diego Morales'),
(12,72.5,15,'2025-03-09','Completado','Jorge Ramirez'),
(13,72.4,15,'2025-03-14','Completado','Diego Morales'),
(14,72.3,15,'2025-03-19','Completado','Jorge Ramirez'),
(15,72.6,15,'2025-03-26','Completado','Diego Morales'),
(16,72.5,15,'2025-04-03','Completado','Jorge Ramirez'),
(17,72.4,15,'2025-04-08','Completado','Diego Morales'),
(19,72.5,15,'2025-04-17','Completado','Jorge Ramirez'),
(20,72.3,15,'2025-04-22','Completado','Diego Morales'),
(21,72.6,15,'2025-05-06','Completado','Jorge Ramirez'),
(22,72.4,15,'2025-05-10','Completado','Diego Morales'),
(23,72.5,15,'2025-05-15','Completado','Jorge Ramirez'),
(24,72.3,15,'2025-05-20','Completado','Diego Morales'),
(26,72.6,15,'2025-06-04','Completado','Jorge Ramirez'),
(27,72.5,15,'2025-06-10','Completado','Diego Morales'),
(28,72.4,15,'2025-06-14','Completado','Jorge Ramirez'),
(29,72.3,15,'2025-06-19','Completado','Diego Morales');

INSERT INTO inventario (producto,presentacion,cantidad,fecha_registro,origen,lote_id,ubicacion,estado) VALUES
('Leche Pasteurizada','1L',8500,'2025-06-01','Planta Central',26,'Bodega A','En almacén'),
('Leche Pasteurizada','500ml',4200,'2025-06-01','Planta Central',27,'Bodega A','En almacén'),
('Leche Pasteurizada','1L',6300,'2025-06-10','Planta Central',27,'Bodega B','En almacén'),
('Leche Pasteurizada','500ml',3100,'2025-06-10','Planta Central',28,'Bodega B','En almacén'),
('Leche Pasteurizada','1L',7200,'2025-06-15','Planta Central',28,'Bodega A','En almacén'),
('Leche Pasteurizada','1L',5400,'2025-06-20','Planta Central',29,'Bodega C','Reservado'),
('Leche Pasteurizada','500ml',2800,'2025-06-20','Planta Central',29,'Bodega C','En almacén'),
('Leche Pasteurizada','1L',3200,'2025-06-25','Planta Central',29,'Bodega A','En almacén'),
('Leche Pasteurizada','250ml',9800,'2025-06-22','Planta Central',26,'Bodega B','En almacén');

INSERT INTO distribucion (cliente,producto,presentacion,cantidad,fecha_salida,responsable,origen_lote,estado) VALUES
('Walmart Guatemala - Zona 10','Leche Pasteurizada','1L',2000,'2025-01-20','Luis Garcia','LP-2025-0001','Entregado'),
('La Torre Supermercados','Leche Pasteurizada','500ml',1500,'2025-01-22','Luis Garcia','LP-2025-0002','Entregado'),
('Walmart Guatemala - Zona 12','Leche Pasteurizada','1L',1800,'2025-02-05','Luis Garcia','LP-2025-0003','Entregado'),
('Supermercado Paiz - Mixco','Leche Pasteurizada','500ml',1200,'2025-02-10','Luis Garcia','LP-2025-0004','Entregado'),
('Despensa Familiar - Zona 7','Leche Pasteurizada','1L',2200,'2025-02-24','Luis Garcia','LP-2025-0005','Entregado'),
('Walmart Guatemala - Zona 1','Leche Pasteurizada','1L',1900,'2025-03-06','Luis Garcia','LP-2025-0006','Entregado'),
('La Torre Supermercados','Leche Pasteurizada','500ml',1400,'2025-03-11','Luis Garcia','LP-2025-0007','Entregado'),
('Supermercado Paiz - Villa Nueva','Leche Pasteurizada','1L',2100,'2025-03-20','Luis Garcia','LP-2025-0008','Entregado'),
('Walmart Guatemala - Zona 18','Leche Pasteurizada','500ml',1600,'2025-03-27','Luis Garcia','LP-2025-0009','Entregado'),
('Despensa Familiar - Zona 12','Leche Pasteurizada','1L',2400,'2025-04-04','Luis Garcia','LP-2025-0010','Entregado'),
('Walmart Guatemala - Zona 10','Leche Pasteurizada','1L',2500,'2025-04-09','Luis Garcia','LP-2025-0011','Entregado'),
('La Torre Supermercados','Leche Pasteurizada','500ml',1300,'2025-04-18','Luis Garcia','LP-2025-0012','Entregado'),
('Supermercado Paiz - Mixco','Leche Pasteurizada','1L',2000,'2025-04-23','Luis Garcia','LP-2025-0013','Entregado'),
('Walmart Guatemala - Zona 14','Leche Pasteurizada','250ml',3000,'2025-05-07','Luis Garcia','LP-2025-0014','Entregado'),
('Despensa Familiar - Zona 7','Leche Pasteurizada','1L',1800,'2025-05-11','Luis Garcia','LP-2025-0015','Entregado'),
('Walmart Guatemala - Zona 1','Leche Pasteurizada','1L',2300,'2025-05-16','Luis Garcia','LP-2025-0016','Entregado'),
('La Torre Supermercados','Leche Pasteurizada','500ml',1700,'2025-05-21','Luis Garcia','LP-2025-0017','Entregado'),
('Supermercado Paiz - Villa Nueva','Leche Pasteurizada','1L',2100,'2025-06-05','Luis Garcia','LP-2025-0019','Entregado'),
('Walmart Guatemala - Zona 12','Leche Pasteurizada','500ml',1900,'2025-06-11','Luis Garcia','LP-2025-0020','Entregado'),
('Despensa Familiar - Zona 12','Leche Pasteurizada','250ml',4200,'2025-06-15','Luis Garcia','LP-2025-0021','Entregado'),
('Walmart Guatemala - Zona 10','Leche Pasteurizada','1L',2600,'2025-06-20','Luis Garcia','LP-2025-0022','Entregado'),
('La Torre Supermercados','Leche Pasteurizada','1L',2000,'2025-06-21','Luis Garcia','LP-2025-0023','Entregado'),
('Supermercado Paiz - Mixco','Leche Pasteurizada','500ml',1500,'2025-06-22','Luis Garcia','LP-2025-0024','Entregado'),
('Walmart Guatemala - Zona 18','Leche Pasteurizada','250ml',3500,'2025-06-23','Luis Garcia','LP-2025-0026','Entregado'),
('Despensa Familiar - Zona 7','Leche Pasteurizada','1L',1700,'2025-06-24','Luis Garcia','LP-2025-0027','Entregado');

INSERT INTO alertas (lote_id,tipo_alerta,descripcion,fecha_alerta,estado) VALUES
(18,'Lote rechazado','Lote LP-2025-0018 rechazado: prueba de alcohol positiva, acidez 0.28%. Lote destruido.','2025-04-12','Resuelta'),
(25,'Lote rechazado','Lote LP-2025-0025 rechazado: olor anormal, acidez 0.31%. Proveedor notificado.','2025-05-24','Resuelta'),
(NULL,'Inventario bajo','Nivel critico Leche 500ml en Bodega C. Solicitar reposicion.','2025-05-30','Resuelta'),
(NULL,'Mantenimiento','Pasteurizador HTST: mantenimiento preventivo programado 2025-06-01.','2025-05-29','Resuelta'),
(30,'Proceso','Lote LP-2025-0030 pendiente de analisis de calidad.','2025-06-25','Activa'),
(NULL,'Inventario bajo','Stock Leche 1L supera 80% capacidad bodega A. Acelerar distribucion.','2025-06-20','Activa'),
(NULL,'Mantenimiento','Calibracion trimestral equipo MilkoScan programada para 2025-07-01.','2025-06-28','En revisión');
