"""
COOPGANCE S.A. - Capa de acceso a datos para Supabase (PostgreSQL)
-------------------------------------------------------------------
Reemplazo directo del archivo database.py original (que usaba SQLite).

INSTRUCCION IMPORTANTE:
  Pegar tu URL de Supabase en la variable DATABASE_URL de abajo (linea 25).
  La URL se obtiene desde:
    Supabase Dashboard -> Project Settings -> Database -> Connection string -> URI
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor


# =====================================================================
# >>> CONFIGURACION: PEGAR TU URL DE SUPABASE AQUI <<<
# =====================================================================
# Reemplaza toda la cadena entre comillas con la tuya.
# Ejemplo real: "postgresql://postgres.abcdef:MiPassword123@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres.oqdxnbaxoonqdedfhpjt:vARANAa1597@aws-1-us-east-2.pooler.supabase.com:6543/postgres")

# =====================================================================


# --- Wrappers para emular la API de sqlite3 ---

class _CursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def __iter__(self):
        return iter(self._cursor)

    def close(self):
        try:
            self._cursor.close()
        except Exception:
            pass


class _ConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def execute(self, query, params=()):
        query = query.replace("?", "%s")
        cursor = self._conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        return _CursorWrapper(cursor)

    def executemany(self, query, seq_of_params):
        query = query.replace("?", "%s")
        cursor = self._conn.cursor()
        try:
            cursor.executemany(query, seq_of_params)
        finally:
            cursor.close()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass


# --- Conexion ---

def get_db_connection():
    url = DATABASE_URL

    if "TUPROYECTO" in url or "TUPASSWORD" in url:
        raise RuntimeError(
            "\n\n"
            "========================================================\n"
            "  ERROR: No has configurado tu URL de Supabase.\n"
            "========================================================\n"
            "  Abre el archivo database.py y reemplaza la variable\n"
            "  DATABASE_URL (linea 25) con tu cadena de conexion real.\n"
            "\n"
            "  Como obtenerla:\n"
            "    1. Entrar a https://supabase.com -> tu proyecto\n"
            "    2. Project Settings -> Database\n"
            "    3. Connection string -> URI\n"
            "    4. Copiar la URL y reemplazar [YOUR-PASSWORD]\n"
            "========================================================\n"
        )

    raw_conn = psycopg2.connect(url, sslmode="require")
    return _ConnectionWrapper(raw_conn)


def init_db():
    """
    Las tablas se crean ejecutando supabase_schema.sql en el SQL Editor.
    Esta funcion solo verifica la conexion al iniciar la app.
    """
    try:
        conn = get_db_connection()
        result = conn.execute("SELECT 1 AS ok").fetchone()
        conn.close()
        if result and result.get("ok") == 1:
            print("[DB] Conexion a Supabase OK")
    except RuntimeError as e:
        print(str(e))
    except Exception as exc:
        print(f"[DB] ERROR de conexion: {exc}")
        print("[DB] Verifica tu DATABASE_URL y que ejecutaste supabase_schema.sql")
