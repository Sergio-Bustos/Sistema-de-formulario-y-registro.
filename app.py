#  Importaciones necesarias para la aplicación Flask

from flask import Flask, jsonify, render_template, request
import psycopg2                        # Para conectarse a PostgreSQL
from psycopg2.extras import RealDictCursor  # Devuelve resultados tipo diccionario
from datetime import datetime          # Para manejar fechas de creación en tiempo real

#  Configuración base de la aplicación Flask

app = Flask(__name__)  # Crea la aplicación Flask


#  Configuración de conexión a la base de datos PostgreSQL

DB_CONFIG = {
    'host': 'localhost',     # Servidor de base de datos (local)
    'database': 'diseño', # Nombre de la base de datos creada
    'user': 'postgres',      # Usuario por defecto de PostgreSQL,o dueño
    'password': '123456',    # Contraseña del usuario
    'port': 5432             # Puerto por defecto de PostgreSQL
}


#  Función para conectar a la base de datos

def conectar_bd():
    """Establece conexión con la base de datos PostgreSQL."""
    try:
        conexion = psycopg2.connect(**DB_CONFIG)
        return conexion  # Devuelve la conexión si es exitosa
    except psycopg2.Error as e: # La e se vuelve una variable de un 'metodo' erroneo para psycopg2
        print(f"Error al conectar a la base de datos: {e}") # Printea el error
        return None      # Devuelve None si no se pudo conectar


#  Página principal: muestra el formulario HTML

@app.route('/') # La primera ruta por defecto por Flask
def inicio(): # Funcion que permitira ejecutar la primera pagina
    """Ruta principal que muestra el formulario HTML."""
    return render_template('index.html')  # Carga de la carpeta templates el archivo index.html


#  Ruta para guardar los datos enviados desde el formulario

@app.route('/formulario', methods=['POST']) # No es una página, es una ruta lógica:
#  No se abre en el navegador como un HTML visual
#  pero sí existe internamente dentro del servidor Flask para recibir datos.

# GET → para pedir datos (por ejemplo, ver información)

# POST → para enviar datos (por ejemplo, enviar un formulario),en este caso para enviar los datos del formulario

# PUT, DELETE → para actualizar o eliminar datos, respectivamente.


# Funcion para guardar cada formulario despues del metodo POST que envia los datos

def guardar_contacto():
    """Guarda los datos del formulario en la base de datos."""
    conexion = None # Por ahora es None la conexion
    cursor = None # Cursos por ahora es None
    try:
        conexion = conectar_bd()  # Hace la funcion de conectarse a la base de datos
        if conexion is None: # Si no se hizo la conexion
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500 # Imprime error 500

        # Captura los datos enviados desde el formulario HTML
        datos = request.form # Metodo para recoger los datos del formulario
        nombre = datos.get('nombre', '').strip() # .strip() para dejar sin espacios y .get para agarrar el valor
        apellido = datos.get('apellido', '').strip() # .strip() para dejar sin espacios y .get para agarrar el valor
        direccion = datos.get('direccion', '').strip() # .strip() para dejar sin espacios y .get para agarrar el valor
        telefono = datos.get('telefono', '').strip() # .strip() para dejar sin espacios y .get para agarrar el valor
        correo = datos.get('correo', '').strip() # .strip() para dejar sin espacios y .get para agarrar el valor
        mensaje = datos.get('mensaje', '').strip() # .strip() para dejar sin espacios y .get para agarrar el valor

        # Validar campos obligatorios
        if not nombre or not correo: # Si no ingreso ni nombre ni correo
            return jsonify({'error': 'Nombre y correo son obligatorios'}), 400 # Imprime error 400

        # Crear cursor para ejecutar la consulta SQL
        cursor = conexion.cursor() 

        # Insertar datos en la tabla 'contactos'
        # Codigo SQL con la funcion del cursor.execute para ejecutar:
        cursor.execute("""
            INSERT INTO contactos (nombre, apellido, direccion, telefono, correo, mensaje)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (nombre, apellido, direccion, telefono, correo, mensaje))

        contacto_id = cursor.fetchone()[0]  # Obtener el ID del registro insertado
        conexion.commit()                   # Confirmar los cambios

        # Respuesta exitosa en formato JSON
        return jsonify({ # Retorna si funciono bien o no
            'mensaje': ' Contacto guardado exitosamente',
            'id': contacto_id
        }), 201

    except Exception as e: # Se crea la variable e con la funcion del error Exception de psycopg2
        print(f" Error al guardar el contacto: {e}") # Y se imprime el error que sucedio: No se pudo guardar el contacto
        return jsonify({'error': 'Error al procesar la solicitud'}), 500 # Se imprime nuevamente si no se pudo cargar la solicitud en la web

    finally:
        # Cerrar cursor y conexión (si existen)
        # Se cierra el cursos y la conexion con la db
        if cursor: # Se cierra el cursos y la conexion con la db
            cursor.close()
        if conexion:
            conexion.close()


#  Ruta para consultar todos los contactos guardados

@app.route('/ver-contactos', methods=['GET']) # No es una página, es una ruta lógica:
#  No se abre en el navegador como un HTML visual
#  pero sí existe internamente dentro del servidor Flask para recibir datos.

# GET → para pedir datos (por ejemplo, ver información),en este caso pedir los datos y agarrarlos para su consulta de los contactos

# POST → para enviar datos (por ejemplo, enviar un formulario)

# PUT, DELETE → para actualizar o eliminar datos, respectivamente.


# Funcion para ver los contactos de la db


def ver_contactos():
    """Devuelve todos los contactos registrados en formato JSON."""
    conexion = None # Conexion None por ahora
    cursor = None # Al igual que el cursor
    try:
        conexion = conectar_bd() # Se activa la conexion con la db
        if conexion is None: # Si no se logro
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500 # Imprime error

        # Crear cursor que devuelve resultados tipo diccionario
        cursor = conexion.cursor(cursor_factory=RealDictCursor)

        # Obtener todos los registros ordenados por fecha descendente
        cursor.execute("""
            SELECT id, nombre, apellido, direccion, telefono, correo, mensaje, creado
            FROM contactos
            ORDER BY creado DESC;
        """)
        contactos = cursor.fetchall() # Su principal función es recuperar todas las filas restantes del conjunto de resultados de la consulta.

        # Formatear la fecha para que sea más legible
        for c in contactos: # Recorre con una variable c la tabla contactos que se va consultar
            if c['creado']: # Si existe la seccion creado en el diccinario que importamos directamente con la funcion from psycopg2.extras import RealDictCursor
                c['creado'] = c['creado'].strftime('%Y-%m-%d %H:%M:%S') # Lo formatea a .strftime,cambia la variable por la misma pero formateada al metodo time

        # Devolver los contactos en formato JSON
        return jsonify(contactos), 200 # Retorna todos los contactos en el formato JSON

    except Exception as e: # Se crea la variable e si pasa la excepcion y no se logra obtener los contactos; los registros en pocas palabras
        print(f"Error al obtener contactos: {e}") # Se imprime
        return jsonify({'error': 'Error al obtener contactos'}), 500 # Se retorna en formato JSON el error

    finally: # Finalmente se cierra el cursor y la conexion
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


#  Punto de inicio del servidor Flask

if __name__ == '__main__': # Si es correcto el aplicativo flask a '__main__' 
    print("🚀 Iniciando servidor Flask...") # Se imprime iniciando servidor para una mejor estetica
    app.run(debug=True, host='0.0.0.0', port=5000) # Y se aplica app.run para poner a correr la aplicacion
