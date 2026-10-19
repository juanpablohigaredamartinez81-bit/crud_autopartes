import pyodbc
import json
import os

class ConexionSqlServer():
    def __init__(self):
        # Carga manual segura del archivo .env para evitar conflictos de codificación
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            with open(dotenv_path, 'r', encoding='latin-1') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, val = line.strip().split('=', 1)
                        os.environ[key.strip()] = val.strip().strip('"\'')

        self.SERVER = os.environ.get("SERVER")
        self.DATABASE_NAME = os.environ.get("DATABASE_NAME")
        self.USER = os.environ.get("USER")
        self.PASSWORD = os.environ.get("PASSWORD")

        self.CNX = None 
        self.CURSOR = None 

    def crear_conexion(self):
        try:
            cadena_conexion = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.SERVER};"
                f"DATABASE={self.DATABASE_NAME};"
                f"UID={self.USER};"
                f"PWD={self.PASSWORD};"
                "TrustServerCertificate=yes;"
            )

            self.CNX = pyodbc.connect(cadena_conexion)
            self.CURSOR = self.CNX.cursor()
            print(f"Conectado al servidor SQL Server: {self.SERVER}")
            return self.CNX
        except pyodbc.Error as e:
            print(f"Error al conectarse al servidor {self.SERVER} de Base de Datos")
            print(e)
            self.CNX = None 
            self.CURSOR = None 
            return None

    def ejecutar(self, sql, parametros=None):
        try:
            if self.CNX is None:
                if self.crear_conexion() is None:
                    return json.dumps(
                        {
                            "estado": False,
                            "mensaje": "No fue posible establecer la conexión"
                        },
                        ensure_ascii=False
                    )
 
            if parametros:
                self.CURSOR.execute(sql, parametros)
            else:
                self.CURSOR.execute(sql)
 
            tipo = sql.strip().split()[0].upper()
            
            if tipo == "SELECT":
                columnas = [columna[0] for columna in self.CURSOR.description]
                registros = self.CURSOR.fetchall()
                resultado = []
                for registro in registros:
                    fila = {}
                    for i, valor in enumerate(registro):
                        fila[columnas[i]] = valor
                    resultado.append(fila)
 
                return json.dumps(
                    {
                        "estado": True,
                        "tipo": "SELECT",
                        "registros": resultado
                    },
                    default=str,
                    ensure_ascii=False 
                )
                
            elif tipo in ("INSERT", "UPDATE", "DELETE"):
                filas = self.CURSOR.rowcount 
                self.CNX.commit() 
                return json.dumps(
                    {
                        "estado": True,
                        "tipo": tipo,
                        "mensaje": "Operación realizada correctamente",
                        "filas_afectadas": filas
                    },
                    ensure_ascii=False
                )
                
            else:
                filas = self.CURSOR.rowcount
                self.CNX.commit()
                return json.dumps(
                    {
                        "estado": True,
                        "tipo": tipo,
                        "mensaje": "Consulta ejecutada correctamente",
                        "filas_afectadas": filas
                    },
                    ensure_ascii=False
                )
                
        except Exception as e:
            if self.CNX:
                self.CNX.rollback()
            return json.dumps({"estado": False, "tipo": "Error", "mensaje": "Error en la base de datos", "error": str(e)}, ensure_ascii=False)   

    def cerrar_conexion(self):
        try:
            if self.CURSOR:
                self.CURSOR.close()
                self.CURSOR = None

            if self.CNX:
                self.CNX.close()
                self.CNX = None 
            print(f"Conexión cerrada con el servidor SQL Server")
            return True
        except Exception as e:
            print(e)
            return False

if __name__ == '__main__':
    cnn = ConexionSqlServer()
    cnn.crear_conexion()

    # CONSULTA SELECT
    sql_select = "SELECT ID_Marca, Nombre_Marca, Pais_Origen FROM Marca LIMIT 5;"
    res_select = cnn.ejecutar(sql_select)
    print("--- RESULTADO SELECT ---")
    print(res_select)

    # CONSULTA INSERT
    sql_insert = "INSERT INTO Marca (Nombre_Marca, Pais_Origen) VALUES (%s, %s);"
    params_insert = ("Milwaukee", "EUA")
    res_insert = cnn.ejecutar(sql_insert, params_insert)
    print("\n--- RESULTADO INSERT ---")
    print(res_insert)

    # CONSULTA UPDATE
    sql_update = "UPDATE Marca SET Pais_Origen = %s WHERE Nombre_Marca = %s;"
    params_update = ("Estados Unidos", "Milwaukee")
    res_update = cnn.ejecutar(sql_update, params_update)
    print("\n--- RESULTADO UPDATE ---")
    print(res_update)

    # CONSULTA DELETE
    sql_delete = "DELETE FROM Marca WHERE Nombre_Marca = %s;"
    params_delete = ("Milwaukee",)
    res_delete = cnn.ejecutar(sql_delete, params_delete)
    print("\n--- RESULTADO DELETE ---")
    print(res_delete)

    cnn.cerrar_conexion()