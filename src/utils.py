# src/json_utils.py
"""
Utilidades para convertir DataFrames a JSON "listo para IA" o para persistencia.
Incluye:
- Reordenamiento de columnas (HASTA..., años, Total, %, resto)
- Envío de filas TOTAL ... al final
- Coerción segura de números desde strings con puntos/ comas y porcentajes
- Soporte para índices simples y MultiIndex
"""

from __future__ import annotations
import json
import pandas as pd
import numpy as np

# --- helpers de orden ---
def _ordenar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    preferidas = ["HASTA 2021", "HASTA 2022", "HASTA 2023", "HASTA 2024", "HASTA 2025"]
    cols = [str(c) for c in df.columns]
    hasta_cols = [c for c in preferidas if c in cols] or [c for c in cols if c.upper().startswith("HASTA ")]
    anios = sorted([c for c in cols if c.isdigit()], key=int)
    total = ["Total general"] if "Total general" in cols else []
    resto = [c for c in cols if c not in (hasta_cols + anios + total + ["%"])]
    pct = ["%"] if "%" in cols else []
    orden = hasta_cols + anios + total + resto + pct
    return df[orden] if orden else df

# --- detectar y mover totales (cualquier TOTAL ...) al final ---
TOTAL_KEYS = {"total general", "total territorial", "total central", "total global"}

def _mover_totales_al_final(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.index, pd.MultiIndex):
        mask = pd.Series(
            [any(str(i).strip().lower() in TOTAL_KEYS for i in idx) for idx in df.index],
            index=df.index
        )
        if mask.any():
            total = df.loc[mask]
            cuerpo = df.loc[~mask]
            return pd.concat([cuerpo, total])
        return df
    else:
        idx_str = df.index.astype(str).str.strip().str.lower()
        mask = idx_str.isin(TOTAL_KEYS)
        if mask.any():
            total = df.loc[mask]
            cuerpo = df.loc[~mask]
            return pd.concat([cuerpo, total])
        return df

# --- coerción numérica segura (para tablas "bonitas") ---
def _to_number_if_possible(v):
    if isinstance(v, (int, float, np.integer, np.floating)) and not pd.isna(v):
        return int(v) if float(v).is_integer() else float(v)
    if isinstance(v, str):
        s = v.strip().replace(".", "").replace(",", ".")
        if s.endswith("%"):
            s = s[:-1].strip()
        try:
            f = float(s)
            return int(f) if f.is_integer() else f
        except ValueError:
            return v
    return v

def _es_num(x):
    return isinstance(x, (int, float, np.integer, np.floating)) and not pd.isna(x)

# --- función principal ---
def dataframe_a_json_tabla(
    df: pd.DataFrame,
    nombre_tabla: str = "tabla",
    redondeo_pct: int = 2,
    coerce_numeric_from_str: bool = False
) -> str:
    """
    Convierte un DataFrame en JSON listo para OpenAI.

    - Reordena columnas (HASTA..., años, Total general, resto, %)
    - Mueve filas TOTAL ... al final (TERRITORIAL/CENTRAL/GENERAL)
    - Si coerce_numeric_from_str=True, convierte '40.818' -> 40818 y '82,30' -> 82.3
    """
    t = df.copy()
    t = _ordenar_columnas(t)
    t = _mover_totales_al_final(t)

    if coerce_numeric_from_str:
        for c in t.columns:
            t[c] = t[c].apply(_to_number_if_possible)

    # Índices
    if isinstance(t.index, pd.MultiIndex):
        idx_names = [n if n is not None else f"index_{i}" for i, n in enumerate(t.index.names)]
        idx_as_records = [dict(zip(idx_names, idx)) for idx in t.index]
    else:
        idx_names = [t.index.name or "index"]
        idx_as_records = [{idx_names[0]: i} for i in t.index]

    cols = [str(c) for c in t.columns]
    rows = []
    for rec, (_, row) in zip(idx_as_records, t.iterrows()):
        out = dict(rec)
        for c in cols:
            v = row[c]
            if c == '%' and _es_num(v):
                out[c] = round(float(v), redondeo_pct)
            elif _es_num(v):
                fv = float(v)
                out[c] = int(fv) if fv.is_integer() else fv
            else:
                out[c] = None if pd.isna(v) else v
        rows.append(out)

    payload = {
        "name": nombre_tabla,
        "index_names": idx_names,
        "columns": cols,
        "rows": rows,
    }
    return json.dumps(payload, ensure_ascii=False)

def guardar_json_tabla(df: pd.DataFrame, ruta_salida: str, **kwargs) -> None:
    """Guarda el JSON generado por `dataframe_a_json_tabla` en un archivo."""
    json_str = dataframe_a_json_tabla(df, **kwargs)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(json_str)