# ENUNCIADO OFICIAL DEL SISTEMA DE INVENTARIO DE REPUESTOS PARA MOTOS

from flask import Flask, request, render_template, redirect, url_for, flash, send_file, session, jsonify
import json
import os
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

app = Flask(_name_)
app.secret_key = "dev_secret_key_change_in_production"


# ---------------------------------------------------------------------------------
# CONFIGURACIÓN Y CONEXIÓN A MYSQL
# ---------------------------------------------------------------------------------
def get_db_connection():
    """Crea y retorna una conexión a MySQL"""
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='',  # XAMPP no tiene contraseña por defecto
        database='inventario_repuestos',
        cursorclass=pymysql.cursors.DictCursor
    )


def ejecutar_query(query, params=None, commit=False, fetch_one=False, fetch_all=False):
    """
    Función auxiliar para ejecutar consultas SQL de forma segura.
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        
        if commit:
            connection.commit()
            last_id = cursor.lastrowid
            return last_id
        
        if fetch_one:
            result = cursor.fetchone()
            return result
        
        if fetch_all:
            results = cursor.fetchall()
            return results
        
        return None
        
    except Exception as e:
        print(f" Error en la base de datos: {e}")
        if commit and connection:
            connection.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ---------------------------------------------------------------------------------
# CONSTANTES
# ---------------------------------------------------------------------------------
STOCK_MINIMO = 5

# Roles disponibles
ROLES = {
    'admin': 'Administrador',
    'vendedor': 'Vendedor',
    'auditor': 'Auditor'
}


# ---------------------------------------------------------------------------------
# FUNCIONES DE CARGA Y GUARDADO (MYSQL)
# ---------------------------------------------------------------------------------
def cargar_productos():
    """Carga todos los productos desde MySQL"""
    query = """
        SELECT id, nombre, categoria, marca, stock, precio_unitario, 
               descripcion, valor_total, fecha_creacion, fecha_actualizacion
        FROM productos
        ORDER BY id
    """
    productos = ejecutar_query(query, fetch_all=True)
    return productos if productos else []


def obtener_producto_por_id(producto_id):
    """Obtiene un producto específico por su ID"""
    query = """
        SELECT id, nombre, categoria, marca, stock, precio_unitario, 
               descripcion, valor_total, fecha_creacion, fecha_actualizacion
        FROM productos
        WHERE id = %s
    """
    return ejecutar_query(query, (producto_id,), fetch_one=True)


def actualizar_producto(producto_id, nombre, categoria, marca, stock, precio_unitario, descripcion):
    """Actualiza un producto existente en MySQL"""
    valor_total = round(stock * precio_unitario, 3)
    
    query = """
        UPDATE productos 
        SET nombre = %s, categoria = %s, marca = %s, stock = %s, 
            precio_unitario = %s, descripcion = %s, valor_total = %s,
            fecha_actualizacion = NOW()
        WHERE id = %s
    """
    params = (nombre, categoria, marca, stock, precio_unitario, descripcion, valor_total, producto_id)
    return ejecutar_query(query, params, commit=True)


def eliminar_producto_db(producto_id):
    """Elimina un producto de MySQL"""
    query = "DELETE FROM productos WHERE id = %s"
    return ejecutar_query(query, (producto_id,), commit=True)


def actualizar_stock_producto(producto_id, nuevo_stock):
    """Actualiza solo el stock de un producto"""
    producto = obtener_producto_por_id(producto_id)
    if not producto:
        return False
    
    valor_total = round(nuevo_stock * producto['precio_unitario'], 3)
    
    query = """
        UPDATE productos 
        SET stock = %s, valor_total = %s, fecha_actualizacion = NOW()
        WHERE id = %s
    """
    return ejecutar_query(query, (nuevo_stock, valor_total, producto_id), commit=True)


def cargar_ventas():
    """Carga todas las ventas desde MySQL"""
    query = """
        SELECT id, fecha, hora, producto_id, producto_nombre, categoria,
               cantidad, precio_unitario, total, usuario_id, usuario_nombre,
               fecha_registro
        FROM ventas
        ORDER BY fecha DESC, hora DESC
    """
    ventas = ejecutar_query(query, fetch_all=True)
    return ventas if ventas else []


def guardar_venta(venta):
    """Guarda una nueva venta en MySQL"""
    query = """
        INSERT INTO ventas (fecha, hora, producto_id, producto_nombre, categoria,
                           cantidad, precio_unitario, total, usuario_id, usuario_nombre)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        venta['fecha'],
        venta['hora'],
        venta['producto_id'],
        venta['producto_nombre'],
        venta['categoria'],
        venta['cantidad'],
        venta['precio_unitario'],
        venta['total'],
        venta.get('usuario_id'),
        venta.get('usuario_nombre')
    )
    return ejecutar_query(query, params, commit=True)


#  NUEVA FUNCIÓN: ELIMINAR VENTA
def eliminar_venta_db(venta_id):
    """Elimina una venta de MySQL"""
    query = "DELETE FROM ventas WHERE id = %s"
    return ejecutar_query(query, (venta_id,), commit=True)


# ---------------------------------------------------------------------------------
# FUNCIONES DE USUARIOS Y AUTENTICACIÓN
# ---------------------------------------------------------------------------------
def cargar_usuarios():
    """Carga todos los usuarios desde MySQL"""
    query = """
        SELECT id, username, password, nombre_completo, rol, activo, 
               fecha_creacion, fecha_actualizacion
        FROM usuarios
        ORDER BY id
    """
    usuarios = ejecutar_query(query, fetch_all=True)
    
    # Si no hay usuarios, crear admin por defecto
    if not usuarios:
        query_insert = """
            INSERT INTO usuarios (username, password, nombre_completo, rol, activo)
            VALUES (%s, %s, %s, %s, %s)
        """
        ejecutar_query(
            query_insert,
            ('admin', generate_password_hash('admin123'), 'Administrador', 'admin', True),
            commit=True
        )
        return cargar_usuarios()
    
    return usuarios


def crear_usuario(username, password, nombre_completo, rol):
    """Crea un nuevo usuario en MySQL"""
    query = """
        INSERT INTO usuarios (username, password, nombre_completo, rol, activo)
        VALUES (%s, %s, %s, %s, %s)
    """
    password_hash = generate_password_hash(password)
    params = (username, password_hash, nombre_completo, rol, True)
    return ejecutar_query(query, params, commit=True)


def actualizar_usuario_estado(usuario_id, activo):
    """Activa o desactiva un usuario"""
    query = """
        UPDATE usuarios 
        SET activo = %s, fecha_actualizacion = NOW()
        WHERE id = %s
    """
    return ejecutar_query(query, (activo, usuario_id), commit=True)


def eliminar_usuario_db(usuario_id):
    """Elimina un usuario de MySQL"""
    query = "DELETE FROM usuarios WHERE id = %s"
    return ejecutar_query(query, (usuario_id,), commit=True)


def actualizar_password_usuario(usuario_id, nueva_password):
    """Actualiza la contraseña de un usuario"""
    query = """
        UPDATE usuarios 
        SET password = %s, fecha_actualizacion = NOW()
        WHERE id = %s
    """
    password_hash = generate_password_hash(nueva_password)
    return ejecutar_query(query, (password_hash, usuario_id), commit=True)


def obtener_usuario_por_id(usuario_id):
    """Obtiene un usuario específico por su ID"""
    query = """
        SELECT id, username, password, nombre_completo, rol, activo, 
               fecha_creacion, fecha_actualizacion
        FROM usuarios
        WHERE id = %s
    """
    return ejecutar_query(query, (usuario_id,), fetch_one=True)

def registrar_log(accion, detalle=""):
    """Registra una acción en los logs de MySQL"""
    query = """
        INSERT INTO logs (fecha, hora, usuario, accion, detalle)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (
        datetime.now().strftime('%Y-%m-%d'),
        datetime.now().strftime('%H:%M:%S'),
        session.get('username', 'Sistema'),
        accion,
        detalle
    )
    ejecutar_query(query, params, commit=True)


def cargar_logs():
    """Carga todos los logs desde MySQL"""
    query = """
    SELECT id, fecha, hora, usuario, accion, detalle, fecha_registro
    FROM logs
    ORDER BY fecha_registro ASC
    """
    logs = ejecutar_query(query, fetch_all=True)
    return logs if logs else []


# ---------------------------------------------------------------------------------
# DECORADORES DE AUTENTICACIÓN
# ---------------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debes iniciar sesión.', 'warning')
                return redirect(url_for('login'))
            
            if session.get('rol') not in roles:
                flash('No tienes permisos para acceder a esta página.', 'danger')
                return redirect(url_for('inicio'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ---------------------------------------------------------------------------------
# RUTAS DE AUTENTICACIÓN
# ---------------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    if 'user_id' in session:
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Por favor completa todos los campos.', 'error')
            return redirect(url_for('login'))
        
        usuarios = cargar_usuarios()
        usuario = next((u for u in usuarios if u['username'] == username), None)
        
        if not usuario:
            flash('Usuario no encontrado.', 'error')
            return redirect(url_for('login'))
        
        if not usuario.get('activo', True):
            flash('Tu cuenta está desactivada. Contacta al administrador.', 'error')
            return redirect(url_for('login'))
        
        if not check_password_hash(usuario['password'], password):
            flash('Contraseña incorrecta.', 'error')
            return redirect(url_for('login'))
        
        # Login exitoso
        session['user_id'] = usuario['id']
        session['username'] = usuario['username']
        session['nombre_completo'] = usuario['nombre_completo']
        session['rol'] = usuario['rol']
        
        registrar_log('Inicio de sesión', f"Usuario: {usuario['username']}")
        
        flash(f'¡Bienvenido {usuario["nombre_completo"]}!', 'success')
        return redirect(url_for('inicio'))
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Cerrar sesión"""
    username = session.get('username', 'Usuario')
    registrar_log('Cierre de sesión', f"Usuario: {username}")
    
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))


# ---------------------------------------------------------------------------------
# RUTAS DE GESTIÓN DE USUARIOS
# ---------------------------------------------------------------------------------
@app.route('/usuarios')
@login_required
@role_required('admin')
def lista_usuarios():
    """Lista de usuarios (solo admin)"""
    usuarios = cargar_usuarios()
    return render_template('usuarios/lista_usuarios.html', usuarios=usuarios, roles=ROLES)


@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def nuevo_usuario():
    """Crear nuevo usuario (solo admin)"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        nombre_completo = request.form.get('nombre_completo', '').strip()
        rol = request.form.get('rol', '')
        
        if not username or not password or not nombre_completo or not rol:
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(url_for('nuevo_usuario'))
        
        if rol not in ROLES:
            flash('Rol inválido.', 'error')
            return redirect(url_for('nuevo_usuario'))
        
        usuarios = cargar_usuarios()
        
        # Verificar si el username ya existe
        if any(u['username'] == username for u in usuarios):
            flash(f'El usuario "{username}" ya existe.', 'error')
            return redirect(url_for('nuevo_usuario'))
        
        # Crear nuevo usuario
        usuario_id = crear_usuario(username, password, nombre_completo, rol)
        
        if usuario_id:
            registrar_log('Usuario creado', f"Nuevo usuario: {username} ({ROLES[rol]})")
            flash(f'Usuario "{username}" creado exitosamente.', 'success')
            return redirect(url_for('lista_usuarios'))
        else:
            flash('Error al crear el usuario.', 'error')
            return redirect(url_for('nuevo_usuario'))
    
    return render_template('usuarios/nuevo_usuario.html', roles=ROLES)


@app.route('/usuarios/<int:id>/toggle')
@login_required
@role_required('admin')
def toggle_usuario(id):
    """Activar/desactivar usuario"""
    usuario = obtener_usuario_por_id(id)
    
    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('lista_usuarios'))
    
    # No permitir desactivar al propio usuario
    if usuario['id'] == session.get('user_id'):
        flash('No puedes desactivar tu propia cuenta.', 'error')
        return redirect(url_for('lista_usuarios'))
    
    nuevo_estado = not usuario.get('activo', True)
    actualizar_usuario_estado(id, nuevo_estado)
    
    estado = "activado" if nuevo_estado else "desactivado"
    registrar_log(f'Usuario {estado}', f"Usuario: {usuario['username']}")
    
    flash(f'Usuario "{usuario["username"]}" {estado}.', 'success')
    return redirect(url_for('lista_usuarios'))


@app.route('/usuarios/<int:id>/eliminar')
@login_required
@role_required('admin')
def eliminar_usuario(id):
    """Eliminar usuario (solo admin)"""
    usuario = obtener_usuario_por_id(id)
    
    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('lista_usuarios'))
    
    # No permitir eliminar al propio usuario
    if usuario['id'] == session.get('user_id'):
        flash('No puedes eliminar tu propia cuenta.', 'error')
        return redirect(url_for('lista_usuarios'))
    
    # No permitir eliminar al admin principal
    if usuario['username'] == 'admin':
        flash('No se puede eliminar el usuario administrador principal.', 'error')
        return redirect(url_for('lista_usuarios'))
    
    eliminar_usuario_db(id)
    
    registrar_log('Usuario eliminado', f"Usuario: {usuario['username']}")
    
    flash(f'Usuario "{usuario["username"]}" eliminado.', 'success')
    return redirect(url_for('lista_usuarios'))


# ---------------------------------------------------------------------------------
# GESTIÓN DE CONTRASEÑAS
# ---------------------------------------------------------------------------------
@app.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    """Permite al usuario cambiar su propia contraseña"""
    if request.method == 'POST':
        password_actual = request.form.get('password_actual', '')
        password_nueva = request.form.get('password_nueva', '')
        password_confirmar = request.form.get('password_confirmar', '')
        
        if not password_actual or not password_nueva or not password_confirmar:
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(url_for('cambiar_password'))
        
        if password_nueva != password_confirmar:
            flash('Las contraseñas nuevas no coinciden.', 'error')
            return redirect(url_for('cambiar_password'))
        
        if len(password_nueva) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return redirect(url_for('cambiar_password'))
        
        usuario = obtener_usuario_por_id(session['user_id'])
        
        if not usuario:
            flash('Usuario no encontrado.', 'error')
            return redirect(url_for('cambiar_password'))
        
        # Verificar contraseña actual
        if not check_password_hash(usuario['password'], password_actual):
            flash('La contraseña actual es incorrecta.', 'error')
            return redirect(url_for('cambiar_password'))
        
        # Cambiar contraseña
        actualizar_password_usuario(usuario['id'], password_nueva)
        
        registrar_log('Contraseña cambiada', f"Usuario: {usuario['username']}")
        
        flash('¡Contraseña actualizada exitosamente!', 'success')
        return redirect(url_for('inicio'))
    
    return render_template('cambiar_password.html')


@app.route('/usuarios/<int:id>/resetear-password', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def resetear_password_usuario(id):
    """Admin puede resetear la contraseña de un usuario"""
    usuario = obtener_usuario_por_id(id)
    
    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('lista_usuarios'))
    
    if request.method == 'POST':
        nueva_password = request.form.get('nueva_password', '')
        confirmar_password = request.form.get('confirmar_password', '')
        
        if not nueva_password or not confirmar_password:
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(url_for('resetear_password_usuario', id=id))
        
        if nueva_password != confirmar_password:
            flash('Las contraseñas no coinciden.', 'error')
            return redirect(url_for('resetear_password_usuario', id=id))
        
        if len(nueva_password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return redirect(url_for('resetear_password_usuario', id=id))
        
        actualizar_password_usuario(id, nueva_password)
        
        registrar_log('Contraseña reseteada por admin', f"Admin reseteó contraseña de: {usuario['username']}")
        
        flash(f'Contraseña de "{usuario["username"]}" actualizada exitosamente.', 'success')
        return redirect(url_for('lista_usuarios'))
    
    return render_template('usuarios/resetear_password.html', usuario=usuario)

@app.route('/logs')
@login_required
@role_required('admin', 'auditor')
def ver_logs():
    """Ver logs del sistema"""
    logs = cargar_logs()
    return render_template('logs.html', logs=logs)


# --------------------------------------------------------------
#  ELIMINAR UN SOLO LOG
# --------------------------------------------------------------
@app.route('/logs/eliminar/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def eliminar_log(id):
    """Elimina un log individual"""
    query = "DELETE FROM logs WHERE id = %s"
    ejecutar_query(query, (id,), commit=True)

    registrar_log("Log eliminado", f"ID del log eliminado: {id}")
    flash("Registro eliminado correctamente.", "success")
    return redirect(url_for('ver_logs'))


# --------------------------------------------------------------
#  ELIMINAR TODOS LOS LOGS (LIMPIAR HISTORIAL)
# --------------------------------------------------------------
@app.route('/logs/limpiar', methods=['POST'])
@login_required
@role_required('admin')
def limpiar_logs():
    """Elimina todos los registros del historial y reinicia el AUTO_INCREMENT"""
    # 1. Borrar todos los logs
    ejecutar_query("DELETE FROM logs", commit=True)
    # 2. Reiniciar el contador AUTO_INCREMENT a 1
    ejecutar_query("ALTER TABLE logs AUTO_INCREMENT = 1", commit=True)
    registrar_log("Historial limpiado", "Se eliminaron todos los logs y se reinició el AUTO_INCREMENT.")
    flash("Historial limpiado correctamente. IDs reiniciados desde 1.", "success")
    return redirect(url_for('ver_logs'))


# ---------------------------------------------------------------------------------
# RUTAS PRINCIPALES DE PRODUCTOS
# ---------------------------------------------------------------------------------
@app.route('/')
@login_required
def inicio():
    """Página de inicio - redirige a lista de productos"""
    return redirect(url_for('lista_productos'))


@app.route('/productos', methods=['GET'])
@login_required
def lista_productos():
    """Lista todos los productos con filtros y búsqueda"""
    productos = cargar_productos()

    # PARÁMETROS DEL BUSCADOR
    query = request.args.get("q", "").lower().strip()
    categoria = request.args.get("categoria", "").strip()
    ordenar = request.args.get("ordenar", "")
    solo_bajo_stock = request.args.get("solo_bajo_stock", "0") == "1"

    # FILTRO POR NOMBRE
    if query:
        productos = [p for p in productos if query in p.get('nombre', '').lower()]

    # FILTRO POR CATEGORÍA
    if categoria:
        productos = [p for p in productos if p.get('categoria') == categoria]

    # FILTRO DE BAJO STOCK
    if solo_bajo_stock:
        productos = [p for p in productos if p.get('stock', 0) < STOCK_MINIMO]

    # ORDENAMIENTO
    if ordenar == "precio_asc":
        productos = sorted(productos, key=lambda x: x.get("precio_unitario", 0))
    elif ordenar == "precio_desc":
        productos = sorted(productos, key=lambda x: x.get("precio_unitario", 0), reverse=True)
    elif ordenar == "stock_asc":
        productos = sorted(productos, key=lambda x: x.get("stock", 0))
    elif ordenar == "stock_desc":
        productos = sorted(productos, key=lambda x: x.get("stock", 0), reverse=True)

    # CONTAR PRODUCTOS DE BAJO STOCK
    todos_productos = cargar_productos()
    bajo_stock_total = sum(1 for p in todos_productos if p.get('stock', 0) < STOCK_MINIMO)

    # LISTA DE CATEGORÍAS PARA EL SELECT
    categorias = sorted({p.get("categoria", "") for p in todos_productos})

    return render_template(
        "productos.html",
        productos=productos,
        categorias=categorias,
        bajo_stock_total=bajo_stock_total,
        solo_bajo_stock=solo_bajo_stock,
        STOCK_MINIMO=STOCK_MINIMO
    )


@app.route('/productos/nuevo', methods=["GET", "POST"])
@login_required
@role_required('admin', 'vendedor')
def nuevo_producto():
    """Crea un nuevo producto"""
    if request.method == "POST":
        try:
            nombre = request.form['nombre'].strip()
            categoria = request.form['categoria'].strip()
            marca = request.form.get('marca', '').strip()
            stock = int(request.form['stock'])
            precio_unitario = round(float(request.form['precio_unitario']), 3)
            descripcion = request.form.get('descripcion', '').strip()

            # Validaciones
            if not nombre or not categoria:
                flash("El nombre y la categoría son obligatorios.", "error")
                return redirect(url_for('nuevo_producto'))

            if stock < 0 or precio_unitario < 0:
                flash("El stock y el precio no pueden ser negativos.", "error")
                return redirect(url_for('nuevo_producto'))

        except ValueError:
            flash("Error en los datos del formulario. Verifica los valores numéricos.", "error")
            return redirect(url_for('nuevo_producto'))
        except KeyError:
            flash("Faltan campos obligatorios en el formulario.", "error")
            return redirect(url_for('nuevo_producto'))

        # Insertar en MySQL
        query = """
            INSERT INTO productos (nombre, categoria, marca, stock, precio_unitario, descripcion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (nombre, categoria, marca, stock, precio_unitario, descripcion)
        producto_id = ejecutar_query(query, params, commit=True)

        if producto_id:
            registrar_log('Producto creado', f"Producto: {nombre} (ID: {producto_id})")
            flash(f"El producto '{nombre}' ha sido registrado con éxito.", "success")
            return redirect(url_for('lista_productos'))
        else:
            flash("Error al guardar el producto en la base de datos.", "error")
            return redirect(url_for('nuevo_producto'))

    return render_template("crear_producto.html")


@app.route('/productos/<int:id>', methods=["GET"])
@login_required
def detalle_producto(id):
    """Muestra los detalles de un producto"""
    producto = obtener_producto_por_id(id)

    if not producto:
        flash(f"El producto con el ID {id} no fue encontrado.", "error")
        return redirect(url_for('lista_productos'))

    return render_template("detalle_producto.html", producto=producto)


@app.route('/productos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'vendedor')
def editar_producto(id):
    """Edita un producto existente"""
    producto = obtener_producto_por_id(id)

    if not producto:
        flash(f"El producto con el ID {id} no pudo ser encontrado.", "error")
        return redirect(url_for('lista_productos'))

    if request.method == 'POST':
        try:
            nombre = request.form['nombre'].strip()
            categoria = request.form['categoria'].strip()
            marca = request.form.get('marca', '').strip()
            stock = int(request.form['stock'])
            precio_unitario = round(float(request.form['precio_unitario']), 3)
            descripcion = request.form.get('descripcion', '').strip()

            # Validaciones
            if stock < 0 or precio_unitario < 0:
                flash("El stock y el precio no pueden ser negativos.", "error")
                return redirect(url_for('editar_producto', id=id))

            # Actualizar producto
            actualizar_producto(id, nombre, categoria, marca, stock, precio_unitario, descripcion)

            registrar_log('Producto actualizado', f"Producto: {nombre} (ID: {id})")

            flash(f"El producto '{nombre}' fue actualizado con éxito.", "success")
            return redirect(url_for('lista_productos'))

        except ValueError:
            flash("Error en los datos del formulario.", "error")
            return redirect(url_for('editar_producto', id=id))

    return render_template("editar_producto.html", producto=producto)


#  RUTA CORREGIDA: ELIMINAR PRODUCTO CON JSON RESPONSE
@app.route("/productos/<int:id>/eliminar", methods=['POST'])
@login_required
@role_required('admin')
def eliminar_producto(id):
    """Elimina un producto"""
    producto = obtener_producto_por_id(id)

    if not producto:
        return jsonify({'success': False, 'message': 'Producto no encontrado'}), 404

    eliminar_producto_db(id)
    registrar_log('Producto eliminado', f"Producto: {producto['nombre']} (ID: {id})")

    return jsonify({'success': True, 'message': f"El producto '{producto['nombre']}' fue eliminado con éxito."})


# ---------------------------------------------------------------------------------
# RUTAS DE VENTAS
# ---------------------------------------------------------------------------------
@app.route('/ventas/nueva', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'vendedor')
def nueva_venta():
    """Registra una nueva venta"""
    productos = cargar_productos()

    if request.method == "POST":
        try:
            producto_id = int(request.form['producto_id'])
            cantidad = int(request.form['cantidad'])

            if cantidad <= 0:
                flash("La cantidad debe ser mayor a 0.", "error")
                return redirect(url_for('nueva_venta'))

        except (ValueError, KeyError):
            flash("Datos inválidos en el formulario.", "error")
            return redirect(url_for('nueva_venta'))

        producto = obtener_producto_por_id(producto_id)

        if not producto:
            flash("Producto no encontrado.", "error")
            return redirect(url_for('nueva_venta'))

        # Validación de stock
        if cantidad > producto['stock']:
            flash(f"No puedes vender {cantidad} unidades. Stock disponible: {producto['stock']}.", "error")
            return redirect(url_for('nueva_venta'))

        # Calcular total
        total_venta = round(cantidad * producto['precio_unitario'], 3)

        # GUARDAR VENTA EN HISTORIAL
        venta = {
            'fecha': datetime.now().strftime('%Y-%m-%d'),
            'hora': datetime.now().strftime('%H:%M:%S'),
            'producto_id': producto['id'],
            'producto_nombre': producto['nombre'],
            'categoria': producto['categoria'],
            'cantidad': cantidad,
            'precio_unitario': producto['precio_unitario'],
            'total': total_venta,
            'usuario_id': session.get('user_id'),
            'usuario_nombre': session.get('nombre_completo')
        }
        guardar_venta(venta)

        registrar_log('Venta registrada', f"{cantidad} unidades de '{producto['nombre']}' por ${total_venta:,.3f}")

        # Actualizar stock
        nuevo_stock = producto['stock'] - cantidad
        actualizar_stock_producto(producto_id, nuevo_stock)

        flash(f" Venta registrada: {cantidad} unidades de '{producto['nombre']}' por ${total_venta:,.0f} COP", "success")
        return redirect(url_for('lista_productos'))

    return render_template("crear_venta.html", productos=productos)


@app.route('/ventas/historial')
@login_required
def historial_ventas():
    """Muestra el historial de ventas"""
    ventas = cargar_ventas()

    # Calcular total general
    total_general = sum(v.get('total', 0) for v in ventas)

    return render_template("historial_ventas.html", ventas=ventas, total_general=total_general)


#  NUEVA RUTA: ELIMINAR VENTA
@app.route('/ventas/<int:id>/eliminar', methods=['POST'])
@login_required
@role_required('admin')
def eliminar_venta(id):
    """Elimina una venta del historial"""
    # Buscar la venta
    query = "SELECT * FROM ventas WHERE id = %s"
    venta = ejecutar_query(query, (id,), fetch_one=True)
    
    if not venta:
        return jsonify({'success': False, 'message': 'Venta no encontrada'}), 404
    
    # Eliminar la venta
    eliminar_venta_db(id)
    
    registrar_log('Venta eliminada', f"Venta ID: {id} - Producto: {venta.get('producto_nombre')}")
    
    return jsonify({'success': True, 'message': 'Venta eliminada correctamente'})


# ---------------------------------------------------------------------------------
# DASHBOARD Y REPORTES
# ---------------------------------------------------------------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard con métricas y estadísticas generales"""
    productos = cargar_productos()
    ventas = cargar_ventas()

    # MÉTRICAS GENERALES
    total_productos = len(productos)
    valor_inventario_total = sum(p.get('valor_total', 0) for p in productos)
    productos_bajo_stock = sum(1 for p in productos if p.get('stock', 0) < STOCK_MINIMO)
    total_ventas_realizadas = len(ventas)

    # INGRESOS TOTALES
    ingresos_totales = sum(v.get('total', 0) for v in ventas)

    # PRODUCTOS MÁS VENDIDOS (Top 5)
    ventas_por_producto = {}
    for v in ventas:
        pid = v.get('producto_id')
        if pid not in ventas_por_producto:
            ventas_por_producto[pid] = {
                'nombre': v.get('producto_nombre'),
                'cantidad_vendida': 0,
                'ingresos': 0
            }
        ventas_por_producto[pid]['cantidad_vendida'] += v.get('cantidad', 0)
        ventas_por_producto[pid]['ingresos'] += v.get('total', 0)

    # Ordenar por cantidad vendida
    top_vendidos = sorted(
        ventas_por_producto.values(),
        key=lambda x: x['cantidad_vendida'],
        reverse=True
    )[:5]

    # VENTAS POR CATEGORÍA
    ventas_por_categoria = {}
    for v in ventas:
        cat = v.get('categoria', 'Sin categoría')
        if cat not in ventas_por_categoria:
            ventas_por_categoria[cat] = {
                'cantidad': 0,
                'ingresos': 0
            }
        ventas_por_categoria[cat]['cantidad'] += v.get('cantidad', 0)
        ventas_por_categoria[cat]['ingresos'] += v.get('total', 0)

    # VENTAS POR DÍA (Últimos 7 días)
    from collections import defaultdict
    ventas_por_dia = defaultdict(lambda: {'cantidad': 0, 'ingresos': 0})

    for v in ventas:
        fecha = v.get('fecha')
        ventas_por_dia[fecha]['cantidad'] += v.get('cantidad', 0)
        ventas_por_dia[fecha]['ingresos'] += v.get('total', 0)

    # Ordenar por fecha
    ventas_diarias = sorted(
        [{'fecha': k, 'cantidad': v['cantidad'], 'ingresos': v['ingresos']}
         for k, v in ventas_por_dia.items() if k],
        key=lambda x: x['fecha']
    )[-7:]  # Últimos 7 días

    # PRODUCTOS CON BAJO STOCK (detalle)
    productos_criticos = [
        p for p in productos
        if p.get('stock', 0) < STOCK_MINIMO
    ]
    productos_criticos = sorted(productos_criticos, key=lambda x: x.get('stock', 0))[:10]

    return render_template(
        'dashboard.html',
        # Métricas principales
        total_productos=total_productos,
        valor_inventario_total=valor_inventario_total,
        productos_bajo_stock=productos_bajo_stock,
        total_ventas_realizadas=total_ventas_realizadas,
        ingresos_totales=ingresos_totales,

        # Datos para gráficas
        top_vendidos=top_vendidos,
        ventas_por_categoria=ventas_por_categoria,
        ventas_diarias=ventas_diarias,
        productos_criticos=productos_criticos,

        STOCK_MINIMO=STOCK_MINIMO
    )


@app.route('/reportes/productos-mas-vendidos')
@login_required
def reporte_mas_vendidos():
    """Reporte detallado de productos más vendidos"""
    ventas = cargar_ventas()

    if not ventas:
        flash("No hay ventas registradas para generar el reporte.", "info")
        return redirect(url_for('dashboard'))

    # Agrupar ventas por producto
    ventas_por_producto = {}
    for v in ventas:
        pid = v.get('producto_id')
        if pid not in ventas_por_producto:
            ventas_por_producto[pid] = {
                'id': pid,
                'nombre': v.get('producto_nombre'),
                'categoria': v.get('categoria'),
                'cantidad_vendida': 0,
                'ingresos': 0,
                'num_ventas': 0
            }
        ventas_por_producto[pid]['cantidad_vendida'] += v.get('cantidad', 0)
        ventas_por_producto[pid]['ingresos'] += v.get('total', 0)
        ventas_por_producto[pid]['num_ventas'] += 1

    # Convertir a lista y ordenar
    productos_vendidos = list(ventas_por_producto.values())

    # Top 5 MÁS vendidos
    top_5_mas = sorted(
        productos_vendidos,
        key=lambda x: x['cantidad_vendida'],
        reverse=True
    )[:5]

    # Top 5 MENOS vendidos
    top_5_menos = sorted(
        productos_vendidos,
        key=lambda x: x['cantidad_vendida']
    )[:5]

    # Todos los productos ordenados
    todos_ordenados = sorted(
        productos_vendidos,
        key=lambda x: x['cantidad_vendida'],
        reverse=True
    )

    return render_template(
        'reporte_productos.html',
        top_5_mas=top_5_mas,
        top_5_menos=top_5_menos,
        todos_productos=todos_ordenados,
        total_productos=len(productos_vendidos)
    )

# ---------------------------------------------------------------------------------
# REPORTE: VENTAS POR PERÍODO (Día / Mes)
# ---------------------------------------------------------------------------------
@app.route('/reportes/ventas-por-periodo')
@login_required
def reporte_ventas_periodo():
    """Reporte de ventas por período usando MySQL"""

    ventas = cargar_ventas()

    if not ventas:
        flash("No hay ventas registradas.", "info")
        return redirect(url_for('dashboard'))

    from collections import defaultdict
    ventas_diarias = defaultdict(lambda: {'cantidad': 0, 'ingresos': 0, 'num_ventas': 0})
    ventas_mensuales = defaultdict(lambda: {'cantidad': 0, 'ingresos': 0, 'num_ventas': 0})

    for v in ventas:
        fecha = v.get('fecha')   # este valor viene de MySQL como date o string

        #  Convertir fecha a string YYYY-MM-DD
        if isinstance(fecha, datetime):
            fecha_str = fecha.strftime("%Y-%m-%d")
        elif hasattr(fecha, "strftime"):  
            fecha_str = fecha.strftime("%Y-%m-%d")
        else:
            fecha_str = str(fecha)

        # VENTAS POR DÍA
        ventas_diarias[fecha_str]['cantidad'] += v.get('cantidad', 0)
        ventas_diarias[fecha_str]['ingresos'] += v.get('total', 0)
        ventas_diarias[fecha_str]['num_ventas'] += 1

        # VENTAS POR MES YYYY-MM
        mes = fecha_str[:7]  # YA ES SEGURO porque fecha_str SIEMPRE es string
        ventas_mensuales[mes]['cantidad'] += v.get('cantidad', 0)
        ventas_mensuales[mes]['ingresos'] += v.get('total', 0)
        ventas_mensuales[mes]['num_ventas'] += 1

    # ORDENAR
    ventas_por_dia = sorted(
        [{'fecha': k, **v} for k, v in ventas_diarias.items()],
        key=lambda x: x['fecha'],
        reverse=True
    )

    ventas_por_mes = sorted(
        [{'mes': k, **v} for k, v in ventas_mensuales.items()],
        key=lambda x: x['mes'],
        reverse=True
    )

    return render_template(
        'reporte_periodo.html',
        ventas_por_dia=ventas_por_dia,
        ventas_por_mes=ventas_por_mes
    )

@app.route("/reportes/inventario-total")
@login_required
def reporte_inventario_total():
    """Reporte completo del inventario total"""
    productos = cargar_productos()

    if not productos:
        flash("No hay productos en el inventario para mostrar el reporte.", "info")
        return redirect(url_for('lista_productos'))

    # Cálculos generales
    total_items = len(productos)
    total_unidades = sum(p.get('stock', 0) for p in productos)
    valor_total_inventario = sum(p.get('stock', 0) * p.get('precio_unitario', 0) for p in productos)

    # Ordenar por categoría y nombre
    productos_ordenados = sorted(productos, key=lambda x: x.get('id', 0))

    return render_template(
        "reportes/reporte_inventario_total.html",
        productos=productos_ordenados,
        total_items=total_items,
        total_unidades=total_unidades,
        valor_total=valor_total_inventario
    )

