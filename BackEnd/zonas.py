# lectura de los archivos kml y manejo de recorridos
from pykml import parser
from lxml import etree
from shapely.geometry import Point, Polygon
import os
import logging

# Importa la función de geocodificación desde el archivo geolocalizacion.py
from BackEnd.geocodificacion import geocodificar_direccion

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


# Lista para almacenar las zonas de recolección
zonas_recoleccion = []
# Variable para almacenar el polígono del área de servicio total
area_servicio = None
# Variable global para el polígono de los límites de Santa Fe
santa_fe_limites = None


def cargar_poligono_santa_fe(ruta_kml_santa_fe):
    """
    Carga un archivo KML y extrae el polígono que representa los límites de la ciudad de Santa Fe.

    Args:
        ruta_kml_santa_fe: La ruta al archivo KML con los límites de la ciudad.
    """
    global santa_fe_limites
    
    if not os.path.exists(ruta_kml_santa_fe):
        logging.error(f"Archivo KML de límites de Santa Fe no encontrado en la ruta: {ruta_kml_santa_fe}")
        return

    try:
        with open(ruta_kml_santa_fe, 'rb') as kml_file:
            root = parser.parse(kml_file).getroot()
        
        logging.debug("KML de límites de Santa Fe cargado. Buscando polígono...")
        document = root.Document
        
        if document is not None:
            for placemark in document.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
                if hasattr(placemark, 'Polygon') and placemark.Polygon is not None:
                    coords_text = placemark.Polygon.outerBoundaryIs.LinearRing.coordinates.text
                    coords_list = [tuple(map(float, c.split(','))) for c in coords_text.strip().split()]
                    
                    polygon_coords = [(c[0], c[1]) for c in coords_list]
                    santa_fe_limites = Polygon(polygon_coords)
                    logging.info(f"Polígono de límites de Santa Fe cargado exitosamente.")
                    return
        logging.warning("No se encontró un polígono en el KML de límites de Santa Fe.")

    except FileNotFoundError:
        logging.error(f"El archivo KML de límites no se encontró en la ruta: {ruta_kml_santa_fe}.")
    except Exception as e:
        logging.error(f"Error al cargar o parsear el KML de límites: {e}")
        import traceback
        traceback.print_exc()

def cargar_kml_zonas(ruta_archivo_kml):
    """
    Carga un archivo KML y extrae los polígonos que representan las zonas de recolección
    y el área de servicio principal usando pykml.
    """
    global zonas_recoleccion, area_servicio
    
    zonas_recoleccion = []
    area_servicio = None

    try:
        with open(ruta_archivo_kml, 'rb') as kml_file:
            root = parser.parse(kml_file).getroot()
        
        logging.debug("KML cargado. Buscando polígonos...")
        
        # En tu KML, el documento principal está anidado dentro de la etiqueta <kml>.
        # Accedemos a él directamente.
        document = root.Document
        
        if document is not None:
            logging.debug(f"Encontrado el Documento principal: '{document.name}'. Procesando sus sub-características...")
            
            # Buscamos todos los Placemarks dentro del Documento
            for placemark in document.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
                feature_name = placemark.name.text
                
                # Comprobación robusta para ver si el Placemark tiene un Polygon
                if hasattr(placemark, 'Polygon') and placemark.Polygon is not None:
                    coords_text = placemark.Polygon.outerBoundaryIs.LinearRing.coordinates.text
                    coords_list = [tuple(map(float, c.split(','))) for c in coords_text.strip().split()]
                    
                    # Las coordenadas en KML son (longitud, latitud, altitud).
                    # Necesitamos (longitud, latitud)
                    polygon_coords = [(c[0], c[1]) for c in coords_list]
                    polygon = Polygon(polygon_coords)

                    feature_name_clean = feature_name.upper().strip()
                    if feature_name_clean == "ZONA LÍMITE" or feature_name_clean == "ZONA LIMITE":
                        area_servicio = polygon
                        logging.info(f"Área de servicio '{feature_name}' cargada.")
                    elif feature_name_clean.startswith('A'):
                        zonas_recoleccion.append({
                            'nombre': feature_name,
                            'poligono': polygon
                        })
                        logging.info(f"Zona de recolección '{feature_name}' cargada.")
                    else:
                        logging.debug(f"> Placemark '{feature_name}' no es un polígono de zona o límite reconocido.")
                else:
                    logging.debug(f"> Placemark '{feature_name}' no tiene una geometría de Polígono. Se omite.")
        else:
            logging.warning("El archivo KML no contiene un Documento principal.")
        
        # Mensajes de estado final
        if area_servicio is None:
            logging.warning("No se encontró el polígono 'ZONA LÍMITE' en el KML.")
        if not zonas_recoleccion:
            logging.warning("No se encontraron zonas de recolección en el KML.")
        
        logging.debug("Procesamiento de KML finalizado.")

    except FileNotFoundError:
        logging.error(f"El archivo KML no se encontró en la ruta: {ruta_archivo_kml}. Asegúrate de que 'ZONA_LIMITE.kml' esté en la carpeta 'Data'.")
    except Exception as e:
        logging.error(f"Error al cargar o parsear el KML: {e}")
        import traceback
        traceback.print_exc()

def esta_en_area_servicio(latitud, longitud):
    """Verifica si un punto está dentro de la zona de servicio."""
    if area_servicio is None:
        logging.error("Área de servicio no definida.")
        return False
    punto = Point(longitud, latitud) 
    return area_servicio.contains(punto)

def obtener_zona_recoleccion(latitud, longitud):
    """Devuelve el nombre de la zona de recolección para un punto dado."""
    punto = Point(longitud, latitud) 
    for zona in zonas_recoleccion:
        if zona['poligono'].contains(punto):
            return zona['nombre']
    return None


def es_de_santa_fe(latitud, longitud):
    """
    Verifica si un punto está dentro de los límites de la ciudad de Santa Fe.
    Usa un polígono de prueba para simular los límites de la ciudad.
    
    NOTA: Reemplazar este polígono por un KML real de los límites de la ciudad
    en un entorno de producción.
    """
    global santa_fe_limites
    if santa_fe_limites is None:
        logging.error("El polígono de Santa Fe no ha sido cargado. No se puede verificar la ubicación.")
        return False

    punto = Point(longitud, latitud)
    return santa_fe_limites.contains(punto)



