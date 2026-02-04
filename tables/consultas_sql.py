from config.db_config import get_engine
from sqlalchemy import text
import pandas as pd
from pathlib import Path

def cargar_improd():
    query = """
    SELECT [ID_CASO],
           [IUS],
           [IUC],
           [FECHA_PGN],
           [FECHA_PRESCRIPCION],
           [ESTADO_CASO],
           [DEPENDENCIA_TITULAR],
           [ETAPA_ACTUAL],
           [NIVEL_TERRITORIAL],
           [TIPO_DEPENDENCIA],
           [ETAPA_PROCESO],
           [ETAPA_HOMOLOGADA],
           [RIESGO],
           [IMPROD],
           [ANIO_PGN]
    FROM [EXT].[IMPROD_DISCIPLINARIO];
    """
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql_query(text(query), conn)
    return df

def exportar_improd_a_csv(ruta_csv: str = "data/sample_improd.csv"):
    """
    Ejecuta la consulta real a la BD y guarda un CSV demo.
    ⚠️ Usar SOLO una vez (no subir credenciales).
    """
    df = cargar_improd()

    # Asegurar carpeta data
    ruta = Path(ruta_csv)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    # Guardar CSV
    df.to_csv(ruta, index=False, encoding="utf-8-sig")

    print(f"✅ CSV demo generado en: {ruta.resolve()}")