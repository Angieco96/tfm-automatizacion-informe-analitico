# src/prompt_payloads.py
import json
import pandas as pd
import numpy as np

def _to_number(v):
    # Convierte '40.818'->40818 ; '82,30'->82.3 ; '100'->100 ; deja texto si no aplica
    if isinstance(v, (int, float, np.integer, np.floating)) and not pd.isna(v):
        return float(v)
    if isinstance(v, str):
        s = v.strip().replace(".", "").replace(",", ".")
        if s.endswith("%"):
            s = s[:-1].strip()
        try:
            return float(s)
        except ValueError:
            return v
    return v

def construir_payload_resumen(json_tabla) -> dict:
    """
    Acepta str (JSON) o dict con la tabla unida (TERRITORIAL + CENTRAL).
    Espera columnas de años (incl. 'HASTA ...'), 'Total general' y '%'.
    Fila subtotal por bloque renombrada como 'TOTAL TERRITORIAL' / 'TOTAL CENTRAL'.
    Calcula totales por nivel, % mayores a 4 años y el año con más casos (global y por nivel).
    """
    data = json.loads(json_tabla) if isinstance(json_tabla, str) else json_tabla
    rows = pd.DataFrame(data["rows"])
    cols = list(data["columns"])

    # detectar 'HASTA ...'
    col_hasta = next((c for c in cols if str(c).strip().upper().startswith("HASTA ")), None)
    if not col_hasta:
        raise ValueError("No se encontró una columna que empiece por 'HASTA '.")

    # columnas índice exportadas
    nivel_col_candidates = ["index_0", "NIVEL_TERRITORIAL", "nivel_territorial"]
    dep_col_candidates = ["TIPO_DEPENDENCIA", "tipo_dependencia", "index_1", "index"]
    nivel_col = next((c for c in nivel_col_candidates if c in rows.columns), None)
    dep_col   = next((c for c in dep_col_candidates   if c in rows.columns), None)
    if nivel_col is None or dep_col is None:
        raise ValueError("Faltan columnas de nivel/dependencia en el JSON.")

    # numericidad
    rows["Total general"] = rows["Total general"].apply(_to_number)
    rows[col_hasta] = rows[col_hasta].apply(_to_number)

    # columnas año YYYY
    year_cols = []
    for c in cols:
        cs = str(c).strip()
        if cs.upper().startswith("HASTA ") or cs in ("Total general", "%"):
            continue
        if cs.isdigit() and len(cs) == 4:
            year_cols.append(cs)
    for yc in year_cols:
        rows[yc] = rows[yc].apply(_to_number)

    def subtotal_nivel(nivel: str):
        mask_total = (rows[nivel_col] == nivel) & (rows[dep_col].str.upper() == f"TOTAL {nivel}".upper())
        if mask_total.any():
            r = rows.loc[mask_total].iloc[0]
            tot   = float(r["Total general"])
            hasta = float(r[col_hasta])
            anhos = {yc: float(r[yc]) for yc in year_cols}
            return tot, hasta, anhos
        bloque = rows[(rows[nivel_col] == nivel) & (~rows[dep_col].str.upper().str.startswith("TOTAL "))]
        if bloque.empty:
            return 0.0, 0.0, {yc: 0.0 for yc in year_cols}
        tot   = float(bloque["Total general"].sum())
        hasta = float(bloque[col_hasta].sum())
        anhos = {yc: float(bloque[yc].sum()) for yc in year_cols}
        return tot, hasta, anhos

    niveles_payload, anhos_global = [], {yc: 0.0 for yc in year_cols}
    for nivel in ["TERRITORIAL", "CENTRAL"]:
        if not (rows[nivel_col] == nivel).any():
            continue
        total_nivel, hasta_nivel, anhos_nivel = subtotal_nivel(nivel)
        pct_hasta_nivel = round((hasta_nivel / total_nivel) * 100, 2) if total_nivel else 0.0
        for yc in year_cols:
            anhos_global[yc] += anhos_nivel.get(yc, 0.0)

        deps = rows[(rows[nivel_col] == nivel) & (~rows[dep_col].str.upper().str.startswith("TOTAL "))]
        if not deps.empty:
            deps = deps.copy()
            deps["pct"] = deps["Total general"].astype(float) / total_nivel * 100.0 if total_nivel else 0.0
            deps = deps.sort_values("pct", ascending=False)
            deps_list = [
                {"dependencia": r[dep_col],
                 "total": int(float(r["Total general"])),
                 "pct": round(float(r["pct"]), 2)}
                for _, r in deps.iterrows()
            ]
            top3 = deps_list[:3]
        else:
            deps_list, top3 = [], []

        anio_max_nivel = max(anhos_nivel.items(), key=lambda kv: kv[1]) if anhos_nivel else (None, 0)
        anio_max_reg = {"nivel": nivel, "anio": int(anio_max_nivel[0]) if anio_max_nivel[0] else None,
                        "total": int(anio_max_nivel[1])}

        niveles_payload.append({
            "nivel": nivel,
            "total": int(total_nivel),
            "mayores_4_anhos": int(hasta_nivel),
            "pct_mayores_4_anhos": pct_hasta_nivel,
            "dependencias": deps_list,
            "top3_dependencias": top3,
            "anio_max": anio_max_reg
        })

    if niveles_payload:
        total_general = sum(n["total"] for n in niveles_payload)
        mayores_4     = sum(n["mayores_4_anhos"] for n in niveles_payload)
    else:
        base = rows[~rows[dep_col].str.upper().str.startswith("TOTAL ")]
        total_general = int(float(base["Total general"].sum()))
        mayores_4     = int(float(base[col_hasta].sum()))
        for yc in year_cols:
            anhos_global[yc] = float(base[yc].sum())

    pct_mayores_4 = round((mayores_4 / total_general) * 100, 2) if total_general else 0.0
    anio_max_glob = max(anhos_global.items(), key=lambda kv: kv[1]) if anhos_global else (None, 0)
    anio_max = {"anio": int(anio_max_glob[0]) if anio_max_glob[0] else None, "total": int(anio_max_glob[1])}

    anio_max_por_nivel = [{"nivel": n["nivel"], "anio": n["anio_max"]["anio"], "total": n["anio_max"]["total"]}
                          for n in niveles_payload]

    return {
        "tabla": data.get("name", "tabla"),
        "corte_hasta": col_hasta,
        "total_activos": int(total_general),
        "mayores_4_anhos": int(mayores_4),
        "pct_mayores_4_anhos": pct_mayores_4,
        "anio_max": anio_max,
        "anio_max_por_nivel": anio_max_por_nivel,
        "niveles": niveles_payload
    }

def construir_payload_top_dependencias(json_tabla) -> dict:
    """
    Payload para tabla TOP 10 por DEPENDENCIA_TITULAR (sin niveles).
    Espera columnas: 'HASTA ...', años YYYY, 'Total general' y '%'.
    El índice exportado debe contener la dependencia (ej. 'DEPENDENCIAS').
    """
    data = json.loads(json_tabla) if isinstance(json_tabla, str) else json_tabla
    rows = pd.DataFrame(data["rows"])
    cols = [str(c) for c in data["columns"]]

    # --- detectar columna dependencia (viene del índice exportado por utils)
    dep_col_candidates = ["DEPENDENCIAS", "DEPENDENCIA_TITULAR", "index", "index_0"]
    dep_col = next((c for c in dep_col_candidates if c in rows.columns), None)
    if dep_col is None:
        raise ValueError("No se encontró la columna de dependencia en el JSON (ej. 'DEPENDENCIAS').")

    # --- detectar columna 'HASTA ...' (bucket de antigüedad)
    col_hasta = next((c for c in cols if str(c).strip().upper().startswith("HASTA ")), None)
    if not col_hasta:
        raise ValueError("No se encontró una columna que empiece por 'HASTA ' en la tabla TOP 10.")

    # --- detectar columnas de años YYYY (excluye HASTA, Total y %)
    year_cols = []
    for c in cols:
        cs = str(c).strip()
        if cs.upper().startswith("HASTA ") or cs in ("Total general", "%"):
            continue
        if cs.isdigit() and len(cs) == 4:
            year_cols.append(cs)

    # --- limpiar numéricos
    if "Total general" in rows.columns:
        rows["Total general"] = rows["Total general"].apply(_to_number)
    if "%" in rows.columns:
        rows["%"] = rows["%"].apply(_to_number)
    # columnas anuales
    rows[col_hasta] = rows[col_hasta].apply(_to_number)
    for yc in year_cols:
        if yc in rows.columns:
            rows[yc] = rows[yc].apply(_to_number)

    # --- quitar filas no deseadas si existieran (por si alguien metió un TOTAL GENERAL)
    mask_total = rows[dep_col].astype(str).str.upper().eq("TOTAL GENERAL")
    base = rows.loc[~mask_total].copy()

    # --- asegurar que sea realmente un TOP 10 (por si alguien entregó más)
    if "Total general" not in base.columns:
        raise ValueError("La tabla no tiene columna 'Total general'.")
    base = base.sort_values("Total general", ascending=False).head(10).reset_index(drop=True)

    # --- totales y ranking
    total_top = float(base["Total general"].sum())
    ranking = [
        {
            "dependencia": r[dep_col],
            "total": int(float(r["Total general"])) if pd.notna(r["Total general"]) else 0,
            "pct": round(float(r["Total general"]) / total_top * 100, 2) if total_top else 0.0
        }
        for _, r in base.iterrows()
    ]

    # top1 y concentración top3
    top1 = ranking[0] if ranking else {"dependencia": None, "total": 0, "pct": 0.0}
    top3_share = round(sum(x["pct"] for x in ranking[:3]), 2) if ranking else 0.0

    # --- distribución anual (suma de las 10 dependencias)
    dist_anual = {col_hasta: float(base[col_hasta].sum())}
    for yc in year_cols:
        dist_anual[yc] = float(base[yc].sum())

    # año (o bucket) con más casos (global del top)
    max_bucket = max(dist_anual.items(), key=lambda kv: kv[1]) if dist_anual else (None, 0.0)
    anio_max = {"bucket": max_bucket[0], "total": int(max_bucket[1]) if max_bucket[1] else 0}

    # --- año pico por cada dependencia (útil para narrativa)
    anio_pico_por_dep = []
    for _, r in base.iterrows():
        vec = {col_hasta: float(r[col_hasta])}
        for yc in year_cols:
            vec[yc] = float(r[yc])
        if vec:
            b, v = max(vec.items(), key=lambda kv: kv[1])
            anio_pico_por_dep.append({
                "dependencia": r[dep_col],
                "bucket": b,
                "total": int(v)
            })

    return {
        "tabla": data.get("name", "top_dependencias"),
        "corte_hasta": col_hasta,
        "total_top": int(total_top),
        "ranking_top10": ranking,            # lista de 10: {dependencia, total, pct}
        "top1": top1,                        # el líder del top
        "top3_share_pct": top3_share,        # concentración de las 3 primeras
        "distribucion_anual": dist_anual,    # { "HASTA 2021": X, "2022": Y, ... }
        "anio_max_global": anio_max,         # {bucket, total}
        "anio_pico_por_dependencia": anio_pico_por_dep  # lista por dependencia
    }
