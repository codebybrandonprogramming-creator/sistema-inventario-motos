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