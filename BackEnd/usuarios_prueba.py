import sqlite3 as sql
from werkzeug.security import generate_password_hash

# Conectar a la base
conn = sql.connect('db/usuarios.db')
cursor = conn.cursor()

# Datos del nuevo usuario
dni = 43957837  # O el campo que uses
contrasena_plana = "1234"
nombre= "Juliana"
email= ""

# Generar hash seguro
hash_contrasena = generate_password_hash(contrasena_plana)

cursor.execute("DELETE FROM usuarios")
conn.commit()

# Insertar
cursor.execute("INSERT INTO usuarios (dni, nombre, email, contrasena) VALUES (?, ?, ? ,?)", (dni,nombre, email,hash_contrasena))
conn.commit()
conn.close()

print("✅ Usuario creado correctamente.")
