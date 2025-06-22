import os
from dotenv import load_dotenv
from fredapi import Fred

# Cargar API Key desde .env
load_dotenv()
fred = Fred(api_key=os.getenv("FRED_API_KEY"))

# Fechas objetivo
fecha_actual = '2025-05-01'
fecha_mes_pasado = '2025-04-01'
fecha_hace_un_año = '2024-05-01'

# Obtener valores
cpi = fred.get_series('CPIAUCSL')
valor_actual = cpi[fecha_actual]
valor_mensual_pasado = cpi[fecha_mes_pasado]
valor_anual_pasado = cpi[fecha_hace_un_año]

# Calcular inflación
inflacion_mensual = round((valor_actual - valor_mensual_pasado) / valor_mensual_pasado * 100, 2)
inflacion_anual = round((valor_actual - valor_anual_pasado) / valor_anual_pasado * 100, 2)

# Respuesta natural
print(f"📊 El último dato del CPI fue en mayo 2025.")
print(f"📈 Inflación mensual: {inflacion_mensual}%")
print(f"📈 Inflación interanual: {inflacion_anual}%")

