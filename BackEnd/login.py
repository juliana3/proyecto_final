#validacion de usuario y contraseña del administrador
import sqlite3 as sql
from werkzeug.security import check_password_hash


#definimos la funcion para validar el usuario y contrasseña
def validar_usuario(_usuario, _contrasena):
    conn = sql.connect('db/usuarios.db')
    cursor = conn.cursor()

    instruccion = "SELECT contrasena FROM usuarios WHERE dni = ?"

    cursor.execute(instruccion, (_usuario,))

    resultado = cursor.fetchone()
    conn.close()

    if resultado and check_password_hash(resultado[0], _contrasena):
        return True
    else:
        return False
    