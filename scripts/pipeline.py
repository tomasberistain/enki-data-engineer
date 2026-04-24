import requests
import pandas as pd

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



def main():

    datos = extraccion()
    if datos:
        print("EXTRAIDO")
        df = transformacion_limpieza(datos)
        print(df.head())
        print("LIMPIO")
        exportar_csv(df)
        print("EXPORTADO")

main()
