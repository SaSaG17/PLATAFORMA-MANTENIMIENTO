from flask import Flask, render_template, request, redirect, url_for, session
from conexion import ConexionBaseDatos
from patron_factory import FabricaDeOrdenes
from patron_builder import RepuestoBuilder
from patron_abstract_factory import FabricaEntradaInventario, FabricaSalidaInventario
from patron_prototype import REGISTRO_PROTOTIPOS

# Importa tus nuevos módulos corte
from patrones_estructurales.adapter_sensores import SensorIoTExterno, AdaptadorSensorIoT
from patrones_estructurales.bridge_notificaciones import EnvioWhatsApp, NotificacionAlertaCritica
from patrones_estructurales.composite_activos import MaquinaIndividual, LineaProduccionComposite
from patrones_estructurales.decorator_ordenes import OrdenTrabajoBase, DecoradorSelloAuditoria
from flask import jsonify, render_template_string

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
# 8. MÓDULO DE REPUESTOS - LISTADO (CONSULTA)
@app.route('/repuestos')
def listar_repuestos():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    db_instancia = ConexionBaseDatos.obtener_instancia()
    conexion = db_instancia.obtener_conexion()
    
    lista_repuestos = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM repuestos ORDER BY id DESC")
        lista_repuestos = cursor.fetchall()
        cursor.close()

    return render_template('repuestos.html', repuestos=lista_repuestos)

# 9. MÓDULO DE REPUESTOS - CREAR (USANDO BUILDER)
@app.route('/repuestos/crear', methods=['GET', 'POST'])
def crear_repuesto():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        # Aplicación del Patrón Builder para construir el repuesto paso a paso
        builder = RepuestoBuilder()
        nuevo_repuesto = (builder
                          .set_codigo(request.form['codigo_pieza'])
                          .set_nombre(request.form['nombre_repuesto'])
                          .set_stock(request.form['stock_actual'])
                          .set_stock_minimo(request.form['stock_minimo'])
                          .set_costo(request.form['costo_unitario'])
                          .build())
        
        db_instancia = ConexionBaseDatos.obtener_instancia()
        conexion = db_instancia.obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            query = """
                INSERT INTO repuestos (codigo_pieza, nombre_repuesto, stock_actual, stock_minimo, costo_unitario)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                nuevo_repuesto.codigo_pieza,
                nuevo_repuesto.nombre_repuesto,
                nuevo_repuesto.stock_actual,
                nuevo_repuesto.stock_minimo,
                nuevo_repuesto.costo_unitario
            ))
            conexion.commit()
            cursor.close()
        return redirect(url_for('listar_repuestos'))
        
    return render_template('form_repuesto.html', repuesto=None)

# 10. MÓDULO DE REPUESTOS - ACTUALIZAR (USANDO BUILDER)
@app.route('/repuestos/editar/<int:id>', methods=['GET', 'POST'])
def editar_repuesto(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    db_instancia = ConexionBaseDatos.obtener_instancia()
    conexion = db_instancia.obtener_conexion()
    
    if request.method == 'POST':
        # Reutilizamos el Builder para estructurar los datos modificados
        builder = RepuestoBuilder()
        repuesto_modificado = (builder
                               .set_codigo(request.form['codigo_pieza'])
                               .set_nombre(request.form['nombre_repuesto'])
                               .set_stock(request.form['stock_actual'])
                               .set_stock_minimo(request.form['stock_minimo'])
                               .set_costo(request.form['costo_unitario'])
                               .build())
        
        if conexion:
            cursor = conexion.cursor()
            query = """
                UPDATE repuestos 
                SET codigo_pieza=%s, nombre_repuesto=%s, stock_actual=%s, stock_minimo=%s, costo_unitario=%s 
                WHERE id=%s
            """
            cursor.execute(query, (
                repuesto_modificado.codigo_pieza,
                repuesto_modificado.nombre_repuesto,
                repuesto_modificado.stock_actual,
                repuesto_modificado.stock_minimo,
                repuesto_modificado.costo_unitario,
                id
            ))
            conexion.commit()
            cursor.close()
        return redirect(url_for('listar_repuestos'))
        
    repuesto = None
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM repuestos WHERE id = %s", (id,))
        repuesto = cursor.fetchone()
        cursor.close()
        
    return render_template('form_repuesto.html', repuesto=repuesto)


# --- MÓDULO KARDEX (ABSTRACT FACTORY) ---

@app.route('/kardex')
def ver_kardex():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    db_instancia = ConexionBaseDatos.obtener_instancia()
    conexion = db_instancia.obtener_conexion()
    registros_kardex = []
    
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        query = """
            SELECT k.*, r.nombre_repuesto, r.codigo_pieza 
            FROM kardex k
            JOIN repuestos r ON k.repuesto_id = r.id
            ORDER BY k.fecha DESC
        """
        cursor.execute(query)
        registros_kardex = cursor.fetchall()
        cursor.close()
        
    return render_template('kardex.html', kardex=registros_kardex)

@app.route('/kardex/nuevo', methods=['GET', 'POST'])
def registrar_movimiento_kardex():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    db_instancia = ConexionBaseDatos.obtener_instancia()
    conexion = db_instancia.obtener_conexion()
    
    if request.method == 'POST':
        repuesto_id = int(request.form['repuesto_id'])
        tipo = request.form['tipo_movimiento']
        cantidad = int(request.form['cantidad'])
        referencia = request.form['referencia']
        
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT stock_actual FROM repuestos WHERE id = %s", (repuesto_id,))
            repuesto = cursor.fetchone()
            stock_actual = repuesto['stock_actual']
            
            try:
                # Aplicación de Abstract Factory
                fabrica = FabricaEntradaInventario() if tipo == 'ENTRADA' else FabricaSalidaInventario()
                documento = fabrica.crear_documento()
                stock_nuevo = documento.calcular_nuevo_stock(stock_actual, cantidad)
                
                cursor.execute("UPDATE repuestos SET stock_actual = %s WHERE id = %s", (stock_nuevo, repuesto_id))
                query_kardex = """
                    INSERT INTO kardex (repuesto_id, tipo_movimiento, cantidad, stock_anterior, stock_nuevo, referencia)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_kardex, (repuesto_id, documento.obtener_tipo(), cantidad, stock_actual, stock_nuevo, referencia))
                conexion.commit()
            except ValueError as e:
                conexion.rollback()
                print(f"Error: {e}")
            finally:
                cursor.close()
        return redirect(url_for('ver_kardex'))
        
    repuestos = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM repuestos")
        repuestos = cursor.fetchall()
        cursor.close()
        
    return render_template('form_kardex.html', repuestos=repuestos)


# --- MÓDULO REGISTRO DE TRABAJO Y EJECUCIÓN (PROTOTYPE + ABSTRACT FACTORY) ---

@app.route('/ordenes/pendientes')
def listar_ordenes_pendientes():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    db_instancia = ConexionBaseDatos.obtener_instancia()
    conexion = db_instancia.obtener_conexion()
    ordenes = []
    
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ordenes_trabajo WHERE estado != 'Completada' ORDER BY id DESC")
        ordenes = cursor.fetchall()
        cursor.close()
        
    return render_template('ordenes_pendientes.html', ordenes=ordenes)

@app.route('/ordenes/ejecutar/<int:orden_id>', methods=['GET', 'POST'])
def ejecutar_orden(orden_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    db_instancia = ConexionBaseDatos.obtener_instancia()
    conexion = db_instancia.obtener_conexion()
    
    if request.method == 'POST':
        observaciones = request.form['observaciones']
        repuesto_id = int(request.form.get('repuesto_id', 0))
        cantidad_usada = int(request.form.get('cantidad_usada', 0))
        
        if conexion:
            cursor = conexion.cursor()
            
            # 1. Guardar el registro principal del trabajo ejecutado
            cursor.execute("""
                INSERT INTO registro_trabajo (orden_id, tecnico_id, observaciones)
                VALUES (%s, %s, %s)
            """, (orden_id, session['usuario_id'], observaciones))
            
            registro_id = cursor.lastrowid
            
            # 2. Si usó repuestos, guardamos el detalle y aplicamos Abstract Factory para descontar stock
            if repuesto_id > 0 and cantidad_usada > 0:
                cursor.execute("""
                    INSERT INTO detalle_repuestos_usados (registro_id, repuesto_id, cantidad_usada)
                    VALUES (%s, %s, %s)
                """, (registro_id, repuesto_id, cantidad_usada))
                
                cursor.execute("SELECT stock_actual FROM repuestos WHERE id = %s", (repuesto_id,))
                res = cursor.fetchone()
                if res:
                    stock_actual = res[0]
                    
                    # Aplicación de Abstract Factory para la salida de inventario
                    fabrica = FabricaSalidaInventario()
                    doc = fabrica.crear_documento()
                    stock_nuevo = doc.calcular_nuevo_stock(stock_actual, cantidad_usada)
                    
                    cursor.execute("UPDATE repuestos SET stock_actual = %s WHERE id = %s", (stock_nuevo, repuesto_id))
                    cursor.execute("""
                        INSERT INTO kardex (repuesto_id, tipo_movimiento, cantidad, stock_anterior, stock_nuevo, referencia)
                        VALUES (%s, 'SALIDA', %s, %s, %s, %s)
                    """, (repuesto_id, cantidad_usada, stock_actual, stock_nuevo, f"Consumo en OT #{orden_id}"))

            # 3. Marcar orden como completada
            cursor.execute("UPDATE ordenes_trabajo SET estado = 'Completada' WHERE id = %s", (orden_id,))
            conexion.commit()
            cursor.close()
            
        return redirect(url_for('listar_ordenes_pendientes'))

    # Aplicación del PATRÓN PROTOTYPE para clonar la plantilla base de intervención
    tipo_clave = "bomba" if "bomba" in str(orden_id).lower() else "sensor"
    prototipo_base = REGISTRO_PROTOTIPOS.get(tipo_clave, REGISTRO_PROTOTIPOS["bomba"])
    plantilla_clonada = prototipo_base.clonar()

    repuestos = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM repuestos")
        repuestos = cursor.fetchall()
        cursor.close()

    return render_template('ejecutar_orden.html', orden_id=orden_id, plantilla=plantilla_clonada, repuestos=repuestos)





# Ruta de prueba para el Adapter (Simula lectura de sensor externo)
@app.route('/api/probar-sensor')
def probar_sensor():
    sensor_externo = SensorIoTExterno()
    adaptador = AdaptadorSensorIoT(sensor_externo)
    datos_normalizados = adaptador.leer_estado()
    return jsonify({"estado": "exito", "datos_procesados": datos_normalizados})

# Ruta de prueba para el Decorator (Impresión de orden con sello ISO)
@app.route('/ordenes/imprimir/<int:orden_id>')
def imprimir_orden_con_sello(orden_id):
    # Aquí consultarías tu base de datos para la orden real
    orden_base = OrdenTrabajoBase(str(orden_id), "Mantenimiento preventivo de motores")
    
    # Si la orden requiere auditoría especial, la decoramos:
    orden_auditada = DecoradorSelloAuditoria(orden_base)
    resultado_impresion = orden_auditada.obtener_texto_impresion()
    
    return render_template('imprimir_orden.html', contenido=resultado_impresion)



# 2. INICIALIZA LA APLICACIÓN FLASK (¡Obligatorio para que @app.route funcione!)
app = Flask(__name__)

# =========================================================
# RUTAS DE PRUEBA (Aquí pegas las rutas que ya tienes)
# =========================================================

@app.route('/api/probar-sensor')
def probar_sensor():
    sensor_externo = SensorIoTExterno()
    adaptador = AdaptadorSensorIoT(sensor_externo)
    datos_normalizados = adaptador.leer_estado()
    return jsonify({"estado": "exito", "datos_procesados": datos_normalizados})

@app.route('/ordenes/imprimir/<int:orden_id>')
def imprimir_orden_con_sello(orden_id):
    orden_base = OrdenTrabajoBase(str(orden_id), "Mantenimiento preventivo de motores")
    orden_auditada = DecoradorSelloAuditoria(orden_base)
    resultado_impresion = orden_auditada.obtener_texto_impresion()
    return render_template_string('<pre>{{ contenido }}</pre>', contenido=resultado_impresion)

@app.route('/probar-adapter', methods=['GET'])
def probar_adapter():
    sensor_externo = SensorIoTExterno()
    adaptador = AdaptadorSensorIoT(sensor_externo)
    datos_normalizados = adaptador.leer_estado()
    return jsonify({
        "patron": "Adapter",
        "mensaje": "Datos del sensor externo traducidos exitosamente al formato del CMMS",
        "resultado": datos_normalizados
    })

@app.route('/probar-bridge', methods=['GET'])
def probar_bridge():
    canal_whatsapp = EnvioWhatsApp()
    alerta = NotificacionAlertaCritica(canal_whatsapp)
    alerta.notificar("+573001234567", "Falla detectada en la Bomba Principal")
    return jsonify({
        "patron": "Bridge",
        "mensaje": "Notificación enviada por WhatsApp correctamente (revisa la consola de tu servidor Flask)."
    })

@app.route('/probar-composite', methods=['GET'])
def probar_composite():
    maquina1 = MaquinaIndividual("Torno CNC 1", 150.0)
    maquina2 = MaquinaIndividual("Fresadora 2", 200.0)
    linea = LineaProduccionComposite("Línea de Ensamble A")
    linea.agregar(maquina1)
    linea.agregar(maquina2)
    costo_total = linea.calcular_costo_mantenimiento()
    return jsonify({
        "patron": "Composite",
        "activo": linea.nombre,
        "costo_total_mantenimiento": costo_total
    })

@app.route('/probar-decorator/<int:orden_id>', methods=['GET'])
def probar_decorator(orden_id):
    orden_base = OrdenTrabajoBase(str(orden_id), "Mantenimiento correctivo de motor principal")
    orden_auditada = DecoradorSelloAuditoria(orden_base)
    texto_final = orden_auditada.obtener_texto_impresion()
    
    template_html = """
    <html>
        <head><title>Impresión de Orden</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h2>Vista de Impresión de Orden de Trabajo</h2>
            <pre style="background: #f4f4f4; padding: 15px; border: 1px solid #ddd;">{{ contenido }}</pre>
            <p><em>Esta orden cuenta con características dinámicas añadidas mediante Decorator.</em></p>
        </body>
    </html>
    """
    return render_template_string(template_html, contenido=texto_final)



print("RUTAS REGISTRADAS:")
for ruta in app.url_map.iter_rules():
    print(ruta)


if __name__ == '__main__':
    app.run(debug=False)
