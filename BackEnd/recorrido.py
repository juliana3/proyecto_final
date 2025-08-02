# lectura de los archivos kml y manejo de recorridos
from pykml import parser
from lxml import etree
from shapely.geometry import Point, Polygon
import os

# Importa la función de geocodificación desde el archivo geolocalizacion.py
from BackEnd.geocodificacion import geocodificar_direccion

# Lista para almacenar las zonas de recolección
zonas_recoleccion = []
# Variable para almacenar el polígono del área de servicio total
area_servicio = None
# Variable global para el polígono de los límites de Santa Fe
santa_fe_limites = None

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
        
        print("DEBUG: KML cargado. Buscando polígonos...")
        
        # En tu KML, el documento principal está anidado dentro de la etiqueta <kml>.
        # Accedemos a él directamente.
        document = root.Document
        
        if document is not None:
            print(f"DEBUG: Encontrado el Documento principal: '{document.name}'. Procesando sus sub-características...")
            
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
                        print(f"Área de servicio '{feature_name}' cargada.")
                    elif feature_name_clean.startswith('A'):
                        zonas_recoleccion.append({
                            'nombre': feature_name,
                            'poligono': polygon
                        })
                        print(f"Zona de recolección '{feature_name}' cargada.")
                    else:
                        print(f"DEBUG:   > Placemark '{feature_name}' no es un polígono de zona o límite reconocido.")
                else:
                    print(f"DEBUG:   > Placemark '{feature_name}' no tiene una geometría de Polígono. Se omite.")
        else:
            print("Advertencia: El archivo KML no contiene un Documento principal.")
        
        # Mensajes de estado final
        if area_servicio is None:
            print("Advertencia: No se encontró el polígono 'ZONA LÍMITE' en el KML.")
        if not zonas_recoleccion:
            print("Advertencia: No se encontraron zonas de recolección en el KML.")
        
        print("\nDEBUG: Procesamiento de KML finalizado.")

    except FileNotFoundError:
        print(f"Error: El archivo KML no se encontró en la ruta: {ruta_archivo_kml}. Asegúrate de que 'ZONA_LIMITE.kml' esté en la carpeta 'Data'.")
    except Exception as e:
        print(f"Error al cargar o parsear el KML: {e}")
        import traceback
        traceback.print_exc()

def esta_en_area_servicio(latitud, longitud):
    """Verifica si un punto está dentro de la zona de servicio."""
    if area_servicio is None:
        print("Error: Área de servicio no definida.")
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
        # Definir los límites de la ciudad de Santa Fe (valores más precisos)
        # Esto es un polígono de prueba más detallado.
        limites = [
            (-60.70862, -31.5635),  
            (-60.66622, -31.59801),  
            (-60.68918, -31.64419),  
            (-60.72693, -31.67182),  
            (-60.73795, -31.65453),  
            (-60.73926, -31.64104),  
            (-60.72235, -31.61685),  
            (-60.75133, -31.58019),
            (-60.70862, -31.5635)   # Cerrar el polígono
        ]
        santa_fe_limites = Polygon(limites)

    punto = Point(longitud, latitud)
    return santa_fe_limites.contains(punto)

if __name__ == "__main__":
    # ... (El código de prueba principal que ya tenías)
    ruta_directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_base_proyecto = os.path.dirname(ruta_directorio_actual)
    ruta_kml_zonas = os.path.join(ruta_base_proyecto, 'Data', 'ZONA_LIMITE.kml')

    print(f"Intentando cargar KML desde: {ruta_kml_zonas}")
    cargar_kml_zonas(ruta_kml_zonas)
    
    # --- PRUEBA CON UNA DIRECCIÓN DE TEXTO USANDO LA FUNCIÓN IMPORTADA ---
    direccion_prueba = "Avenida General Paz 5450"
    print(f"\nIntentando geocodificar la dirección: '{direccion_prueba}'")
    coords_prueba = geocodificar_direccion(direccion_prueba)

    if coords_prueba:
        lat_prueba, lon_prueba = coords_prueba
        print(f"Coordenadas obtenidas: Latitud={lat_prueba}, Longitud={lon_prueba}")

        print(f"\nProbando punto (Lat: {lat_prueba}, Lon: {lon_prueba}):")
        if es_de_santa_fe(lat_prueba, lon_prueba):
            print("El punto está dentro de los límites de la ciudad de Santa Fe.")
            if esta_en_area_servicio(lat_prueba, lon_prueba):
                print("Está dentro del área de servicio.")
                zona = obtener_zona_recoleccion(lat_prueba, lon_prueba)
                if zona:
                    print(f"Pertenece a la zona: {zona}")
                else:
                    print("No pertenece a una zona de recolección específica dentro del área de servicio.")
            else:
                print("Está en Santa Fe, pero NO está dentro del área de servicio específica.")
        else:
            print("El punto NO está dentro de los límites de la ciudad de Santa Fe.")

    else:
        print("No se pudo geocodificar la dirección. Fin del programa.")
    
    # --- PRUEBAS CON COORDENADAS FIJAS ORIGINALES ---
    print("\n--- PRUEBAS CON COORDENADAS FIJAS ORIGINALES ---")
    lat_dentro_area_servicio = -31.63696
    lon_dentro_area_servicio = -60.70776
    lat_en_santa_fe_pero_fuera_servicio = -31.65,
    lon_en_santa_fe_pero_fuera_servicio = -60.72

    print(f"\nProbando punto (Lat: {lat_dentro_area_servicio}, Lon: {lon_dentro_area_servicio}):")
    if es_de_santa_fe(lat_dentro_area_servicio, lon_dentro_area_servicio):
        print("El punto está dentro de los límites de la ciudad de Santa Fe.")
        if esta_en_area_servicio(lat_dentro_area_servicio, lon_dentro_area_servicio):
            print("Está dentro del área de servicio.")
            zona = obtener_zona_recoleccion(lat_dentro_area_servicio, lon_dentro_area_servicio)
            if zona:
                print(f"Pertenece a la zona: {zona}")
        else:
            print("Está en Santa Fe, pero NO está dentro del área de servicio específica.")
    else:
        print("El punto NO está dentro de los límites de la ciudad de Santa Fe.")
    
    print(f"\nProbando punto (Lat: {lat_en_santa_fe_pero_fuera_servicio}, Lon: {lon_en_santa_fe_pero_fuera_servicio}):")
    if es_de_santa_fe(lat_en_santa_fe_pero_fuera_servicio, lon_en_santa_fe_pero_fuera_servicio):
        print("El punto está dentro de los límites de la ciudad de Santa Fe.")
        if esta_en_area_servicio(lat_en_santa_fe_pero_fuera_servicio, lon_en_santa_fe_pero_fuera_servicio):
            print("Está dentro del área de servicio.")
        else:
            print("Está en Santa Fe, pero NO está dentro del área de servicio específica.")
    else:
        print("El punto NO está dentro de los límites de la ciudad de Santa Fe.")
