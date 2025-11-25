import logging
import os
import requests

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

API_KEY = os.getenv("OPENCAGE_API_KEY")  

def geocodificar_direccion(direccion_usuario):
    """
    Convierte la dirección de texto a coordenadas (lat y lon).
    Devuelve una tupla (lat, lon) o None si no se encuentra.
    """

    direccion_completa = f"{direccion_usuario}, Santa Fe capital, Santa Fe, Argentina"
    logging.info(f"Geocodificando la dirección con OpenCage: '{direccion_completa}'")

    try:
        url = "https://api.opencagedata.com/geocode/v1/json"
        params = {
            "q": direccion_completa,
            "key": API_KEY,
            "language": "es",
            "limit": 1
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            logging.error(f"Error HTTP {response.status_code} desde OpenCage")
            return None

        data = response.json()

        if data["results"]:
            result = data["results"][0]

            # Nivel de confianza (0 a 10)
            confidence = result.get("confidence", 0)
            components = result.get("components", {})

            # Coordenadas
            lat = result["geometry"]["lat"]
            lon = result["geometry"]["lng"]

            # Validación 1: confianza baja
            if confidence < 5:
                logging.warning(f"Resultado poco confiable (confidence={confidence}).")
                return None

            # Validación 2: dirección demasiado genérica (no tiene calle)
            if "road" not in components:
                logging.warning("La dirección encontrada es demasiado genérica (no contiene calle).")
                return None

            logging.info(f"Coordenadas encontradas: Lat = {lat}, Lon = {lon} (conf={confidence})")
            return (lat, lon)

        else:
            logging.warning("No se encontraron resultados en OpenCage.")
            return None

    except requests.exceptions.Timeout:
        logging.error("OpenCage excedió el tiempo de espera")
        return None
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        return None
