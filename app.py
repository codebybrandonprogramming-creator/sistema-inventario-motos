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


    