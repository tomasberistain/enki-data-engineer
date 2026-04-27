import requests
import pandas as pd
import sqlite3


#DEFINICIÓN DE PARAMETROS
URL_ = "https://api.open-meteo.com/v1/forecast"
PARAMETROS = {
    'latitude': 19.43,
    'longitude': -99.13,
    "hourly": "temperature_2m,precipitation",
    "past_days": 7,
    "forecast_days": 0
}

#FUNCION QUE REALIZA LA EXTRACCIÓN DE LOS DATOS A PARTIR DE LLAMADA A LA API
#MANEJO DE ERRORES USANDO TRY EXCEPT
def extraccion():
    try:
        response = requests.get(URL_, params=PARAMETROS, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "hourly" not in data:
            print(f"ERROR: respuesta inesperada de la API: {data}")
            return None
        hourly = data["hourly"]
        return hourly
    except requests.exceptions.ConnectionError:
        print("ERROR AL CONECTARSE A LA API")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"ERROR HTTP: {e}")
        return None
    except requests.exceptions.Timeout:
        print("ERROR: la API tardó demasiado en responder.")
        return None

#FUNCION QUE TRANSFORMA LOS DATOS
#TRANSFORMACION DE LOS NOMBRES DE COLUMNAS, FORMATO DE FECHA, RANGO DE HORA
#REVISIÓN DE REGISTROS NULOS Y NEGATIVOS
def transformacion_limpieza(hourly):

    df = pd.DataFrame({
        "fecha": hourly["time"],
        "temperatura_c": hourly["temperature_2m"],
        "precipitacion_mm": hourly["precipitation"]
    })

    df['fecha'] = pd.to_datetime(df["fecha"])
    df = df[df["fecha"].dt.hour.between(6,22)]


    nulos = df[["temperatura_c","precipitacion_mm"]].isnull().any(axis=1).sum()
    negativos = (df[["temperatura_c", "precipitacion_mm"]]<0).any(axis=1).sum()
    print(f"Nulos (registros que tienen al menos un nulo): {nulos}")
    print(f"Negativos (registros que tienen al menos un negativo): {negativos}")

    return df

#FUNCION QUE EXPORTA EL DF EN UN CSV
def exportar_csv(df, ruta="../data/datos_clima_cdmx.csv"):
    df.to_csv(ruta, index=False)
    print(f"CSV exportado: {ruta} ({len(df)} registros)")


#FUNCIONES PARA LA EJECUCION DE SQL

#FUNCION QUE CARGA EL CSV EN SQLITE
def cargar_sqlite(csv_path="../data/datos_clima_cdmx.csv", db_path="../data/clima_cdmx.db"):
    df = pd.read_csv(csv_path)
    conn = sqlite3.connect(db_path)
    df.to_sql("clima", conn, if_exists="replace", index=False)
    print(f"Datos cargados en SQLite: {len(df)} registros")
    conn.close()

#FUNCION QUE EJECUTA LAS CONSULTAS DESDE EL .SQL
#CONSULTAS SEPARADAS POR EL DELIMITADOR --, TERMINADAS EN ;
def ejecutar_consultas(db_path="../data/clima_cdmx.db", sql_path="../sql/consultas.sql"):
    with open(sql_path, "r", encoding="utf-8") as f:
        contenido = f.read()

    # DELIMITADOR -- SEPARA LAS CONSULTAS
    bloques = [b.strip() for b in contenido.split(";") if b.strip()]

    conn = sqlite3.connect(db_path)
    for bloque in bloques:
        # NOMBRE DE LA CONSULTA DESDE EL COMENTARIO
        lineas = bloque.strip().splitlines()
        nombre = lineas[0].replace("--", "").strip() if lineas[0].startswith("--") else "Consulta"
        print(f"\n--- {nombre} ---")
        query = "\n".join(lineas[1:]).strip()
        df = pd.read_sql_query(query, conn)
        print(df.to_string(index=False))

    conn.close()


#FUNCION MAIN QUE ORQUESTA LA EJECUCIÓN DEL SCRIPT
def main():

    datos = extraccion()
    if datos:
        df = transformacion_limpieza(datos)
        exportar_csv(df)
        cargar_sqlite()
        ejecutar_consultas()

main()
