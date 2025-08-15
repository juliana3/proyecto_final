#Calculo de la distancia entre el camion y el usuario
from datetime import timedelta
from geopy.distance import geodesic
from shapely.geometry import Point, LineString

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
        return {'estado': 'sin_servicio_en_esta_zona', 'mensaje': 'No hay camiones en servicio en esta zona en este momento.'}
    
    # Creamos un punto Shapely para la ubicación del usuario
    punto_usuario = Point(longitud_usuario, latitud_usuario)

    mejor_camion = None
    distancia_minima_a_ruta = float('inf')

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

    # Si encontramos el camión de la ruta más cercana
    if mejor_camion and mejor_camion.get('estado') == 'en_ruta':
        linea_recorrido = mejor_camion.get('ruta_line_string')

        # Proyectamos la ubicación del camión y del usuario en la ruta.
        # `project` retorna la distancia a lo largo de la línea desde el inicio.
        distancia_camion_a_inicio = linea_recorrido.project(Point(mejor_camion.get('longitud'), mejor_camion.get('latitud')))
        distancia_usuario_a_inicio = linea_recorrido.project(punto_usuario)

        # Verificamos si el camión ya ha pasado la posición proyectada del usuario.
        # Usamos un pequeño margen de error para evitar problemas de precisión.
        if distancia_camion_a_inicio >= distancia_usuario_a_inicio:
            return {
                'estado': 'ya_paso_por_su_direccion',
                'mensaje': 'El camión de recolección ya pasó por su dirección.'
            }
        
        # Si el camión aún no ha pasado, calculamos el tiempo de llegada
        tiempo_restante_ruta_str = mejor_camion.get('tiempo_restante')
        
        # Convertimos la cadena de tiempo a un objeto timedelta
        try:
            parts = list(map(int, tiempo_restante_ruta_str.split(':')))
            tiempo_restante_ruta = timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2])
        except (ValueError, IndexError):
            # En caso de que el formato de tiempo sea diferente (ej. '0:15:00.123456')
            # Lo manejamos convirtiendo a segundos
            tiempo_restante_ruta_segundos = float(str(mejor_camion.get('tiempo_restante')).split(' ')[-1])
            tiempo_restante_ruta = timedelta(seconds=tiempo_restante_ruta_segundos)

        # Calculamos el porcentaje de la ruta que le falta al camión para llegar al punto del usuario
        largo_total_ruta = linea_recorrido.length
        distancia_recorrido_a_usuario = distancia_usuario_a_inicio - distancia_camion_a_inicio
        
        # Proporción del tiempo total de la ruta que le falta al camión para llegar al usuario
        proporcion_pendiente = distancia_recorrido_a_usuario / largo_total_ruta
        
        # Calculamos el tiempo estimado de llegada
        tiempo_estimado_total = tiempo_restante_ruta * proporcion_pendiente

        return {
            'camion_id': mejor_camion['camion_id'],
            'distancia_a_camion_km': mejor_camion['distancia_restante'],
            'tiempo_estimado_llegada': str(tiempo_estimado_total),
            'identificador_ruta': mejor_camion['identificador_ruta']
        }
    else:
        # Si no se encuentra un camión en ruta en la ruta más cercana
        return {
            'estado': 'no_camion_en_ruta',
            'mensaje': 'El camión de la ruta más cercana no está en servicio en este momento.'
        }




if __name__ == '__main__':
    # --- PRUEBA DEL MÓDULO DISTANCIA ---
    
    # Creamos datos de prueba simulados que incluyen la LineString
    from shapely.geometry import LineString
    
    # Rutas de ejemplo
    ruta_ejemplo_ns = LineString([(-60.71, -31.62), (-60.71, -31.64)])
    ruta_ejemplo_eo = LineString([(-60.67, -31.65), (-60.7, -31.65)])
    
    posiciones_simuladas = [
        # El camión NS se encuentra a 31.62, 60.71
        {'estado': 'en_ruta', 'camion_id': 'camion_NS', 'latitud': -31.62, 'longitud': -60.71, 'distancia_restante': 5.0, 'tiempo_restante': '0:15:00', 'turno': 'matutino', 'identificador_ruta': 'NS', 'ruta_line_string': ruta_ejemplo_ns},
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

