# 🏍️ Sistema de Inventario H&D — Moto Repuestos

Sistema web para la gestión de inventario de repuestos de motocicletas.  
Desarrollado en **Python Flask**, con base de datos **MySQL local**, e interfaz en **Bootstrap 5**.

---

## 🚀 Tecnologías utilizadas
- Python 3
- Flask
- MySQL Local (XAMPP / WAMP / MySQL Server)
- PyMySQL
- Bootstrap 5
- Reportlab (PDF)
- Openpyxl (Excel)
- Werkzeug

---

## 🗄️ Base de datos (MySQL Local)

1. Abre **phpMyAdmin** o tu servidor MySQL local.
2. Crea una base de datos llamada:

inventario_repuestos

3. Importa el archivo SQL del proyecto (si existe) o crea las tablas necesarias manualmente.

4. Configura tu conexión en `app.py`:

```python
db = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="inventario_repuestos",
    cursorclass=pymysql.cursors.DictCursor
)

Si tienes contraseña en MySQL, modifícala en el campo password.


---

🔧 Instalación del proyecto

1. Instalar dependencias:



pip install flask pymysql werkzeug openpyxl reportlab

2. Ejecutar la aplicación:



python app.py

3. Abrir en navegador:



http://127.0.0.1:5000



---

📂 Estructura del proyecto

/inventario
│── app.py
│── static/
│── templates/
│── reports/
│── uploads/
│── database.sql (opcional)
│── requirements.txt
│── README.md


---

📦 Archivo requirements.txt

Flask==3.0.0
PyMySQL==1.1.0
Werkzeug==3.0.1
openpyxl==3.1.2
reportlab==4.0.7


---

📝 Funciones principales del sistema

🛒 Registro y edición de productos

📉 Alerta automática de bajo stock

🖨️ Exportación a PDF y Excel

📦 Entrada y salida de inventario

🧮 Totalización en tiempo real

🔎 Buscador inteligente

👤 Sistema de login simple

📊 Panel general del inventario



---

📈 Próximas mejoras (roadmap)

Roles de usuario (admin/empleado)

Historial completo de movimientos

Respaldo automático de BD

Panel de estadísticas



---

👨‍🔧 Autor

Proyecto desarrollado para H&D Moto Repuestos.
Para soporte o mejoras, puedes contactarme.
