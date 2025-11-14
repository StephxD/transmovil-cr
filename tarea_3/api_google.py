import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv

# ------------------------------------------------------------
# Cargar la API Key desde el archivo .env
# ------------------------------------------------------------
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# ------------------------------------------------------------
# Rutas de ejemplo
# ------------------------------------------------------------
rutas = [
    ("San José, Costa Rica", "Alajuela, Costa Rica"),
    ("San José, Costa Rica", "Cartago, Costa Rica"),
    ("San José, Costa Rica", "Heredia, Costa Rica"),
    ("Alajuela, Costa Rica", "Cartago, Costa Rica"),
]

def obtener_datos_ruta(origen, destino):
    """
    Consulta la API de Google Maps Directions y devuelve datos de distancia, duración y tráfico.
    """
    url = (
        "https://maps.googleapis.com/maps/api/directions/json"
        f"?origin={origen}&destination={destino}&departure_time=now&key={API_KEY}"
    )

    r = requests.get(url)
    data = r.json()

    if data["status"] != "OK":
        print(f"Error con la ruta {origen}-{destino}: {data['status']}")
        return None

    leg = data["routes"][0]["legs"][0]
    distancia = leg["distance"]["value"] / 1000  # en km
    duracion_normal = leg["duration"]["value"] / 60  # en minutos
    duracion_trafico = leg.get("duration_in_traffic", leg["duration"])["value"] / 60  # min
    velocidad_promedio = distancia / (duracion_trafico / 60)  # km/h aprox

    return {
        "ruta": f"{origen} - {destino}",
        "origen": origen,
        "destino": destino,
        "distancia_km": round(distancia, 1),
        "duracion_min": round(duracion_normal, 1),
        "duracion_trafico_min": round(duracion_trafico, 1),
        "velocidad_promedio": round(velocidad_promedio, 1),
    }

# ------------------------------------------------------------
# Ejecutar consultas y guardar resultados
# ------------------------------------------------------------
datos = []
for o, d in rutas:
    print(f"Consultando {o} -> {d}")
    datos.append(obtener_datos_ruta(o, d))
    time.sleep(1) 

df = pd.DataFrame(datos)
df.to_excel("datos/rutas_api.xlsx", index=False)
print(" Archivo 'rutas_api.xlsx' creado con éxito.")
