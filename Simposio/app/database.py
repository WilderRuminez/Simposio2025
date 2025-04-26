import os
import pyodbc

class Database:
    def __init__(self):
        self.server = os.getenv('DB_SERVER', r'(localdb)\Lenovo')
        self.database = os.getenv('DB_NAME', 'login')
        self.username = os.getenv('DB_USER', 'sa')
        self.password = os.getenv('DB_PASSWORD', 'GpiSistemas')
        self.driver = 'ODBC Driver 18 for SQL Server'
        self.connection = None

    def connect(self):
        try:
            self.connection = pyodbc.connect(
                f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
            )
            print("Conexión exitosa a SQL Server")
            return self.connection
        except pyodbc.Error as e:
            print("Error al conectar con SQL Server:", e)
            return None

    def close(self):
        if self.connection:
            try:
                self.connection.close()
                print("Conexión cerrada con SQL Server")
            except pyodbc.Error as e:
                print("Error al cerrar la conexión:", e)