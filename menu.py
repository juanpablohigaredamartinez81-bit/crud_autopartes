import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QFormLayout, QWidget, QMessageBox, QLabel, 
                             QStackedWidget, QFrame, QHeaderView, QDialog, 
                             QProgressBar, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt

# Importamos las conexiones de tu proyecto de autopartes
from refpg import ConexionPostgres
from refsql import ConexionSqlServer

# =========================================================================
# HOJA DE ESTILOS: NUEVO DISEÑO "INDUSTRIAL NEON / RACING HUD"
# =========================================================================
ESTILO_INDUSTRIAL_HUD = """
QMainWindow {
    background-color: #050507;
}
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #E2E8F0;
}
/* Cabecera y Contenedores */
#HeaderPrincipal {
    background-color: #0A0A0F;
    border-bottom: 2px solid #FF6B00;
}
#TituloLogo {
    color: #FF6B00;
    font-size: 20px;
    font-weight: 900;
    letter-spacing: 1.5px;
}
#EstadoBD {
    color: #00FFCC;
    font-size: 13px;
    font-weight: bold;
}
/* Tarjetas de Navegación del Dashboard Principal */
#CardMenu {
    background-color: #0E0E14;
    border: 1px solid #1F1F2E;
    border-radius: 12px;
}
#CardMenu:hover {
    background-color: #161622;
    border: 1px solid #FF6B00;
}
#LabelCardTitulo {
    color: #FFFFFF;
    font-size: 16px;
    font-weight: bold;
}
#LabelCardDesc {
    color: #8A8A9E;
    font-size: 12px;
}
/* Botones Generales */
QPushButton {
    background-color: #FF6B00;
    border: none;
    color: #FFFFFF;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #E05D00;
}
QPushButton#BtnRegresar {
    background-color: #1F1F2E;
    color: #A0A0B2;
    border: 1px solid #33334D;
}
QPushButton#BtnRegresar:hover {
    background-color: #2E2E42;
    color: #FFFFFF;
}
QPushButton#BtnPeligro {
    background-color: #FF3366;
}
QPushButton#BtnPeligro:hover {
    background-color: #E02855;
}
/* Formularios e Inputs */
QLineEdit {
    background-color: #0E0E14;
    border: 1px solid #222233;
    padding: 10px;
    color: #FFFFFF;
    border-radius: 6px;
    font-size: 13px;
}
QLineEdit:focus {
    border: 1px solid #00FFCC;
    background-color: #050507;
}
QFrame#FrameFormulario {
    background-color: #0A0A0F;
    border: 1px solid #1F1F2E;
    border-radius: 10px;
}
/* Tablas Estilo Terminal */
QTableWidget {
    background-color: #0A0A0F;
    border: 1px solid #1F1F2E;
    color: #E2E8F0;
    gridline-color: #161622;
    selection-background-color: #FF6B00;
    selection-color: #FFFFFF;
    border-radius: 8px;
}
QHeaderView::section {
    background-color: #12121C;
    color: #FF6B00;
    border: none;
    border-right: 1px solid #1F1F2E;
    border-bottom: 1px solid #1F1F2E;
    padding: 10px;
    font-weight: bold;
}
QProgressBar {
    border: 1px solid #1F1F2E;
    border-radius: 4px;
    text-align: center;
    color: white;
    font-weight: bold;
    background-color: #050507;
}
QProgressBar::chunk {
    background-color: #00FFCC;
    border-radius: 3px;
}
"""

# ==========================================
# 1. PANTALLA INICIAL DE SELECCIÓN DE BD
# ==========================================
class SeleccionBD(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conexión HUD - AutoPartes del Valle")
        self.resize(400, 220)
        self.db = None 
        
        self.setStyleSheet("""
            QDialog { background-color: #050507; }
            QLabel { font-size: 15px; font-weight: bold; color: #FFFFFF; }
            QPushButton { background-color: #FF6B00; color: white; padding: 12px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #E05D00; }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(15)

        label = QLabel("⚡ SELECCIONE NÚCLEO DE DATOS:")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_pg = QPushButton("Conectar a PostgreSQL")
        self.btn_sql = QPushButton("Conectar a SQL Server")
        
        layout.addWidget(label)
        layout.addWidget(self.btn_pg)
        layout.addWidget(self.btn_sql)
        self.setLayout(layout)
        
        self.btn_pg.clicked.connect(self.conectar_postgres)
        self.btn_sql.clicked.connect(self.conectar_sqlserver)

    def conectar_postgres(self):
        self.db = ConexionPostgres()
        if self.db.crear_conexion():
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Fallo en PostgreSQL. Revisa tu archivo .env")

    def conectar_sqlserver(self):
        self.db = ConexionSqlServer()
        if self.db.crear_conexion():
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Fallo en SQL Server. Revisa tu archivo .env")

# ==========================================
# 2. CLASE BASE PARA VISTAS CRUD (HUD PANEL)
# ==========================================
class VistaCRUDBase(QWidget):
    def __init__(self, db_conexion, titulo, columnas_tabla, callback_regresar):
        super().__init__()
        self.db = db_conexion
        
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(30, 30, 30, 30)
        layout_principal.setSpacing(15)
        
        # Cabecera de la sección con botón de retorno estilo HUD
        layout_top_sec = QHBoxLayout()
        btn_regresar = QPushButton("⬅ VOLVER AL DASHBOARD")
        btn_regresar.setObjectName("BtnRegresar")
        btn_regresar.clicked.connect(callback_regresar)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 22px; color: #FF6B00; font-weight: 900;")
        
        layout_top_sec.addWidget(btn_regresar)
        layout_top_sec.addStretch()
        layout_principal.addLayout(layout_top_sec)
        layout_principal.addWidget(lbl_titulo)

        # Formulario
        frame_form = QFrame()
        frame_form.setObjectName("FrameFormulario")
        self.layout_formulario = QFormLayout(frame_form)
        self.layout_formulario.setContentsMargins(20, 20, 20, 20)
        self.layout_formulario.setSpacing(12)

        # Botones de Acción
        self.layout_botones = QHBoxLayout()
        self.btn_insertar = QPushButton("⚡ Registrar")
        self.btn_actualizar = QPushButton("✏️ Modificar")
        self.btn_eliminar = QPushButton("🗑️ Dar de Baja")
        self.btn_eliminar.setObjectName("BtnPeligro")
        self.btn_consultar = QPushButton("🔍 Buscar")

        self.layout_botones.addWidget(self.btn_insertar)
        self.layout_botones.addWidget(self.btn_actualizar)
        self.layout_botones.addWidget(self.btn_eliminar)
        self.layout_botones.addWidget(self.btn_consultar)

        # Tabla de Datos
        self.tabla = QTableWidget(0, len(columnas_tabla))
        self.tabla.setHorizontalHeaderLabels(columnas_tabla)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setMinimumHeight(320)

        layout_principal.addWidget(frame_form)
        layout_principal.addLayout(self.layout_botones)
        layout_principal.addWidget(self.tabla)

    def obtener_marcador(self):
        return "?" if type(self.db).__name__ == "ConexionSqlServer" else "%s"

    def procesar_respuesta(self, respuesta_json, accion="Operación"):
        datos = json.loads(respuesta_json)
        if datos["estado"]:
            QMessageBox.information(self, "Ejecución Exitosa", datos.get("mensaje", f"{accion} realizada."))
            self.limpiar_campos()
            self.consultar_todos()
        else:
            QMessageBox.critical(self, "Error en Base de Datos", datos.get("mensaje", "Error SQL"))

    def cargar_tabla(self, sql, parametros=None):
        respuesta = self.db.ejecutar(sql, parametros) if parametros else self.db.ejecutar(sql)
        datos = json.loads(respuesta)
        if datos["estado"]:
            registros = datos["registros"]
            self.tabla.setRowCount(0)
            for f, fila_datos in enumerate(registros):
                self.tabla.insertRow(f)
                for c, valor in enumerate(fila_datos.values()):
                    self.tabla.setItem(f, c, QTableWidgetItem(str(valor) if valor is not None else ""))
        else:
            QMessageBox.critical(self, "Error", datos.get("mensaje", "Error al consultar"))

    def consultar_todos(self): pass 
    def limpiar_campos(self): pass 

# ==========================================
# 3. VISTAS CRUD ESPECÍFICAS
# ==========================================
class VistaRefaccion(VistaCRUDBase):
    def __init__(self, db, callback):
        super().__init__(db, "⚙️ GESTIÓN DE REFACCIONES E INVENTARIO", ["ID", "Código Parte", "Nombre Refacción", "Categoría", "Stock"], callback)
        self.id_input = QLineEdit()
        self.codigo_input = QLineEdit()
        self.nombre_input = QLineEdit()
        self.categoria_input = QLineEdit()
        self.stock_input = QLineEdit()
        
        self.layout_formulario.addRow("ID Refacción:", self.id_input)
        self.layout_formulario.addRow("Código de Parte:", self.codigo_input)
        self.layout_formulario.addRow("Nombre Refacción:", self.nombre_input)
        self.layout_formulario.addRow("Categoría:", self.categoria_input)
        self.layout_formulario.addRow("Stock Inicial:", self.stock_input)
        
        self.btn_consultar.clicked.connect(self.consultar)
        self.btn_insertar.clicked.connect(self.insertar)
        self.btn_actualizar.clicked.connect(self.actualizar)
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.consultar_todos()

    def limpiar_campos(self):
        self.id_input.clear(); self.codigo_input.clear(); self.nombre_input.clear()
        self.categoria_input.clear(); self.stock_input.clear()

    def consultar_todos(self):
        self.cargar_tabla("SELECT id_Refaccion, Codigo_Parte, Nombre_Refaccion, Categoria, Stock_Disponible FROM Refaccion;")

    def consultar(self):
        m = self.obtener_marcador()
        cond, params = [], []
        if self.id_input.text().strip(): cond.append(f"id_Refaccion = {m}"); params.append(self.id_input.text().strip())
        if self.codigo_input.text().strip(): cond.append(f"Codigo_Parte LIKE {m}"); params.append(f"%{self.codigo_input.text().strip()}%")
        if self.nombre_input.text().strip(): cond.append(f"Nombre_Refaccion LIKE {m}"); params.append(f"%{self.nombre_input.text().strip()}%")
        
        if cond: self.cargar_tabla(f"SELECT id_Refaccion, Codigo_Parte, Nombre_Refaccion, Categoria, Stock_Disponible FROM Refaccion WHERE {' AND '.join(cond)};", tuple(params))
        else: self.consultar_todos()

    def insertar(self):
        m = self.obtener_marcador()
        stk = self.stock_input.text().strip() or "0"
        self.procesar_respuesta(self.db.ejecutar(f"INSERT INTO Refaccion (Codigo_Parte, Nombre_Refaccion, Categoria, Stock_Disponible) VALUES ({m}, {m}, {m}, {m});", 
                                                 (self.codigo_input.text(), self.nombre_input.text(), self.categoria_input.text(), stk)))

    def actualizar(self):
        m = self.obtener_marcador()
        stk = self.stock_input.text().strip() or "0"
        self.procesar_respuesta(self.db.ejecutar(f"UPDATE Refaccion SET Codigo_Parte={m}, Nombre_Refaccion={m}, Categoria={m}, Stock_Disponible={m} WHERE id_Refaccion={m};", 
                                                 (self.codigo_input.text(), self.nombre_input.text(), self.categoria_input.text(), stk, self.id_input.text())))

    def eliminar(self):
        m = self.obtener_marcador()
        self.procesar_respuesta(self.db.ejecutar(f"DELETE FROM Refaccion WHERE id_Refaccion={m};", (self.id_input.text(),)))

class VistaCliente(VistaCRUDBase):
    def __init__(self, db, callback):
        super().__init__(db, "👥 DIRECTORIO DE CLIENTES", ["ID", "RFC", "Nombre Completo", "Dirección Fiscal", "Teléfono"], callback)
        self.id_input = QLineEdit()
        self.rfc_input = QLineEdit()
        self.nombre_input = QLineEdit()
        self.dir_input = QLineEdit()
        self.tel_input = QLineEdit()

        self.layout_formulario.addRow("ID Cliente:", self.id_input)
        self.layout_formulario.addRow("RFC:", self.rfc_input)
        self.layout_formulario.addRow("Nombre Completo:", self.nombre_input)
        self.layout_formulario.addRow("Dirección Fiscal:", self.dir_input)
        self.layout_formulario.addRow("Teléfono:", self.tel_input)
        
        self.btn_consultar.clicked.connect(self.consultar)
        self.btn_insertar.clicked.connect(self.insertar)
        self.btn_actualizar.clicked.connect(self.actualizar)
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.consultar_todos()

    def limpiar_campos(self):
        self.id_input.clear(); self.rfc_input.clear(); self.nombre_input.clear(); self.dir_input.clear(); self.tel_input.clear()

    def consultar_todos(self):
        self.cargar_tabla("SELECT id_Cliente, Rfc, Nombre_Completo, Direccion_Fiscal, Telefono FROM Cliente;")

    def consultar(self): self.consultar_todos()

    def insertar(self):
        m = self.obtener_marcador()
        self.procesar_respuesta(self.db.ejecutar(f"INSERT INTO Cliente (Rfc, Nombre_Completo, Direccion_Fiscal, Telefono) VALUES ({m}, {m}, {m}, {m});", 
                                                 (self.rfc_input.text(), self.nombre_input.text(), self.dir_input.text(), self.tel_input.text())))

    def actualizar(self):
        m = self.obtener_marcador()
        self.procesar_respuesta(self.db.ejecutar(f"UPDATE Cliente SET Rfc={m}, Nombre_Completo={m}, Direccion_Fiscal={m}, Telefono={m} WHERE id_Cliente={m};", 
                                                 (self.rfc_input.text(), self.nombre_input.text(), self.dir_input.text(), self.tel_input.text(), self.id_input.text())))

    def eliminar(self):
        m = self.obtener_marcador()
        self.procesar_respuesta(self.db.ejecutar(f"DELETE FROM Cliente WHERE id_Cliente={m};", (self.id_input.text(),)))

class VistaEmpleado(VistaCRUDBase):
    def __init__(self, db, callback):
        super().__init__(db, "👨‍🔧 CONTROL DE EMPLEADOS", ["ID", "Nombre", "Puesto", "Turno"], callback)
        self.id_input = QLineEdit()
        self.nombre_input = QLineEdit()
        self.puesto_input = QLineEdit()
        self.turno_input = QLineEdit()
        self.turno_input.setPlaceholderText("Matutino / Vespertino / Nocturno")

        self.layout_formulario.addRow("ID Empleado:", self.id_input)
        self.layout_formulario.addRow("Nombre:", self.nombre_input)
        self.layout_formulario.addRow("Puesto:", self.puesto_input)
        self.layout_formulario.addRow("Turno:", self.turno_input)
        
        self.btn_consultar.clicked.connect(self.consultar)
        self.btn_insertar.clicked.connect(self.insertar)
        self.btn_actualizar.clicked.connect(self.actualizar)
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.consultar_todos()

    def limpiar_campos(self):
        self.id_input.clear(); self.nombre_input.clear(); self.puesto_input.clear(); self.turno_input.clear()

    def consultar_todos(self):
        self.cargar_tabla("SELECT id_Empleado, Nombre, Puesto, Turno FROM Empleado;")

    def consultar(self): self.consultar_todos()

    def insertar(self):
        m = self.obtener_marcador()
        self.procesar_respuesta(self.db.ejecutar(f"INSERT INTO Empleado (Nombre, Puesto, Turno) VALUES ({m}, {m}, {m});", 
                                                 (self.nombre_input.text(), self.puesto_input.text(), self.turno_input.text())))

    def actualizar(self):
        m = self.obtener_marcador()
        self.procesar_respuesta(self.db.ejecutar(f"UPDATE Empleado SET Nombre={m}, Puesto={m}, Turno={m} WHERE id_Empleado={m};", 
                                                 (self.nombre_input.text(), self.puesto_input.text(), self.turno_input.text(), self.id_input.text())))

    def eliminar(self):
        m = self.obtener_marcador()
        self.procesar_respuesta(self.db.ejecutar(f"DELETE FROM Empleado WHERE id_Empleado={m};", (self.id_input.text(),)))

class VistaProveedor(VistaCRUDBase):
    def __init__(self, db, callback):
        super().__init__(db, "🏭 DIRECTORIO DE PROVEEDORES", ["ID", "Razón Social", "Contacto", "Teléfono"], callback)
        self.id_input = QLineEdit()
        self.razon_input = QLineEdit()
        self.contacto_input = QLineEdit()
        self.tel_input = QLineEdit()

        self.layout_formulario.addRow("ID Proveedor:", self.id_input)
        self.layout_formulario.addRow("Razón Social:", self.razon_input)
        self.layout_formulario.addRow("Contacto:", self.contacto_input)
        self.layout_formulario.addRow("Teléfono Contacto:", self.tel_input)
        
        self.btn_consultar.clicked.connect(self.consultar)
        self.btn_insertar.clicked.connect(self.insertar)
        self.btn_actualizar.clicked.connect(self.actualizar)
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.consultar_todos()

    def limpiar_campos(self):
        self.id_input.clear(); self.razon_input.clear(); self.contacto_input.clear(); self.tel_input.clear()

    def consultar_todos(self):
        self.cargar_tabla("SELECT id_Proveedor, Razon_Social, Nombre_Contacto, Telefono_Contacto FROM Proveedor;")

    def consultar(self): self.consultar_todos()

    def insertar(self):
        m = self.obtener_marcador()
        self.procesar_respuesta(self.db.ejecutar(f"INSERT INTO Proveedor (Razon_Social, Nombre_Contacto, Telefono_Contacto) VALUES ({m}, {m}, {m});", 
                                                 (self.razon_input.text(), self.contacto_input.text(), self.tel_input.text())))

    def actualizar(self):
        m = self.obtener_marcador()
        self.procesar_respuesta(self.db.ejecutar(f"UPDATE Proveedor SET Razon_Social={m}, Nombre_Contacto={m}, Telefono_Contacto={m} WHERE id_Proveedor={m};", 
                                                 (self.razon_input.text(), self.contacto_input.text(), self.tel_input.text(), self.id_input.text())))

    def eliminar(self):
        m = self.obtener_marcador()
        self.procesar_respuesta(self.db.ejecutar(f"DELETE FROM Proveedor WHERE id_Proveedor={m};", (self.id_input.text(),)))

# ==========================================
# 4. VISTAS DE MONITOREO Y REPORTES
# ==========================================
class VistaVentas(QWidget):
    def __init__(self, db_conexion, callback):
        super().__init__()
        self.db = db_conexion
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        btn_regresar = QPushButton("⬅ VOLVER AL DASHBOARD")
        btn_regresar.setObjectName("BtnRegresar")
        btn_regresar.clicked.connect(callback)
        layout.addWidget(btn_regresar, alignment=Qt.AlignmentFlag.AlignLeft)
        
        lbl_titulo = QLabel("💳 HISTORIAL DE VENTAS REGISTRADAS")
        lbl_titulo.setStyleSheet("font-size: 22px; color: #FF6B00; font-weight: 900;")
        layout.addWidget(lbl_titulo)
        
        btn_recargar = QPushButton("↻ Refrescar Datos")
        btn_recargar.clicked.connect(self.cargar_datos)
        layout.addWidget(btn_recargar)

        self.tabla = QTableWidget(0, 5)
        self.tabla.setHorizontalHeaderLabels(["ID Venta", "Cliente", "Fecha", "Método Pago", "Total ($)"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla)
        self.cargar_datos()

    def cargar_datos(self):
        sql = """
        SELECT V.id_Venta, C.Nombre_Completo AS Cliente, V.Fecha_Venta, V.Metodo_Pago, V.Total_Venta
        FROM Venta V
        INNER JOIN Cliente C ON V.id_Cliente = C.id_Cliente;
        """
        datos = json.loads(self.db.ejecutar(sql))
        if datos["estado"]:
            registros = datos["registros"]
            self.tabla.setRowCount(0)
            for f, fila in enumerate(registros):
                self.tabla.insertRow(f)
                for c, valor in enumerate(fila.values()):
                    self.tabla.setItem(f, c, QTableWidgetItem(str(valor) if valor is not None else ""))

class VistaOrdenesCompra(QWidget):
    def __init__(self, db_conexion, callback):
        super().__init__()
        self.db = db_conexion
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        btn_regresar = QPushButton("⬅ VOLVER AL DASHBOARD")
        btn_regresar.setObjectName("BtnRegresar")
        btn_regresar.clicked.connect(callback)
        layout.addWidget(btn_regresar, alignment=Qt.AlignmentFlag.AlignLeft)
        
        lbl_titulo = QLabel("📋 ÓRDENES DE COMPRA A PROVEEDORES")
        lbl_titulo.setStyleSheet("font-size: 22px; color: #FF6B00; font-weight: 900;")
        layout.addWidget(lbl_titulo)
        
        btn_recargar = QPushButton("↻ Refrescar Órdenes")
        btn_recargar.clicked.connect(self.cargar_datos)
        layout.addWidget(btn_recargar)

        self.tabla = QTableWidget(0, 6)
        self.tabla.setHorizontalHeaderLabels(["ID Órden", "Empleado Solicitante", "Proveedor", "Fecha Solicitud", "Estado", "Costo Total ($)"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla)
        self.cargar_datos()

    def cargar_datos(self):
        sql = """
        SELECT O.id_Orden, E.Nombre AS Empleado, P.Razon_Social AS Proveedor, O.Fecha_Solicitud, O.Estado_Entrega, O.Costo_Total
        FROM Orden_Compra O
        INNER JOIN Empleado E ON O.id_Empleado = E.id_Empleado
        INNER JOIN Proveedor P ON O.id_Proveedor = P.id_Proveedor;
        """
        datos = json.loads(self.db.ejecutar(sql))
        if datos["estado"]:
            registros = datos["registros"]
            self.tabla.setRowCount(0)
            for f, fila in enumerate(registros):
                self.tabla.insertRow(f)
                for c, valor in enumerate(fila.values()):
                    self.tabla.setItem(f, c, QTableWidgetItem(str(valor) if valor is not None else ""))

class VistaReportes(QWidget):
    def __init__(self, db_conexion, callback):
        super().__init__()
        self.db = db_conexion
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        btn_regresar = QPushButton("⬅ VOLVER AL DASHBOARD")
        btn_regresar.setObjectName("BtnRegresar")
        btn_regresar.clicked.connect(callback)
        layout.addWidget(btn_regresar, alignment=Qt.AlignmentFlag.AlignLeft)
        
        lbl_titulo = QLabel("📊 PANEL DE MÉTRICAS Y KPIS - AUTOPARTES")
        lbl_titulo.setStyleSheet("font-size: 22px; color: #FF6B00; font-weight: 900; margin-bottom: 15px;")
        layout.addWidget(lbl_titulo)
        
        self.grid_kpis = QGridLayout()
        layout.addLayout(self.grid_kpis)
        layout.addStretch()

        btn_recargar = QPushButton("↻ Recalcular Métricas")
        btn_recargar.clicked.connect(self.cargar_kpis)
        layout.addWidget(btn_recargar)
        self.cargar_kpis()

    def crear_tarjeta(self, titulo, valor, color, fila, col):
        frame = QFrame()
        frame.setObjectName("CardMenu")
        frame.setStyleSheet(f"border-left: 6px solid {color}; padding: 25px;")
        lyt = QVBoxLayout(frame)
        lbl_t = QLabel(titulo)
        lbl_t.setStyleSheet("color: #8A8A9E; font-size: 14px; font-weight: bold;")
        lbl_v = QLabel(str(valor))
        lbl_v.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: 900;")
        lyt.addWidget(lbl_t)
        lyt.addWidget(lbl_v)
        self.grid_kpis.addWidget(frame, fila, col)

    def cargar_kpis(self):
        for i in reversed(range(self.grid_kpis.count())): 
            self.grid_kpis.itemAt(i).widget().setParent(None)

        d_ventas = json.loads(self.db.ejecutar("SELECT SUM(Total_Venta) FROM Venta;"))
        d_clientes = json.loads(self.db.ejecutar("SELECT COUNT(*) FROM Cliente;"))
        d_refacciones = json.loads(self.db.ejecutar("SELECT COUNT(*) FROM Refaccion;"))
        d_ordenes = json.loads(self.db.ejecutar("SELECT COUNT(*) FROM Orden_Compra;"))
        
        def extraer_valor(datos):
            if datos.get("estado") and datos.get("registros"):
                fila = datos["registros"][0]
                valores = list(fila.values())
                if valores and valores[0] is not None:
                    return valores[0]
            return 0

        val_ventas = f"${extraer_valor(d_ventas):,.2f}" if isinstance(extraer_valor(d_ventas), (int, float)) else f"${extraer_valor(d_ventas)}"
        val_clientes = str(extraer_valor(d_clientes))
        val_refacciones = str(extraer_valor(d_refacciones))
        val_ordenes = str(extraer_valor(d_ordenes))

        self.crear_tarjeta("💰 Ventas Totales", val_ventas, "#00FFCC", 0, 0)
        self.crear_tarjeta("👥 Clientes Registrados", val_clientes, "#38BDF8", 0, 1)
        self.crear_tarjeta("⚙️ Catálogo Refacciones", val_refacciones, "#C084FC", 1, 0)
        self.crear_tarjeta("📑 Órdenes de Compra", val_ordenes, "#FF6B00", 1, 1)

# ==========================================
# 5. DASHBOARD PRINCIPAL (MENÚ DE TARJETAS TÁCTICAS)
# ==========================================
class DashboardPrincipal(QWidget):
    def __init__(self, cambiar_vista_callback):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        lbl_bienvenida = QLabel("🛠️ CENTRO DE COMANDO — AUTOPARTES DEL VALLE")
        lbl_bienvenida.setStyleSheet("font-size: 22px; color: #FFFFFF; font-weight: 900;")
        lbl_sub = QLabel("Seleccione un módulo interactivo para iniciar la administración de la base de datos:")
        lbl_sub.setStyleSheet("font-size: 14px; color: #8A8A9E;")

        layout.addWidget(lbl_bienvenida)
        layout.addWidget(lbl_sub)

        grid = QGridLayout()
        grid.setSpacing(20)

        modulos = [
            ("⚙️ Gestión de Refacciones", "Administrar inventario, stock y piezas mecánicas.", 0, 0, 1),
            ("👥 Directorio de Clientes", "Control de fichas fiscales, RFC y contactos.", 0, 1, 2),
            ("👨‍🔧 Personal y Empleados", "Altas, puestos y turnos laborales.", 1, 0, 3),
            ("🏭 Proveedores", "Registro de empresas proveedoras y teléfonos.", 1, 1, 4),
            ("💳 Historial de Ventas", "Monitoreo de transacciones y montos totales.", 2, 0, 5),
            ("📋 Órdenes de Compra", "Seguimiento a pedidos de mercancía.", 2, 1, 6),
            ("📊 Dashboard de KPIs", "Estadísticas y métricas generales del sistema.", 3, 0, 7)
        ]

        for titulo, desc, fila, col, index in modulos:
            btn_card = QPushButton()
            btn_card.setObjectName("CardMenu")
            btn_card.setMinimumHeight(110)
            
            lyt_card = QVBoxLayout(btn_card)
            lbl_t = QLabel(titulo)
            lbl_t.setObjectName("LabelCardTitulo")
            lbl_d = QLabel(desc)
            lbl_d.setObjectName("LabelCardDesc")
            
            lyt_card.addWidget(lbl_t)
            lyt_card.addWidget(lbl_d)
            
            btn_card.clicked.connect(lambda checked, idx=index: cambiar_vista_callback(idx))
            grid.addWidget(btn_card, fila, col)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget_interior = QWidget()
        widget_interior.setLayout(grid)
        scroll.setWidget(widget_interior)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        layout.addWidget(scroll)

# ==========================================
# 6. VENTANA PRINCIPAL DEL SISTEMA
# ==========================================
class SistemaAutoPartesHUD(QMainWindow):
    def __init__(self, db_conexion):
        super().__init__()
        self.setWindowTitle("Sistema HUD - Refaccionaria AutoPartes del Valle")
        self.resize(1150, 750)
        self.db = db_conexion
        
        widget_central = QWidget()
        layout_principal = QVBoxLayout(widget_central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # Encabezado Fijo superior
        header = QFrame()
        header.setObjectName("HeaderPrincipal")
        header.setFixedHeight(55)
        layout_header = QHBoxLayout(header)
        layout_header.setContentsMargins(25, 0, 25, 0)
        
        lbl_logo = QLabel("🚗 AUTOPARTES DEL VALLE [HUD SYSTEM]")
        lbl_logo.setObjectName("TituloLogo")
        
        motor = "SQL Server" if type(self.db).__name__ == "ConexionSqlServer" else "PostgreSQL"
        lbl_estado = QLabel(f"● Estado: {motor} Conectado")
        lbl_estado.setObjectName("EstadoBD")
        
        layout_header.addWidget(lbl_logo)
        layout_header.addStretch()
        layout_header.addWidget(lbl_estado)

        # Stacked Widget para cambiar de pantallas de forma limpia
        self.stacked_widget = QStackedWidget()
        
        # 0. Dashboard Principal de Tarjetas
        self.dashboard = DashboardPrincipal(self.cambiar_vista)
        self.stacked_widget.addWidget(self.dashboard) # Index 0

        # Módulos Funcionales
        self.stacked_widget.addWidget(VistaRefaccion(self.db, lambda: self.cambiar_vista(0)))     # Index 1
        self.stacked_widget.addWidget(VistaCliente(self.db, lambda: self.cambiar_vista(0)))       # Index 2
        self.stacked_widget.addWidget(VistaEmpleado(self.db, lambda: self.cambiar_vista(0)))      # Index 3
        self.stacked_widget.addWidget(VistaProveedor(self.db, lambda: self.cambiar_vista(0)))     # Index 4
        self.stacked_widget.addWidget(VistaVentas(self.db, lambda: self.cambiar_vista(0)))        # Index 5
        self.stacked_widget.addWidget(VistaOrdenesCompra(self.db, lambda: self.cambiar_vista(0))) # Index 6
        self.stacked_widget.addWidget(VistaReportes(self.db, lambda: self.cambiar_vista(0)))      # Index 7

        layout_principal.addWidget(header)
        layout_principal.addWidget(self.stacked_widget)
        self.setCentralWidget(widget_central)

    def cambiar_vista(self, index):
        self.stacked_widget.setCurrentIndex(index)

# ==========================================
# EJECUCIÓN DEL SISTEMA
# ==========================================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(ESTILO_INDUSTRIAL_HUD)
    
    ventana_seleccion = SeleccionBD()
    
    if ventana_seleccion.exec() == QDialog.DialogCode.Accepted:
        ventana_principal = SistemaAutoPartesHUD(ventana_seleccion.db)
        ventana_principal.show()
        sys.exit(app.exec())