#convierte la direccion proporcionada en texto por el usuario a coordenadas geograficas.
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def geocodificar_direccion(direccion_usuario):
    """ Convierte la direccion de texto a coordenadas (lat y lon). Tambien agrega automaticamente ciudad y pasi automaticamente.
    Devuelve una tupla con la latitud y longitud o un None"""

    geolocator = Nominatim(user_agent="BasureroApp")
    direccion_completa = f"{direccion_usuario}, Santa Fe, Argentina"
    print(f"Geocodificando la direccion: '{direccion_completa}'")

    try:
        location= geolocator.geocode(direccion_completa, timeout=5)

        if location:
            latitud = location.latitude
            longitud = location.longitude
            print(f"Coordenadas encontradas: Latidud = {latitud}, Longitud = {longitud}")
            return (latitud,longitud)
        else:
            print("ADV: No se encontraron resultados para la direccion")
            return None
    except GeocoderTimedOut:
        print("ERR: El servicio de geocodificacion excedió el tiempo de espera")
        return None
    except GeocoderServiceError as e:
        print(f"ERR: Error en el servicio de geocodificacion")
        return None
    


# Ejemplo de uso (solo se ejecuta si se corre este archivo directamente)
if __name__ == "__main__":
    direccion_ejemplo = "Avenida General Paz 5450"
    coordenadas = geocodificar_direccion(direccion_ejemplo)
    
    if coordenadas:
        print(f"La dirección '{direccion_ejemplo}' se encuentra en Latitud: {coordenadas[0]}, Longitud: {coordenadas[1]}")
    else:
        print(f"No se pudo encontrar las coordenadas para la dirección: '{direccion_ejemplo}'")