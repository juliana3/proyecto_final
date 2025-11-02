#Aca se simula el movimiento de los camiones de recoleccion de basura

import os
import logging
import random
from datetime import datetime, timedelta, time

#librerias para manejar arcchivos KML y geometria
from pykml import parser
from shapely.geometry import LineString

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


#definimos turnos de trabajo
TURNOS = {
    'A1': {"nombre": "matutino", "inicio": time(8, 0), "fin": time(12, 59)},
    'A2': {"nombre": "nocturno", "inicio": time(19, 0), "fin": time(23, 59)},
    'A3': {"nombre": "vespertino", "inicio": time(13, 0), "fin": time(18, 59)}
}

def calcular_horario_turno(hora_actual, hora_inicio, hora_fin):
    """
    Calcula los datetimes de inicio y fin de un turno, considerando turnos que cruzan la medianoche.
    """
    inicio = datetime.combine(hora_actual.date(), hora_inicio)
    fin = datetime.combine(hora_actual.date(), hora_fin)

    if hora_inicio > hora_fin:  # caso turno cruzando medianoche
        if hora_actual.time() < hora_fin:
            inicio = datetime.combine(hora_actual.date() - timedelta(days=1), hora_inicio)
        else:
            fin = datetime.combine(hora_actual.date() + timedelta(days=1), hora_fin)

    return inicio, fin


class Simulador:
    #Clase que gestiona la simulacion de los camiones
    #encapsula el estado y los metodos relacionados

    def __init__(self, ruta_archivos):
        self.rutas_kml = {}
        self.simulacion_data = {}
        self.ruta_archivos = ruta_archivos
        self.inicializar_simulacion()
    

    def cargar_rutas_kml(self):
        """ Carga todos los archivos KML de las rutas de los camiones desde el directorio de datos y los almacenaa en el diccionario rutas_kml"""

        logging.info("Cargando rutas kml")

        #creamos la ruta absoluta al directorio donde estan los recorridos
        rutas_dir = os.path.join(self.ruta_archivos, 'Recorridos')

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
                    self.rutas_kml[nombre_ruta] = line
                    logging.info(f"Ruta '{nombre_ruta}' cargada con exito")

                except Exception as e:
                    logging.error(f"No se pudo procesar el archivo kml '{filename}': {e}")



    def inicializar_simulacion(self):
        """
        Carga las rutas KML y pre-calcula la duración de la simulación para cada camión
        y turno. Esta función debe llamarse una sola vez al inicio de la aplicación.
        """
        self.cargar_rutas_kml()
        logging.info("Asignando duraciones aleatorias a cada camion por turno...")
     


        for zona, info_turno in TURNOS.items():
            for identificador in ['NS', 'EO']:
                nombre_ruta = f"RECORRIDO-{zona}-{identificador}"
                clave_simulacion = f"{nombre_ruta}_{info_turno['nombre']}"
                        
                # Obtener la duración total del turno en segundos
                inicio_segundos = info_turno['inicio'].hour * 3600 + info_turno['inicio'].minute * 60
                fin_segundos = info_turno['fin'].hour * 3600 + info_turno['fin'].minute * 60
                        
                # Manejar turnos que cruzan la medianoche
                if inicio_segundos > fin_segundos:
                    duracion_turno = (24 * 3600 - inicio_segundos) + fin_segundos
                else:
                    duracion_turno = fin_segundos - inicio_segundos

                # Generar una duración de ruta aleatoria más realista
                # Se asigna una duración que es un 90-95% del total del turno
                porcentaje_duracion = random.uniform(0.90, 0.95)
                duracion_realista = int(duracion_turno * porcentaje_duracion)
                        
                self.simulacion_data[clave_simulacion] = timedelta(seconds=duracion_realista)
   
        logging.info("Simulacion inicializada. Duraciones aleatorias asignadas por zona")
        logging.info(self.simulacion_data)


        




    def obtener_posicion_camion(self,zona,hora_actual):
        """
            Calcula la posición simulada del camión de la zona en un momento dado.
            
            Args:
                zona (str): El nombre de la zona (ej. 'A1').
                hora_actual (datetime): El objeto datetime con la hora actual.
                
            Returns:
                dict or None: Un diccionario con la posición y el estado del camión, o None si el camión no está en ruta.
            """

        info_turno = TURNOS.get(zona) #Busca la info del turno segun el nombre de la zona

        if not info_turno:
            return [{'estado': 'error_configuracion', 'mensaje': 'Zona no encontrada.'}]
        
        turno_activo = info_turno["nombre"]
        hora_inicio = info_turno["inicio"]
        hora_fin = info_turno["fin"]

        #determinamos si estamos fuera de servicio
        if hora_actual.time() < time (8,0):
            estado_global = 'fuera_de_servicio'
        else:
            estado_global = None


        #lista para almacenar los reusltados de cada camion
        posiciones_camiones =[]
        identificadores_rutas = ['NS','EO']

        #Iterar sobre los 2 camiones para cada zona
        for identificador in identificadores_rutas:
            camion_id = f"camion_{identificador}"
            nombre_ruta = f"RECORRIDO-{zona}-{identificador}"
            clave_simulacion = f"{nombre_ruta}_{turno_activo}"

            linea_recorrido = self.rutas_kml.get(nombre_ruta)
            duracion_total = self.simulacion_data.get(clave_simulacion)

            if not linea_recorrido or not duracion_total:
                logging.error(f"No se encontro la ruta o datos de simulacion para {clave_simulacion}")
                posiciones_camiones.append({'estado': 'error_configuracion', 'camion_id': camion_id})
                continue
            
            #si estamos antes de las 8 de la mañanaa, directamente estamos fuera de servicio
            if estado_global == 'fuera_de_servicio':
                posiciones_camiones.append({
                    'estado': 'fuera_de_servicio',
                    'camion_id': camion_id,
                    'identificador_ruta': nombre_ruta,
                    'ruta_line_string': linea_recorrido
                })
                continue

            # COMENTARIO: Se definen los objetos datetime para las horas de inicio y fin del turno.
            horario_inicio_turno, horario_fin_turno = calcular_horario_turno(hora_actual, hora_inicio, hora_fin) 
            
            if hora_actual < horario_inicio_turno:
                estado = 'no_iniciado'
                posiciones_camiones.append({
                    'estado': estado, 
                    'camion_id': camion_id, 
                    'identificador_ruta': nombre_ruta,
                    'ruta_line_string': linea_recorrido
                })
            elif horario_inicio_turno <= hora_actual < horario_fin_turno:
                tiempo_transcurrido = hora_actual - horario_inicio_turno
                if tiempo_transcurrido >= duracion_total:
                    estado = 'finalizado'
                    posiciones_camiones.append({
                        'estado': estado, 
                        'camion_id': camion_id, 
                        'identificador_ruta': nombre_ruta,
                        'ruta_line_string': linea_recorrido
                    })
                else:
                    estado = 'en_ruta'
                    #calcular la posicion actual del camion en la ruta
                    porcentaje_recorrido = tiempo_transcurrido / duracion_total
                    posicion_actual = linea_recorrido.interpolate(linea_recorrido.length * porcentaje_recorrido, normalized=False)

                    latitud_actual = posicion_actual.y
                    longitud_actual = posicion_actual.x

                    #calcular distancia y tiempo restantes.
                    longitud_recorrida = linea_recorrido.length * porcentaje_recorrido
                    distancia_restante_km = (linea_recorrido.length - longitud_recorrida) / 1000
                    tiempo_restante = duracion_total - tiempo_transcurrido

                    posiciones_camiones.append({
                        'estado': 'en_ruta',
                        'camion_id': camion_id,
                        'latitud': latitud_actual,
                        'longitud': longitud_actual,
                        'distancia_restante': distancia_restante_km,
                        'tiempo_restante': tiempo_restante,
                        'turno': turno_activo,
                        'identificador_ruta': nombre_ruta,
                        'ruta_line_string': linea_recorrido
                    })
                    
            else:
                estado = 'finalizado'
                posiciones_camiones.append({
                    'estado': estado,
                    'camion_id': camion_id,
                    'identificador_ruta': nombre_ruta,
                    'ruta_line_string': linea_recorrido
                })
                

        return posiciones_camiones
        











