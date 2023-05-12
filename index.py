from flask import Flask, make_response, render_template, request, redirect, url_for, session, current_app
from flask_mysqldb import MySQL
import MySQLdb.cursors
import time
import re
import pdfkit


app = Flask(__name__,template_folder='templates')

#Conexion base de datos
app.secret_key = ' key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'clinica'

mysql = MySQL(app)

#ruta por defecto
@app.route('/')
def index_():
    return render_template('login.html')

#ruta de busqueda por nombre de usuario
@app.route('/busqueda/', methods = ['GET','POST'])
def buscador():
    search = ''

    if request.method == "POST":
        search = request.form['buscar']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Usuarios WHERE userName = %s ORDER BY id DESC', (search, ))
    
        resultado = cursor.fetchone()
        return render_template('/busqueda.html', miData = resultado, buscador = search)
    else:
        return render_template('/index.html')

#ruta y metodo del login
@app.route('/login.html/', methods = ['GET', 'POST'])
def login():

    msg = ''
    template = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        current_app.logger.info(username)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Usuarios WHERE userName = %s AND password = %s', (username, password,))
    
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['userName']

            return redirect(url_for('home'))
        
        else:
            msg = 'Usuario o contraseña incorrectos!'
            template = 'login.html'
            #return render_template('login.html', msg = msg)

    return render_template('login.html', msg = msg)

#@app.route('/index.html')
#def index():
    #return render_template('index.html')

#ruta y medoto de registro de   usuarios
@app.route('/register.html/', methods=['GET', 'POST'])
def register():
    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'nombre' in request.form and 'apellidoPaterno' in request.form and 'apellidoMaterno' in request.form:
       
        nombre = request.form['nombre']
        apellidoPaterno = request.form['apellidoPaterno']
        apellidoMaterno = request.form['apellidoMaterno']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Usuarios WHERE userName = %s', (username,))
        account = cursor.fetchone()
        

        if account :
            msg = "La cuenta ya existe!!"
            
        
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Correo electronico invalido'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'El usuario debe de contener números y letras'
        elif not username or not password or not email:
            msg = 'Por favor llena los campos vacios'
        else:
            cursor.execute('INSERT INTO Usuarios VALUES (NULL, %s, %s, %s, %s, %s, %s)', (nombre, apellidoPaterno,apellidoMaterno, email, password, username,))
            mysql.connection.commit()
            msg = 'Te acabas de registrar correctamente!'
            #return render_template('register.html', msg=msg)
        
    elif not request.method == 'POST':
        msg = 'Por favor llene el formulario!'
        
    return render_template('register.html',msg=msg)

#ruta con inicio de sesion para agregar doctores
@app.route('/clinicalogin/doctores/agregar_doctor')
def form_insertar():
    return render_template('agregar_doctor.html')

#ruta y metodo para insertar datos de los medicos a la base de datos
@app.route('/clinicalogin/doctores/agregar_doctor', methods=['GET', 'POST'])
def insert_doctores():
    msg = ''

    #if request.method == 'POST' and 'name' in request.form and 'apellPaterno' in request.form and 'apellMaterno' in request.form and 'especial' in request.form and 'correo' in request.form and 'telefono' in request.form:

    nombre = request.form['nombre']
    apellidoPaterno = request.form['apellPaterno']
    apellidoMaterno = request.form['apellMaterno']
    especial = request.form['especial']
    correo = request.form['correo']
    telefono = request.form['telefono']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM doctores WHERE nombre = %s AND apellidoPaterno = %s AND apellidoMaterno = %s', (nombre, apellidoPaterno, apellidoMaterno,))
    user = cursor.fetchone()

    if user:
        msg = "Ya se registro a este doctor!!"
    else:
        cursor.execute('INSERT INTO doctores VALUES (NULL, %s, %s, %s, %s, %s, %s)', (nombre, apellidoPaterno,apellidoMaterno, especial, correo, telefono,))
        mysql.connection.commit()
        
        msg = 'Doctor agregado correctamente!!'
        #return redirect('/clinicalogin/doctores.html')

    #elif not request.method == 'POST':
        #msg = 'Por favor llene el formulario!'

    return render_template('agregar_doctor.html', msg=msg)

#ruta y metodo para mostrar los datos de la tabla de doctores
@app.route('/clinicalogin/doctores/lista_doctores', methods=['GET'])
def obtener_doctores():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM doctores")
    doctores = cursor.fetchall()

    return render_template('/doctores.html', data = doctores)

#ruta y metodo para eliminar datos de la tabla de doctores 
@app.route('/clinicalogin/doctores/eliminar_doctor', methods=['POST'])
def eliminar_doctores():

    id = request.form['id']
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM doctores WHERE id = %s", (id,))
    mysql.connection.commit()

    return redirect('/clinicalogin/doctores/lista_doctores')

#ruta y metodo para obtener lo datos a actualizar
@app.route('/clinicalogin/doctores/form_update', methods=['POST'])
def editar_datos():
    id = request.form['id']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, nombre, apellidoPaterno, apellidoMaterno, especialidad, correo, telefono FROM doctores WHERE id = %s", (id,))
    datos = cursor.fetchone()

    return render_template("update_doctor.html", datos = datos)

#metodo para actualizar los datos que deseemos
@app.route('/clinicalogin/doctores/actualizar_doctores', methods=['POST'])
def actualizar_doctores():

    id = request.form['id']
    nombre = request.form['nombre']
    apellidoPaterno = request.form['apellPaterno']
    apellidoMaterno = request.form['apellMaterno']
    especialidad = request.form['especial']
    correo = request.form['correo']
    telefono = request.form['telefono']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE doctores SET nombre = %s, apellidoPaterno = %s, apellidoMaterno = %s, especialidad = %s, correo = %s, telefono = %s WHERE id = %s",
                   (nombre, apellidoPaterno, apellidoMaterno, especialidad, correo, telefono, id))
    mysql.connection.commit()
    return redirect('/clinicalogin/doctores/lista_doctores')

#ruta para el formulario de pacientes
@app.route('/clinicalogin/pacientes/agregar_pacientes')
def form_insertarPacientes():
    return render_template('agregar_pacientes.html')

#ruta y metodo para agregar pacientes a la tabla de la bd
@app.route('/clinicalogin/pacientes/agregar_pacientes', methods=['GET', 'POST'])
def insert_pacientes():
    msg = ''

    #if request.method == 'POST' and 'name' in request.form and 'apellPaterno' in request.form and 'apellMaterno' in request.form and 'especial' in request.form and 'correo' in request.form and 'telefono' in request.form:

    nombre = request.form['nombre']
    apellidoPaterno = request.form['apellPaterno']
    apellidoMaterno = request.form['apellMaterno']
    edad = request.form['edad']
    direccion = request.form['direccion']
    fecha = request.form['fecha']
    telefono = request.form['telefono']
    correo = request.form['correo']

    current_app.logger.info(nombre)    

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM pacientes WHERE nombre = %s AND apellidoPaterno = %s AND apellidoMaterno = %s', (nombre, apellidoPaterno, apellidoMaterno,))
    user = cursor.fetchone()

    if user:
        msg = "Ya se registro a este paciente!!"
    else:
        cursor.execute('INSERT INTO pacientes VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)', (nombre, apellidoPaterno,apellidoMaterno, edad, direccion, fecha, telefono, correo,))
        mysql.connection.commit()
        
        msg = 'Paciente agregado correctamente!!'
        #return redirect('/clinicalogin/doctores.html')

    #elif not request.method == 'POST':
        #msg = 'Por favor llene el formulario!'

    return render_template('agregar_pacientes.html', msg=msg)

#ruta y metodo para obtener los datos de la tabla pacientes
@app.route('/clinicalogin/pacientes/lista_pacientes', methods=['GET'])
def obtener_pacientes():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM pacientes")
    paciente = cursor.fetchall()

    return render_template('/pacientes.html', data = paciente)

#ruta y metodo para eliminar datos de la tabla de pacientes 
@app.route('/clinicalogin/pacientes/eliminar_paciente', methods=['POST'])
def eliminar_pacientes():

    id = request.form['id']
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM pacientes WHERE id = %s", (id,))
    mysql.connection.commit()

    return redirect('/clinicalogin/pacientes/lista_pacientes')

#ruta y metodo para obtener lo datos a actualizar
@app.route('/clinicalogin/pacientes/form_updatePacientes', methods=['POST'])
def editar_datosPaciente():
    id = request.form['id']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, nombre, apellidoPaterno, apellidoMaterno, edad, direccion, fechaNacimiento, telefono, correo FROM pacientes WHERE id = %s", (id,))
    datos = cursor.fetchone()

    return render_template("update_paciente.html", datos = datos)

#metodo para actualizar los datos que deseemos
@app.route('/clinicalogin/pacientes/actualizar_pacientes', methods=['POST'])
def actualizar_pacientes():

    id = request.form['id']
    nombre = request.form['nombre']
    apellidoPaterno = request.form['apellPaterno']
    apellidoMaterno = request.form['apellMaterno']
    edad = request.form['edad']
    direccion = request.form['direccion']
    fecha = request.form['fecha']
    telefono = request.form['telefono']
    correo = request.form['correo']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE pacientes SET nombre = %s, apellidoPaterno = %s, apellidoMaterno = %s, edad = %s, direccion = %s, fechaNacimiento = %s, telefono = %s, correo = %s WHERE id = %s",
                   (nombre, apellidoPaterno, apellidoMaterno, edad, direccion, fecha, telefono, correo, id))
    mysql.connection.commit()
    return redirect('/clinicalogin/pacientes/lista_pacientes')

#metodo para cerrar sesion
@app.route('/clinicalogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

#ruta del inicio de la pagina de la clinica
@app.route('/clinicalogin/home')
def home():
    if 'loggedin' in session:
        return render_template('index.html', username=session['username'])
    
    return redirect(url_for('login'))

#ruta para obtener los datos de los pacientes y poder realizar las citas
@app.route('/clinicalogin/citas/lista_citas', methods=['GET'])                        
def obtener_pacientesCita():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM pacientes")
    cita = cursor.fetchall()

    return render_template('/citas.html', data = cita)

#ruta y metodo para obtener lo datos de pacientes para realizar la cita
@app.route('/clinicalogin/citas/form_citas', methods=['GET','POST'])
def datos_cita():
    id = request.form['id']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT CONCAT(nombre, ' ',apellidoPaterno, ' ',apellidoMaterno)nombrePaciente, telefono, correo FROM pacientes WHERE id = %s", (id,))
    cita = cursor.fetchone()

    return render_template("agregar_cita.html", cita=cita)


#ruta y metodo para agregar citas a la tabla de la bd
@app.route('/clinicalogin/citas/hacer_cita', methods=['GET', 'POST'])
def insert_cita():
    msg = ''
    #if request.method == 'POST' and 'name' in request.form and 'apellPaterno' in request.form and 'apellMaterno' in request.form and 'especial' in request.form and 'correo' in request.form and 'telefono' in request.form:
    
    nombre = request.form['nombre']
    telefono = request.form['telefono']
    correo = request.form['correo']
    sintoma = request.form['sintoma']
    fecha = request.form['fecha']
    departamento = request.form['dep']
    genero = request.form['gen']
    hora = request.form['hora']    

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM citas WHERE hora = %s AND fecha = %s', (hora, fecha,))
    user = cursor.fetchone()

    if user:
        msg = "Ya hay una cita a esa hora en ese departamento!!"
    else:
        cursor.execute('INSERT INTO citas VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)', (nombre, telefono, correo, sintoma, fecha, departamento, genero, hora,))
        mysql.connection.commit()
        
        msg = 'Cita creada correctamente!!'
        #return redirect('/clinicalogin/doctores.html')

    #elif not request.method == 'POST':
        #msg = 'Por favor llene el formulario!'

    return redirect('/clinicalogin/citas/lista_citas')

@app.route('/clinicalogin/citas/enviar_cita', methods=['GET','POST'])
def form_enviar():
    return render_template('/enviar_cita.html')

#con esta ruta se puede observar como queda la hoja de cita
@app.route('/clinicalogin/citas/generar_pdf', methods=['GET','POST'])
def generar():

    cita=[]
    correo = request.form['email']


    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM citas WHERE email = %s', (correo,))
    cita = cursor.fetchone()

    current_app.logger.info(correo)
    return render_template('/hoja_cita.html', cita=cita)


@app.route('/clinicalogin/citas/PDF_Cita', methods=['POST'])
def generar_Pdf():
 
    id = request.form['id']
    nombre = request.form['nombre']
    telefono = request.form['telefono']
    correo = request.form['correo']
    sintomas = request.form['sintomas']
    fecha = request.form['fecha']
    departamento = request.form['departamento']
    genero = request.form['genero']
    hora = request.form['hora']   


    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM citas WHERE email = %s', (correo,))
    cita = cursor.fetchone()
    

    options = {
        "orientation": "landscape",
        "page-size": "A4",
        "margin-top": "1.0cm",
        "margin-right": "1.0cm",
        "margin-bottom": "1.0cm",
        "margin-left": "1.0cm",
        "encoding": "UTF-8",
        "enable-local-file-access": ""
    }

    salida = render_template('/hoja_cita.html', cita=cita)

    citas = str(salida);
    pdf = pdfkit.from_string(salida, options = options, verbose=True)
    res = make_response(pdf)
    res.headers["Content-Type"] = "application/pdf"
    res.headers["Content-Disposition"] = "inline; filename=HojaCita.pdf"

    return res

@app.route('/clinicalogin/pacientes')
def paciente():
    return render_template('pacientes.html')

@app.route('/clinicalogin/contact.html')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)