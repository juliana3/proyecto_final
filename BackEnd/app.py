#Inicia Flask y se definen rutas de APIs y de vistas

from flask import Flask, request, redirect, url_for, session, render_template
import login

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
            return "Usuario o contraseña incorrectos."
    
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'usuario' in session:
        return f"Bienvenido {session['usuario']} al panel de configuraciones."
    else:
        return redirect(url_for('login_route'))
    

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login_route'))




if __name__ == "__main__":
    app.run(debug=True, port = 4000)