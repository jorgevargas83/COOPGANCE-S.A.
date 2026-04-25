import sqlite3

DB_NAME = "coopgance.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def agregar_columna_si_no_existe(cur, tabla, columna, definicion):
    columnas = [col[1] for col in cur.execute(f"PRAGMA table_info({tabla})").fetchall()]
    if columna not in columnas:
        cur.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL,
        estado TEXT NOT NULL DEFAULT 'Activo'
    );

    CREATE TABLE IF NOT EXISTS productores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        direccion TEXT,
        estado TEXT NOT NULL DEFAULT 'Activo'
    );

    CREATE TABLE IF NOT EXISTS centros_acopio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        ubicacion TEXT,
        estado TEXT NOT NULL DEFAULT 'Activo'
    );

    CREATE TABLE IF NOT EXISTS lotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_lote TEXT UNIQUE NOT NULL,
        fecha_registro TEXT NOT NULL,
        volumen_litros REAL NOT NULL,
        estado_lote TEXT NOT NULL,
        productor_id INTEGER NOT NULL,
        centro_id INTEGER NOT NULL,
        responsable_recepcion TEXT DEFAULT 'No registrado',
        FOREIGN KEY (productor_id) REFERENCES productores(id),
        FOREIGN KEY (centro_id) REFERENCES centros_acopio(id)
    );

    CREATE TABLE IF NOT EXISTS analisis_calidad (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lote_id INTEGER NOT NULL,
        temperatura REAL NOT NULL,
        olor TEXT NOT NULL,
        color TEXT NOT NULL,
        acidez REAL NOT NULL,
        densidad REAL NOT NULL,
        prueba_alcohol TEXT NOT NULL,
        resultado TEXT NOT NULL,
        fecha_analisis TEXT NOT NULL,
        responsable_calidad TEXT DEFAULT 'No registrado',
        FOREIGN KEY (lote_id) REFERENCES lotes(id)
    );

    CREATE TABLE IF NOT EXISTS alertas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lote_id INTEGER,
        tipo_alerta TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        fecha_alerta TEXT NOT NULL,
        estado TEXT NOT NULL DEFAULT 'Activa',
        FOREIGN KEY (lote_id) REFERENCES lotes(id)
    );

    CREATE TABLE IF NOT EXISTS produccion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lote_id INTEGER NOT NULL,
        temperatura_proceso REAL NOT NULL,
        tiempo_proceso INTEGER NOT NULL,
        fecha_produccion TEXT NOT NULL,
        estado TEXT NOT NULL,
        responsable_produccion TEXT DEFAULT 'No registrado',
        FOREIGN KEY (lote_id) REFERENCES lotes(id)
    );

    CREATE TABLE IF NOT EXISTS inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        fecha_registro TEXT NOT NULL,
        origen TEXT NOT NULL,
        ubicacion TEXT DEFAULT 'Cámara Fría 1 - Rack A',
        estado TEXT DEFAULT 'En almacén'
    );

    CREATE TABLE IF NOT EXISTS distribucion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT NOT NULL,
        producto TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        fecha_salida TEXT NOT NULL,
        responsable TEXT NOT NULL,
        inventario_id INTEGER,
        origen_lote TEXT
    );
    """)

    agregar_columna_si_no_existe(cur, "lotes", "responsable_recepcion", "TEXT DEFAULT 'No registrado'")
    agregar_columna_si_no_existe(cur, "analisis_calidad", "responsable_calidad", "TEXT DEFAULT 'No registrado'")
    agregar_columna_si_no_existe(cur, "produccion", "responsable_produccion", "TEXT DEFAULT 'No registrado'")
    agregar_columna_si_no_existe(cur, "inventario", "ubicacion", "TEXT DEFAULT 'Cámara Fría 1 - Rack A'")
    agregar_columna_si_no_existe(cur, "inventario", "estado", "TEXT DEFAULT 'En almacén'")
    agregar_columna_si_no_existe(cur, "distribucion", "inventario_id", "INTEGER")
    agregar_columna_si_no_existe(cur, "distribucion", "origen_lote", "TEXT")

    admin = cur.execute("SELECT * FROM usuarios WHERE usuario = ?", ("admin",)).fetchone()
    if not admin:
        cur.execute("""
            INSERT INTO usuarios (nombre, usuario, password, rol)
            VALUES (?, ?, ?, ?)
        """, ("Administrador General", "admin", "1234", "Administrador"))

    productores = cur.execute("SELECT COUNT(*) AS total FROM productores").fetchone()["total"]
    if productores == 0:
        cur.executemany("""
            INSERT INTO productores (nombre, telefono, direccion)
            VALUES (?, ?, ?)
        """, [
            ("Productor Norte 1", "5555-1001", "Zona Norte"),
            ("Productor Sur 1", "5555-1002", "Zona Sur"),
            ("Productor Oriente 1", "5555-1003", "Zona Oriente"),
            ("Productor Occidente 1", "5555-1004", "Zona Occidente")
        ])

    centros = cur.execute("SELECT COUNT(*) AS total FROM centros_acopio").fetchone()["total"]
    if centros == 0:
        cur.executemany("""
            INSERT INTO centros_acopio (nombre, ubicacion)
            VALUES (?, ?)
        """, [
            ("Centro de Acopio Norte", "Guatemala"),
            ("Centro de Acopio Sur", "Guatemala"),
            ("Centro de Acopio Oriente", "Guatemala"),
            ("Centro de Acopio Occidente", "Guatemala")
        ])

    conn.commit()
    conn.close()