from flask import Flask, jsonify, render_template, request # Importa flask para crear la web en en enlace raiz
import psycopg2 # Permite conectarse con la base de datos
from psycopg2.extras import RealDictCursor # Devuelve los resultados de las consultas que se hagan
import os # Permite las variables de sistema 
from datetime import datetime # Sirve para trabajar con fechas y horas exactas


# Congifuracion de la aplicacion:

app = Flask(__name__) 
DB_CONFIG = { # La configuracion interna de la base de la datos
    'host': 'localhost',
    'database': 'diseño',
    'user': 'postgres',
    'password': 123456,
    'port': 5432
}

def conectar_db(): # Funcion para conectar la base de datos
    try: # Intentar hacer una conexion con los datos de configuracion
        conexion = psycopg2.connect(**DB_CONFIG) # importar la libreria de psycopg2
        return conexion # Si todo sale correcto devuelve la conexion
    except psycopg2.Error as e: # Si sale mal saldra en la consola
        print("La conexion con la base de datos fue erronea", e)
        return None # retorna un mensaje si falta la conexion
    # Crear la tabla contactos
def crear_tabla():
    conexion = conectar_db() # Se conectara a la base de datos directamente si todo sale bien
    if conexion:
        cursor = conexion.cursor() # Se crea un cursor para la conexion con la db
        cursor.execute("""
        CREATE TABLE if NOT EXISTS contactos(
                       id SERIAL PRIMARY KEY, --- Identificador unico ---
                       nombre VARCHAR (100) NOT NULL, --- Campo del nombre ---
                       correo VARCHAR (100) NOT NULL, --- Campo del correo ---
                       mesaje TEXT, --- Campo del mensaje ---
                       creado TIMESTAMP DEFAULT NOW() --- Fecha y hora de creacion ---
                       );

""")
        conexion.commit() # Guarda los cambios al trabajar en la base de datos
        cursor.close() # Cierra el cursor
        conexion.close() # Cierra la conexion con la base de datos


# Página principal (registro)
@app.route('/')
def index(): # Ruta del registro
    return render_template("index.html", titulo="Registro de cuenta")
@app.route('/contactos',methods=['POST'])
def guardar_contactos():
    try:
        conexion =conectar_db() # Conexion a la base de datos
        if conexion is None: # Si no se puede conectar a la base de datos devuelve error
            return jsonify({'error': 'no se pudo conectar a la base de datos'}), 500 # Retorna error 500 de conexion por no poder conectar la base de datos
        
        # OBTIENE TODOS LOS DATOS ENVIADOS EN FORMATO json
        datos = request.get_json()
        nombre = datos.get('nombre'.strip) # Obtiene el nombre sin espacio o genera error
        correo = datos.get('correo'.strip)
        mensaje = datos.get('mensaje'.strip) # Obtiene el nombre sin espacio o genera error

        # Validar que nombre y correo no esten vacios
        if not nombre or not correo:
            return jsonify({'error': 'no se pudo conectar a la base de datos'}), 400 # Retorna erro 400 de campos obligatorios 
        # Crear el cursor para ejecutarlo en SQL
        cursor = conexion.cursor()
        sql_insertar = """
        INSERT INTO contactos (nombre,correo,mensaje)
        VALUE(%s,%s,%s)
        RETURNIG id;
        """ # Conexion a consulta en la tabla para los nuevos contacto

        # ejecutar las consultas con las consultas recibidas
        cursor.execute(sql_insertar,(nombre,correo,mensaje))

        conectar_id = cursor.fetchone()[0] # obtiene el id del registro

        conexion.commit() # Guarda los cambios al trabajar en la base de datos

        cursor.close() # Cierra el cursor

        conexion.close() # Cierra la conexion con la base de datos

        # Devuelve un mensaje de exito con el id generado
        return jsonify({
            'mensaje': 'contacto guardado exitosamente',
            'id': 'contacto_id'
        })
    except Exception as e:
        print("Error al guardar el contacto ",e) # Si ocurre un error lo muestra y devuelve un mensaje de error
        return jsonify({'error': 'Error al procesar la solicitud'}), 500 # Retorna error 500 de conexion por no poder conectar la base de datos

# Ruta para consultar los datos guardados

@app.route('/contactos',methods=['GET'])
def ver_contactos():
    try:
        conexion = conectar_db() # Conexion a la base de datos
        if conexion is None:
            return jsonify({'error': 'no se pudo conectar a la base de datos'}), 500 # Retorna error 500 de conexion por no poder conectar la base de datos
        cursor = conexion.cursor(cursor_factory= RealDictCursor) # Crea un cursor que retorna diccionarios desde el inicio hasta el final
        cursor.execute("SELECT * FROM contactos ORDER BY creado DESC")# Sentencia SQL para seleccionar todos los contactos
        contactos = cursor.fetchall() # Obtiene todos los registros
        cursor.close() # Cierra la conexion
        # Formatear la fecha de creacion para que sea legible
        for contacto in contactos:
            if contacto['Creado']:
                contacto['Creado'] = contacto['Creado'].strftime('%y-%m-%d %H:%M:%S')
        # Devuelve la lista de datos de contacto en formato JSON
        return jsonify(contactos),200
    except Exception as e:
        print("Error al conectar la base de datos",e) # Si ocurre un error lo muestra y devuelve un mensaje de error
        return jsonify({'error': 'No se puede conectar la base de dato'}), 500 # Retorna error 500 de conexion por no poder conectar la base de datos
if __name__ == '__main__':
    print("Iniciando servidor. . . . . . . . . ")
    # crear_tabla() # Crea una tabla si no tengo conexion
    app.run(debug=True)





