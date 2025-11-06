#funciones auxiliares
import math
from datetime import timedelta  

def formatear_tiempo_a_mensaje(segundos):
    """
    Función auxiliar para formatear un tiempo en segundos a un mensaje legible.
    """

    # Si es un timedelta, convertirlo a segundos
    if hasattr(segundos, "total_seconds"):
        segundos = segundos.total_seconds()

    if segundos < 60:
        return "🚛 ¡El camión está a punto de llegar a tu dirección, en menos de 1 minuto!"
    elif segundos < 3600:  # Menos de una hora
        minutos = math.floor((segundos % 3600) / 60)
        return f"⏳ El camión más cercano pasa en {minutos} minutos. ¡Prepará tus residuos!"
    else:  # Más de una hora
        horas = math.floor(segundos / 3600)
        minutos = math.floor((segundos % 3600) / 60)
        return f"🕒 El camión más cercano llegará en {horas} hora(s) y {minutos} minuto(s). ¡Tené todo listo!"


def convertir_timedelta_a_str(obj):
    """Convierte todos los timedelta dentro de dicts/listas a strings."""
    if isinstance(obj, timedelta):
        return str(obj)
    if isinstance(obj, dict):
        return {k: convertir_timedelta_a_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convertir_timedelta_a_str(i) for i in obj]
    return obj
