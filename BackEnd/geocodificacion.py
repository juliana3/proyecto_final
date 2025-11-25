#convierte la direccion proporcionada en texto por el usuario a coordenadas geograficas.
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def geocodificar_direccion(direccion_usuario):
    """ Convierte la direccion de texto a coordenadas (lat y lon). Tambien agrega automaticamente ciudad y pasi automaticamente.
    Devuelve una tupla con la latitud y longitud o un None"""

    geolocator = Nominatim(user_agent="BasureroApp/1.0 (araujojuli1234@gmail.com)")
    direccion_completa = f"{direccion_usuario}, Santa Fe capital, Santa Fe, Argentina"
    logging.info(f"Geocodificando la direccion: '{direccion_completa}'")

    try:
        location= geolocator.geocode(direccion_completa, timeout=10)

        if location:
            latitud = location.latitude
            longitud = location.longitude
            logging.info(f"Coordenadas encontradas: Latidud = {latitud}, Longitud = {longitud}")
            return (latitud,longitud)
        else:
            logging.warning("No se encontraron resultados para la direccion")
            return None
    except GeocoderTimedOut:
        logging.error("El servicio de geocodificacion excedió el tiempo de espera")
        return None
    except GeocoderServiceError as e:
        logging.error(f"Error en el servicio de geocodificacion: {e}")
        return None
    


