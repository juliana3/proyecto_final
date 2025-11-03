"""
Módulo para gestionar el modo DEMO de la aplicación.
Contiene las direcciones de prueba y sus respuestas predefinidas.

Ubicación sugerida: BackEnd/demo.py
"""

import logging

# Escenarios de DEMO
ESCENARIOS_DEMO = {
    "calle falsa 1": {
        "mensaje": "🚫 Tu dispositivo no se encuentra en la ciudad de Santa Fe. Por favor ingresá la dirección manualmente.",
        "status_code": 200
    },
    "calle falsa 2": {
        "mensaje": "Estás en Santa Fe, pero fuera del área de servicio de recolección.",
        "status_code": 200
    },
    "calle falsa 3": {
        "mensaje": "⏳ El camión más cercano pasa en 20 minutos. ¡Prepará tus residuos!",
        "status_code": 200
    },
    "calle falsa 4": {
        "mensaje": "🕒 El camión más cercano llegará en 1 hora(s) y 30 minuto(s) ¡Tené todo listo!",
        "status_code": 200
    },
    "calle falsa 5": {
        "mensaje": "🚛 ¡El camión está a punto de llegar a tu dirección, en menos de 1 minuto!",
        "status_code": 200
    },
    "calle falsa 6": {
        "mensaje": "👍 Hoy el camión ya pasó. Mañana regresamos entre las 8:00Hs y las 12:00Hs.",
        "status_code": 200
    },
    "calle falsa 7": {
        "mensaje": "ℹ️ No hay camiones disponibles en tu zona por ahora. Probá en unos minutos!",
        "status_code": 200
    },
    "calle falsa 8": {
        "mensaje": "⚠️ Hubo un error interno. No encontramos la ruta del camión. Probá en unos minutos!",
        "status_code": 200
    },
    "calle falsa 9": {
        "mensaje": "⌛ ¡Todavía no comenzamos! Pasaremos a tu dirección entre las 19:00 y las 00:00.",
        "status_code": 200
    },
    "calle falsa 10": {
        "mensaje": "🚫 ¡Ups! No estamos en servicio ahora. Nuestro horario es de 8:00 a 00:00.",
        "status_code": 200
    },
    "calle falsa 11": {
        "mensaje": "📍 Dirección no válida. Vas a ser redirigido otra vez.",
        "status_code": 200
    },
    "calle falsa 12": {
        "mensaje": "Estás en Santa Fe, pero fuera del área de servicio de recolección.",
        "status_code": 200
    },

    "calle falsa 13": {
        "mensaje" : "🚫 Error de conexión. Intentalo más tarde.",
        "status_code": 400
    }
}


def normalizar_direccion(direccion):
    """
    Normaliza la dirección para comparación.
    Convierte a minúsculas y elimina espacios extras.
    """
    return ' '.join(direccion.lower().strip().split())


def es_direccion_demo(direccion):
    """
    Verifica si la dirección es parte del modo DEMO.
    """
    direccion_norm = normalizar_direccion(direccion)
    return direccion_norm in ESCENARIOS_DEMO


def obtener_respuesta_demo(direccion):
    """
    Obtiene la respuesta predefinida para una dirección DEMO.
    """
    direccion_norm = normalizar_direccion(direccion)
    escenario = ESCENARIOS_DEMO.get(direccion_norm)
    
    if escenario:
        logging.info(f"[MODO DEMO] Dirección detectada: {direccion}")
        return {
            'mensaje': escenario['mensaje'],
            'status_code': escenario['status_code']
        }
    
    return None