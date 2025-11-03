from datetime import datetime
from flask import Flask, jsonify, request, render_template
import os
import logging
from flask_cors import CORS  # <--- agregado para CORS

from BackEnd.zonas import (
    cargar_kml_zonas,
    esta_en_area_servicio,
    es_de_santa_fe,
    cargar_poligono_santa_fe,
    obtener_zona_recoleccion
)
from BackEnd.geocodificacion import geocodificar_direccion
from BackEnd.simulador import Simulador, TURNOS
from BackEnd.distancia import calcular_tiempo_a_destino
from BackEnd.DEMO import es_direccion_demo, obtener_respuesta_demo

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Inicializar app Flask
app = Flask(__name__)

# Habilitar CORS (puede ser CORS(app, origins=["http://localhost:5173"]) para limitar)
CORS(app)

app.config['SERVER_NAME'] = None  # Permite cualquier host

# Rutas absolutas del proyecto y datos
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, 'Data')

# Cargar datos geográficos
ruta_kml_zonas = os.path.join(DATA_DIR, 'ZONA_LIMITE.kml')
ruta_kml_limites_santa_fe = os.path.join(DATA_DIR, 'poligono-santa-fe.kml')

logging.info("Cargando datos geográficos...")
cargar_poligono_santa_fe(ruta_kml_limites_santa_fe)
cargar_kml_zonas(ruta_kml_zonas)
logging.info("Carga de KML finalizada.")

# Inicializar simulador
logging.info("Inicializando simulador...")
simulador_camiones = Simulador(DATA_DIR)
logging.info("Simulador listo. La aplicación puede empezar a recibir peticiones.")


# Ruta principal
@app.route('/')
def index():
    return jsonify({
        'message': 'API de BASURAPP funcionando correctamente',
        'version': '1.0',
        'endpoints': ['/consultar_ubicacion']
    })


# Endpoint principal: recibe dirección escrita o coordenadas GPS
@app.route('/consultar_ubicacion', methods=['POST'])
def consultar_ubicacion():
    datos = request.get_json()
    lat_usuario = None
    lon_usuario = None

    # Verificar modo DEMO
    if datos.get('direccion'):
        direccion_escrita = datos.get('direccion')
        
        if es_direccion_demo(direccion_escrita):
            respuesta_demo = obtener_respuesta_demo(direccion_escrita)
            return jsonify({
                'mensaje': respuesta_demo['mensaje']
            }), respuesta_demo['status_code']


    # Si vienen coordenadas
    if datos.get('latitud') is not None and datos.get('longitud') is not None:
        lat_usuario = datos.get('latitud')
        lon_usuario = datos.get('longitud')
        logging.info("Cálculo mediante coordenadas del navegador (UBICACIÓN ACTUAL)")
    elif datos.get('direccion'):
        # Si viene dirección escrita 
        direccion_escrita = datos.get('direccion')
        direccion_coordenadas = geocodificar_direccion(direccion_escrita)

        logging.info("Cálculo mediante dirección escrita.")
        if not direccion_coordenadas:
            logging.info("No se pudo encontrar la dirección.")
            return jsonify({'mensaje': 'No se pudo encontrar la dirección. Por favor verificá la dirección.'}), 404

        lat_usuario, lon_usuario = direccion_coordenadas
    else:
        logging.info("No se recibió ubicación válida.")
        return jsonify({
            'mensaje': 'No recibimos ubicación válida. Compartí tu ubicación o ingresá tu dirección manualmente.'}), 400

    # 1: Verificar si está en Santa Fe
    if not es_de_santa_fe(lat_usuario, lon_usuario):
        logging.info("El dispositivo no se encuentra en la ciudad de Santa Fe.")
        return jsonify({
            'mensaje': 'Tu dispositivo no se encuentra en la ciudad de Santa Fe. Por favor ingresá la dirección manualmente.'})

    # 2: Verificar si está en el área de servicio
    if not esta_en_area_servicio(lat_usuario, lon_usuario):
        logging.info("El dispositivo se encuentra en Santa Fe pero fuera del área de servicio.")
        return jsonify({
            'mensaje': 'Estás en Santa Fe, pero fuera del área de servicio de recolección.'})

    # 3: Obtener la zona de recolección
    zona = obtener_zona_recoleccion(lat_usuario, lon_usuario)
    if not zona:
        logging.info("No se pudo asignar la dirección a una zona específica.")
        return jsonify({'mensaje': 'Tu dirección está en el área de servicio, pero no se pudo asignar a una zona específica.'})

    # 4: Calcular el tiempo de llegada del camión más cercano
    hora_actual = datetime.now()
    posiciones_camiones = simulador_camiones.obtener_posicion_camion(zona, hora_actual)
    logging.info(f"Posiciones de camiones para la zona {zona} a las {hora_actual}: {posiciones_camiones}")

    logging.info("Calculando tiempo estimado de llegada...")
    resultado_distancia = calcular_tiempo_a_destino(lat_usuario, lon_usuario, posiciones_camiones)
    logging.info(f"Resultado del cálculo de distancia a la dirección {lat_usuario}, {lon_usuario}: {resultado_distancia}")

    return jsonify(resultado_distancia)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4000))  # Usa el puerto de Render o 4000 local
    app.run(debug=False, port=port, host='0.0.0.0')  # debug=False en producción
