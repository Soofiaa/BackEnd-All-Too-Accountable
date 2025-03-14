import sqlite3

DB_NAME = "alltooaccountable.db"

def crear_tablas():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    # Tabla usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT NOT NULL,
            correo TEXT NOT NULL,
            contrasena TEXT NOT NULL,
            fecha_nacimiento TEXT NOT NULL
        )
    """)

    # Tabla categorias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL,
            id_usuario INTEGER NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        )
    """)

    # Tabla transacciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacciones (
            id_transaccion INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            monto REAL NOT NULL,
            categoria TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            tipo_pago TEXT NOT NULL,
            imagen TEXT,
            cuotas INTEGER,
            interes REAL,
            valor_cuota REAL,
            total_credito REAL,
            tipo TEXT NOT NULL, -- 'ingreso' o 'gasto'
            se_repite INTEGER,
            id_usuario INTEGER NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        )
    """)

    # Tabla gastos mensuales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos_mensuales (
            id_gasto INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL,
            id_usuario INTEGER NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        )
    """)

    # Tabla metas de ahorro
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metas_ahorro (
            id_meta INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            fecha_limite TEXT NOT NULL,
            monto_meta REAL NOT NULL,
            id_usuario INTEGER NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        )
    """)

    conexion.commit()
    conexion.close()
