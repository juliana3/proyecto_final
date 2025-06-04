import sqlite3 as sql
import os
ruta_bd = os.path.join(os.path.dirname(__file__), 'usuarios.db')

def crearDB():
    conn = sql.connect(ruta_bd)  # Conectar a la base de datos (se crea si no existe)
    print("Base de datos creada exitosamente")
    conn.commit()  # Guardar los cambios
    conn.close() # Cerrar la conexión

def crearTabla():
    conn = sql.connect(ruta_bd)  # Conectar a la base de datos
    cursor = conn.cursor()  # Crear un cursor para ejecutar comandos SQL
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            dni INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL
        )"""
    )  # Crear la tabla si no existe

    print("Tabla creada exitosamente")
    conn.commit()  # Guardar los cambios
    conn.close()  # Cerrar la conexión

#CRUD
def crearUsuario(dni,nombre,email,contrasena):
    conn = sql.connect(ruta_bd)  # Conectar a la base de datos
    cursor = conn.cursor()  # Crear un cursor para ejecutar comandos SQL

    #verificar si el usuario ya existe mediante el mail
    cursor.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,))
    usuario = cursor.fetchone() # Obtener el primer resultado

    if usuario is None:
        instruccion = "INSERT INTO usuarios (dni,nombre, email, contrasena) VALUES (?,?, ?, ?)"
        cursor.execute(instruccion, (dni,nombre, email, contrasena))

        print("Usuario creado exitosamente")
    else:
        print("Ya existe un usuario con esa DNI")


    

    conn.commit()  # Guardar los cambios
    conn.close()  # Cerrar la conexión

def verUsuarios():
    conn = sql.connect(ruta_bd)  # Conectar a la base de datos
    cursor = conn.cursor()  # Crear un cursor para ejecutar comandos SQL

    
    instruccion = "SELECT * FROM usuarios"
    cursor.execute(instruccion)

    usuarios = cursor.fetchall()  # Obtener todos los resultados
    if usuarios: #si existen usuarios, mostrarlos
        for usuario in usuarios:
            print(f"DNI: {usuario[0]}, Nombre: {usuario[1]}, Email: {usuario[2]}")
    else:
        print("No hay usuarios registrados.")

    conn.commit()  # Guardar los cambios
    conn.close()  # Cerrar la conexión

    return usuarios

def buscarUsuario(dni):
    conn = sql.connect(ruta_bd)  # Conectar a la base de datos
    cursor = conn.cursor()  # Crear un cursor para ejecutar comandos SQL

    
    instruccion = "SELECT * FROM usuarios WHERE dni = ?"
    cursor.execute(instruccion, (dni,))

    usuarios = cursor.fetchall()  # Obtener todos los resultados
    if usuarios: #si existen usuarios, mostrarlos
        for usuario in usuarios:
            print(f"DNI: {usuario[0]}, Nombre: {usuario[1]}, Email: {usuario[2]}")
    else:
        print("No hay usuarios registrados con ese DNI.")

    conn.commit()  # Guardar los cambios
    conn.close()  # Cerrar la conexión

def actualizarUsuario(dni, new_email, new_contrasena):
    conn = sql.connect(ruta_bd)  # Conectar a la base de datos
    cursor = conn.cursor()  # Crear un cursor para ejecutar comandos SQL

    
    instruccion = "UPDATE usuarios SET  email = ?, contrasena = ? WHERE dni = ?"
    cursor.execute(instruccion, (new_email,new_contrasena, dni))


    #verificar si se modifico el usuario

    if cursor.rowcount >0:
        print("Usuario actualizado exitosamente.")
    else:
        print("No se encontró un usuario con ese DNI")


    conn.commit()  # Guardar los cambios
    conn.close()  # Cerrar la conexión

def eliminarUsuario(dni):
    conn = sql.connect(ruta_bd)  # Conectar a la base de datos
    cursor = conn.cursor()  # Crear un cursor para ejecutar comandos SQL

    instruccion = "DELETE FROM usuarios WHERE dni = ?"
    cursor.execute(instruccion, (dni,))

    #verificar que se elimino el usuario
    if cursor.rowcount >0: #rowcount devuelve el numero de filas afectadas, si se elimino un usuario devuelve 1.
        print("Usuario eliminado exitosamente.")
    else:
        print("No se encontró un usuario con ese DNI")

    conn.commit()
    conn.close()

if __name__ == "__main__": #se ejecuta solo en el archivo donde esta escrito.
   pass