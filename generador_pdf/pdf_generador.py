"""
📋 GENERADOR DE PDF PROFESIONAL - PARTE 1
Sistema de Inventario H&D - Moto Repuestos

Requisitos:
pip install reportlab

Uso:
python generar_pdf_profesional.py
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from datetime import datetime


# ==================== CONFIGURACIÓN ====================
PDF_FILENAME = "Sistema_Inventario_HD_Documentacion_Completa.pdf"
TITLE = "Sistema de Inventario H&D"
SUBTITLE = "Moto Repuestos Profesional"
VERSION = "Versión 2.0 - MySQL"
AUTHOR = "Equipo de Desarrollo"


# ==================== ESTILOS PERSONALIZADOS ====================
def crear_estilos():
    """Crea estilos personalizados para el documento"""
    styles = getSampleStyleSheet()
    
    # Título principal (portada)
    styles.add(ParagraphStyle(
        name='TituloPortada',
        parent=styles['Title'],
        fontSize=36,
        textColor=colors.HexColor('#1e3c72'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Subtítulo portada
    styles.add(ParagraphStyle(
        name='SubtituloPortada',
        parent=styles['Normal'],
        fontSize=20,
        textColor=colors.HexColor('#2a5298'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))
    
    # Encabezado de sección
    styles.add(ParagraphStyle(
        name='Seccion',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1e3c72'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderWidth=2,
        borderColor=colors.HexColor('#ffd700'),
        borderPadding=8,
        backColor=colors.HexColor('#f0f8ff')
    ))
    
    # Subsección
    styles.add(ParagraphStyle(
        name='Subseccion',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2a5298'),
        spaceAfter=10,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    ))
    
    # Texto normal con justificación
    styles.add(ParagraphStyle(
        name='Justificado',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leading=16
    ))
    
    # Lista con viñetas
    styles.add(ParagraphStyle(
        name='Viñeta',
        parent=styles['Normal'],
        fontSize=11,
        leftIndent=20,
        spaceAfter=6,
        bulletIndent=10,
        leading=14
    ))
    
    # Cuadro destacado
    styles.add(ParagraphStyle(
        name='Destacado',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1e3c72'),
        backColor=colors.HexColor('#fffacd'),
        borderWidth=1,
        borderColor=colors.HexColor('#ffd700'),
        borderPadding=10,
        spaceAfter=12,
        alignment=TA_JUSTIFY
    ))
    
    return styles


# ==================== ENCABEZADO Y PIE DE PÁGINA ====================
class PDFWithHeader(canvas.Canvas):
    """Clase personalizada para agregar encabezado y pie de página"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        page_count = len(self.pages)
        for page_num, page in enumerate(self.pages, 1):
            self.__dict__.update(page)
            if page_num > 1:  # No poner encabezado en portada
                self.draw_header_footer(page_num, page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_header_footer(self, page_num, page_count):
        """Dibuja encabezado y pie de página"""
        # Encabezado
        self.setFont('Helvetica-Bold', 10)
        self.setFillColor(colors.HexColor('#1e3c72'))
        self.drawString(50, letter[1] - 40, "Sistema de Inventario H&D")
        
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#666666'))
        self.drawRightString(letter[0] - 50, letter[1] - 40, f"Versión 2.0 - MySQL")
        
        # Línea decorativa
        self.setStrokeColor(colors.HexColor('#ffd700'))
        self.setLineWidth(2)
        self.line(50, letter[1] - 45, letter[0] - 50, letter[1] - 45)
        
        # Pie de página
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#666666'))
        self.drawString(50, 30, f"Página {page_num} de {page_count}")
        self.drawRightString(letter[0] - 50, 30, f"Generado: {datetime.now().strftime('%d/%m/%Y')}")


# ==================== CONTENIDO DEL PDF ====================
def crear_portada(styles):
    """Crea la portada del documento"""
    story = []
    
    # Espacio superior
    story.append(Spacer(1, 2*inch))
    
    # Título principal
    story.append(Paragraph("📋 SISTEMA DE INVENTARIO H&D", styles['TituloPortada']))
    story.append(Spacer(1, 0.3*inch))
    
    # Subtítulo
    story.append(Paragraph("🏍️ Moto Repuestos Profesional", styles['SubtituloPortada']))
    story.append(Spacer(1, 0.5*inch))
    
    # Información de versión
    version_text = f"""
    <para align=center>
    <font size=14 color='#2a5298'><b>Versión 2.0 - MySQL</b></font><br/>
    <font size=12 color='#666666'>Documentación Completa del Sistema</font><br/><br/>
    <font size=10 color='#999999'>Base de datos robusta y segura</font><br/>
    <font size=10 color='#999999'>Multiusuario con control de accesos</font><br/>
    <font size=10 color='#999999'>Reportes profesionales y exportaciones</font>
    </para>
    """
    story.append(Paragraph(version_text, styles['Normal']))
    story.append(Spacer(1, 1*inch))
    
    # Fecha de generación
    fecha_actual = datetime.now().strftime('%d de %B de %Y')
    story.append(Paragraph(
        f"<para align=center><font size=11 color='#666666'>Generado el {fecha_actual}</font></para>",
        styles['Normal']
    ))
    
    story.append(PageBreak())
    return story


def seccion_descripcion(styles):
    """Sección: Descripción General"""
    story = []
    
    story.append(Paragraph("🎯 DESCRIPCIÓN GENERAL", styles['Seccion']))
    
    texto = """
    El <b>Sistema de Inventario H&D</b> es una solución completa y profesional diseñada específicamente 
    para la gestión integral de un negocio de repuestos de motocicletas. Desarrollado con tecnologías 
    modernas como <b>Python Flask</b>, <b>MySQL</b> y <b>Bootstrap 5</b>, ofrece una plataforma web 
    robusta, segura y fácil de usar para administrar productos, ventas, usuarios y generar reportes 
    detallados en tiempo real.
    """
    story.append(Paragraph(texto, styles['Justificado']))
    story.append(Spacer(1, 0.2*inch))
    
    # Características destacadas
    story.append(Paragraph("✨ Características Principales:", styles['Subseccion']))
    
    caracteristicas = [
        "💾 <b>Base de datos MySQL</b>: Persistencia permanente y segura de todos los datos",
        "👥 <b>Sistema multiusuario</b>: 3 roles con permisos diferenciados (Admin, Vendedor, Auditor)",
        "🔐 <b>Seguridad robusta</b>: Contraseñas encriptadas y control de acceso por roles",
        "📊 <b>Dashboard ejecutivo</b>: Métricas en tiempo real con gráficas interactivas",
        "📑 <b>Reportes profesionales</b>: Análisis detallados de ventas, productos y períodos",
        "📤 <b>Exportaciones</b>: Generación de archivos Excel y PDF con formato profesional",
        "📜 <b>Sistema de logs</b>: Auditoría completa de todas las acciones del sistema",
        "🎨 <b>3 Temas visuales</b>: Premium, Trabajo y Oscuro adaptables a preferencias",
        "📱 <b>Diseño responsive</b>: Funciona perfectamente en computadoras, tablets y móviles",
        "⚡ <b>Alertas inteligentes</b>: Notificaciones automáticas de productos con stock bajo"
    ]
    
    for caract in caracteristicas:
        story.append(Paragraph(f"• {caract}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    return story


def seccion_informacion_tecnica(styles):
    """Sección: Información Técnica"""
    story = []
    
    story.append(Paragraph("🏢 INFORMACIÓN TÉCNICA", styles['Seccion']))
    
    # Tabla de información técnica
    data = [
        ['Aspecto', 'Detalle'],
        ['Nombre del Sistema', 'Inventario H&D - Moto Repuestos Profesional'],
        ['Versión', '2.0 (Migrado a MySQL)'],
        ['Tecnologías Backend', 'Python 3.x + Flask Framework'],
        ['Base de Datos', 'MySQL (XAMPP)'],
        ['Frontend', 'HTML5 + Bootstrap 5 + JavaScript'],
        ['Gráficas', 'Chart.js 4.4.0'],
        ['Iconos', 'Bootstrap Icons'],
        ['Tipo de Aplicación', 'Web (accesible desde navegador)'],
        ['Seguridad', 'Werkzeug Security (hash de contraseñas)'],
        ['Exportaciones', 'openpyxl (Excel) + reportlab (PDF)'],
        ['Compatibilidad', 'Windows, macOS, Linux'],
    ]
    
    table = Table(data, colWidths=[2.5*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f8ff')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2a5298')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    return story


def seccion_gestion_productos(styles):
    """Sección: Gestión de Productos"""
    story = []
    
    story.append(Paragraph("📦 1. GESTIÓN DE PRODUCTOS", styles['Seccion']))
    
    texto = """
    El módulo de gestión de productos es el corazón del sistema, permitiendo un control completo 
    y detallado de todo el inventario de repuestos de motocicletas.
    """
    story.append(Paragraph(texto, styles['Justificado']))
    story.append(Spacer(1, 0.15*inch))
    
    # Registro de productos
    story.append(Paragraph("📝 Registro de Productos", styles['Subseccion']))
    
    campos = [
        "<b>ID del producto</b>: Generado automáticamente por MySQL (autoincremental)",
        "<b>Nombre del producto</b>: Descripción clara del repuesto",
        "<b>Categoría</b>: Clasificación (Filtros, Aceites, Frenos, Kit de Arrastre, Bujías, Rodamientos, Cascos, etc.)",
        "<b>Marca</b>: Fabricante o marca del producto",
        "<b>Stock disponible</b>: Cantidad actual en inventario (validado: no negativo)",
        "<b>Precio unitario</b>: Precio en pesos colombianos (COP) con 3 decimales",
        "<b>Descripción</b>: Información adicional detallada del producto",
        "<b>Valor total</b>: Calculado automáticamente (stock × precio unitario)",
        "<b>Fechas</b>: Registro automático de creación y última actualización"
    ]
    
    for campo in campos:
        story.append(Paragraph(f"• {campo}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Operaciones disponibles
    story.append(Paragraph("⚙️ Operaciones Disponibles", styles['Subseccion']))
    
    operaciones = [
        "✅ <b>Crear nuevos productos</b>: Formulario intuitivo con validaciones",
        "✅ <b>Editar productos existentes</b>: Modificar cualquier campo excepto el ID",
        "✅ <b>Eliminar productos</b>: Borrado permanente (solo Administradores)",
        "✅ <b>Ver detalles completos</b>: Vista detallada de cada producto",
        "✅ <b>Búsqueda inteligente</b>: Filtrado en tiempo real por nombre",
        "✅ <b>Filtrar por categoría</b>: Selección de categoría específica",
        "✅ <b>Ordenar por precio</b>: Ascendente o descendente",
        "✅ <b>Ordenar por stock</b>: Ver primero productos con más/menos existencias",
        "✅ <b>Alertas de bajo stock</b>: Productos con menos de 5 unidades destacados en rojo",
        "✅ <b>Cálculo automático</b>: Valor total actualizado al modificar stock o precio"
    ]
    
    for operacion in operaciones:
        story.append(Paragraph(f"• {operacion}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Cuadro destacado
    texto_destacado = """
    <b>💡 Característica destacada:</b> El sistema valida automáticamente que el stock y el precio 
    no sean negativos, y recalcula el valor total en tiempo real cada vez que se edita un producto, 
    eliminando errores de cálculo manual.
    """
    story.append(Paragraph(texto_destacado, styles['Destacado']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    return story


def seccion_gestion_ventas(styles):
    """Sección: Gestión de Ventas"""
    story = []
    
    story.append(Paragraph("🛒 2. GESTIÓN DE VENTAS", styles['Seccion']))
    
    texto = """
    El módulo de ventas permite registrar transacciones de forma rápida y segura, actualizando 
    automáticamente el inventario y generando un historial completo para análisis posteriores.
    """
    story.append(Paragraph(texto, styles['Justificado']))
    story.append(Spacer(1, 0.15*inch))
    
    # Proceso de registro
    story.append(Paragraph("📝 Proceso de Registro de Venta", styles['Subseccion']))
    
    pasos = [
        "<b>1. Selección de producto</b>: Búsqueda inteligente con filtrado en tiempo real por nombre",
        "<b>2. Ingreso de cantidad</b>: Validación automática contra el stock disponible",
        "<b>3. Cálculo automático del total</b>: Cantidad × Precio unitario (sin decimales en COP)",
        "<b>4. Validación de stock</b>: El sistema no permite vender más unidades de las disponibles",
        "<b>5. Registro de la venta</b>: Almacenamiento en base de datos con todos los detalles",
        "<b>6. Actualización automática</b>: Descuento del stock vendido del inventario",
        "<b>7. Registro de auditoría</b>: Log automático con usuario, fecha y hora exacta"
    ]
    
    for paso in pasos:
        story.append(Paragraph(f"• {paso}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Información registrada
    story.append(Paragraph("📊 Información Registrada por Venta", styles['Subseccion']))
    
    info_venta = [
        "<b>Fecha</b>: Día de la venta (formato: YYYY-MM-DD)",
        "<b>Hora</b>: Hora exacta de registro (formato: HH:MM:SS)",
        "<b>Producto ID y nombre</b>: Identificación del artículo vendido",
        "<b>Categoría</b>: Clasificación del producto",
        "<b>Cantidad vendida</b>: Número de unidades",
        "<b>Precio unitario</b>: Precio al momento de la venta",
        "<b>Total de la venta</b>: Monto total en pesos colombianos (COP)",
        "<b>Usuario vendedor</b>: ID y nombre completo de quien registró la venta"
    ]
    
    for info in info_venta:
        story.append(Paragraph(f"• {info}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Características de seguridad
    story.append(Paragraph("🔒 Características de Seguridad", styles['Subseccion']))
    
    seguridad = [
        "✅ <b>Validación de stock en tiempo real</b>: Imposible vender productos agotados",
        "✅ <b>Transacciones atómicas</b>: Si falla algo, no se registra nada (integridad de datos)",
        "✅ <b>Trazabilidad completa</b>: Cada venta registra quién, cuándo y qué se vendió",
        "✅ <b>Historial permanente</b>: Las ventas nunca se eliminan, solo se consultan",
        "✅ <b>Formato de moneda consistente</b>: Siempre en pesos colombianos (COP)",
        "✅ <b>Cálculos precisos</b>: Sin errores de redondeo o decimales incorrectos"
    ]
    
    for item in seguridad:
        story.append(Paragraph(f"• {item}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Cuadro destacado
    texto_destacado = """
    <b>⚡ Ventaja clave:</b> El sistema actualiza el stock automáticamente al registrar una venta, 
    eliminando la necesidad de hacerlo manualmente y evitando descuadres en el inventario. Además, 
    todo queda registrado en el historial con fecha, hora y usuario responsable.
    """
    story.append(Paragraph(texto_destacado, styles['Destacado']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    return story


# ==================== CONTINUARÁ EN PARTE 2 ====================

"""
📋 GENERADOR DE PDF PROFESIONAL - PARTE 2A
Sistema de Inventario H&D - Moto Repuestos

ESTA ES LA CONTINUACIÓN DE LA PARTE 1
Pega este código después de la Parte 1
"""

# ==================== CONTINUACIÓN DE SECCIONES ====================

def seccion_dashboard(styles):
    """Sección: Dashboard Ejecutivo"""
    story = []
    
    story.append(Paragraph("📊 3. DASHBOARD EJECUTIVO", styles['Seccion']))
    
    texto = """
    El Dashboard es el centro de control del sistema, proporcionando una vista completa y en tiempo real 
    de todas las métricas importantes del negocio. Incluye gráficas interactivas, tablas informativas 
    y análisis detallados para la toma de decisiones estratégicas.
    """
    story.append(Paragraph(texto, styles['Justificado']))
    story.append(Spacer(1, 0.15*inch))
    
    # Métricas principales
    story.append(Paragraph("📈 Métricas Principales", styles['Subseccion']))
    
    metricas = [
        "<b>Total de productos en inventario</b>: Número de referencias diferentes",
        "<b>Valor total del inventario</b>: Suma de todos los productos (stock × precio)",
        "<b>Productos con stock bajo</b>: Artículos con menos de 5 unidades",
        "<b>Total de ventas realizadas</b>: Número histórico de transacciones",
        "<b>Ingresos totales</b>: Suma de todos los montos vendidos (en COP)"
    ]
    
    for metrica in metricas:
        story.append(Paragraph(f"• {metrica}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Gráficas disponibles
    story.append(Paragraph("📊 Análisis Visual con Gráficas", styles['Subseccion']))
    
    graficas = [
        "<b>Gráfica de líneas - Evolución de ventas (últimos 7 días)</b>: Muestra tendencia de unidades vendidas e ingresos diarios",
        "<b>Gráfica de barras - Ventas por categoría</b>: Comparación visual de rendimiento entre categorías de productos",
        "<b>Gráfica de pastel - Distribución de ingresos</b>: Proporción de ingresos por categoría con porcentajes automáticos"
    ]
    
    for grafica in graficas:
        story.append(Paragraph(f"• {grafica}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Tablas informativas
    story.append(Paragraph("📋 Tablas Informativas", styles['Subseccion']))
    
    tablas = [
        "<b>Top 5 productos más vendidos</b>: Ranking con trofeos, unidades vendidas e ingresos generados",
        "<b>Productos con stock crítico</b>: Alertas destacadas en rojo para productos que requieren reabastecimiento",
        "<b>Ventas por categoría</b>: Resumen de unidades vendidas e ingresos por tipo de producto"
    ]
    
    for tabla in tablas:
        story.append(Paragraph(f"• {tabla}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Cuadro destacado
    texto_destacado = """
    <b>🎯 Ventaja estratégica:</b> El Dashboard actualiza todas las métricas en tiempo real. 
    No hay necesidad de calcular manualmente ni esperar reportes: al momento de registrar una venta 
    o agregar productos, las estadísticas se actualizan instantáneamente.
    """
    story.append(Paragraph(texto_destacado, styles['Destacado']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    return story


def seccion_reportes(styles):
    """Sección: Reportes Avanzados"""
    story = []
    
    story.append(Paragraph("📑 4. REPORTES AVANZADOS", styles['Seccion']))
    
    texto = """
    El sistema incluye tres tipos de reportes profesionales diseñados para análisis profundo 
    del negocio, permitiendo identificar patrones, tendencias y oportunidades de mejora.
    """
    story.append(Paragraph(texto, styles['Justificado']))
    story.append(Spacer(1, 0.15*inch))
    
    # Reporte A
    story.append(Paragraph("A. Reporte de Productos Más/Menos Vendidos", styles['Subseccion']))
    
    reporte_a = [
        "<b>Top 5 productos MÁS vendidos</b>: Con indicadores visuales de trofeos y badges",
        "<b>Top 5 productos MENOS vendidos</b>: Para identificar productos de baja rotación",
        "<b>Listado completo ordenado</b>: Todos los productos ordenados por cantidad vendida",
        "<b>Métricas incluidas</b>: Unidades vendidas, número de transacciones, ingresos totales generados"
    ]
    
    for item in reporte_a:
        story.append(Paragraph(f"• {item}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.15*inch))
    
    # Reporte B
    story.append(Paragraph("B. Reporte de Ventas por Período", styles['Subseccion']))
    
    reporte_b = [
        "<b>Análisis mensual completo</b>:",
        "  - Unidades vendidas por mes",
        "  - Número de ventas por mes",
        "  - Ingresos totales por mes",
        "  - Promedio de ingresos por venta",
        "  - Identificación del mejor mes de ventas",
        "<b>Análisis diario detallado</b>:",
        "  - Ventas día por día con fecha exacta",
        "  - Identificación del mejor día de ventas",
        "  - Historial completo con unidades e ingresos"
    ]
    
    for item in reporte_b:
        story.append(Paragraph(f"• {item}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.15*inch))
    
    # Reporte C
    story.append(Paragraph("C. Reporte de Inventario Total", styles['Subseccion']))
    
    reporte_c = [
        "<b>Listado completo</b>: Todos los productos del inventario",
        "<b>Resumen ejecutivo</b>:",
        "  - Total de productos diferentes en stock",
        "  - Total de unidades disponibles",
        "  - Valor total del inventario en pesos colombianos (COP)",
        "<b>Vista profesional</b>: Diseño 3D con efectos glassmorphism",
        "<b>Exportación disponible</b>: A Excel y PDF con formato corporativo"
    ]
    
    for item in reporte_c:
        story.append(Paragraph(f"• {item}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    return story


def seccion_exportaciones(styles):
    """Sección: Exportaciones"""
    story = []
    
    story.append(Paragraph("📤 5. EXPORTACIONES PROFESIONALES", styles['Seccion']))
    
    texto = """
    El sistema permite exportar el reporte de inventario total en dos formatos profesionales, 
    perfectos para análisis externo, presentaciones o documentación oficial.
    """
    story.append(Paragraph(texto, styles['Justificado']))
    story.append(Spacer(1, 0.15*inch))
    
    # Excel
    story.append(Paragraph("📊 Exportación a Excel (.xlsx)", styles['Subseccion']))
    
    excel_features = [
        "<b>Formato profesional</b>: Encabezados con colores corporativos (azul y dorado)",
        "<b>Totales destacados</b>: Resumen ejecutivo en la parte superior",
        "<b>Tabla completa</b>: Con todos los productos y sus detalles",
        "<b>Estilos aplicados</b>: Bordes, colores alternados, texto centrado",
        "<b>Formato de moneda</b>: Columnas de precios con símbolo $ y separador de miles",
        "<b>Columnas ajustadas</b>: Ancho automático según el contenido",
        "<b>Listo para análisis</b>: Compatible con Excel, LibreOffice, Google Sheets"
    ]
    
    for feature in excel_features:
        story.append(Paragraph(f"• {feature}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # PDF
    story.append(Paragraph("📄 Exportación a PDF", styles['Subseccion']))
    
    pdf_features = [
        "<b>Diseño horizontal (landscape)</b>: Optimizado para tablas anchas",
        "<b>Encabezados corporativos</b>: Título profesional con información del sistema",
        "<b>Totales destacados</b>: Cuadro resumen antes de la tabla principal",
        "<b>Tabla estructurada</b>: Con bordes, colores y formato consistente",
        "<b>Paginación automática</b>: Si hay muchos productos, se divide en varias páginas",
        "<b>Listo para imprimir</b>: Formato A4 optimizado",
        "<b>Tamaño de archivo pequeño</b>: Fácil de compartir por email"
    ]
    
    for feature in pdf_features:
        story.append(Paragraph(f"• {feature}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Cuadro destacado
    texto_destacado = """
    <b>💼 Uso profesional:</b> Las exportaciones están diseñadas con calidad corporativa. 
    Son perfectas para reuniones con directivos, auditorías, presentaciones a inversores 
    o simplemente para tener respaldos impresos del inventario.
    """
    story.append(Paragraph(texto_destacado, styles['Destacado']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    return story


def seccion_usuarios_roles(styles):
    """Sección: Gestión de Usuarios y Roles"""
    story = []
    
    story.append(Paragraph("👥 6. GESTIÓN DE USUARIOS Y ROLES", styles['Seccion']))
    
    texto = """
    El sistema implementa un control de acceso robusto con tres niveles de permisos, 
    permitiendo que múltiples personas trabajen simultáneamente con accesos diferenciados 
    según sus responsabilidades en el negocio.
    """
    story.append(Paragraph(texto, styles['Justificado']))
    story.append(Spacer(1, 0.15*inch))
    
    # Tabla de roles
    story.append(Paragraph("🛡️ Roles y Permisos", styles['Subseccion']))
    
    # Administrador
    story.append(Paragraph("<b>ADMINISTRADOR</b> - Acceso Total 🔓", styles['Subseccion']))
    admin_perms = [
        "✅ Control total del sistema",
        "✅ Crear, editar y eliminar productos",
        "✅ Registrar ventas",
        "✅ Ver todos los reportes y dashboard",
        "✅ Gestionar usuarios (crear, activar, desactivar, eliminar)",
        "✅ Ver logs del sistema (auditoría completa)",
        "✅ Resetear contraseñas de otros usuarios",
        "✅ Exportar reportes a Excel y PDF"
    ]
    for perm in admin_perms:
        story.append(Paragraph(f"• {perm}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.15*inch))
    
    # Vendedor
    story.append(Paragraph("<b>VENDEDOR</b> - Acceso Operativo 🛒", styles['Subseccion']))
    vendedor_perms = [
        "✅ Crear y editar productos",
        "✅ Registrar ventas",
        "✅ Ver inventario completo",
        "✅ Ver historial de ventas",
        "✅ Ver dashboard y reportes",
        "✅ Exportar datos",
        "❌ NO puede eliminar productos",
        "❌ NO puede gestionar usuarios",
        "❌ NO puede ver logs del sistema"
    ]
    for perm in vendedor_perms:
        story.append(Paragraph(f"• {perm}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.15*inch))
    
    # Auditor
    story.append(Paragraph("<b>AUDITOR</b> - Solo Lectura 👁️", styles['Subseccion']))
    auditor_perms = [
        "✅ Ver productos e inventario",
        "✅ Ver historial de ventas",
        "✅ Ver dashboard y reportes",
        "✅ Ver logs del sistema (auditoría)",
        "✅ Exportar reportes",
        "❌ NO puede crear, editar ni eliminar nada",
        "❌ NO puede registrar ventas",
        "❌ NO puede gestionar usuarios"
    ]
    for perm in auditor_perms:
        story.append(Paragraph(f"• {perm}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Funciones de gestión
    story.append(Paragraph("⚙️ Funciones de Gestión de Usuarios", styles['Subseccion']))
    
    funciones = [
        "<b>Crear usuarios</b>: Asignar username, contraseña, nombre completo y rol",
        "<b>Activar/Desactivar</b>: Suspender acceso sin eliminar la cuenta",
        "<b>Eliminar usuarios</b>: Borrado permanente (excepto admin principal)",
        "<b>Cambiar contraseña propia</b>: Cada usuario puede actualizar su contraseña",
        "<b>Resetear contraseñas</b>: Administradores pueden cambiar contraseñas de otros"
    ]
    
    for funcion in funciones:
        story.append(Paragraph(f"• {funcion}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    return story


def seccion_seguridad(styles):
    """Sección: Sistema de Seguridad"""
    story = []
    
    story.append(Paragraph("🔐 7. SISTEMA DE SEGURIDAD", styles['Seccion']))
    
    texto = """
    La seguridad es una prioridad en el sistema. Todas las contraseñas están encriptadas, 
    los accesos están controlados por roles y cada acción importante queda registrada 
    en el sistema de logs para auditoría completa.
    """
    story.append(Paragraph(texto, styles['Justificado']))
    story.append(Spacer(1, 0.15*inch))
    
    # Autenticación
    story.append(Paragraph("🔑 Autenticación Segura", styles['Subseccion']))
    
    autenticacion = [
        "<b>Login con usuario y contraseña</b>: Validación obligatoria para acceder",
        "<b>Contraseñas encriptadas</b>: Hash con Werkzeug Security (bcrypt/scrypt)",
        "<b>Nunca se almacenan en texto plano</b>: Imposible recuperar contraseñas originales",
        "<b>Sesiones seguras</b>: Flask Session con secret_key única",
        "<b>Validación de usuarios activos</b>: Cuentas desactivadas no pueden entrar",
        "<b>Protección de rutas</b>: Decoradores @login_required en todas las páginas"
    ]
    
    for item in autenticacion:
        story.append(Paragraph(f"• {item}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Autorización
    story.append(Paragraph("🛡️ Autorización por Roles", styles['Subseccion']))
    
    autorizacion = [
        "<b>Control de acceso basado en roles</b>: Cada usuario solo ve lo que le corresponde",
        "<b>Decoradores @role_required</b>: Protección automática de funciones sensibles",
        "<b>Redirección automática</b>: Si no tienes permisos, vuelves al inicio",
        "<b>Validación en cada petición</b>: Se verifica el rol en cada acción",
        "<b>Sin acceso directo por URL</b>: No puedes acceder escribiendo la ruta directamente"
    ]
    
    for item in autorizacion:
        story.append(Paragraph(f"• {item}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Auditoría
    story.append(Paragraph("📜 Sistema de Logs (Auditoría)", styles['Subseccion']))
    
    auditoria = [
        "<b>Registro automático de acciones</b>: Login, logout, creación, edición, eliminación",
        "<b>Información completa</b>: Fecha, hora, usuario, acción y detalles",
        "<b>Trazabilidad total</b>: Saber quién hizo qué y cuándo",
        "<b>Historial permanente</b>: Los logs nunca se eliminan",
        "<b>Búsqueda y filtrado</b>: Encontrar eventos específicos rápidamente",
        "<b>Acceso controlado</b>: Solo Administradores y Auditores pueden ver logs"
    ]
    
    for item in auditoria:
        story.append(Paragraph(f"• {item}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Cuadro destacado
    texto_destacado = """
    <b>🔒 Seguridad multinivel:</b> El sistema implementa tres capas de seguridad: 
    autenticación (¿quién eres?), autorización (¿qué puedes hacer?) y auditoría (¿qué hiciste?). 
    Esto garantiza que solo personal autorizado acceda a funciones sensibles y que todo quede registrado.
    """
    story.append(Paragraph(texto_destacado, styles['Destacado']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    return story


def seccion_base_datos(styles):
    """Sección: Base de Datos MySQL"""
    story = []
    
    story.append(Paragraph("💾 8. BASE DE DATOS MYSQL", styles['Seccion']))
    
    texto = """
    El sistema utiliza MySQL como motor de base de datos, proporcionando persistencia permanente, 
    integridad referencial y alta velocidad en consultas. La estructura está optimizada para 
    un rendimiento óptimo incluso con miles de registros.
    """
    story.append(Paragraph(texto, styles['Justificado']))
    story.append(Spacer(1, 0.15*inch))
    
    # Tabla productos
    story.append(Paragraph("📦 Tabla: productos", styles['Subseccion']))
    
    data_productos = [
        ['Campo', 'Tipo', 'Descripción'],
        ['id', 'INT AUTO_INCREMENT', 'Identificador único (clave primaria)'],
        ['nombre', 'VARCHAR(255)', 'Nombre del producto'],
        ['categoria', 'VARCHAR(100)', 'Categoría del producto'],
        ['marca', 'VARCHAR(100)', 'Marca o fabricante'],
        ['stock', 'INT', 'Cantidad disponible'],
        ['precio_unitario', 'DECIMAL(10,3)', 'Precio por unidad'],
        ['descripcion', 'TEXT', 'Descripción detallada'],
        ['valor_total', 'DECIMAL(12,3)', 'Stock × precio (calculado)'],
        ['fecha_creacion', 'TIMESTAMP', 'Fecha de registro'],
        ['fecha_actualizacion', 'TIMESTAMP', 'Última modificación'],
    ]
    
    table_productos = Table(data_productos, colWidths=[1.5*inch, 1.5*inch, 3.5*inch])
    table_productos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f8ff')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2a5298')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(table_productos)
    story.append(Spacer(1, 0.2*inch))
    
    # Ventajas de MySQL
    story.append(Paragraph("✅ Ventajas de usar MySQL", styles['Subseccion']))
    
    ventajas = [
        "<b>Persistencia permanente</b>: Los datos nunca se pierden",
        "<b>Mayor velocidad</b>: Consultas optimizadas",
        "<b>Integridad referencial</b>: Relaciones garantizadas",
        "<b>Backups fáciles</b>: Exportar/importar completo",
        "<b>Escalabilidad</b>: Crece con el negocio",
        "<b>Acceso concurrente</b>: Múltiples usuarios simultáneos",
        "<b>Transacciones seguras</b>: Rollback automático"
    ]
    
    for ventaja in ventajas:
        story.append(Paragraph(f"• {ventaja}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    return story


# ==================== CONTINUARÁ EN PARTE 2B ====================

"""
📋 GENERADOR DE PDF PROFESIONAL - PARTE 2B (FINAL)
Sistema de Inventario H&D - Moto Repuestos

ESTA ES LA ÚLTIMA PARTE
Pega este código después de la Parte 2A
"""

# ==================== CONTINUACIÓN DE SECCIONES ====================

def seccion_casos_uso(styles):
    """Sección: Casos de Uso"""
    story = []
    
    story.append(Paragraph("🎯 9. CASOS DE USO REALES", styles['Seccion']))
    
    texto = """
    A continuación se presentan escenarios típicos de uso del sistema en el día a día del negocio, 
    mostrando cómo cada funcionalidad facilita las operaciones cotidianas.
    """
    story.append(Paragraph(texto, styles['Justificado']))
    story.append(Spacer(1, 0.15*inch))
    
    # Caso 1
    story.append(Paragraph("📦 Caso 1: Llegada de Mercancía Nueva", styles['Subseccion']))
    
    caso1_pasos = [
        "<b>1.</b> Vendedor o Admin inicia sesión en el sistema",
        "<b>2.</b> Hace clic en 'Nuevo Producto' desde el menú superior",
        "<b>3.</b> Completa el formulario: nombre, categoría, marca, stock inicial, precio",
        "<b>4.</b> El sistema calcula automáticamente el valor total (stock × precio)",
        "<b>5.</b> Presiona 'Guardar Producto'",
        "<b>6.</b> El producto queda registrado y disponible para venta inmediata",
        "<b>7.</b> Se registra un log con la acción y el usuario que la realizó"
    ]
    
    for paso in caso1_pasos:
        story.append(Paragraph(f"• {paso}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.15*inch))
    
    # Caso 2
    story.append(Paragraph("🛒 Caso 2: Venta de un Producto", styles['Subseccion']))
    
    caso2_pasos = [
        "<b>1.</b> Vendedor va a 'Registrar Venta'",
        "<b>2.</b> Busca el producto escribiendo su nombre (búsqueda en tiempo real)",
        "<b>3.</b> Selecciona el producto de la lista",
        "<b>4.</b> Ingresa la cantidad a vender",
        "<b>5.</b> El sistema valida que haya stock suficiente",
        "<b>6.</b> Calcula automáticamente el total de la venta",
        "<b>7.</b> Presiona 'Registrar Venta'",
        "<b>8.</b> El sistema descuenta el stock automáticamente",
        "<b>9.</b> La venta queda registrada en el historial con fecha, hora y vendedor",
        "<b>10.</b> Se genera un log de auditoría"
    ]
    
    for paso in caso2_pasos:
        story.append(Paragraph(f"• {paso}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.15*inch))
    
    # Caso 3
    story.append(Paragraph("📊 Caso 3: Revisión Ejecutiva del Negocio", styles['Subseccion']))
    
    caso3_pasos = [
        "<b>1.</b> Dueño (Admin) entra al Dashboard",
        "<b>2.</b> Revisa las métricas principales: productos, valor del inventario, ventas totales",
        "<b>3.</b> Analiza las gráficas de tendencias de ventas",
        "<b>4.</b> Identifica productos con stock bajo que necesitan reabastecimiento",
        "<b>5.</b> Va a 'Reportes' → 'Ventas por Período'",
        "<b>6.</b> Genera el reporte del mes actual",
        "<b>7.</b> Exporta el reporte a Excel para análisis externo o reuniones",
        "<b>8.</b> Toma decisiones basadas en datos reales y actualizados"
    ]
    
    for paso in caso3_pasos:
        story.append(Paragraph(f"• {paso}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.15*inch))
    
    # Caso 4
    story.append(Paragraph("🔍 Caso 4: Auditoría Contable", styles['Subseccion']))
    
    caso4_pasos = [
        "<b>1.</b> Contador (Auditor) inicia sesión",
        "<b>2.</b> Accede al historial de ventas completo",
        "<b>3.</b> Filtra ventas por fecha o producto específico",
        "<b>4.</b> Revisa los logs del sistema para verificar acciones realizadas",
        "<b>5.</b> Genera reporte de inventario total",
        "<b>6.</b> Exporta a PDF para documentación oficial",
        "<b>7.</b> Presenta el reporte en la auditoría contable"
    ]
    
    for paso in caso4_pasos:
        story.append(Paragraph(f"• {paso}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    return story


def seccion_interfaz(styles):
    """Sección: Interfaz Visual"""
    story = []
    
    story.append(Paragraph("🎨 10. INTERFAZ VISUAL Y TEMAS", styles['Seccion']))
    
    texto = """
    El sistema ofrece una experiencia visual moderna y profesional con tres temas personalizables, 
    adaptándose a diferentes preferencias y ambientes de trabajo.
    """
    story.append(Paragraph(texto, styles['Justificado']))
    story.append(Spacer(1, 0.15*inch))
    
    # Tres temas
    story.append(Paragraph("🌈 3 Temas Disponibles", styles['Subseccion']))
    
    temas = [
        "<b>🌟 Premium</b>: Diseño colorido con efectos glassmorphism, degradados vibrantes y animaciones suaves",
        "<b>☀️ Trabajo</b>: Modo claro optimizado para ambientes luminosos, colores profesionales y alta legibilidad",
        "<b>🌙 Oscuro</b>: Modo nocturno para reducir fatiga visual, colores suaves y bajo contraste"
    ]
    
    for tema in temas:
        story.append(Paragraph(f"• {tema}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Características de diseño
    story.append(Paragraph("✨ Características de Diseño", styles['Subseccion']))
    
    caracteristicas = [
        "<b>Diseño responsive</b>: Se adapta perfectamente a computadoras, tablets y móviles",
        "<b>Efectos 3D y animaciones</b>: Transiciones suaves y efectos visuales modernos",
        "<b>Iconos Bootstrap Icons</b>: Biblioteca completa de iconos profesionales",
        "<b>Colores corporativos</b>: Azul, dorado y verde para identidad de marca",
        "<b>Tablas con efectos hover</b>: Resaltado al pasar el mouse para mejor UX",
        "<b>Botones con elevación</b>: Sensación táctil y feedback visual",
        "<b>Alertas destacadas</b>: Productos con bajo stock en rojo brillante",
        "<b>Selector de tema visible</b>: Cambio instantáneo con un clic"
    ]
    
    for caract in caracteristicas:
        story.append(Paragraph(f"• {caract}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Navegación
    story.append(Paragraph("🧭 Navegación Intuitiva", styles['Subseccion']))
    
    navegacion = [
        "<b>Menú superior horizontal</b>: Acceso rápido a todas las funciones principales",
        "<b>Logo corporativo animado</b>: Identidad visual con efecto flotante",
        "<b>Usuario logueado visible</b>: Muestra nombre completo y rol actual",
        "<b>Botón de cerrar sesión</b>: Siempre accesible desde cualquier página"
    ]
    
    for nav in navegacion:
        story.append(Paragraph(f"• {nav}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    return story


def seccion_ventajas(styles):
    """Sección: Ventajas del Sistema"""
    story = []
    
    story.append(Paragraph("🚀 11. VENTAJAS DEL SISTEMA", styles['Seccion']))
    
    # Para el negocio
    story.append(Paragraph("💼 Para el Negocio", styles['Subseccion']))
    
    ventajas_negocio = [
        "<b>📊 Control total del inventario</b>: Visibilidad completa en tiempo real de todos los productos",
        "<b>💰 Seguimiento preciso de ventas</b>: Registro detallado de cada transacción con trazabilidad",
        "<b>⚠️ Alertas automáticas</b>: Notificaciones de productos con stock bajo o agotado",
        "<b>📈 Análisis visual de rendimiento</b>: Gráficas y métricas para decisiones informadas",
        "<b>📑 Reportes profesionales</b>: Documentación lista para presentaciones y auditorías",
        "<b>🔐 Seguridad y trazabilidad</b>: Registro de todas las acciones con usuarios responsables",
        "<b>💾 Datos permanentes</b>: MySQL garantiza que nunca se pierda información"
    ]
    
    for ventaja in ventajas_negocio:
        story.append(Paragraph(f"• {ventaja}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Para el personal
    story.append(Paragraph("👥 Para el Personal", styles['Subseccion']))
    
    ventajas_personal = [
        "<b>👥 Accesos diferenciados</b>: Cada usuario tiene permisos según su rol y responsabilidad",
        "<b>🎯 Interfaz intuitiva</b>: Fácil de aprender y usar, sin curva de aprendizaje complicada",
        "<b>⚡ Registro rápido</b>: Ventas y productos se registran en segundos",
        "<b>🔍 Búsqueda eficiente</b>: Encuentra productos al instante escribiendo su nombre",
        "<b>📱 Acceso desde cualquier dispositivo</b>: Computadora, tablet o móvil"
    ]
    
    for ventaja in ventajas_personal:
        story.append(Paragraph(f"• {ventaja}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Técnicas
    story.append(Paragraph("⚙️ Ventajas Técnicas", styles['Subseccion']))
    
    ventajas_tecnicas = [
        "<b>💾 Base de datos robusta</b>: MySQL profesional para miles de registros",
        "<b>🔒 Contraseñas encriptadas</b>: Seguridad con hash Werkzeug Security",
        "<b>📜 Auditoría completa</b>: Logs de todas las acciones importantes",
        "<b>📤 Exportaciones profesionales</b>: Excel y PDF con formato corporativo",
        "<b>🎨 Diseño moderno</b>: Bootstrap 5 con efectos visuales avanzados",
        "<b>🌐 Multiplataforma</b>: Funciona en Windows, macOS y Linux"
    ]
    
    for ventaja in ventajas_tecnicas:
        story.append(Paragraph(f"• {ventaja}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    return story


def seccion_metricas(styles):
    """Sección: Métricas y Analítica"""
    story = []
    
    story.append(Paragraph("📊 12. MÉTRICAS Y ANALÍTICA", styles['Seccion']))
    
    texto = """
    El Dashboard del sistema proporciona análisis completo y métricas actualizadas en tiempo real 
    para la toma de decisiones estratégicas basadas en datos reales.
    """
    story.append(Paragraph(texto, styles['Justificado']))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("📈 Métricas Disponibles", styles['Subseccion']))
    
    metricas = [
        "<b>Total de productos diferentes</b>: Número de referencias en inventario",
        "<b>Valor monetario total</b>: Suma del valor de todo el stock disponible",
        "<b>Productos con stock crítico</b>: Número de artículos con menos de 5 unidades",
        "<b>Total de ventas realizadas</b>: Cantidad histórica de transacciones",
        "<b>Ingresos totales acumulados</b>: Suma de todos los montos vendidos",
        "<b>Tendencia de ventas</b>: Gráfica de los últimos 7 días",
        "<b>Productos con mejor rotación</b>: Top 5 más vendidos con unidades e ingresos",
        "<b>Categorías con mayor demanda</b>: Análisis de ventas por tipo de producto",
        "<b>Distribución de ingresos</b>: Proporción por categoría con porcentajes"
    ]
    
    for metrica in metricas:
        story.append(Paragraph(f"• {metrica}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    return story


def seccion_expansiones(styles):
    """Sección: Posibles Expansiones Futuras"""
    story = []
    
    story.append(Paragraph("🔮 13. POSIBLES EXPANSIONES FUTURAS", styles['Seccion']))
    
    texto = """
    El sistema está diseñado con arquitectura escalable, permitiendo agregar nuevas funcionalidades 
    según las necesidades del negocio crezcan. Algunas posibles mejoras incluyen:
    """
    story.append(Paragraph(texto, styles['Justificado']))
    story.append(Spacer(1, 0.15*inch))
    
    expansiones = [
        "<b>📧 Notificaciones por email</b>: Alertas automáticas de stock bajo o ventas importantes",
        "<b>📷 Código de barras</b>: Escaneo rápido de productos con lector de código de barras",
        "<b>📦 Gestión de proveedores</b>: Registro de proveedores con historial de compras",
        "<b>👥 Registro de clientes</b>: Base de datos de clientes frecuentes con historial",
        "<b>📝 Sistema de cotizaciones</b>: Generar presupuestos antes de confirmar ventas",
        "<b>🔄 Devoluciones de productos</b>: Gestión de devoluciones con reingreso al inventario",
        "<b>📊 Reportes más avanzados</b>: Análisis de rentabilidad, rotación y proyecciones",
        "<b>📱 App móvil dedicada</b>: Aplicación nativa para iOS y Android",
        "<b>☁️ Sincronización en la nube</b>: Backup automático y acceso remoto",
        "<b>📈 Análisis predictivo</b>: Predicción de demanda con inteligencia artificial",
        "<b>🏪 Sucursales múltiples</b>: Gestión de inventario en varias ubicaciones",
        "<b>🎁 Programa de puntos</b>: Sistema de fidelización de clientes"
    ]
    
    for expansion in expansiones:
        story.append(Paragraph(f"• {expansion}", styles['Viñeta']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    return story


def seccion_conclusion(styles):
    """Sección: Conclusión"""
    story = []
    
    story.append(Paragraph("✅ CONCLUSIÓN", styles['Seccion']))
    
    texto_conclusion = """
    El <b>Sistema de Inventario H&D</b> representa una solución integral, moderna y profesional 
    para la gestión completa de un negocio de repuestos de motocicletas. Con su arquitectura 
    robusta basada en <b>MySQL</b>, su diseño visual atractivo con <b>Bootstrap 5</b> y su 
    sistema de seguridad multinivel, ofrece todas las herramientas necesarias para llevar un 
    control preciso y eficiente del inventario, las ventas y el personal.
    <br/><br/>
    La implementación de <b>tres roles diferenciados</b> (Administrador, Vendedor y Auditor) 
    garantiza que cada persona en el negocio tenga acceso exactamente a las funciones que necesita, 
    mientras que el <b>sistema de logs</b> proporciona trazabilidad completa de todas las acciones 
    importantes.
    <br/><br/>
    Las funcionalidades de <b>reportes avanzados</b>, <b>exportaciones profesionales</b> a Excel 
    y PDF, y el <b>Dashboard ejecutivo</b> con gráficas interactivas facilitan la toma de 
    decisiones estratégicas basadas en datos reales y actualizados en tiempo real.
    <br/><br/>
    Con su <b>interfaz intuitiva</b>, su <b>diseño responsive</b> que funciona en cualquier 
    dispositivo, y sus <b>tres temas visuales</b> personalizables, el sistema no solo es 
    funcional sino también agradable de usar.
    <br/><br/>
    En resumen, el Sistema de Inventario H&D optimiza las operaciones diarias del negocio, 
    reduce errores humanos mediante cálculos automáticos, proporciona seguridad robusta con 
    contraseñas encriptadas, y ofrece la información necesaria para hacer crecer el negocio 
    de manera sostenible e informada.
    """
    
    story.append(Paragraph(texto_conclusion, styles['Justificado']))
    story.append(Spacer(1, 0.3*inch))
    
    # Cuadro final destacado
    texto_final = """
    <b>💡 Sistema diseñado para crecer contigo:</b> El Sistema de Inventario H&D no es solo 
    una herramienta para el presente, sino una plataforma escalable que puede evolucionar junto 
    con tu negocio, agregando nuevas funcionalidades conforme las necesites.
    """
    story.append(Paragraph(texto_final, styles['Destacado']))
    
    story.append(Spacer(1, 0.5*inch))
    
    # Información de contacto (opcional)
    info_contacto = """
    <para align=center>
    <font size=12 color='#1e3c72'><b>Sistema de Inventario H&D v2.0</b></font><br/>
    <font size=10 color='#666666'>Moto Repuestos Profesional</font><br/><br/>
    <font size=9 color='#999999'>Documentación generada automáticamente</font><br/>
    <font size=9 color='#999999'>© 2025 - Todos los derechos reservados</font>
    </para>
    """
    story.append(Paragraph(info_contacto, styles['Normal']))
    
    return story


# ==================== FUNCIÓN PRINCIPAL ====================
def generar_pdf():
    """Función principal que genera el PDF completo"""
    print("=" * 60)
    print("📄 GENERANDO PDF PROFESIONAL")
    print("   Sistema de Inventario H&D - Moto Repuestos")
    print("=" * 60)
    print()
    
    # Crear estilos
    print("🎨 Creando estilos personalizados...")
    styles = crear_estilos()
    
    # Crear documento con canvas personalizado
    print("📋 Inicializando documento...")
    doc = SimpleDocTemplate(
        PDF_FILENAME,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=60,
        bottomMargin=50,
        title="Sistema de Inventario H&D - Documentación Completa",
        author=AUTHOR
    )
    
    # Construir contenido
    story = []
    
    print("📄 Generando portada...")
    story.extend(crear_portada(styles))
    
    print("📝 Generando sección: Descripción general...")
    story.extend(seccion_descripcion(styles))
    
    print("🏢 Generando sección: Información técnica...")
    story.extend(seccion_informacion_tecnica(styles))
    
    print("📦 Generando sección: Gestión de productos...")
    story.extend(seccion_gestion_productos(styles))
    
    print("🛒 Generando sección: Gestión de ventas...")
    story.extend(seccion_gestion_ventas(styles))
    
    print("📊 Generando sección: Dashboard ejecutivo...")
    story.extend(seccion_dashboard(styles))
    
    print("📑 Generando sección: Reportes avanzados...")
    story.extend(seccion_reportes(styles))
    
    print("📤 Generando sección: Exportaciones...")
    story.extend(seccion_exportaciones(styles))
    
    print("👥 Generando sección: Usuarios y roles...")
    story.extend(seccion_usuarios_roles(styles))
    
    print("🔐 Generando sección: Seguridad...")
    story.extend(seccion_seguridad(styles))
    
    print("💾 Generando sección: Base de datos...")
    story.extend(seccion_base_datos(styles))
    
    print("🎯 Generando sección: Casos de uso...")
    story.extend(seccion_casos_uso(styles))
    
    print("🎨 Generando sección: Interfaz visual...")
    story.extend(seccion_interfaz(styles))
    
    print("🚀 Generando sección: Ventajas del sistema...")
    story.extend(seccion_ventajas(styles))
    
    print("📊 Generando sección: Métricas y analítica...")
    story.extend(seccion_metricas(styles))
    
    print("🔮 Generando sección: Expansiones futuras...")
    story.extend(seccion_expansiones(styles))
    
    print("✅ Generando sección: Conclusión...")
    story.extend(seccion_conclusion(styles))
    
    # Generar PDF con encabezado y pie de página
    print("🔨 Compilando PDF con encabezados y paginación...")
    doc.build(story, canvasmaker=PDFWithHeader)
    
    print()
    print("=" * 60)
    print("✅ ¡PDF GENERADO EXITOSAMENTE!")
    print(f"📁 Archivo: {PDF_FILENAME}")
    print("=" * 60)
    print()
    print("💡 El PDF incluye:")
    print("   ✓ Portada profesional")
    print("   ✓ 13 secciones detalladas")
    print("   ✓ Casos de uso reales")
    print("   ✓ Tablas informativas")
    print("   ✓ Diseño corporativo")
    print("   ✓ Encabezados y pies de página")
    print("   ✓ Numeración automática")
    print()
    print("🎉 ¡Listo para entregar al cliente!")
    print()


# ==================== EJECUTAR ====================
if __name__ == "__main__":
    try:
        generar_pdf()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()