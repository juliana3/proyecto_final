#funciones auxiliares
import math

def formatear_tiempo_a_mensaje(segundos):
    """
    Función auxiliar para formatear un tiempo en segundos a un mensaje legible.
    """
    if segundos < 60:
        return "🚛 ¡El camión está a punto de llegar a tu dirección, en menos de 1 minuto!"
    elif segundos < 3600:  # Menos de una hora
        minutos = math.floor((segundos % 3600) / 60)
        return f"⏳ El camión más cercano pasa en {minutos} minutos. ¡Prepará tus residuos!"
    else:  # Más de una hora
        horas = math.floor(segundos / 3600)
        minutos = math.floor((segundos % 3600) / 60)
        return f"🕒 El camión más cercano llegará en {horas} hora(s) y {minutos} minuto(s). ¡Tené todo listo!"
