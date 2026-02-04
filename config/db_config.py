# config/db_config.py
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables desde .env (en la raíz del proyecto)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

_engine = None  # lazy singleton

def get_engine():
    """
    Crea y retorna el engine SOLO cuando se necesita (USE_DB=1).
    Así el proyecto puede correr en modo demo sin BD.
    """
    global _engine
    if _engine is not None:
        return _engine

    server   = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    driver   = os.getenv("ODBC_DRIVER", "ODBC Driver 17 for SQL Server")

    if not all([server, database, username, password]):
        raise ValueError("Faltan variables de BD en .env (DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD).")

    username_q = quote_plus(username)
    password_q = quote_plus(password)
    driver_q   = quote_plus(driver)

    conn_url = (
        f"mssql+pyodbc://{username_q}:{password_q}@{server}/{database}"
        f"?driver={driver_q}&Encrypt=yes&TrustServerCertificate=no&Connection Timeout=30"
    )

    _engine = create_engine(conn_url, fast_executemany=True)
    return _engine


def run_query(sql: str):
    """Ejecuta una consulta SQL y devuelve un DataFrame."""
    import pandas as pd
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


def test_connection():
    """Prueba de conexión a la base de datos (usar manualmente, NO en flujo demo)."""
    try:
        engine = get_engine()
        with engine.begin() as con:
            row = con.execute(
                text("SELECT DB_NAME() AS db, SUSER_SNAME() AS who, GETDATE() AS ahora")
            ).one()
            print(f"Conexión OK | DB: {row.db} | Usuario: {row.who} | {row.ahora}")
    except Exception as e:
        print(f"Error de conexión: {e}")
