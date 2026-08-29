import mysql.connector
from mysql.connector import Error

class ConexionBaseDatos:
    _instancia = None

    def __init__(self):
        if ConexionBaseDatos._instancia is not None:
            raise Exception("Esta clase es un Singleton. Usa el método obtener_instancia().")
        else:
            self.conexion = None
            try:
                self.conexion = mysql.connector.connect(
                    host="localhost",
                    database="mantenimiento_predictivo",
                    user="root",
                    password="admin" 
                )
                if self.conexion.is_connected():
                    print("¡Conexión Singleton establecida con éxito!")
            except Error as e:
                print(f"Error al conectar a MySQL: {e}")
                self.conexion = None

    @staticmethod
    def obtener_instancia():
        if ConexionBaseDatos._instancia is None:
            ConexionBaseDatos._instancia = ConexionBaseDatos()
        return ConexionBaseDatos._instancia

    def obtener_conexion(self):
        # Verificamos si la conexión sigue viva o se cerró, y si es así la reconectamos
        try:
            if self.conexion is None or not self.conexion.is_connected():
                self.conexion = mysql.connector.connect(
                    host="localhost",
                    database="mantenimiento_predictivo",
                    user="root",
                    password="admin"
                )
        except Error as e:
            print(f"Error al reconectar: {e}")
            self.conexion = None
        return self.conexion
