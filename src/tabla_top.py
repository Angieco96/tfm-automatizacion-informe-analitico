import pandas as pd

def construir_tabla_top_dependencias(df: pd.DataFrame, filtro_improd: str = "disciplinarios") -> pd.DataFrame:
    """
    TOP 10 de DEPENDENCIAS por total, discriminado por ANIO_PGN tal cual
    (valores como 'HASTA 2021', '2022', '2023', ...). Sin fila TOTAL GENERAL.
    El % es sobre el total mostrado (Top 10).
    """
    # 1) Filtrar por IMPROD
    d = df[df["IMPROD"].str.contains(filtro_improd, case=False, na=False)].copy()
    if d.empty:
        return pd.DataFrame()

    # 2) Usar ANIO_PGN tal cual (nada de astype(int))
    d["_anio_bucket"] = d["ANIO_PGN"].astype(str).str.strip()

    # 3) Crosstab
    tabla = pd.crosstab(d["DEPENDENCIA_TITULAR"], d["_anio_bucket"])

    # 4) Asegurar orden de columnas
    orden = ["HASTA 2021", "2022", "2023", "2024", "2025"]
    tabla.columns = tabla.columns.astype(str)
    for c in orden:
        if c not in tabla.columns:
            tabla[c] = 0
    tabla = tabla[orden]

    # 5) Total y % global (del Top 10)
    tabla["Total general"] = tabla.sum(axis=1)
    tabla = tabla.sort_values("Total general", ascending=False).head(10)
    total = float(tabla["Total general"].sum())
    tabla["%"] = (tabla["Total general"] / total * 100).round(0).astype(int)

    # 6) Etiquetas + formato
    tabla.index.name = "DEPENDENCIAS"
    tabla.columns.name = "FECHA DE LA QUEJA"

    def fmt_miles(x): 
        try: return f"{int(x):,}".replace(",", ".")
        except: return x

    for c in orden + ["Total general"]:
        tabla[c] = tabla[c].astype(int).map(fmt_miles)
    tabla["%"] = tabla["%"].map(lambda v: f"{v:d}%")

    return tabla