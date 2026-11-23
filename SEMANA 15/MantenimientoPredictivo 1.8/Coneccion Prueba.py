import mysql.connector

try:
    conexion = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="admin",
        database="mantenimiento_predictivo"
    )

    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM usuarios")

    usuarios = cursor.fetchall()

    print("✅ Conexión exitosa")
    print("\nUsuarios registrados:")

    for usuario in usuarios:
        print(usuario)

except mysql.connector.Error as error:
    print("❌ Error:", error)

finally:
    if 'conexion' in locals() and conexion.is_connected():
        cursor.close()
        conexion.close()