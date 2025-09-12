#Calculo de la distancia entre el camion y el usuario
import logging
from geopy.distance import geodesic
from shapely.geometry import Point, LineString

from BackEnd.simulador import TURNOS
from BackEnd.helpers import formatear_tiempo_a_mensaje

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def calcular_tiempo_a_destino(latitud_usuario, longitud_usuario, posiciones_camiones):
    """
        Calcula el tiempo estimado de llegada del camión más cercano a la ubicación
        del usuario.

        Args:
            latitud_usuario (float): Latitud actual del usuario.
            longitud_usuario (float): Longitud actual del usuario.
            posiciones_camiones (list): Una lista de diccionarios con la posición y estado de todos los camiones de una zona devuelta por el simulador.

        Returns:
            dict: Un diccionario con la información del camión más cercano y el tiempo
                estimado de llegada. Retorna un diccionario vacío si no hay camiones
                en ruta.
    """
     
    if not posiciones_camiones:
        return {
                'camion_id': None,
                'estado': 'sin_servicio_en_esta_zona',
                'mensaje': 'No hay camiones en servicio en este momento.',
                'distancia_a_camion_km': None,
                'tiempo_estimado_llegada': None,
                'identificador_ruta': None
            }      
    
    # Creamos un punto Shapely para la ubicación del usuario
    punto_usuario = Point(longitud_usuario, latitud_usuario)
    distancia_minima_a_ruta = float('inf')
    mejor_camion = None

    # Primero determinamos cuál de las dos rutas de la zona es la más cercana al usuario
    for camion in posiciones_camiones:
        linea_recorrido = camion.get('ruta_line_string')
        
        if not linea_recorrido:
            continue

        # Calculamos la distancia mínima del punto del usuario a la LineString de la ruta para decidir cual de las rutas es la que sirve.
        distancia_a_ruta = punto_usuario.distance(linea_recorrido)
        
        if distancia_a_ruta < distancia_minima_a_ruta:
            distancia_minima_a_ruta = distancia_a_ruta
            mejor_camion = camion
            logging.info(f"Nuevo camión más cercano encontrado: {mejor_camion['camion_id']} a una distancia de {distancia_a_ruta:.6f} metr.")

    if not mejor_camion or not mejor_camion.get("estado"):
        #Si no se encontró ningún camión o ruta válida.
        return {
                'camion_id':mejor_camion.get('camion_id') if mejor_camion else None,
                'estado': 'no_hay_camion_disponible',
                'mensaje': 'No se encontró un camión disponible para esta zona.',
                'distancia_a_camion_km':  round(geodesic((mejor_camion["latitud"], mejor_camion["longitud"]), (latitud_usuario, longitud_usuario)).km, 2) if mejor_camion else None,
                'tiempo_estimado_llegada': mejor_camion['tiempo_restante'] if mejor_camion else None,
                'identificador_ruta': mejor_camion['identificador_ruta'] if mejor_camion else None
            }
    logging.info(f"Camión más cercano: {mejor_camion['camion_id']} con estado {mejor_camion['estado']}.")
        



    #SEGUNDO hacemos la logica para el camion de la ruta mas cerca
    estado = mejor_camion.get('estado')
    info_turno = None
    inicio = None
    fin = None
    if mejor_camion.get('identificador_ruta'):
        zona = mejor_camion['identificador_ruta'].split('-')[1]
        info_turno = TURNOS.get(zona, {})
        inicio = info_turno.get('inicio')
        fin = info_turno.get('fin')

    if estado == "en_ruta":
        linea_recorrido = mejor_camion.get('ruta_line_string')

        # Proyectamos la ubicación del camión y del usuario en la ruta.
        # `project` retorna la distancia a lo largo de la línea desde el inicio.
        distancia_desde_inicio_camion = linea_recorrido.project(Point(mejor_camion.get('longitud'), mejor_camion.get('latitud')))
        distancia_desde_inicio_usuario = linea_recorrido.project(punto_usuario)

        # Verificamos si el camión ya ha pasado la posición proyectada del usuario.
        # Usamos un pequeño margen de error para evitar problemas de precisión.
        if distancia_desde_inicio_camion > distancia_desde_inicio_usuario - 0.001:
            mensaje = "El camión de recolección ya pasó!."
            if info_turno and inicio and fin:
                mensaje += f" El proximo servicio de recolección para tu dirección comienza mañana. De {inicio.strftime('%H:%M')} a {fin.strftime('%H:%M')}."
            
            return {
                'camion_id': mejor_camion['camion_id'],
                'estado': 'ya_paso_por_su_direccion',
                'mensaje': mensaje,
                'distancia_a_camion_km': round(geodesic((mejor_camion["latitud"], mejor_camion["longitud"]), (latitud_usuario, longitud_usuario)).km, 2),
                'tiempo_estimado_llegada': mejor_camion['tiempo_restante'],
                'identificador_ruta': mejor_camion['identificador_ruta']
            }
        
        

        #DISTANCIA RESTNTE EN LA RUTA DESDE EL CAMION HASTA EL USUARIO
        distancia_total_recorrido = linea_recorrido.length
        distancia_restante_hasta_usuario = distancia_desde_inicio_usuario - distancia_desde_inicio_camion

        #PROPORCION DE DISTANCIA HASTA EL USUARIO RESPECTO AL TOTAL
        proporcion_distancia_hasta_usuario = distancia_restante_hasta_usuario / (distancia_total_recorrido - distancia_desde_inicio_camion)

        #TIEMPO RESTANTE HASTA EL USUARIO SEGUN LA PROPORCION
        tiempo_restante_camion = mejor_camion["tiempo_restante"]
        tiempo_estimado_usuario = tiempo_restante_camion * proporcion_distancia_hasta_usuario
        
        mensaje_tiempo = formatear_tiempo_a_mensaje(tiempo_estimado_usuario.total_seconds())
        return {
            'camion_id': mejor_camion['camion_id'],
            'distancia_a_camion_km': round(geodesic((mejor_camion["latitud"], mejor_camion["longitud"]), (latitud_usuario, longitud_usuario)).km, 2),
            'tiempo_estimado_llegada': mensaje_tiempo,
            'identificador_ruta': mejor_camion['identificador_ruta']
        }
    else: #si el camion no esta en ruta, devuelvo un mensaje segun el estado
        if estado == 'finalizado' and info_turno and inicio and fin:
            mensaje = f"El turno de recolección ya finalizó!. El proximo servicio de recolección para tu dirección comienza mañana. De {inicio.strftime('%H:%M')} a {fin.strftime('%H:%M')}."
        elif estado == 'fuera_de_servicio' and info_turno and inicio and fin:
            mensaje = f"Los servicios de recolección no están en servicio en este momento!. El horario de servicio es de 8:00 a 00:00."
        elif estado == 'ya_paso_por_su_direccion' and info_turno and inicio and fin:
            mensaje = f"El camión de recolección ya pasó! El proximo servicio de recolección para tu dirección comienza mañana. De {inicio.strftime('%H:%M')} a {fin.strftime('%H:%M')}."
        elif estado == 'error_configuracion':
            mensaje = "Error en la configuración del simulador. No se encontró la ruta para este camión."
        elif estado == 'no_iniciado' and info_turno and inicio and fin:
            mensaje = f"El turno de recolección aún no empezó!. Comenzará a las {inicio.strftime('%H:%M')} y hasta las {fin.strftime('%H:%M')}."
        else:
            mensaje = "No hay camiones en servicio en esta zona en este momento."

    return {'estado': estado, 'mensaje': mensaje}

        




