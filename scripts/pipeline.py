import requests
import pandas as pd
import sqlite3

URL_ = "https://api.open-meteo.com/v1/forecast"
PARAMETROS = {
    'latitude': 19.43,
    'longitude': -99-13,
    "hourly": "temperature_2m,precipitation",
    "past_days": 7,
    "forecast_days": 0
}

def extraccion():
    try:
        response = requests.get(URL_, params=PARAMETROS)
        response.raise_for_status()
        data = response.json()
        hourly = data["hourly"]
        return hourly
    except requests.exceptions.ConnectionError:
        print("ERROR AL CONECTARSE A LA API")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"ERROR HTTP: {e}")
        return None


def transformacion_limpieza(hourly):

    df = pd.DataFrame({
        "fecha": hourly["time"],
        "temperatura_c": hourly["temperature_2m"],
        "precipitacion_mm": hourly["precipitation"]
    })

    df['fecha'] = pd.to_datetime(df["fecha"])
    df = df[df["fecha"].dt.hour.between(6,22)]


    nulos = df[["temperatura_c","precipitacion_mm"]].isnull().sum().sum()
    negativo = (df[["temperatura_c", "precipitacion_mm"]]<0).sum().sum()
    print(f"Nulos: {nulos}")
    print(f"Negativos: {negativo}")

    return df


def exportar_csv(df, ruta="../data/datos_clima_cdmx.csv"):
    df.to_csv(ruta, index=False)
    print(f"CSV exportado: {ruta} ({len(df)} registros)")

def cargar_sqlite(csv_path="../data/datos_clima_cdmx.csv", db_path="../data/clima_cdmx.db"):
    df = pd.read_csv(csv_path)
    conn = sqlite3.connect(db_path)
    df.to_sql("clima", conn, if_exists="replace", index=False)
    print(f"Datos cargados en SQLite: {len(df)} registros")
    conn.close()


def ejecutar_consultas(db_path="../data/clima_cdmx.db"):
    conn = sqlite3.connect(db_path)

    consultas = {
        "A - Temperatura promedio por día": """
            SELECT DATE(fecha) AS dia, ROUND(AVG(temperatura_c), 2) AS temp_promedio
            FROM clima GROUP BY DATE(fecha) ORDER BY temp_promedio DESC
        """,
        "B - Horas con precipitación > 0": """
            SELECT DATE(fecha) AS dia, TIME(fecha) AS hora, precipitacion_mm
            FROM clima WHERE precipitacion_mm > 0 ORDER BY fecha ASC
        """,
        "C - Día con mayor variación térmica": """
            SELECT DATE(fecha) AS dia, ROUND(MAX(temperatura_c) - MIN(temperatura_c), 2) AS variacion_termica
            FROM clima GROUP BY DATE(fecha) ORDER BY variacion_termica DESC LIMIT 1
        """,
        "D - Resumen diario": """
            SELECT DATE(fecha) AS dia, ROUND(MIN(temperatura_c), 2) AS temp_minima,
            ROUND(MAX(temperatura_c), 2) AS temp_maxima, ROUND(AVG(temperatura_c), 2) AS temp_promedio,
            ROUND(SUM(precipitacion_mm), 2) AS precipitacion_total
            FROM clima GROUP BY DATE(fecha) ORDER BY dia ASC
        """
    }

    for nombre, query in consultas.items():
        print(f"\n--- {nombre} ---")
        df = pd.read_sql_query(query, conn)
        print(df.to_string(index=False))

    conn.close()






def main():

    datos = extraccion()
    if datos:
        print("EXTRAIDO")
        df = transformacion_limpieza(datos)
        print(df.head())
        print("LIMPIO")
        exportar_csv(df)
        print("EXPORTADO")

        cargar_sqlite()
        ejecutar_consultas()

main()
