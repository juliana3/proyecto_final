#Inicia Flask y se definen rutas de APIs y de vistas

from datetime import datetime
from flask import Flask, jsonify, request, render_template
import os
import logging

from BackEnd.zonas import cargar_kml_zonas, esta_en_area_servicio, es_de_santa_fe, cargar_poligono_santa_fe, obtener_zona_recoleccion
from BackEnd.geocodificacion import geocodificar_direccion
from BackEnd import simulador
from BackEnd import distancia

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = Flask(__name__)
app.secret_key = 'f1144cc94278494f8b3a61a689a658a2' #clave para la sesion

# Obtenemos la ruta absoluta del directorio del proyecto
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# La ruta a la carpeta 'Data' dentro del proyecto
DATA_DIR = os.path.join(PROJECT_ROOT, 'Data')

#cargar las zonas y areas de servicios
ruta_kml_zonas = os.path.join(DATA_DIR, 'ZONA_LIMITE.kml')
ruta_kml_limites_santa_fe = os.path.join(DATA_DIR, 'poligono-santa-fe.kml')

logging.info("Cargando datos geográficos...")
cargar_poligono_santa_fe(ruta_kml_limites_santa_fe)
cargar_kml_zonas(ruta_kml_zonas)
logging.info("Carga de KML finalizada.")


# Inicializamos el simulador al inicio del script, en lugar de usar un decorador
logging.info("Inicializando simulador...")
simulador.inicializar_simulacion(DATA_DIR)
logging.info("Simulador listo. La aplicación puede empezar a recibir peticiones.")


# Rutas de la API
@app.route('/') #aca va lo primero qe ve el usuario + boton de login
def index():
    return render_template('index.html')


@app.route('/verificar_ubicacion', methods=['POST'])
def verificar_ubicacion():
    """endpoint para recibir las coorddenadas GPS desde el front y validar si estan en santa fe"""

    datos = request.get_json()
    latitud = datos.get("latitud")
    longitud = datos.get("longitud")

    if latitud is not None and longitud is not None:
        #verificamos quee el usuario este en la ciudad de santa fe
        en_santa_fe = es_de_santa_fe(latitud,longitud)

       
        return jsonify({
            'en_santa_fe': en_santa_fe
        })
    else:
        return jsonify({'error':'Coordenadas no proporcionadas'}), 400


@app.route('/consultar_direccion', methods=['POST'])
def consultar_direccion():
    """
    Recibe una dirección de texto, la geocodifica, verifica si está en un
    área de servicio y devuelve el estado del camión más cercano.
    """
    datos = request.get_json()
    direccion = datos.get('direccion')

    if not direccion:
        return jsonify({'error': 'La dirección es requerida'}), 400

    
    coordenadas = geocodificar_direccion(direccion)

    if not coordenadas:
        return jsonify({'mensaje': 'No se pudo encontrar la dirección. Intenta ser más específico.'}), 404

    latitud_usuario, longitud_usuario = coordenadas

    # Paso 2: Verificar si la dirección está dentro de los límites de Santa Fe y del área de servicio
    en_santa_fe = es_de_santa_fe(latitud_usuario, longitud_usuario)
    en_area_servicio = esta_en_area_servicio(latitud_usuario, longitud_usuario)

    if not en_santa_fe:
        return jsonify({'mensaje': 'Tu dirección no se encuentra en la ciudad de Santa Fe.'})
    
    if not en_area_servicio:
        return jsonify({'mensaje': 'Estás en Santa Fe, pero fuera del área de servicio de recolección.'})

    # Paso 3: Si todo está bien, buscar la zona y el camión
    zona = obtener_zona_recoleccion(latitud_usuario, longitud_usuario)
    if not zona:
        return jsonify({'mensaje': 'Tu dirección está en el área de servicio, pero no se pudo asignar a una zona específica.'})

    hora_actual = datetime.now()
    posiciones_camiones = simulador.obtener_posicion_camion(zona, hora_actual)
    resultado_distancia = distancia.calcular_tiempo_a_destino(latitud_usuario, longitud_usuario, posiciones_camiones)
    
    return jsonify(resultado_distancia)

# Endpoint para obtener la posición de los camiones de una zona específica
@app.route('/api/camiones/posicion/<string:zona>', methods=['GET'])
def get_posicion_camiones(zona):
    """
    Endpoint para obtener la posición actual de los camiones de una zona específica.
    
    Args:
        zona: El identificador de la zona (ej. 'A1', 'A2', 'A3').
        
    Returns:
        json: Un objeto JSON con la posición de los camiones o un mensaje de error.
    """
    hora_actual = datetime.now()
    posiciones = simulador.obtener_posicion_camion(zona, hora_actual)
    
    if posiciones and 'estado' in posiciones[0] and posiciones[0]['estado'] == 'error_configuracion':
        return jsonify({'error': 'Error en la configuración del simulador'}), 500
    
    # En este caso, solo devolvemos los datos esenciales para la visualización en el mapa,
    # ya que no se necesita la geometría de la ruta completa en este endpoint.
    posiciones_simples = [
        {
            'estado': p['estado'],
            'camion_id': p['camion_id'],
            'latitud': p['latitud'],
            'longitud': p['longitud'],
            'turno': p['turno'],
            'identificador_ruta': p['identificador_ruta']
        } for p in posiciones if p.get('estado') == 'en_ruta'
    ]
    
    return jsonify(posiciones_simples)


# ENDPOINT para obtener el tiempo estimado de llegada
@app.route('/api/camiones/tiempo-estimado/<string:zona>', methods=['POST'])
def get_tiempo_estimado(zona):
    """
    Endpoint para calcular el tiempo de llegada del camión más cercano a la ubicación
    del usuario en una zona específica.
    
    Args:
        zona: El identificador de la zona (ej. 'A1', 'A2', 'A3').
        
    Returns:
        json: Un objeto JSON con el tiempo estimado de llegada o un mensaje de error.
    """
    datos = request.get_json()
    latitud_usuario = datos.get('latitud')
    longitud_usuario = datos.get('longitud')
    
    if latitud_usuario is None or longitud_usuario is None:
        return jsonify({'error': 'Latitud y longitud son requeridas'}), 400
        
    hora_actual = datetime.now()
    
    # Obtenemos la posición de los camiones, incluyendo la geometría de la ruta
    posiciones_camiones = simulador.obtener_posicion_camion(zona, hora_actual)
    
    # Verificamos si la respuesta del simulador es válida
    if posiciones_camiones and 'estado' in posiciones_camiones[0] and posiciones_camiones[0]['estado'] != 'en_ruta':
        # El camión de la zona no está en servicio, finalizado, o hay un error.
        return jsonify(posiciones_camiones[0])
    
    # Llamamos a la función de distancia para calcular el tiempo de llegada
    resultado_distancia = distancia.calcular_tiempo_a_destino(latitud_usuario, longitud_usuario, posiciones_camiones)
    
    return jsonify(resultado_distancia)


if __name__ == "__main__":
    app.run(debug=True, port = 4000)