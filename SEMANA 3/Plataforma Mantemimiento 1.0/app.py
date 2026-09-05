from flask import Flask, render_template, request, redirect, url_for, session
from conexion import ConexionBaseDatos

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura'

# 1. RUTA DE LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    error_mensaje = None
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']

        db_instancia = ConexionBaseDatos.obtener_instancia()
        conexion = db_instancia.obtener_conexion()

        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (correo,))
            usuario = cursor.fetchone()
            cursor.close()

            if usuario and usuario['password'] == contrasena:
                session['usuario_id'] = usuario['id']
                session['nombre'] = usuario['nombre']
                session['rol'] = usuario['rol']
                return redirect(url_for('menu_principal'))
            else:
                error_mensaje = "Correo o contraseña incorrectos."

    return render_template('login.html', error=error_mensaje)

# 2. MENÚ PRINCIPAL
@app.route('/')
def menu_principal():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('inicio.html', nombre=session['nombre'], rol=session['rol'])

# 3. MÓDULO DE MONITOREO DE SENSORES
@app.route('/sensores')
def sensores():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    db_instancia = ConexionBaseDatos.obtener_instancia()
    conexion = db_instancia.obtener_conexion()
    
    lista_sensores = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sensores")
        lista_sensores = cursor.fetchall()
        cursor.close()

    return render_template('sensores.html', sensores=lista_sensores)

# 4. GESTIÓN DE EMPLEADOS Y ROLES (Solo administradores)
@app.route('/usuarios', methods=['GET', 'POST'])
def gestionar_usuarios():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    if session.get('rol') != 'administrador':
        return redirect(url_for('menu_principal'))

    db_instancia = ConexionBaseDatos.obtener_instancia()
    conexion = db_instancia.obtener_conexion()
    
    mensaje_exito = None
    error_mensaje = None

    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        rol = request.form['rol']

        if conexion:
            try:
                cursor = conexion.cursor()
                consulta = "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, %s)"
                cursor.execute(consulta, (nombre, correo, contrasena, rol))
                conexion.commit()
                cursor.close()
                mensaje_exito = "¡Empleado registrado con éxito!"
            except Exception as e:
                error_mensaje = f"Error al registrar (verifique si el correo ya existe): {e}"

    lista_usuarios = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, email, rol, creado_en FROM usuarios")
        lista_usuarios = cursor.fetchall()
        cursor.close()

    return render_template('usuarios.html', lista_usuarios=lista_usuarios, mensaje=mensaje_exito, error=error_mensaje)

# 5. CERRAR SESIÓN
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False)