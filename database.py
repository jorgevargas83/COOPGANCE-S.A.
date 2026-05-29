"""
COOPGANCE S.A. - Conexion a Supabase (PostgreSQL)

INSTRUCCIONES:
  1. Copiar la URL de tu proyecto desde:
     Supabase Dashboard > Project Settings > Database > Connection string > URI
  2. Reemplazar DATABASE_URL con tu URL real
  3. Ejecutar supabase_schema.sql en el SQL Editor de Supabase
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres.oqdxnbaxoonqdedfhpjt:vARANAa1597@aws-1-us-east-2.pooler.supabase.com:6543/postgres"
)


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
        cursor = self._conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        return _CursorWrapper(cursor)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass


def get_db_connection():
    raw_conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    return _ConnectionWrapper(raw_conn)


def init_db():
    """Verifica la conexion al iniciar la app."""
    try:
        conn = get_db_connection()
        result = conn.execute("SELECT 1 AS ok").fetchone()
        conn.close()
        if result and result.get("ok") == 1:
            print("[COOPGANCE] ✅ Conexion a Supabase OK")
    except Exception as exc:
        print(f"[COOPGANCE] ❌ Error de conexion: {exc}")
        print("[COOPGANCE] Verifica DATABASE_URL y que ejecutaste supabase_schema.sql")
