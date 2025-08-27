#Aca se simula el movimiento de los camiones de recoleccion de basura

import os
import logging
import random
from datetime import datetime, timedelta, time

#librerias para manejar arcchivos KML y geometria
from pykml import parser
from shapely.geometry import LineString
from geopy.distance import geodesic

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


#Definimos un diccionario para almacenar las rutas
#la estructura es {'A1_ruta1': Linestring, 'A1_ruta2': Linestring....}
rutas_kml = {}

#definimos turnos de trabajo
TURNOS = {
    'A1':{"nombre" : "matutino", "inicio": time(7,0), "fin": time(11,0)},
    'A2':{"nombre": "nocturno", "inicio": time(19,0), "fin": time(0,0)},
    'A3': {"nombre": "vespertino", "inicio": time(13,0), "fin": time(17,0)}
}

#definimos un diccionario para almacenar la duracion de la simulacion para cada camion, por turno
#se calcula una sola vez cuando se inicia la aplicacin
"""Estructura: 
    {'A1_ruta1_matutino': timedelta}"""

simaulacion_data = {}

def cargar_rutas_kml(ruta_archivos):
    """ Carga todos los archivos KML de las rutas de los camiones desde el directorio de datos y los almacenaa en el diccionario rutas_kml"""

    global rutas_kml
    logging.info("Cargando rutas kml")

    #creamos la ruta absoluta al directorio donde estan los recorridos
    rutas_dir = os.path.join(ruta_archivos, 'Recorridos')

    if not os.path.isdir(rutas_dir):
        logging.error(f"No se encontro el directorio: {rutas_dir}")
        return
    
    for filename in os.listdir(rutas_dir):
        if filename.endswith('.kml'):
            file_path = os.path.join(rutas_dir, filename)
            try:
                with open(file_path, 'rb') as kml_file:
                    root = parser.parse(kml_file).getroot()
                
                line_string_tag = root.Document.Placemark.LineString.coordinates
                coords_text = line_string_tag.text.strip()

                #convertimos las coordenadas de lon,lat,alt a lon y lat para que shapely pueda leer
                coord_list = [tuple(map(float, c.split(',')))[:2] for c in coords_text.split()]

                #Creo un objeto LineString
                line = LineString(coord_list)

                #Usamos el nombre del archivo como clave
                nombre_ruta = os.path.splitext(filename)[0]
                rutas_kml[nombre_ruta] = line
                logging.info(f"Ruta '{nombre_ruta}' cargada con exito")

            except Exception as e:
                logging.error(f"No se pudo procesar el archivo kml '{filename}': {e}")



def inicializar_simulacion(ruta_archivos):
    """
    Carga las rutas KML y pre-calcula la duración de la simulación para cada camión
    y turno. Esta función debe llamarse una sola vez al inicio de la aplicación.
    
    Args:
        ruta_base_data (str): La ruta al directorio 'Data' """
    
    global simaulacion_data

    cargar_rutas_kml(ruta_archivos)

    #asigno una duracion aleatoria para cada camion por turno
    #el rango es de 3 a 5 hs

    min_horas = 3
    max_horas= 5

    identificadores_rutas = ['NS','EO']
    zonas = ["A1", "A2", "A3"]
    for zona in zonas:
        for identificador in identificadores_rutas: #camion 1 y 2
            clave_simulacion = f"RECORRIDO-{zona}-{identificador}_{TURNOS[zona]["nombre"]}"

            #asignamos la duracion aleatoria
            duracion_horas = random.uniform(min_horas,max_horas)
            duracion_timedelta = timedelta(hours = duracion_horas)

            simaulacion_data[clave_simulacion] = duracion_timedelta

    logging.info("Simulacion inicializada. Duraciones aleatorias asignadas por zona")



def obtener_posicion_camion(zona,hora_actual):
    """
    Calcula la posición simulada del camión de la zona en un momento dado.
    
    Args:
        zona (str): El nombre de la zona (ej. 'A1').
        hora_actual (datetime): El objeto datetime con la hora actual.
        
    Returns:
        dict or None: Un diccionario con la posición y el estado del camión, o None si el camión no está en ruta.
    """

    info_turno = TURNOS.get(zona)
    if not info_turno:
        return {'estado': 'fuera_de_servicio'}
    
    turno_activo = info_turno["nombre"]
    horario_inicio_turno = None
    hora_inicio = info_turno["inicio"]
    hora_fin = info_turno["fin"]

    #Primero manejamos los turnos que no cruzan la medianoche
    if hora_inicio < hora_fin:
        if hora_inicio <= hora_actual.time() < hora_fin:
            horario_inicio_turno = datetime.combine(hora_actual.date(), hora_inicio)
        else:
            return {'estado': 'fuera_de_servicio'}
        
    else:
        #tunos que cruzan la medianoche
        if hora_inicio <=hora_actual.time() or hora_actual.time() < hora_fin:
            if hora_actual.time() < hora_fin:
                horario_inicio_turno = datetime.combine(hora_actual.date()- timedelta(days=1), hora_inicio)
            else:
                horario_inicio_turno = datetime.combine(hora_actual.date(), hora_inicio)
        else:
            return {'estado': 'fuera_de_servicio'}


    #lista para almacenar los reusltados de cada camion
    posiciones_camiones =[]
    identificadores_rutas = ['NS','EO']

    #Iterar sobre los 2 camiones para cada zona
    for identificador in identificadores_rutas:
        camion_id = f"camion_{identificador}"
        nombre_ruta = f"RECORRIDO-{zona}-{identificador}"
        clave_simulacion = f"{nombre_ruta}_{turno_activo}"

        linea_recorrido = rutas_kml.get(nombre_ruta)
        duracion_total = simaulacion_data.get(clave_simulacion)

        if not linea_recorrido or not duracion_total:
            logging.error(f"No se encontro la ruta o datos de simulacion para {clave_simulacion}")
            posiciones_camiones.append({'estado': 'error_configuracion', 'camion_id': camion_id})
            continue

        #calcular el tiempo y la distancia
        tiempo_transcurrido = hora_actual - horario_inicio_turno
        if tiempo_transcurrido > duracion_total:
            posiciones_camiones.append({'estado': 'finalizado', 'camion_id': camion_id})
            continue

        porcentaje_recorrido = tiempo_transcurrido / duracion_total

        posicion_actual = linea_recorrido.interpolate(linea_recorrido.length * porcentaje_recorrido, normalized=False)

        latitud_actual = posicion_actual.y
        longitud_actual = posicion_actual.x

        #calcular distancia y tiempo restantes.
        punto_final_ruta = LineString(linea_recorrido.coords).coords[-1]

        posicion_actual_geodesic = (latitud_actual,longitud_actual)
        punto_final_geodesic = (punto_final_ruta[1], punto_final_ruta[0])

        distancia_restante_km = geodesic(posicion_actual_geodesic, punto_final_geodesic).km
        tiempo_restante = duracion_total - tiempo_transcurrido

        posiciones_camiones.append({
            'estado': 'en_ruta',
            'camion_id': camion_id,
            'latitud': latitud_actual,
            'longitud': longitud_actual,
            'distancia_restante': distancia_restante_km,
            'tiempo_restante': str(tiempo_restante),
            'turno': turno_activo,
            'identificador_ruta': identificador,
            'ruta_line_string': linea_recorrido
        })

    return posiciones_camiones





if __name__ == "__main__":
    print("--- INICIANDO PRUEBA DEL SIMULADOR ---")
    
    # La siguiente lógica asume la estructura de directorios:
    # Proyecto/
    # ├── BackEnd/
    # │   └── simulador.py
    # └── Data/
    #     └── Recorridos/
    
    ruta_base = os.path.dirname(os.path.abspath(__file__)) # .../Proyecto/BackEnd
    ruta_proyecto = os.path.dirname(ruta_base) # .../Proyecto
    ruta_data = os.path.join(ruta_proyecto, 'Data') # .../Proyecto/Data
    
    inicializar_simulacion(ruta_data)
    
    # Ejemplo 1: Hora en el turno matutino (Zona A1)
    hora_ejemplo_matutino = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
    print(f"\n--- Probando simulación en Zona A1 a las {hora_ejemplo_matutino.strftime('%H:%M')} ---")
    posiciones_matutino = obtener_posicion_camion('A1', hora_ejemplo_matutino)
    print(posiciones_matutino)
    
    # Ejemplo 2: Hora en el turno vespertino (Zona A3)
    hora_ejemplo_vespertino = datetime.now().replace(hour=14, minute=30, second=0, microsecond=0)
    print(f"\n--- Probando simulación en Zona A3 a las {hora_ejemplo_vespertino.strftime('%H:%M')} ---")
    posiciones_vespertino = obtener_posicion_camion('A3', hora_ejemplo_vespertino)
    print(posiciones_vespertino)
    
    # Ejemplo 3: Hora en el turno nocturno (Zona A2)
    hora_ejemplo_nocturno = datetime.now().replace(hour=21, minute=0, second=0, microsecond=0)
    print(f"\n--- Probando simulación en Zona A2 a las {hora_ejemplo_nocturno.strftime('%H:%M')} ---")
    posiciones_nocturno = obtener_posicion_camion('A2', hora_ejemplo_nocturno)
    print(posiciones_nocturno)

    # Ejemplo 4: Hora fuera de cualquier turno (12:30)
    hora_ejemplo_fuera_turno = datetime.now().replace(hour=12, minute=30, second=0, microsecond=0)
    print(f"\n--- Probando simulación en Zona A1 a las {hora_ejemplo_fuera_turno.strftime('%H:%M')} ---")
    posiciones_fuera = obtener_posicion_camion('A1', hora_ejemplo_fuera_turno)
    print(posiciones_fuera)
    
    print("\n--- FIN DE LA PRUEBA DEL SIMULADOR ---")
