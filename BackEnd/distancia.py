#Calculo de la distancia entre el camion y el usuario
import logging
from datetime import timedelta
import math
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
       return {'estado': 'sin_servicio_en_esta_zona', 'mensaje': 'No hay camiones en servicio en este momento. AAAA'} #ESTO SE ARREGLA AJUSTANDO LOS HORARIOS DE LOS TURNOS!!!!!!!!
      
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

    if not mejor_camion or not mejor_camion.get("estado"):
        #Si no se encontró ningún camión o ruta válida.
        return {'estado': 'no_camion_disponible', 'mensaje': 'No se encontró un camión disponible para esta zona.BBBB'}
        



    #SEGUNDO hacemos la logica para el camion de la ruta mas cerca
    estado = mejor_camion.get('estado')

    if estado == "en_ruta":
        linea_recorrido = mejor_camion.get('ruta_line_string')

        # Proyectamos la ubicación del camión y del usuario en la ruta.
        # `project` retorna la distancia a lo largo de la línea desde el inicio.
        distancia_camion_a_inicio = linea_recorrido.project(Point(mejor_camion.get('longitud'), mejor_camion.get('latitud')))
        distancia_usuario_a_inicio = linea_recorrido.project(punto_usuario)

        # Verificamos si el camión ya ha pasado la posición proyectada del usuario.
        # Usamos un pequeño margen de error para evitar problemas de precisión.
        if distancia_camion_a_inicio >= distancia_usuario_a_inicio - 0.001:
            return {
                'estado': 'ya_paso_por_su_direccion',
                'mensaje': 'El camión de recolección ya pasó por su dirección.'
            }
        

        #DISTANCIA RESTNTE EN LA RUTA DESDE EL CAMION HASTA EL USUARIO
        distancia_total_recorrido = linea_recorrido.length
        distancia_restante_hasta_usuario = distancia_usuario_a_inicio - distancia_camion_a_inicio

        #PROPORCION DE DISTANCIA HASTA EL USUARIO RESPECTO AL TOTAL
        proporcion_distancia_hasta_usuario = distancia_restante_hasta_usuario / (distancia_total_recorrido - distancia_camion_a_inicio)

        #TIEMPO RESTANTE HASTA EL USUARIO SEGUN LA PROPORCION
        tiempo_restante_camion = mejor_camion["tiempo_restante"]

        #TIEMPO ESTIMADO HASTA EL USUARIO SEGUN LA PROPORCION
        tiempo_estimado_usuario = tiempo_restante_camion * proporcion_distancia_hasta_usuario
        
        mensaje_tiempo = formatear_tiempo_a_mensaje(tiempo_estimado_usuario.total_seconds())
        return {
            'camion_id': mejor_camion['camion_id'],
            'distancia_a_camion_km': round(geodesic((mejor_camion["latitud"], mejor_camion["longitud"]), (latitud_usuario, longitud_usuario)).km, 2),
            'tiempo_estimado_llegada': mensaje_tiempo,
            'identificador_ruta': mejor_camion['identificador_ruta']
        }
    else: #si el camion no esta en ruta, devuelvo un mensaje segun el estado
        info_turno = None

        if mejor_camion.get('identificador_ruta'):
            zona = mejor_camion['identificador_ruta'].split('-')[1]
            info_turno = TURNOS.get(zona, {})
            inicio = info_turno.get('inicio')
            fin = info_turno.get('fin')


        if estado == 'finalizado' and info_turno and inicio and fin:
            mensaje = f"El turno de recolección ya finalizó. Horario de servicio: {inicio.strftime('%H:%M')} a {fin.strftime('%H:%M')}."
        elif estado == 'fuera_de_servicio' and info_turno and inicio and fin:
            mensaje = f"El camión no está en servicio en este momento. Horario de servicio: {inicio.strftime('%H:%M')} a {fin.strftime('%H:%M')}."
        elif estado == 'error_configuracion':
            mensaje = "Error en la configuración del simulador. No se encontró la ruta para este camión."
        else:
            mensaje = "No hay camiones en servicio en esta zona en este momento."

    return {'estado': estado, 'mensaje': mensaje}

        




if __name__ == '__main__':
    # --- PRUEBA DEL MÓDULO DISTANCIA ---
    
    # Creamos datos de prueba simulados que incluyen la LineString
    from shapely.geometry import LineString
    
    # Rutas de ejemplo
    ruta_ejemplo_ns = LineString([(-60.71, -31.62), (-60.71, -31.64)])
    ruta_ejemplo_eo = LineString([(-60.67, -31.65), (-60.7, -31.65)])
    
    posiciones_simuladas = [
        # El camión NS se encuentra a 31.62, 60.71
        {'estado': 'en_ruta', 'camion_id': 'camion_NS', 'latitud': -31.635, 'longitud': -60.71, 'distancia_restante': 5.0, 'tiempo_restante': '0:15:00', 'turno': 'matutino', 'identificador_ruta': 'NS', 'ruta_line_string': ruta_ejemplo_ns},
        {'estado': 'en_ruta', 'camion_id': 'camion_EO', 'latitud': -31.65, 'longitud': -60.68, 'distancia_restante': 8.0, 'tiempo_restante': '0:25:00', 'turno': 'matutino', 'identificador_ruta': 'EO', 'ruta_line_string': ruta_ejemplo_eo}
    ]

    # Ubicación del usuario de prueba 1: Cerca de la ruta EO, el camión no ha pasado
    latitud_usuario_prueba_1 = -31.65
    longitud_usuario_prueba_1 = -60.685

    print("--- INICIANDO PRUEBA DEL MÓDULO DISTANCIA ---")
    resultado_1 = calcular_tiempo_a_destino(latitud_usuario_prueba_1, longitud_usuario_prueba_1, posiciones_simuladas)
    print("Resultado del cálculo (camión no ha pasado):")
    print(resultado_1)

    print("-" * 40)

    # Ubicación del usuario de prueba 2: Cerca de la ruta NS, pero el camión YA PASÓ
    latitud_usuario_prueba_2 = -31.63
    longitud_usuario_prueba_2 = -60.71
    # La posición del camión NS es (-31.62, -60.71)
    # La posición del usuario es (-31.63, -60.71), más al sur, por lo que el camión ya pasó
    
    resultado_2 = calcular_tiempo_a_destino(latitud_usuario_prueba_2, longitud_usuario_prueba_2, posiciones_simuladas)
    print("Resultado del cálculo (camión YA ha pasado):")
    print(resultado_2)

    print("\n--- FIN DE LA PRUEBA ---")

