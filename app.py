# ENUNCIADO OFICIAL DEL SISTEMA DE INVENTARIO DE REPUESTOS PARA MOTOS

# Desarrollar un Sistema de Inventario para un negocio de repuestos
# de motocicletas, utilizando Flask, archivos JSON y Bootstrap.
# El sistema debe permitir al dueño del negocio registrar, consultar y 
# mantener actualizada la información de todos los productos en stock.

# ---
# OBJETIVO DEL SISTEMA

# Crear una aplicación web que permita gestionar un inventario completo y 
# organizado de repuestos de motos, con la posibilidad de agregar, 
# listar, editar y eliminar productos de forma sencilla y profesional.

# ---

# FUNCIONALIDADES OBLIGATORIAS (VERSIÓN 1 – Profesional básica)
# Registrar productos
# ID del producto (generado automáticamente)
# Nombre
# Categoría (aceites, llantas, frenos, correas, kit de arrastre, bujías, rodamientos, cascos, etc.)
# Marca
# Stock disponible
# Precio unitario
# Descripción
# Valor total (stock × precio unitario)


# Listar productos
# Mostrar todos los productos en una tabla
# Ver botones de detalle, editar y eliminar

# Ver detalle del producto
# Mostrar toda la información completa


# Editar productos
# Permitir modificar nombre, categoría, marca, stock y precio
# Recalcular valor total automáticamente

# Eliminar productos

# Persistencia en archivo JSON
# Todos los cambios deben guardarse en data/productos.json


# Interfaz profesional con Bootstrap
# Diseño limpio, elegante y moderno
# Cabecera fija con el nombre del sistema
# Plantilla base con Jinja

# ---

# VERSIÓN 2 (Cuando terminemos lo básico) — Mejoras profesionales

# Estas se agregarán después:
# Buscador de productos
# Filtro por categoría
# Ordenar por precio
# Alerta de bajo stock
# Registro automático de ventas (restar stock sin hacerlo a mano)
# Historial de movimientos (entradas/salidas)
# Exportar reportes en PDF
# Conexión a MySQL para manejo real en producción

from flask import Flask, request, render_template, redirect, url_for, flash, send_file, session, jsonify
import json
import os
from datetime import datetime
from collections import defaultdict
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from flask_wtf import CSRFProtect


app = Flask(__name__)
app.secret_key = "dev_secret_key_change_in_production"

# Headers de seguridad
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# ---------------------------------------------------------------------------------
# CONFIGURACIÓN Y CONEXIÓN A MYSQL
# ---------------------------------------------------------------------------------
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'inventario_repuestos'),
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
        import logging
        logging.error(f"Error DB: {e}")
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
        SELECT id, codigo_sku, nombre, categoria, marca, stock, precio_unitario, 
               porcentaje_ganancia, precio_venta, descripcion, valor_total, 
               fecha_creacion, fecha_actualizacion
        FROM productos
        ORDER BY id
    """
    productos = ejecutar_query(query, fetch_all=True)
    return productos if productos else []


def obtener_producto_por_id(producto_id):
    """Obtiene un producto específico por su ID"""
    query = """
        SELECT id, codigo_sku, nombre, categoria, marca, stock, precio_unitario, 
               porcentaje_ganancia, precio_venta, descripcion, valor_total, 
               fecha_creacion, fecha_actualizacion
        FROM productos
        WHERE id = %s
    """
    return ejecutar_query(query, (producto_id,), fetch_one=True)

def actualizar_producto(producto_id, nombre, categoria, marca, stock, precio_unitario, descripcion, codigo_sku=None, porcentaje_ganancia=0):
    """Actualiza un producto existente en MySQL"""
    valor_total = round(stock * precio_unitario, 3)
    
    precio_con_iva = round(precio_unitario * 1.19, 3)
    precio_venta = round(precio_con_iva * (1 + porcentaje_ganancia / 100), 3)

    if stock < 0 or precio_unitario < 0:
        flash("El stock y el precio no pueden ser negativos.", "error")
        return redirect(url_for('editar_producto', id=id))
    
    query = """
        UPDATE productos 
        SET nombre = %s, categoria = %s, marca = %s, stock = %s, 
            precio_unitario = %s, porcentaje_ganancia = %s, precio_venta = %s,
            descripcion = %s, valor_total = %s, codigo_sku = %s,
            fecha_actualizacion = NOW()
        WHERE id = %s
    """
    params = (nombre, categoria, marca, stock, precio_unitario, porcentaje_ganancia, 
              precio_venta, descripcion, valor_total, codigo_sku, producto_id)
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

def reiniciar_autoincrement_productos():
    """Reinicia el AUTO_INCREMENT de la tabla productos si está vacía"""
    try:
        count_query = "SELECT COUNT(*) as total FROM productos"
        result = ejecutar_query(count_query, fetch_one=True)
        
        if result and result.get('total', 0) == 0:
            reset_query = "ALTER TABLE productos AUTO_INCREMENT = 1"
            ejecutar_query(reset_query, commit=True)
            return True
        return False
    except Exception as e:
        print(f"❌ Error al reiniciar AUTO_INCREMENT: {e}")
        return False


def reiniciar_autoincrement_ventas():
    """Reinicia el AUTO_INCREMENT de la tabla ventas si está vacía"""
    try:
        count_query = "SELECT COUNT(*) as total FROM ventas"
        result = ejecutar_query(count_query, fetch_one=True)
        
        if result and result.get('total', 0) == 0:
            reset_query = "ALTER TABLE ventas AUTO_INCREMENT = 1"
            ejecutar_query(reset_query, commit=True)
            return True
        return False
    except Exception as e:
        print(f"❌ Error al reiniciar AUTO_INCREMENT de ventas: {e}")
        return False


def cargar_ventas():
    """Carga todas las ventas desde MySQL con todos los campos"""
    query = """
        SELECT 
            id, fecha, hora, producto_id, producto_nombre, categoria,
            cantidad, precio_unitario, total, iva_total,
            ganancia_unitaria, ganancia_total, porcentaje_ganancia,
            usuario_id, usuario_nombre, fecha_registro
        FROM ventas
        ORDER BY fecha DESC, hora DESC
    """
    ventas = ejecutar_query(query, fetch_all=True)
    return ventas if ventas else []


def guardar_venta(venta):
    """Guarda una nueva venta en MySQL con IVA y ganancia desglosados"""
    query = """
        INSERT INTO ventas (
            fecha, hora, producto_id, producto_nombre, categoria,
            cantidad, precio_unitario, 
            iva_unitario, precio_con_iva, porcentaje_ganancia, 
            ganancia_unitaria, precio_venta_unitario,
            subtotal, iva_total, ganancia_total, total,
            usuario_id, usuario_nombre
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        venta['fecha'],
        venta['hora'],
        venta['producto_id'],
        venta['producto_nombre'],
        venta['categoria'],
        venta['cantidad'],
        venta['precio_unitario'],
        venta.get('iva_unitario', 0),
        venta.get('precio_con_iva', 0),
        venta.get('porcentaje_ganancia', 0),
        venta.get('ganancia_unitaria', 0),
        venta.get('precio_venta_unitario', 0),
        venta.get('subtotal', 0),
        venta.get('iva_total', 0),
        venta.get('ganancia_total', 0),
        venta['total'],
        venta.get('usuario_id'),
        venta.get('usuario_nombre')
    )
    return ejecutar_query(query, params, commit=True)


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
        
        if any(u['username'] == username for u in usuarios):
            flash(f'El usuario "{username}" ya existe.', 'error')
            return redirect(url_for('nuevo_usuario'))
        
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
    
    if usuario['id'] == session.get('user_id'):
        flash('No puedes eliminar tu propia cuenta.', 'error')
        return redirect(url_for('lista_usuarios'))
    
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
        
        if not check_password_hash(usuario['password'], password_actual):
            flash('La contraseña actual es incorrecta.', 'error')
            return redirect(url_for('cambiar_password'))
        
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


@app.route('/logs/limpiar', methods=['POST'])
@login_required
@role_required('admin')
def limpiar_logs():
    """Elimina todos los registros del historial y reinicia el AUTO_INCREMENT"""
    ejecutar_query("DELETE FROM logs", commit=True)
    ejecutar_query("ALTER TABLE logs AUTO_INCREMENT = 1", commit=True)
    registrar_log("Historial limpiado", "Se eliminaron todos los logs y se reinició el AUTO_INCREMENT.")
    flash("Historial limpiado correctamente. IDs reiniciados desde 1.", "success")
    return redirect(url_for('ver_logs'))