#Inicia Flask y se definen rutas de APIs y de vistas

from datetime import datetime
from flask import Flask, jsonify, request, render_template
import os
import logging

from BackEnd.zonas import cargar_kml_zonas, esta_en_area_servicio, es_de_santa_fe, cargar_poligono_santa_fe, obtener_zona_recoleccion
from BackEnd.geocodificacion import geocodificar_direccion
from BackEnd.simulador import Simulador, TURNOS
from BackEnd.distancia import calcular_tiempo_a_destino

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
simulador_camiones = Simulador(DATA_DIR)
logging.info("Simulador listo. La aplicación puede empezar a recibir peticiones.")


# Rutas de la API
@app.route('/') #aca va lo primero qe ve el usuario 
def index():
    return render_template('index.html')


#este endpoitn puede recibit una direccion escrita o coordenadas gps
@app.route('/consultar_ubicacion', methods=['POST'])
def consultar_ubicacion():
    datos = request.get_json()
    lat_usuario = datos.get("latitud")
    lon_usuario = datos.get("longitud")
    direccion_escrita = datos.get("direccion")
    direccion_coordenadas = None

    if direccion_escrita:
        #si se recibe una direccion escrita se la geocodifica, se la pasa a coordenadas
        direccion_coordenadas = geocodificar_direccion(direccion_escrita)
        if not direccion_coordenadas:
            return jsonify({'mensaje': 'No se pudo encontrar la dirección. Por favor verificá la direccion que colocaste.'}), 404
        
        lat_usuario, lon_usuario = direccion_coordenadas
    elif lat_usuario is not None and lon_usuario is not None:
        #si se reciben coordenadas gps, se las usa directamente
        pass
    else:
        return jsonify({'error': 'Se requiere una dirección o coordenadas GPS'}), 400
    
    # --1: VERIFICAR SI ESTA EN SANTA FE
    en_santa_fe = es_de_santa_fe(lat_usuario, lon_usuario)
    if not en_santa_fe:
        return jsonify({'mensaje': 'Tu dispositivo no se encuentra en la ciudad de Santa Fe. Por favor ingresa la direccion manualmente.'})
    
    # --2: VERIFICAR SI ESTA EN EL AREA DE SERVICIO
    en_area_servicio = esta_en_area_servicio(lat_usuario, lon_usuario)
    if not en_area_servicio:
        return jsonify({'mensaje': 'Estás en Santa Fe, pero fuera del área de servicio de recolección.'})

    # --3: OBTENER LA ZONA DE RECOLECCION
    zona = obtener_zona_recoleccion(lat_usuario, lon_usuario)
    if not zona:
        return jsonify({'mensaje': 'Tu dirección está en el área de servicio, pero no se pudo asignar a una zona específica.'})
    
    hora_actual = datetime.now()
    posiciones_camiones = simulador_camiones.obtener_posicion_camion(zona, hora_actual)
    logging.info(f"Posiciones de camiones para la zona {zona} a las {hora_actual}: {posiciones_camiones}")

    # --4: CALCULAR EL TIEMPO DE LLEGADA DEL CAMION MAS CERCANO
    logging.info("Calculando tiempo estimado de llegada...")
    resultado_distancia = calcular_tiempo_a_destino(lat_usuario, lon_usuario,posiciones_camiones)
    logging.info(f"Resultado del cálculo de distancia a la dirección {lat_usuario}, {lon_usuario}: {resultado_distancia}")

    return jsonify(resultado_distancia)



if __name__ == "__main__":
    app.run(debug=True, port = 4000, host='0.0.0.0')