import json
import os
import psycopg2

class ConexionPostgres:
    
    def __init__(self):
        # Lectura blindada del archivo .env ignorando bytes corruptos
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            with open(dotenv_path, 'r', encoding='latin-1', errors='ignore') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        parts = line.strip().split('=', 1)
                        if len(parts) == 2:
                            key, val = parts
                            os.environ[key.strip()] = val.strip().strip('"\'')

        self.__SERVER = os.environ.get("PG_SERVER")
        self.__PORT = os.environ.get("PG_PORT")
        self.__DATABASE = os.environ.get("PG_DATABASE")
        self.__USER = os.environ.get("PG_USER")
        self.__PASSWORD = os.environ.get("PG_PASSWORD")
        self.__CNX = None
        self.__CURSOR = None

    def crear_conexion(self):
        try:
            self.__CNX = psycopg2.connect(
                host=self.__SERVER,
                port=self.__PORT,
                database=self.__DATABASE,
                user=self.__USER,
                password=self.__PASSWORD,
                client_encoding='utf8'
            )
            self.__CURSOR = self.__CNX.cursor()
            print(f"Conectado al servidor PostgreSQL: {self.__SERVER}")
            return self.__CNX
        except psycopg2.Error as e:
            print(f"Error al conectarse al servidor {self.__SERVER} de Base de Datos")
            print(e)
            self.__CNX = None
            self.__CURSOR = None
            return None

    def ejecutar(self, sql, parametros=None):
        try:
            if self.__CNX is None or self.__CNX.closed != 0:
                if self.crear_conexion() is None:
                    return json.dumps(
                        {
                            "estado": False,
                            "mensaje": "No fue posible establecer la conexión"
                        },
                        ensure_ascii=False
                    )

            if parametros:
                self.__CURSOR.execute(sql, parametros)
            else:
                self.__CURSOR.execute(sql)

            tipo = sql.strip().split()[0].upper()

            if tipo == "SELECT":
                columnas = [columna[0] for columna in self.__CURSOR.description]
                registros = self.__CURSOR.fetchall()
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

            elif tipo == "INSERT":
                filas = self.__CURSOR.rowcount
                self.__CNX.commit()
                return json.dumps(
                    {
                        "estado": True,
                        "tipo": "INSERT",
                        "mensaje": "Registro insertado correctamente",
                        "filas_afectadas": filas
                    },
                    ensure_ascii=False
                )

            elif tipo == "UPDATE":
                filas = self.__CURSOR.rowcount
                self.__CNX.commit()
                return json.dumps(
                    {
                        "estado": True,
                        "tipo": "UPDATE",
                        "mensaje": "Registro actualizado correctamente",
                        "filas_afectadas": filas
                    },
                    ensure_ascii=False
                )

            elif tipo == "DELETE":
                filas = self.__CURSOR.rowcount
                self.__CNX.commit()
                return json.dumps(
                    {
                        "estado": True,
                        "tipo": "DELETE",
                        "mensaje": "Registro eliminado correctamente",
                        "filas_afectadas": filas
                    },
                    ensure_ascii=False
                )

            else:
                filas = self.__CURSOR.rowcount
                self.__CNX.commit()
                return json.dumps(
                    {
                        "estado": True,
                        "tipo": tipo,
                        "mensaje": "Consulta ejecutada correctamente",
                        "filas_afectadas": filas
                    },
                    ensure_ascii=False
                )

        except psycopg2.IntegrityError as e:
            if self.__CNX:
                self.__CNX.rollback()
            return json.dumps({"estado": False, "tipo": "IntegrityError", "mensaje": "Violación de integridad", "error": str(e)}, ensure_ascii=False)
        except psycopg2.ProgrammingError as e:
            if self.__CNX:
                self.__CNX.rollback()
            return json.dumps({"estado": False, "tipo": "ProgrammingError", "mensaje": "Error SQL", "error": str(e)}, ensure_ascii=False)
        except psycopg2.Error as e:
            if self.__CNX:
                self.__CNX.rollback()
            return json.dumps({"estado": False, "tipo": "DatabaseError", "mensaje": "Error en BD", "error": str(e)}, ensure_ascii=False)
        except Exception as e:
            if self.__CNX:
                self.__CNX.rollback()
            return json.dumps({"estado": False, "tipo": "Error", "mensaje": "Error inesperado", "error": str(e)}, ensure_ascii=False)

    def cerrar_conexion(self):
        try:
            if self.__CURSOR:
                self.__CURSOR.close()
                self.__CURSOR = None
            if self.__CNX:
                self.__CNX.close()
                self.__CNX = None
            print(f"Se ha cerrado la conexion al servidor PostgreSQL: {self.__SERVER}")
            return True
        except psycopg2.Error as e:
            print("Error al desconectarse del servidor de base de datos")
            print(e)
            return False

if __name__ == '__main__':
    cnn = ConexionPostgres()
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