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

