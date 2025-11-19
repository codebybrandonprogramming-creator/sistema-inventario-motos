import pymysql
from werkzeug.security import generate_password_hash

print("🔧 Actualizando datos del administrador...")

try:
    # Conectar a MySQL
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='inventario_repuestos'
    )
    
    cursor = connection.cursor()
    
    # Solicitar nueva contraseña
    print("\n📝 Ingresa los nuevos datos:")
    nueva_password = input("Nueva contraseña: ")
    
    # Generar hash
    nuevo_hash = generate_password_hash(nueva_password)
    
    # Actualizar datos
    query = """
        UPDATE usuarios 
        SET username = %s, 
            nombre_completo = %s, 
            password = %s,
            fecha_actualizacion = NOW()
        WHERE id = 1
    """
    
    cursor.execute(query, ('Brandon', 'Jhon Brandon', nuevo_hash))
    connection.commit()
    
    print("\n✅ Datos actualizados exitosamente:")
    print("📌 Usuario: Brandon")
    print("📌 Nombre completo: Jhon Brandon")
    print(f"📌 Contraseña: {nueva_password}")
    
    cursor.close()
    connection.close()

except Exception as e:
    print(f"❌ Error: {e}")