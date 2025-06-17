import os
from dotenv import load_dotenv
from fredapi import Fred
from datetime import datetime
import calendar

load_dotenv()
fred = Fred(api_key=os.getenv("FRED_API_KEY"))

def obtener_inflacion_humana():
    serie = fred.get_series('CPIAUCNS')
    serie = serie.dropna()

    ultimo_mes = serie.index[-1]
    mes_texto = calendar.month_name[ultimo_mes.month]
    anio = ultimo_mes.year

    cpi_actual = serie.iloc[-1]
    cpi_anterior = serie.iloc[-2]
    cpi_anio_pasado = serie.loc[serie.index[-13]]

    inflacion_mensual = round(((cpi_actual - cpi_anterior) / cpi_anterior) * 100, 2)
    inflacion_anual = round(((cpi_actual - cpi_anio_pasado) / cpi_anio_pasado) * 100, 2)

    return f"""📊 El último dato del CPI fue en {mes_texto} {anio}.
📈 Inflación mensual: {inflacion_mensual}%  
📉 Inflación interanual: {inflacion_anual}%"""
