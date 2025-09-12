#funciones auxiliares
import math

def formatear_tiempo_a_mensaje(segundos):
    """
    Función auxiliar para formatear un tiempo en segundos a un mensaje legible.
    """
    if segundos < 60:
        return "El camión está a menos de 1 minuto de tu ubicación."
    elif segundos < 3600:  # Menos de una hora
        minutos = math.floor((segundos % 3600) / 60)
        return f"Tu camión pasará en aproximadamente {minutos} minutos."
    else:  # Más de una hora
        horas = math.floor(segundos / 3600)
        minutos = math.floor((segundos % 3600) / 60)
        return f"Tu camión pasará en aproximadamente {horas} horas y {minutos} minutos."