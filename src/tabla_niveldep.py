def construir_tabla1(df, filtro_improd="disciplinarios"):
    """
    Construye tabla unida (TERRITORIAL + CENTRAL) a partir de un DataFrame.
    Incluye subtotales (TOTAL TERRITORIAL, TOTAL CENTRAL) y un TOTAL GENERAL.
    El porcentaje (%) es POR NIVEL: cada fila se calcula contra el subtotal de su bloque.
    El índice se renombra y el encabezado de columnas queda como 'AÑO_PGN'.
    Los enteros se muestran con separador de miles (punto) y % con coma.
    """
    import pandas as pd

    def construir_tabla_bloque(df_bloque, nombre_total):
        tabla = pd.crosstab(df_bloque['TIPO_DEPENDENCIA'], df_bloque['ANIO_PGN'])

        # Asegurar columnas ordenadas
        orden = ['HASTA 2021', '2022', '2023', '2024', '2025']
        tabla.columns = tabla.columns.astype(str)
        for c in orden:
            if c not in tabla.columns:
                tabla[c] = 0
        tabla = tabla[orden]

        # Totales por fila y subtotal del bloque
        tabla['Total general'] = tabla.sum(axis=1)
        total_row = tabla.sum(axis=0).to_frame().T
        total_row.index = [nombre_total]  # "TOTAL TERRITORIAL" o "TOTAL CENTRAL"
        tabla = pd.concat([tabla, total_row])

        tabla.index.name = "TIPO_DEPENDENCIA"
        return tabla

    # 1) Filtrar IMPROD
    df_filtrado = df[df['IMPROD'].str.contains(filtro_improd, case=False, na=False)]

    # 2) Construir bloques
    df_terr = df_filtrado[df_filtrado['NIVEL_TERRITORIAL'] == 'TERRITORIAL']
    df_cent = df_filtrado[df_filtrado['NIVEL_TERRITORIAL'] == 'CENTRAL']

    tabla_terr = construir_tabla_bloque(df_terr, "TOTAL TERRITORIAL") if not df_terr.empty else None
    tabla_cent = construir_tabla_bloque(df_cent, "TOTAL CENTRAL") if not df_cent.empty else None

    # 3) Unir en MultiIndex (solo lo que exista)
    partes = []
    if tabla_terr is not None:
        partes.append(('TERRITORIAL', tabla_terr))
    if tabla_cent is not None:
        partes.append(('CENTRAL', tabla_cent))

    if not partes:
        # No hay datos
        return pd.DataFrame()

    tabla_unida = pd.concat([p[1] for p in partes], keys=[p[0] for p in partes])

    # 4) % POR NIVEL: cada fila se divide por el subtotal de su nivel
    tabla_unida['%'] = 0.0  # columna numérica temporal
    for nivel in tabla_unida.index.get_level_values(0).unique():
        subtotal_name = f"TOTAL {nivel}"
        # Si el subtotal existe:
        if (nivel, subtotal_name) in tabla_unida.index:
            denom = float(tabla_unida.loc[(nivel, subtotal_name), 'Total general'])
            if denom > 0:
                idx_nivel = tabla_unida.index.get_level_values(0) == nivel
                # porcentaje por nivel
                tabla_unida.loc[idx_nivel, '%'] = (tabla_unida.loc[idx_nivel, 'Total general'] / denom * 100)
                # Asegurar 100% en el subtotal del nivel
                tabla_unida.loc[(nivel, subtotal_name), '%'] = 100.0

    # 5) TOTAL GENERAL (suma de subtotales de los niveles existentes)
    total_general = None
    if ('TERRITORIAL', 'TOTAL TERRITORIAL') in tabla_unida.index:
        total_general = tabla_unida.loc[('TERRITORIAL', 'TOTAL TERRITORIAL')].copy()
    if ('CENTRAL', 'TOTAL CENTRAL') in tabla_unida.index:
        if total_general is None:
            total_general = tabla_unida.loc[('CENTRAL', 'TOTAL CENTRAL')].copy()
        else:
            total_general = total_general + tabla_unida.loc[('CENTRAL', 'TOTAL CENTRAL')]

    if total_general is not None:
        total_general.name = ('TOTAL GENERAL', '')
        total_general['%'] = 100.0  # el total global se muestra como 100%

        # Concatenar al final
        tabla_final = pd.concat([tabla_unida, pd.DataFrame([total_general])])
    else:
        tabla_final = tabla_unida.copy()

    # 6) Nombres bonitos
    tabla_final.index.set_names(["NIVEL_TERRITORIAL", "TIPO_DEPENDENCIA"], inplace=True)
    tabla_final.columns.name = "AÑO_PGN"

    # 7) Formateo: miles con punto y % con coma (hacerlo al final, cuando ya no se calcula nada más)
    for col in tabla_final.columns:
        if col != '%':
            # asegurar int antes de formatear
            tabla_final[col] = tabla_final[col].astype(int).map(lambda x: f"{x:,}".replace(",", "."))
    tabla_final['%'] = tabla_final['%'].round(2).map(lambda x: f"{x:.2f}".replace(".", ","))

    return tabla_final