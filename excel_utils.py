# excel_utils.py

import pandas as pd
from datetime import datetime

# Cargar el Excel una vez (ajusta si cambias el nombre o ubicación)
EXCEL_PATH = "Macro Raw File.xlsx"
df_excel = pd.read_excel(EXCEL_PATH, sheet_name="Sheet1")

# Limpieza de columnas
df_excel.columns = df_excel.columns.str.strip()
df_excel["Event Date"] = pd.to_datetime(df_excel["Event Date"], errors="coerce")
df_excel["Event"] = df_excel["Event"].astype(str).str.strip()
df_excel["Currency"] = df_excel["Currency"].astype(str).str.strip()

# Función para buscar los últimos N datos
def buscar_ultimos_datos_excel(evento, pais, n=3):
    filtro = (
        (df_excel["Currency"].str.upper() == pais.upper()) &
        (df_excel["Event"].str.contains(evento, case=False, na=False, regex=False)) &
        (~df_excel["Actual"].isna())
    )
    datos_filtrados = df_excel[filtro].sort_values(by="Event Date", ascending=False).head(n)

    if datos_filtrados.empty:
        return f"No se encontraron datos para el evento '{evento}' en '{pais}'."

    datos_ordenados = datos_filtrados.sort_values(by="Event Date")

    respuesta = f"📈 {evento} en {pais} – Últimos {n} datos:\n"
    for _, row in datos_ordenados.iterrows():
        fecha = row["Event Date"].strftime("%B %Y")
        valor = row["Actual"]
        respuesta += f"- {fecha}: {valor}\n"

    respuesta += "\n(Fuente: Base de datos local Excel)"
    return respuesta
