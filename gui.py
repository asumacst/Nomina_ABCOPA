import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QMessageBox, QTextEdit, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea, QGroupBox, QFrame, QDialog,
    QDialogButtonBox, QFormLayout, QSizePolicy, QRadioButton
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor, QIcon
from datetime import datetime
import pandas as pd
import os
from main import (
    calculate_payroll_quincenal,
    agregar_empleado,
    eliminar_empleado,
    modificar_empleado,
    leer_empleados_normalizado
)

# Paleta de colores Gruvbox (versión suave)
class GruvboxColors:
    # Backgrounds
    BG_DARK = '#282828'      # bg0
    BG_DARKER = '#1d2021'    # bg0_h
    BG_LIGHT = '#3c3836'     # bg1
    BG_LIGHTER = '#504945'   # bg2
    
    # Foregrounds
    FG = '#ebdbb2'           # fg
    FG_DARK = '#a89984'      # fg2
    
    # Accent colors (suaves)
    BLUE = '#83a598'         # blue
    AQUA = '#8ec07c'         # aqua
    GREEN = '#b8bb26'        # green
    YELLOW = '#fabd2f'       # yellow
    ORANGE = '#fe8019'       # orange
    RED = '#fb4934'          # red
    PURPLE = '#d3869b'       # purple
    
    # Neutral
    GRAY = '#928374'         # gray
    BUTTON_TEXT = '#282828'  # texto sobre botones de acento


# Paleta Aqua/Tema claro (#E3FDFD, #CBF1F5, #A6E3E9, #71C9CE) con texto negro
class AquaColors:
    # Backgrounds (del más claro al más oscuro de la paleta)
    BG_DARK = '#E3FDFD'      # más claro - fondo principal
    BG_DARKER = '#CBF1F5'
    BG_LIGHT = '#A6E3E9'
    BG_LIGHTER = '#71C9CE'   # más oscuro - acentos

    # Foregrounds - negro para contraste
    FG = '#000000'
    FG_DARK = '#333333'

    # Accent colors (usando la paleta)
    BLUE = '#71C9CE'
    AQUA = '#71C9CE'
    GREEN = '#71C9CE'
    YELLOW = '#A6E3E9'
    ORANGE = '#71C9CE'
    RED = '#d9534f'          # rojo para Salir (contraste sobre claro)
    PURPLE = '#71C9CE'

    GRAY = '#666666'
    BUTTON_TEXT = '#000000'  # negro sobre botones de acento


# Tema actual y selector
CURRENT_THEME = 'aqua'


def get_colors():
    """Devuelve la paleta del tema actual."""
    return GruvboxColors if CURRENT_THEME == 'gruvbox' else AquaColors


class GruvboxStyle:
    @staticmethod
    def apply_style(app, theme='gruvbox'):
        """Aplica el estilo a la aplicación según el tema (gruvbox o aqua)."""
        C = GruvboxColors if theme == 'gruvbox' else AquaColors
        style = f"""
        QMainWindow {{
            background-color: {C.BG_DARK};
            color: {C.FG};
        }}
        QWidget {{
            background-color: {C.BG_DARK};
            color: {C.FG};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        QPushButton {{
            background-color: {C.BG_LIGHT};
            color: {C.FG};
            border: 2px solid {C.BG_LIGHTER};
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 12pt;
            min-height: 40px;
        }}
        QPushButton:hover {{
            background-color: {C.BG_LIGHTER};
            border-color: {C.BLUE};
        }}
        QPushButton:pressed {{
            background-color: {C.BG_LIGHTER};
            border-color: {C.AQUA};
        }}
        QPushButton:disabled {{
            background-color: {C.BG_DARKER};
            color: {C.GRAY};
            border-color: {C.BG_DARKER};
        }}
        QLabel {{
            color: {C.FG};
            background-color: transparent;
        }}
        QLineEdit, QTextEdit {{
            background-color: {C.BG_LIGHT};
            color: {C.FG};
            border: 2px solid {C.BG_LIGHTER};
            border-radius: 4px;
            padding: 6px;
            font-size: 11pt;
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border-color: {C.BLUE};
        }}
        QGroupBox {{
            border: 2px solid {C.BG_LIGHTER};
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
            color: {C.AQUA};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }}
        QTableWidget {{
            background-color: {C.BG_LIGHT};
            color: {C.FG};
            border: 1px solid {C.BG_LIGHTER};
            gridline-color: {C.BG_LIGHTER};
            selection-background-color: {C.BLUE};
            selection-color: {C.BG_DARK};
            alternate-background-color: {C.BG_LIGHT};
        }}
        QTableWidget::item {{
            background-color: {C.BG_LIGHT};
            color: {C.FG};
        }}
        QTableWidget::item:selected {{
            background-color: {C.BLUE};
            color: {C.BG_DARK};
        }}
        QHeaderView::section {{
            background-color: {C.BG_LIGHTER};
            color: {C.AQUA};
            padding: 8px;
            border: 1px solid {C.BG_LIGHTER};
            font-weight: bold;
        }}
        QScrollArea {{
            border: none;
            background-color: {C.BG_DARK};
        }}
        QScrollBar:vertical {{
            background-color: {C.BG_LIGHT};
            width: 12px;
            border: none;
        }}
        QScrollBar::handle:vertical {{
            background-color: {C.BG_LIGHTER};
            min-height: 20px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {C.BLUE};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QDialog {{
            background-color: {C.BG_DARK};
        }}
        QRadioButton {{
            color: {C.FG};
        }}
        """
        app.setStyleSheet(style)


class NominaApp(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Sistema de Nómina ABCOPA")
        self.setMinimumSize(1000, 700)
        self._logo_has_image = False
        self._logo_path = "logo.png"

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 30, 40, 30)

        # Logo y título Quintas del Este
        logo_container = QVBoxLayout()
        logo_container.setAlignment(Qt.AlignCenter)
        logo_container.setSpacing(10)

        self.logo_label = QLabel()
        if os.path.exists(self._logo_path):
            pixmap = QPixmap(self._logo_path)
            scaled_pixmap = pixmap.scaled(300, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
            self._logo_has_image = True
        else:
            self.logo_label.setText("Quintas del Este")
            self._logo_has_image = False
        self.logo_label.setAlignment(Qt.AlignCenter)
        logo_container.addWidget(self.logo_label)

        self.title_label = QLabel("Quintas del Este")
        self.title_label.setAlignment(Qt.AlignCenter)
        logo_container.addWidget(self.title_label)

        main_layout.addLayout(logo_container)

        self.subtitle_label = QLabel("Sistema de Nomina")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.subtitle_label)

        # Caja de selección de tema
        theme_group = QGroupBox("Tema")
        theme_layout = QHBoxLayout(theme_group)
        theme_layout.setAlignment(Qt.AlignCenter)
        self.theme_gruvbox = QRadioButton("Gruvbox (oscuro)")
        self.theme_aqua = QRadioButton("Aqua (claro)")
        self.theme_aqua.setChecked(True)
        theme_layout.addWidget(self.theme_gruvbox)
        theme_layout.addWidget(self.theme_aqua)
        self.theme_gruvbox.toggled.connect(self._on_theme_changed)
        self.theme_aqua.toggled.connect(self._on_theme_changed)
        main_layout.addWidget(theme_group)

        # Botones principales
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(15)

        self.main_buttons = []
        buttons = [
            ("Calcular Nómina Quincenal", self.open_calculate_payroll),
            ("Gestionar Empleados", self.open_manage_employees),
            ("Ver Nómina", self.view_payroll),
            ("Ver Información", self.show_info),
            ("Salir", self.close),
        ]
        for text, command in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(command)
            self.main_buttons.append((btn, text == "Salir"))
            button_layout.addWidget(btn)

        main_layout.addLayout(button_layout)
        self._apply_theme_to_widgets()

        # Espaciador para centrar verticalmente
        main_layout.addStretch()

    def _on_theme_changed(self):
        global CURRENT_THEME
        if self.theme_aqua.isChecked():
            CURRENT_THEME = 'aqua'
        else:
            CURRENT_THEME = 'gruvbox'
        GruvboxStyle.apply_style(self.app, CURRENT_THEME)
        self._apply_theme_to_widgets()

    def _apply_theme_to_widgets(self):
        global CURRENT_THEME
        C = get_colors()
        # En modo Aqua (claro) los títulos van en negro para mejor contraste
        title_color = C.FG if CURRENT_THEME == 'aqua' else C.AQUA
        subtitle_color = C.FG if CURRENT_THEME == 'aqua' else C.YELLOW
        if not self._logo_has_image:
            self.logo_label.setStyleSheet(
                f"font-size: 48pt; font-weight: bold; color: {title_color};"
            )
        self.title_label.setStyleSheet(
            f"font-size: 36pt; font-weight: bold; color: {title_color}; margin: 10px;"
        )
        self.subtitle_label.setStyleSheet(
            f"font-size: 28pt; font-weight: bold; color: {subtitle_color}; margin: 20px;"
        )
        for btn, is_exit in self.main_buttons:
            color = C.RED if is_exit else C.AQUA
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {C.BUTTON_TEXT};
                    border: 2px solid {color};
                    border-radius: 8px;
                    padding: 15px 30px;
                    font-weight: bold;
                    font-size: 14pt;
                    min-width: 350px;
                    min-height: 50px;
                }}
                QPushButton:hover {{
                    background-color: {C.BG_LIGHT};
                    color: {color};
                    border-color: {color};
                }}
                QPushButton:pressed {{
                    background-color: {C.BG_LIGHTER};
                }}
            """)

    def open_calculate_payroll(self):
        """Abre la ventana para calcular nómina"""
        self.calc_window = CalculatePayrollWindow(self)
        self.calc_window.show()
    
    def open_manage_employees(self):
        """Abre la ventana para gestionar empleados"""
        self.manage_window = ManageEmployeesWindow(self)
        self.manage_window.show()
    
    def view_payroll(self):
        """Permite seleccionar y ver un archivo de nómina"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de nómina",
            os.getcwd(),
            "Archivos Excel (*.xlsx);;Todos los archivos (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            df = pd.read_excel(file_path)
            
            if df.empty:
                QMessageBox.information(self, "Información", "El archivo de nómina está vacío.")
                return
            
            # Reorganizar columnas
            if 'Pago Quincenal' in df.columns:
                df = df.rename(columns={'Pago Quincenal': 'Total Pago a Empleados'})
                other_cols = [col for col in df.columns if col != 'Total Pago a Empleados']
                df = df[other_cols + ['Total Pago a Empleados']]
            
            # Calcular total general
            if 'Total Pago a Empleados' in df.columns:
                total_general = df['Total Pago a Empleados'].sum()
            elif 'Pago Quincenal' in df.columns:
                total_general = df['Pago Quincenal'].sum()
            else:
                total_general = 0
            
            # Crear ventana para mostrar nómina
            view_window = ViewPayrollWindow(self, df, total_general, os.path.basename(file_path))
            view_window.show()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al leer el archivo de nómina:\n{str(e)}")
    
    def show_info(self):
        """Muestra información del sistema"""
        info_text = """
SISTEMA DE NÓMINA ABCOPA

Este sistema permite calcular la nómina quincenal de los empleados
basándose en las horas trabajadas registradas.

FUNCIONALIDADES:
• Calcular nómina quincenal automáticamente
• Gestionar empleados (agregar, eliminar, modificar)
• Cálculo automático de horas extra (25% adicional después de las 3 PM)
• Cálculo automático de pago por feriados/domingos (50% adicional)

ARCHIVOS REQUERIDOS:
• employees_information.xlsx - Información de empleados
• Reporte de Asistencia.xlsx - Reporte de asistencia del escáner biométrico

TIPOS DE EMPLEADOS:
• Salario Fijo: Cobran lo mismo sin importar las horas trabajadas
• Empleado Fijo: Tienen un sueldo mínimo garantizado + bono por horas extra
  si trabajan más de las horas requeridas para ese sueldo
• Por Horas: Reciben pago según horas trabajadas con bonos por horas extra

IMPORTANTE:
• Se requiere exactamente 2 registros por día por empleado (entrada y salida)
• Los empleados fijos no pueden ser ambos tipos a la vez
        """
        QMessageBox.information(self, "Información del Sistema", info_text)


class ViewPayrollWindow(QDialog):
    def __init__(self, parent, df, total_general, filename):
        super().__init__(parent)
        self.setWindowTitle("Nómina Quincenal")
        self.setMinimumSize(1200, 700)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("NÓMINA QUINCENAL")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 24pt; font-weight: bold; color: {get_colors().AQUA}; margin: 10px;")
        layout.addWidget(title)
        
        # Información del archivo
        file_info = QLabel(f"Archivo: {filename}")
        file_info.setAlignment(Qt.AlignCenter)
        file_info.setStyleSheet(f"font-size: 12pt; color: {get_colors().FG_DARK};")
        layout.addWidget(file_info)
        
        # Tabla con scroll horizontal
        table = QTableWidget()
        table.setRowCount(len(df))
        table.setColumnCount(len(df.columns))
        table.setHorizontalHeaderLabels(df.columns)
        
        # Insertar datos
        for i, row in df.iterrows():
            for j, col in enumerate(df.columns):
                val = row[col]
                if pd.isna(val):
                    item_text = ''
                elif isinstance(val, (int, float)) and ('Pago' in col or 'Total' in col or 'Salario' in col or 'Bono' in col):
                    item_text = f"${val:,.2f}"
                else:
                    item_text = str(val)
                
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                if 'Total' in col or 'Pago' in col:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                table.setItem(i, j, item)
        
        # Configurar columnas para permitir scroll horizontal
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.horizontalHeader().setMinimumSectionSize(100)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(False)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Asegurar fondo oscuro para todas las celdas
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().FG};
                gridline-color: {get_colors().BG_LIGHTER};
            }}
            QTableWidget::item {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().FG};
            }}
            QTableWidget::item:selected {{
                background-color: {get_colors().BLUE};
                color: {get_colors().BUTTON_TEXT};
            }}
        """)
        
        layout.addWidget(table)
        
        # Total general
        total_frame = QFrame()
        total_layout = QHBoxLayout(total_frame)
        total_layout.setAlignment(Qt.AlignCenter)
        
        total_label = QLabel("TOTAL GENERAL A PAGAR:")
        total_label.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {get_colors().AQUA};")
        total_layout.addWidget(total_label)
        
        total_value = QLabel(f"${total_general:,.2f}")
        total_value.setStyleSheet(f"""
            font-size: 20pt; font-weight: bold;
            background-color: {get_colors().YELLOW};
            color: {get_colors().BUTTON_TEXT};
            padding: 15px 30px;
            border-radius: 8px;
        """)
        total_layout.addWidget(total_value)
        
        info_label = QLabel(f"({len(df)} empleados)")
        info_label.setStyleSheet(f"font-size: 12pt; color: {get_colors().FG_DARK}; margin-left: 15px;")
        total_layout.addWidget(info_label)
        
        layout.addWidget(total_frame)
        
        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 10px 30px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().AQUA};
            }}
        """)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)


class CalculatePayrollThread(QThread):
    finished = pyqtSignal(object, str)
    error = pyqtSignal(str)
    
    def __init__(self, employees_file, hours_file, quincena_fecha):
        super().__init__()
        self.employees_file = employees_file
        self.hours_file = hours_file
        self.quincena_fecha = quincena_fecha
    
    def run(self):
        try:
            import sys
            from io import StringIO
            
            old_stdout = sys.stdout
            sys.stdout = output = StringIO()
            
            result = calculate_payroll_quincenal(
                employees_file=self.employees_file,
                hours_file=self.hours_file,
                output_file=None,
                quincena_fecha=self.quincena_fecha
            )
            
            sys.stdout = old_stdout
            output_text = output.getvalue()
            
            self.finished.emit(result, output_text)
        except Exception as e:
            self.error.emit(str(e))


class CalculatePayrollWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Calcular Nómina Quincenal")
        self.setMinimumSize(700, 650)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Título
        title = QLabel("CALCULAR NÓMINA QUINCENAL")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 20pt; font-weight: bold; color: {get_colors().AQUA}; margin: 10px;")
        layout.addWidget(title)
        
        # Botones principales
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        self.calculate_btn = QPushButton("Calcular Nómina")
        self.calculate_btn.clicked.connect(self.calculate_payroll)
        self.calculate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 150px;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().AQUA};
            }}
        """)
        button_layout.addWidget(self.calculate_btn)
        
        self.continue_btn = QPushButton("Continuar")
        self.continue_btn.clicked.connect(self.continue_operation)
        self.continue_btn.setEnabled(False)
        self.continue_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 150px;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().AQUA};
            }}
        """)
        button_layout.addWidget(self.continue_btn)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 150px;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().AQUA};
            }}
        """)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Frame de archivos
        files_group = QGroupBox("Archivos")
        files_layout = QVBoxLayout(files_group)
        
        # Archivo de empleados
        emp_layout = QHBoxLayout()
        emp_label = QLabel("Archivo de Empleados:")
        emp_layout.addWidget(emp_label)
        
        self.emp_file_edit = QLineEdit("employees_information.xlsx")
        emp_layout.addWidget(self.emp_file_edit)
        
        emp_browse_btn = QPushButton("Buscar")
        emp_browse_btn.clicked.connect(lambda: self.browse_file(self.emp_file_edit))
        emp_layout.addWidget(emp_browse_btn)
        
        files_layout.addLayout(emp_layout)
        
        # Archivo de horas
        hours_layout = QHBoxLayout()
        hours_label = QLabel("Archivo de Reporte de Asistencia:")
        hours_layout.addWidget(hours_label)
        
        self.hours_file_edit = QLineEdit("Reporte de Asistencia.xlsx")
        hours_layout.addWidget(self.hours_file_edit)
        
        hours_browse_btn = QPushButton("Buscar")
        hours_browse_btn.clicked.connect(lambda: self.browse_file(self.hours_file_edit))
        hours_layout.addWidget(hours_browse_btn)
        
        files_layout.addLayout(hours_layout)
        
        layout.addWidget(files_group)
        
        # Frame de fecha
        date_group = QGroupBox("Fecha de Referencia (Opcional)")
        date_layout = QVBoxLayout(date_group)
        
        date_hint = QLabel("Deje vacío para usar la quincena más reciente")
        date_hint.setStyleSheet(f"color: {get_colors().FG_DARK}; font-style: italic;")
        date_layout.addWidget(date_hint)
        
        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText("DD/MM/YYYY (ejemplo: 15/01/2026)")
        date_layout.addWidget(self.date_edit)
        
        layout.addWidget(date_group)
        
        # Área de mensajes
        msg_group = QGroupBox("Mensajes")
        msg_layout = QVBoxLayout(msg_group)
        
        self.message_text = QTextEdit()
        self.message_text.setReadOnly(True)
        self.message_text.setFont(QFont("Consolas", 9))
        msg_layout.addWidget(self.message_text)
        
        layout.addWidget(msg_group)
        
        # Indicador de estado
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"font-size: 11pt; font-weight: bold; color: {get_colors().AQUA};")
        layout.addWidget(self.status_label)
        
        self.calc_thread = None
    
    def browse_file(self, line_edit):
        """Abre diálogo para buscar archivo"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo",
            os.getcwd(),
            "Excel files (*.xlsx *.xls);;All files (*.*)"
        )
        if filename:
            line_edit.setText(filename)
    
    def continue_operation(self):
        """Permite continuar después de calcular la nómina"""
        self.calculate_btn.setEnabled(True)
        self.continue_btn.setEnabled(False)
        self.status_label.setText("")
        self.status_label.setStyleSheet(f"font-size: 11pt; font-weight: bold; color: {get_colors().AQUA};")
    
    def calculate_payroll(self):
        """Calcula la nómina"""
        employees_file = self.emp_file_edit.text().strip()
        hours_file = self.hours_file_edit.text().strip()
        date_str = self.date_edit.text().strip()
        
        # Validar archivos
        if not employees_file:
            QMessageBox.critical(self, "Error", "Debe especificar el archivo de empleados")
            return
        
        if not hours_file:
            QMessageBox.critical(self, "Error", "Debe especificar el archivo de reporte de asistencia")
            return
        
        if not os.path.exists(employees_file):
            QMessageBox.critical(self, "Error", f"El archivo de empleados no existe: {employees_file}")
            return
        
        if not os.path.exists(hours_file):
            QMessageBox.critical(self, "Error", f"El archivo de horas no existe: {hours_file}")
            return
        
        # Validar fecha
        quincena_fecha = None
        if date_str:
            try:
                datetime.strptime(date_str, '%d/%m/%Y')
                quincena_fecha = date_str
            except ValueError:
                QMessageBox.critical(self, "Error", "Formato de fecha inválido. Use DD/MM/YYYY (ejemplo: 15/01/2026)")
                return
        
        # Limpiar mensajes
        self.message_text.clear()
        self.calculate_btn.setEnabled(False)
        self.continue_btn.setEnabled(False)
        self.status_label.setText("⏳ Calculando nómina... Por favor espere.")
        self.status_label.setStyleSheet(f"font-size: 11pt; font-weight: bold; color: {get_colors().YELLOW};")
        
        # Mostrar mensaje de inicio
        self.message_text.append("Calculando nómina...")
        self.message_text.append(f"Archivo de empleados: {employees_file}")
        self.message_text.append(f"Archivo de reporte de asistencia: {hours_file}")
        if quincena_fecha:
            self.message_text.append(f"Fecha de referencia: {quincena_fecha}")
        self.message_text.append("-" * 60)
        
        # Ejecutar cálculo en hilo separado
        self.calc_thread = CalculatePayrollThread(employees_file, hours_file, quincena_fecha)
        self.calc_thread.finished.connect(self.update_result)
        self.calc_thread.error.connect(self.show_error)
        self.calc_thread.start()
    
    def update_result(self, result, output_text):
        """Actualiza la interfaz con el resultado del cálculo"""
        self.message_text.append(output_text)
        
        if result is not None:
            self.message_text.append("\n" + "=" * 60)
            self.message_text.append("✓ NÓMINA CALCULADA EXITOSAMENTE")
            self.message_text.append("=" * 60)
            self.status_label.setText("✓ Nómina calculada exitosamente. Presione 'Continuar' para realizar otra operación.")
            self.status_label.setStyleSheet(f"font-size: 11pt; font-weight: bold; color: {get_colors().GREEN};")
            self.calculate_btn.setEnabled(True)
            self.continue_btn.setEnabled(True)
            QMessageBox.information(
                self,
                "Éxito",
                "La nómina ha sido calculada exitosamente.\n\nRevise el área de mensajes para ver los detalles.\n\nPresione 'Continuar' para realizar otra operación."
            )
        else:
            self.status_label.setText("✗ Error al calcular la nómina. Revise los mensajes.")
            self.status_label.setStyleSheet(f"font-size: 11pt; font-weight: bold; color: {get_colors().RED};")
            self.calculate_btn.setEnabled(True)
            self.continue_btn.setEnabled(True)
            QMessageBox.critical(
                self,
                "Error",
                "No se pudo calcular la nómina.\n\nRevise el área de mensajes para ver los errores.\n\nPresione 'Continuar' para intentar nuevamente."
            )
    
    def show_error(self, error_msg):
        """Muestra un error en la interfaz"""
        self.message_text.append(f"\nERROR: {error_msg}")
        self.status_label.setText(f"✗ Error: {error_msg[:50]}...")
        self.status_label.setStyleSheet(f"font-size: 11pt; font-weight: bold; color: {get_colors().RED};")
        self.calculate_btn.setEnabled(True)
        self.continue_btn.setEnabled(True)
        QMessageBox.critical(
            self,
            "Error",
            f"Error al calcular la nómina:\n{error_msg}\n\nPresione 'Continuar' para intentar nuevamente."
        )


class ManageEmployeesWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Gestionar Empleados")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Título
        title = QLabel("GESTIONAR EMPLEADOS")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 20pt; font-weight: bold; color: {get_colors().AQUA}; margin: 10px;")
        layout.addWidget(title)
        
        # Botones de acción
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(10)
        
        buttons = [
            ("Ver Lista de Empleados", self.view_employees),
            ("Agregar Empleado", self.add_employee),
            ("Modificar Empleado", self.modify_employee),
            ("Eliminar Empleado", self.delete_employee)
        ]
        
        for text, command in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(command)
            # Usar AQUA para todos excepto eliminar (que usa RED)
            color = get_colors().RED if "Eliminar" in text else get_colors().AQUA
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {get_colors().BUTTON_TEXT};
                    border: 2px solid {color};
                    border-radius: 6px;
                    padding: 12px 25px;
                    font-size: 12pt;
                    min-width: 250px;
                }}
                QPushButton:hover {{
                    background-color: {get_colors().BG_LIGHT};
                    color: {color};
                }}
            """)
            button_layout.addWidget(btn)
        
        layout.addLayout(button_layout)
        
        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().FG};
                border: 2px solid {get_colors().BG_LIGHTER};
                border-radius: 6px;
                padding: 10px 30px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHTER};
                border-color: {get_colors().BLUE};
            }}
        """)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
    
    def view_employees(self):
        """Muestra la lista de empleados"""
        try:
            df = leer_empleados_normalizado()
            if df is None or df.empty:
                QMessageBox.information(self, "Información", "No hay empleados registrados.")
                return
            
            view_window = ViewEmployeesWindow(self, df)
            view_window.show()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al leer empleados:\n{str(e)}")
    
    def add_employee(self):
        """Abre ventana para agregar empleado"""
        add_window = AddEmployeeWindow(self)
        add_window.exec_()
    
    def modify_employee(self):
        """Abre ventana para modificar empleado"""
        modify_window = ModifyEmployeeWindow(self)
        modify_window.exec_()
    
    def delete_employee(self):
        """Elimina un empleado"""
        delete_window = DeleteEmployeeWindow(self)
        delete_window.exec_()


class ViewEmployeesWindow(QDialog):
    def __init__(self, parent, df):
        super().__init__(parent)
        self.setWindowTitle("Lista de Empleados")
        self.setMinimumSize(900, 500)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("LISTA DE EMPLEADOS")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {get_colors().AQUA}; margin: 10px;")
        layout.addWidget(title)
        
        # Tabla
        table = QTableWidget()
        table.setRowCount(len(df))
        table.setColumnCount(len(df.columns))
        table.setHorizontalHeaderLabels([col.replace('_', ' ').title() for col in df.columns])
        
        # Insertar datos
        for i, row in df.iterrows():
            for j, col in enumerate(df.columns):
                val = row[col]
                item_text = str(val) if pd.notna(val) else ''
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, j, item)
        
        # Configurar columnas para permitir scroll horizontal
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.horizontalHeader().setMinimumSectionSize(100)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(False)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Asegurar fondo oscuro para todas las celdas
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().FG};
                gridline-color: {get_colors().BG_LIGHTER};
            }}
            QTableWidget::item {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().FG};
            }}
            QTableWidget::item:selected {{
                background-color: {get_colors().BLUE};
                color: {get_colors().BUTTON_TEXT};
            }}
        """)
        
        layout.addWidget(table)
        
        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 10px 30px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().AQUA};
            }}
        """)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)


class AddEmployeeWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Agregar Empleado")
        self.setMinimumSize(500, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Título
        title = QLabel("AGREGAR NUEVO EMPLEADO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {get_colors().AQUA}; margin: 10px;")
        layout.addWidget(title)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.vars = {}
        fields = [
            ("ID (deje vacío para auto-generar):", "id"),
            ("Nombre:", "nombre"),
            ("Cargo:", "cargo"),
            ("Salario (por hora):", "salario"),
            ("Número de Cuenta:", "n_de_cuenta"),
            ("Banco:", "banco"),
            ("Tipo de Cuenta:", "tipo_de_cuenta"),
            ("Salario Fijo (S/N):", "salario_fijo"),
            ("Empleado Fijo (S/N):", "empleado_fijo"),
            ("Salario Mínimo (mensual):", "salario_minimo")
        ]
        
        for label_text, field_name in fields:
            line_edit = QLineEdit()
            self.vars[field_name] = line_edit
            form_layout.addRow(label_text, line_edit)
        
        layout.addLayout(form_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        add_btn = QPushButton("Agregar")
        add_btn.clicked.connect(self.add_employee)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 10px 25px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().AQUA};
            }}
        """)
        button_layout.addWidget(add_btn)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 10px 25px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().AQUA};
            }}
        """)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def add_employee(self):
        """Agrega el empleado"""
        import sys
        from io import StringIO
        import builtins
        
        original_input = builtins.input
        
        inputs = []
        id_val = self.vars['id'].text().strip()
        inputs.append(id_val if id_val else '')
        inputs.append(self.vars['nombre'].text().strip())
        inputs.append(self.vars['cargo'].text().strip())
        inputs.append(self.vars['salario'].text().strip())
        inputs.append(self.vars['n_de_cuenta'].text().strip())
        inputs.append(self.vars['banco'].text().strip())
        inputs.append(self.vars['tipo_de_cuenta'].text().strip())
        salario_fijo_val = self.vars['salario_fijo'].text().strip().upper()
        inputs.append('S' if salario_fijo_val == 'S' else 'N')
        empleado_fijo_val = self.vars['empleado_fijo'].text().strip().upper()
        inputs.append('S' if empleado_fijo_val == 'S' else 'N')
        
        if salario_fijo_val == 'S' and empleado_fijo_val == 'S':
            QMessageBox.critical(self, "Error", "Un empleado no puede ser 'Salario Fijo' y 'Empleado Fijo' al mismo tiempo")
            return
        
        if empleado_fijo_val == 'S':
            salario_minimo_val = self.vars['salario_minimo'].text().strip()
            if not salario_minimo_val:
                QMessageBox.critical(self, "Error", "El salario mínimo es obligatorio para empleados fijos")
                return
            try:
                float(salario_minimo_val)
            except ValueError:
                QMessageBox.critical(self, "Error", "El salario mínimo debe ser un número válido")
                return
            inputs.append(salario_minimo_val)
        else:
            inputs.append('')
        
        input_index = [0]
        
        def mock_input(prompt=''):
            if input_index[0] < len(inputs):
                result = inputs[input_index[0]]
                input_index[0] += 1
                return result
            return ''
        
        if not self.vars['nombre'].text().strip():
            QMessageBox.critical(self, "Error", "El nombre es obligatorio")
            return
        
        if not self.vars['salario'].text().strip():
            QMessageBox.critical(self, "Error", "El salario es obligatorio")
            return
        
        try:
            float(self.vars['salario'].text().strip())
        except ValueError:
            QMessageBox.critical(self, "Error", "El salario debe ser un número válido")
            return
        
        try:
            builtins.input = mock_input
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            result = agregar_empleado()
            
            sys.stdout = old_stdout
            builtins.input = original_input
            
            if result is not None:
                QMessageBox.information(self, "Éxito", "Empleado agregado exitosamente")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "No se pudo agregar el empleado.\nVerifique los datos e intente nuevamente.")
        
        except Exception as e:
            builtins.input = original_input
            sys.stdout = old_stdout
            QMessageBox.critical(self, "Error", f"Error al agregar empleado:\n{str(e)}")


class ModifyEmployeeWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Modificar Empleado")
        self.setMinimumSize(500, 650)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Título
        title = QLabel("MODIFICAR EMPLEADO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {get_colors().AQUA}; margin: 10px;")
        layout.addWidget(title)
        
        # ID del empleado
        id_layout = QHBoxLayout()
        id_label = QLabel("ID del Empleado:")
        id_layout.addWidget(id_label)
        
        self.id_edit = QLineEdit()
        id_layout.addWidget(self.id_edit)
        
        search_btn = QPushButton("Buscar Empleado")
        search_btn.clicked.connect(self.load_employee)
        search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 8px 15px;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().AQUA};
            }}
        """)
        id_layout.addWidget(search_btn)
        
        layout.addLayout(id_layout)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.vars = {}
        self.entries = []
        fields = [
            ("Nombre:", "nombre"),
            ("Cargo:", "cargo"),
            ("Salario (por hora):", "salario"),
            ("Número de Cuenta:", "n_de_cuenta"),
            ("Banco:", "banco"),
            ("Tipo de Cuenta:", "tipo_de_cuenta"),
            ("Salario Fijo (S/N):", "salario_fijo"),
            ("Empleado Fijo (S/N):", "empleado_fijo"),
            ("Salario Mínimo (mensual):", "salario_minimo")
        ]
        
        for label_text, field_name in fields:
            line_edit = QLineEdit()
            line_edit.setEnabled(False)
            self.vars[field_name] = line_edit
            self.entries.append(line_edit)
            form_layout.addRow(label_text, line_edit)
        
        layout.addLayout(form_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        self.modify_btn = QPushButton("Modificar")
        self.modify_btn.clicked.connect(self.modify_employee)
        self.modify_btn.setEnabled(False)
        self.modify_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 10px 25px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().AQUA};
            }}
        """)
        button_layout.addWidget(self.modify_btn)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 10px 25px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().AQUA};
            }}
        """)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_employee(self):
        """Carga los datos del empleado"""
        employee_id = self.id_edit.text().strip()
        if not employee_id:
            QMessageBox.critical(self, "Error", "Debe ingresar un ID")
            return
        
        try:
            df = leer_empleados_normalizado()
            if df is None or df.empty:
                QMessageBox.critical(self, "Error", "No hay empleados en la base de datos")
                return
            
            def normalize_id(id_val):
                if pd.isna(id_val):
                    return None
                if isinstance(id_val, float) and id_val.is_integer():
                    return str(int(id_val))
                return str(id_val).strip()
            
            ids_normalizados = df['ID'].apply(normalize_id)
            mask = ids_normalizados == employee_id.strip()
            employee = df[mask]
            
            if employee.empty:
                QMessageBox.critical(self, "Error", f"No se encontró un empleado con ID: {employee_id}")
                return
            
            emp = employee.iloc[0]
            
            self.vars['nombre'].setText(str(emp['nombre']))
            self.vars['cargo'].setText(str(emp.get('cargo', '')))
            self.vars['salario'].setText(str(emp['salario']))
            self.vars['n_de_cuenta'].setText(str(emp.get('n_de_cuenta', '')))
            self.vars['banco'].setText(str(emp.get('banco', '')))
            self.vars['tipo_de_cuenta'].setText(str(emp.get('tipo_de_cuenta', '')))
            salario_fijo_val = bool(emp.get('salario_fijo', False))
            empleado_fijo_val = bool(emp.get('empleado_fijo', False))
            salario_minimo_val = emp.get('salario_minimo', 0) if pd.notna(emp.get('salario_minimo')) else 0
            self.vars['salario_fijo'].setText('S' if salario_fijo_val else 'N')
            self.vars['empleado_fijo'].setText('S' if empleado_fijo_val else 'N')
            self.vars['salario_minimo'].setText(str(salario_minimo_val))
            
            for entry in self.entries:
                entry.setEnabled(True)
            self.modify_btn.setEnabled(True)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar empleado:\n{str(e)}")
    
    def modify_employee(self):
        """Modifica el empleado"""
        employee_id = self.id_edit.text().strip()
        if not employee_id:
            QMessageBox.critical(self, "Error", "Debe ingresar un ID")
            return
        
        import sys
        from io import StringIO
        import builtins
        
        original_input = builtins.input
        
        inputs = [
            employee_id,
            self.vars['nombre'].text().strip() or '',
            self.vars['cargo'].text().strip() or '',
            self.vars['salario'].text().strip() or '',
            self.vars['n_de_cuenta'].text().strip() or '',
            self.vars['banco'].text().strip() or '',
            self.vars['tipo_de_cuenta'].text().strip() or '',
            self.vars['salario_fijo'].text().strip().upper() or '',
            self.vars['empleado_fijo'].text().strip().upper() or '',
            self.vars['salario_minimo'].text().strip() or ''
        ]
        
        input_index = [0]
        
        def mock_input(prompt=''):
            if input_index[0] < len(inputs):
                result = inputs[input_index[0]]
                input_index[0] += 1
                return result
            return ''
        
        try:
            builtins.input = mock_input
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            result = modificar_empleado()
            
            sys.stdout = old_stdout
            builtins.input = original_input
            
            if result is not None:
                QMessageBox.information(self, "Éxito", "Empleado modificado exitosamente")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "No se pudo modificar el empleado.\nVerifique los datos e intente nuevamente.")
        
        except Exception as e:
            builtins.input = original_input
            sys.stdout = old_stdout
            QMessageBox.critical(self, "Error", f"Error al modificar empleado:\n{str(e)}")


class DeleteEmployeeWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Eliminar Empleado")
        self.setMinimumSize(400, 200)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Título
        title = QLabel("ELIMINAR EMPLEADO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {get_colors().AQUA}; margin: 10px;")
        layout.addWidget(title)
        
        # ID
        id_label = QLabel("ID del Empleado:")
        layout.addWidget(id_label)
        
        self.id_edit = QLineEdit()
        layout.addWidget(self.id_edit)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        delete_btn = QPushButton("Eliminar")
        delete_btn.clicked.connect(self.delete_employee)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().RED};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().RED};
                border-radius: 6px;
                padding: 10px 25px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().RED};
            }}
        """)
        button_layout.addWidget(delete_btn)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 10px 25px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().AQUA};
            }}
        """)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def delete_employee(self):
        """Elimina el empleado"""
        employee_id = self.id_edit.text().strip()
        if not employee_id:
            QMessageBox.critical(self, "Error", "Debe ingresar un ID")
            return
        
        import sys
        from io import StringIO
        import builtins
        
        original_input = builtins.input
        
        inputs = [employee_id, 'S']
        
        input_index = [0]
        
        def mock_input(prompt=''):
            if input_index[0] < len(inputs):
                result = inputs[input_index[0]]
                input_index[0] += 1
                return result
            return ''
        
        try:
            builtins.input = mock_input
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            result = eliminar_empleado()
            
            sys.stdout = old_stdout
            builtins.input = original_input
            
            if result is not None:
                QMessageBox.information(self, "Éxito", "Empleado eliminado exitosamente")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar el empleado.\nVerifique el ID e intente nuevamente.")
        
        except Exception as e:
            builtins.input = original_input
            sys.stdout = old_stdout
            QMessageBox.critical(self, "Error", f"Error al eliminar empleado:\n{str(e)}")


def main():
    app = QApplication(sys.argv)
    GruvboxStyle.apply_style(app, CURRENT_THEME)

    window = NominaApp(app)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
