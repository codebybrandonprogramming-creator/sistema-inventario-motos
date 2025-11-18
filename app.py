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

from flask import Flask, request, render_template, redirect, url_for, flash, send_file, session
import json
import os
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

app = Flask(__name__)
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
    
    Args:
        query: Consulta SQL con placeholders %s
        params: Tupla con los parámetros
        commit: True si es INSERT/UPDATE/DELETE
        fetch_one: True para obtener un solo registro
        fetch_all: True para obtener todos los registros
    
    Returns:
        - Si fetch_one: Un diccionario o None
        - Si fetch_all: Lista de diccionarios
        - Si commit: ID del último registro insertado (lastrowid)
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
        print(f"❌ Error en la base de datos: {e}")
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
    
    # Calcular precio_venta basado en precio_unitario + IVA + ganancia
    precio_con_iva = round(precio_unitario * 1.19, 2)
    precio_venta = round(precio_con_iva * (1 + porcentaje_ganancia / 100), 2)
    
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

