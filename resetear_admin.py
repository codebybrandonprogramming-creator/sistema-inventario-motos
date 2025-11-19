import pymysql
from werkzeug.security import generate_password_hash

print("🔧 Iniciando reset de contraseña del admin...")

try:
    # Conectar a MySQL
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='inventario_repuestos'
    )
    
    cursor = connection.cursor()
    
    # Generar nuevo hash para "admin123"
    nuevo_hash = generate_password_hash('admin123')
    
    print(f"✅ Hash generado: {nuevo_hash[:50]}...")
    
    # Actualizar la contraseña del admin
    query = "UPDATE usuarios SET password = %s WHERE username = 'admin'"
    cursor.execute(query, (nuevo_hash,))
    connection.commit()
    
    print("✅ Contraseña del admin reseteada exitosamente")
    print("📌 Usuario: admin")
    print("📌 Contraseña: admin123")
    
    cursor.close()
    connection.close()

except Exception as e:
    print(f"❌ Error: {e}")