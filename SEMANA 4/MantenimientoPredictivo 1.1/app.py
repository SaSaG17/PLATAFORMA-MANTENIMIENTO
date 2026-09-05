from flask import Flask, render_template, request, redirect, url_for, session
from conexion import ConexionBaseDatos
from patron_factory import FabricaDeOrdenes

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
                try:
                    consulta = "INSERT INTO usuarios (nombre, email, password, rol, estado) VALUES (%s, %s, %s, %s, 'activo')"
                    cursor.execute(consulta, (nombre, correo, contrasena, rol))
                except:
                    consulta = "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, %s)"
                    cursor.execute(consulta, (nombre, correo, contrasena, rol))
                
                conexion.commit()
                cursor.close()
                mensaje_exito = "¡Empleado registrado con éxito!"
            except Exception as e:
                error_mensaje = f"Error al registrar: {e}"

    lista_usuarios = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, nombre, email, rol, estado, creado_en FROM usuarios")
        except:
            cursor.execute("SELECT id, nombre, email, rol, 'activo' as estado, creado_en FROM usuarios")
        lista_usuarios = cursor.fetchall()
        cursor.close()

    return render_template('usuarios.html', lista_usuarios=lista_usuarios, mensaje=mensaje_exito, error=error_mensaje)

# 5. MÓDULO DE EDICIÓN DE EMPLEADOS (Rol y Estado)
@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if 'usuario_id' not in session or session.get('rol') != 'administrador':
        return redirect(url_for('login'))

    db_instancia = ConexionBaseDatos.obtener_instancia()
    conexion = db_instancia.obtener_conexion()
    
    if request.method == 'POST':
        nuevo_rol = request.form['rol']
        nuevo_estado = request.form['estado']

        if conexion:
            try:
                cursor = conexion.cursor()
                consulta = "UPDATE usuarios SET rol = %s, estado = %s WHERE id = %s"
                cursor.execute(consulta, (nuevo_rol, nuevo_estado, id))
                conexion.commit()
                cursor.close()
                return redirect(url_for('gestionar_usuarios'))
            except Exception as e:
                print(f"Error al actualizar: {e}")

    usuario_a_editar = None
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, nombre, email, rol, estado FROM usuarios WHERE id = %s", (id,))
        except:
            cursor.execute("SELECT id, nombre, email, rol, 'activo' as estado FROM usuarios WHERE id = %s", (id,))
        usuario_a_editar = cursor.fetchone()
        cursor.close()

    return render_template('editar_usuario.html', usuario=usuario_a_editar)

# 6. CERRAR SESIÓN
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



# 7. MÓDULO DE ÓRDENES DE TRABAJO - LISTADO GENERAL
@app.route('/ordenes')
def listar_ordenes():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    db_instancia = ConexionBaseDatos.obtener_instancia()
    conexion = db_instancia.obtener_conexion()
    
    lista_ordenes = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)        
        query = """
            SELECT ot.*, s.nombre_equipo, s.codigo_sensor, u.nombre AS nombre_tecnico 
            FROM ordenes_trabajo ot
            JOIN sensores s ON ot.sensor_id = s.id
            JOIN usuarios u ON ot.asignado_a = u.id
            ORDER BY ot.creado_en DESC
        """
        cursor.execute(query)
        lista_ordenes = cursor.fetchall()
        cursor.close()

    return render_template('ordenes.html', ordenes=lista_ordenes)

# 8. CREAR ORDEN DE TRABAJO (Factory Method)
@app.route('/ordenes/crear', methods=['GET', 'POST'])
def crear_orden():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    db_instancia = ConexionBaseDatos.obtener_instancia()
    conexion = db_instancia.obtener_conexion()
    
    if request.method == 'POST':
        sensor_id = request.form['sensor_id']
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        asignado_a = request.form['asignado_a']
        prioridad = request.form['prioridad']

        # APLICACIÓN DEL FACTORY METHOD:
        # La fábrica decide la logica interna según la prioridad seleccionada
        fabrica = FabricaDeOrdenes.crear_orden(prioridad)
        detalles_orden = fabrica.procesar_orden()
        
        sla_horas = detalles_orden["sla_horas"]
        notificar = detalles_orden["notificar_admin"]

        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                    INSERT INTO ordenes_trabajo 
                    (sensor_id, titulo, descripcion, asignado_a, prioridad, estado, sla_horas, requiere_notificacion_admin) 
                    VALUES (%s, %s, %s, %s, %s, 'pendiente', %s, %s)
                """
                cursor.execute(query, (sensor_id, titulo, descripcion, asignado_a, prioridad, sla_horas, notificar))
                conexion.commit()
                cursor.close()
                return redirect(url_for('listar_ordenes'))
            except Exception as e:
                print(f"Error al crear orden de trabajo: {e}")

    # Cargar sensores y empleados técnicos disponibles para los selectores del formulario
    sensores = []
    empleados = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre_equipo FROM sensores")
        sensores = cursor.fetchall()
        
        # Filtramos o traemos los usuarios para asignar la tarea
        cursor.execute("SELECT id, nombre, rol FROM usuarios WHERE estado = 'activo'")
        empleados = cursor.fetchall()
        cursor.close()

    return render_template('crear_orden.html', sensores=sensores, empleados=empleados)

# 9. EDITAR ESTADO DE LA ORDEN DE TRABAJO
@app.route('/ordenes/editar/<int:id>', methods=['GET', 'POST'])
def editar_orden(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    db_instancia = ConexionBaseDatos.obtener_instancia()
    conexion = db_instancia.obtener_conexion()
    
    if request.method == 'POST':
        nuevo_estado = request.form['estado']
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("UPDATE ordenes_trabajo SET estado = %s WHERE id = %s", (nuevo_estado, id))
                conexion.commit()
                cursor.close()
                return redirect(url_for('listar_ordenes'))
            except Exception as e:
                print(f"Error al actualizar orden: {e}")

    orden = None
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ordenes_trabajo WHERE id = %s", (id,))
        orden = cursor.fetchone()
        cursor.close()

    return render_template('editar_orden.html', orden=orden)

if __name__ == '__main__':
    app.run(debug=True)g