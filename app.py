#Inicia Flask y se definen rutas de APIs y de vistas

from flask import Flask, request, redirect, url_for, session, render_template, flash
import os
from werkzeug.utils import secure_filename
import BackEnd.login as login
from BackEnd.db import usuarios

app = Flask(__name__)
app.secret_key = 'f1144cc94278494f8b3a61a689a658a2' #clave para la sesion

# Rutas de la API
@app.route('/')
def index():
    return "API DE USUARIOS!!!"

@app.route('/login', methods=['POST', 'GET'])
def login_route():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        if login.validar_usuario(usuario, contrasena):
            session['usuario'] = usuario
            return redirect(url_for('dashboard'))
        else:
            flash("Usuario o contraseña incorrectos.")
            return redirect(url_for('login_route'))
        
    
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'usuario' in session:
        lista_usuarios = usuarios.verUsuarios()
        return render_template('dashboard.html', usuarios=lista_usuarios)
    else:
        return redirect(url_for('login_route'))


@app.route('/eliminar_usuario', methods = ['POST'])
def eliminar_usuario():
    ids_seleccionados = request.form.getlist('ids')

    for id in ids_seleccionados:
        usuarios.eliminarUsuario(id)
    
    return redirect(url_for('dashboard'))

@app.route('/agregar_usuario', methods = ['POST'])
def agregar_usuario():
    dni = request.form['dni']
    nombre = request.form['nombre']
    email = request.form['email']
    contrasena = request.form['contrasena']

    usuarios.crearUsuario(dni,nombre,email,contrasena)

    return redirect(url_for('dashboard'))

    
# Carpeta donde se guardan los archivos subidos
CARPETA_KML = os.path.join(os.path.dirname(__file__), 'Data')
ALLOWED_EXTENSIONS = {'kml'}

#validar que la extension del archivo sea valida
def extension_valida(nombre_archivo):
    return '.' in nombre_archivo and nombre_archivo.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/agregar_recorrido', methods = ['POST'])
def agregar_recorrido():
    if 'archivos_kml' not in request.files:
        flash('No se enviaron los archivos.')
        return redirect(url_for('dashboard'))
    
    archivos = request.files.getlist('archivos_kml')
    print("Cantidad de archivos recibidos:", len(archivos))
    for a in archivos:
        print("→", a.filename)

    for archivo in archivos:
        if archivo.filename == '':
            flash('No se seleccionó ningún archivo.')

        if archivo and extension_valida(archivo.filename):
            nombre_seguro = secure_filename(archivo.filename)
            ruta = os.path.join(CARPETA_KML, nombre_seguro)
            archivo.save(ruta)
            flash('Archivo subido exitosamente.')
        else:
            flash('Formato de archivo no permitido. Solo se permiten archivos KML.')

    

    

    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login_route'))



if __name__ == "__main__":
    app.run(debug=True, port = 4000)