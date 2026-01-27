import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QMessageBox, QTextEdit, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea, QGroupBox, QFrame, QDialog,
    QDialogButtonBox, QFormLayout, QSizePolicy, QRadioButton, QComboBox, QDateEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QDate
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor, QIcon
from datetime import datetime
import pandas as pd
import os
from main import (
    calculate_payroll_quincenal,
    agregar_empleado,
    eliminar_empleado,
    modificar_empleado,
    leer_empleados_normalizado,
    ensure_prestamos_file,
    obtener_prestamos,
    crear_prestamo,
    actualizar_estado_prestamo,
    cerrar_prestamo,
    obtener_pagos_prestamo,
    registrar_pago_manual_prestamo,
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
    # Botones "Salir" (menos saturado, tipo vino)
    EXIT = '#c06c84'
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
    # Botones "Salir" (menos saturado, tipo vino)
    EXIT = '#c06c84'
    PURPLE = '#71C9CE'

    GRAY = '#666666'
    BUTTON_TEXT = '#000000'  # negro sobre botones de acento


# Tema actual y selector
CURRENT_THEME = 'aqua'


def get_colors():
    """Devuelve la paleta del tema actual."""
    return GruvboxColors if CURRENT_THEME == 'gruvbox' else AquaColors


def adjust_window_to_screen(window, width_ratio=0.85, height_ratio=0.85, min_width_ratio=0.55, min_height_ratio=0.55):
    """
    Ajusta el tamaño de una ventana a la pantalla disponible, evitando tamaños fijos
    que puedan verse mal en resoluciones pequeñas o grandes.
    """
    try:
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        w = max(400, int(geo.width() * width_ratio))
        h = max(300, int(geo.height() * height_ratio))
        window.resize(w, h)
        window.setMinimumSize(
            max(360, min(geo.width(), int(geo.width() * min_width_ratio))),
            max(260, min(geo.height(), int(geo.height() * min_height_ratio))),
        )
        # Centrar
        frame = window.frameGeometry()
        frame.moveCenter(geo.center())
        window.move(frame.topLeft())
    except Exception:
        # Si falla, no bloquear la UI
        return


def style_danger_button(btn: QPushButton):
    """
    Aplica el estilo de botón de acción peligrosa (Eliminar / Salir):
    - Ancho angosto y consistente
    - Texto y borde en color vino (EXIT/RED)
    - Fondo neutro para combinar con el tema actual
    """
    C = get_colors()
    color = getattr(C, "EXIT", C.RED)
    btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    btn.setMinimumWidth(160)
    btn.setMaximumWidth(220)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {C.BG_LIGHT};
            color: {color};
            border: 2px solid {color};
            border-radius: 8px;
            padding: 8px 18px;
            font-weight: bold;
            font-size: 11pt;
        }}
        QPushButton:hover {{
            background-color: {C.BG_LIGHTER};
            color: {color};
            border-color: {color};
        }}
    """)


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
            color: {C.FG if theme == 'aqua' else C.AQUA};
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
        adjust_window_to_screen(self, width_ratio=0.65, height_ratio=0.75, min_width_ratio=0.50, min_height_ratio=0.55)
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
        self._buttons_container = QWidget()
        self._buttons_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        button_layout = QVBoxLayout(self._buttons_container)
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(15)

        self.main_buttons = []
        buttons = [
            ("Calcular Nómina Quincenal", self.open_calculate_payroll),
            ("Gestionar Empleados", self.open_manage_employees),
            ("Gestionar Préstamos", self.open_manage_loans),
            ("Ver Nómina", self.view_payroll),
            ("Ver Información", self.show_info),
            ("Salir", self.close),
        ]
        for text, command in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(command)
            self.main_buttons.append((btn, text == "Salir"))
            button_layout.addWidget(btn)

        main_layout.addWidget(self._buttons_container, alignment=Qt.AlignCenter)
        self._apply_theme_to_widgets()
        self._update_main_buttons_container_width()

        # Espaciador para centrar verticalmente
        main_layout.addStretch()

    def _update_main_buttons_container_width(self):
        """
        Mantiene los botones más angostos sin perder adaptabilidad.
        Ajusta el ancho del contenedor en función del tamaño de la ventana.
        """
        try:
            # 55% del ancho actual, con límites para pantallas pequeñas/grandes
            target = int(self.width() * 0.55)
            target = max(300, min(target, 560))
            self._buttons_container.setMaximumWidth(target)
        except Exception:
            pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_main_buttons_container_width()

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
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            if is_exit:
                exit_color = getattr(C, "EXIT", C.RED)
                # Normal: mismo estilo "hover" (fondo neutro, texto/borde vino)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {C.BG_LIGHT};
                        color: {exit_color};
                        border: 2px solid {exit_color};
                        border-radius: 8px;
                        padding: 10px 20px;
                        font-weight: bold;
                        font-size: 11pt;
                    }}
                    QPushButton:hover {{
                        background-color: {C.BG_LIGHTER};
                        color: {exit_color};
                        border-color: {exit_color};
                    }}
                    QPushButton:pressed {{
                        background-color: {C.BG_LIGHTER};
                    }}
                """)
            else:
                color = C.AQUA
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        color: {C.BUTTON_TEXT};
                        border: 2px solid {color};
                        border-radius: 8px;
                        padding: 10px 20px;
                        font-weight: bold;
                        font-size: 11pt;
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

    def open_manage_loans(self):
        """Abre la ventana para gestionar préstamos"""
        self.loans_window = ManageLoansWindow(self)
        self.loans_window.show()
    
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
• Gestionar préstamos:
  - Crear préstamo y definir cuota quincenal
  - Pausar / reanudar
  - Registrar pago manual
  - Ver pagos (NÓMINA / MANUAL) con bitácora
  - Cierre automático al saldar
• Empleados de Seguridad (turnos):
  - Turno configurable (por defecto 12h)
  - Soporta turnos que cruzan medianoche (entrada/salida se emparejan consecutivamente)
  - Margen de salida configurable (± minutos)
  - Tolerancia de duración configurable (genera alertas si las marcas no cuadran)
• Cálculo automático de horas extra (25% adicional después de las 3 PM)
• Cálculo automático de pago por feriados/domingos (50% adicional)
• Ventanas adaptables a la resolución de la pantalla

ARCHIVOS REQUERIDOS:
• employees_information.xlsx - Información de empleados
• Reporte de Asistencia.xlsx - Reporte de asistencia del escáner biométrico
• prestamos.xlsx - Control de préstamos y bitácora de pagos (se crea automáticamente si no existe)
• seguridad_horario.xlsx - Configuración de turnos de seguridad (se crea automáticamente si no existe)

TIPOS DE EMPLEADOS:
• Salario Fijo: Cobran lo mismo sin importar las horas trabajadas
• Empleado Fijo: Tienen un sueldo mínimo garantizado + bono por horas extra
  si trabajan más de las horas requeridas para ese sueldo
• Por Horas: Reciben pago según horas trabajadas con bonos por horas extra
• Seguridad: Cobra como “Por Horas”, pero con turnos configurables (ej. 12h)

IMPORTANTE:
• Se requiere exactamente 2 registros por día por empleado (entrada y salida)
  (Excepto Seguridad: puede cruzar medianoche y se valida por pares de registros)
• Los empleados fijos no pueden ser ambos tipos a la vez
• Seguridad no puede ser “Salario Fijo” ni “Empleado Fijo”
        """
        QMessageBox.information(self, "Información del Sistema", info_text)


class ViewPayrollWindow(QDialog):
    def __init__(self, parent, df, total_general, filename):
        super().__init__(parent)
        self.setWindowTitle("Nómina Quincenal")
        adjust_window_to_screen(self, width_ratio=0.90, height_ratio=0.85, min_width_ratio=0.60, min_height_ratio=0.60)
        self._is_fullscreen = False
        
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
                elif isinstance(val, (int, float)) and ('Pago' in col or 'Total' in col or 'Salario' in col or 'Bono' in col or 'Seguro' in col or 'ISLR' in col or 'Descuento' in col):
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
        
        # Botones de acción
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(10)
        
        fullscreen_btn = QPushButton("Pantalla Completa")
        fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        fullscreen_btn.setStyleSheet(f"""
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
        button_layout.addWidget(fullscreen_btn)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border: 2px solid {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border-radius: 6px;
                padding: 10px 30px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHTER};
                color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border-color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
            }}
        """)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def toggle_fullscreen(self):
        """Alterna entre pantalla completa y modo ventana"""
        if self._is_fullscreen:
            self.showNormal()
            self._is_fullscreen = False
        else:
            self.showFullScreen()
            self._is_fullscreen = True


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
        adjust_window_to_screen(self, width_ratio=0.70, height_ratio=0.80, min_width_ratio=0.55, min_height_ratio=0.60)
        self._is_fullscreen = False
        
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
        self.calculate_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.calculate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12pt;
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
        self.continue_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.continue_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().AQUA};
            }}
        """)
        button_layout.addWidget(self.continue_btn)
        
        fullscreen_btn = QPushButton("Pantalla Completa")
        fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        fullscreen_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        fullscreen_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().AQUA};
            }}
        """)
        button_layout.addWidget(fullscreen_btn)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        close_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border: 2px solid {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHTER};
                color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border-color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
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
    
    def toggle_fullscreen(self):
        """Alterna entre pantalla completa y modo ventana"""
        if self._is_fullscreen:
            self.showNormal()
            self._is_fullscreen = False
        else:
            self.showFullScreen()
            self._is_fullscreen = True
    
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
        adjust_window_to_screen(self, width_ratio=0.70, height_ratio=0.80, min_width_ratio=0.55, min_height_ratio=0.60)
        self._is_fullscreen = False
        
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
            ("Eliminar Empleado", self.delete_employee),
        ]
        
        for text, command in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(command)
            # Mantener adaptabilidad vertical pero limitar el ancho para que no sean tan largos
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setMaximumWidth(380)  # similar al ancho visual de los botones de la ventana principal
            
            if "Eliminar" in text:
                # Misma estética que los botones de Cerrar (fondo claro, texto/borde rojo)
                exit_color = get_colors().EXIT if hasattr(get_colors(), "EXIT") else get_colors().RED
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {get_colors().BG_LIGHT};
                        color: {exit_color};
                        border: 2px solid {exit_color};
                        border-radius: 6px;
                        padding: 8px 22px;
                        font-size: 11pt;
                    }}
                    QPushButton:hover {{
                        background-color: {get_colors().BG_LIGHTER};
                        color: {exit_color};
                        border-color: {exit_color};
                    }}
                """)
            else:
                # Botones más angostos (menos padding y fuente ligeramente menor)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {get_colors().AQUA};
                        color: {get_colors().BUTTON_TEXT};
                        border: 2px solid {get_colors().AQUA};
                        border-radius: 6px;
                        padding: 8px 22px;
                        font-size: 11pt;
                    }}
                    QPushButton:hover {{
                        background-color: {get_colors().BG_LIGHT};
                        color: {get_colors().AQUA};
                    }}
                """)
            
            button_layout.addWidget(btn, alignment=Qt.AlignCenter)
        
        layout.addLayout(button_layout)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(10)
        
        fullscreen_btn = QPushButton("Pantalla Completa")
        fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        fullscreen_btn.setStyleSheet(f"""
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
        button_layout.addWidget(fullscreen_btn)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border: 2px solid {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border-radius: 6px;
                padding: 10px 30px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHTER};
                color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border-color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
            }}
        """)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def toggle_fullscreen(self):
        """Alterna entre pantalla completa y modo ventana"""
        if self._is_fullscreen:
            self.showNormal()
            self._is_fullscreen = False
        else:
            self.showFullScreen()
            self._is_fullscreen = True
    
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
        adjust_window_to_screen(self, width_ratio=0.90, height_ratio=0.80, min_width_ratio=0.60, min_height_ratio=0.55)
        self._is_fullscreen = False
        
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
        
        # Botones de acción
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(10)
        
        fullscreen_btn = QPushButton("Pantalla Completa")
        fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        fullscreen_btn.setStyleSheet(f"""
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
        button_layout.addWidget(fullscreen_btn)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border: 2px solid {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border-radius: 6px;
                padding: 10px 30px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHTER};
                color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border-color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
            }}
        """)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def toggle_fullscreen(self):
        """Alterna entre pantalla completa y modo ventana"""
        if self._is_fullscreen:
            self.showNormal()
            self._is_fullscreen = False
        else:
            self.showFullScreen()
            self._is_fullscreen = True


class AddEmployeeWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Agregar Empleado")
        adjust_window_to_screen(self, width_ratio=0.55, height_ratio=0.80, min_width_ratio=0.45, min_height_ratio=0.60)
        
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
            ("Seguridad (S/N):", "seguridad"),
            ("Salario Mínimo (mensual):", "salario_minimo"),
            ("Empleado por contrato (S/N):", "empleado_por_contrato"),
            ("ISLR (Impuesto sobre la renta):", "islr")
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
        seguridad_val = self.vars['seguridad'].text().strip().upper()
        inputs.append('S' if seguridad_val == 'S' else 'N')
        empleado_contrato_val = self.vars['empleado_por_contrato'].text().strip().upper()
        inputs.append('S' if empleado_contrato_val == 'S' else 'N')
        islr_val = self.vars['islr'].text().strip()
        inputs.append(islr_val if islr_val else '')
        
        if salario_fijo_val == 'S' and empleado_fijo_val == 'S':
            QMessageBox.critical(self, "Error", "Un empleado no puede ser 'Salario Fijo' y 'Empleado Fijo' al mismo tiempo")
            return

        if seguridad_val == 'S' and (salario_fijo_val == 'S' or empleado_fijo_val == 'S'):
            QMessageBox.critical(self, "Error", "Un empleado de Seguridad no puede ser 'Salario Fijo' ni 'Empleado Fijo'. Debe cobrar por hora.")
            return
        
        if empleado_contrato_val == 'S':
            islr_val = self.vars['islr'].text().strip()
            if not islr_val:
                QMessageBox.critical(self, "Error", "El ISLR es obligatorio para empleados por contrato")
                return
            try:
                float(islr_val)
            except ValueError:
                QMessageBox.critical(self, "Error", "El ISLR debe ser un número válido")
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
        adjust_window_to_screen(self, width_ratio=0.55, height_ratio=0.85, min_width_ratio=0.45, min_height_ratio=0.60)
        
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
            ("Seguridad (S/N):", "seguridad"),
            ("Salario Mínimo (mensual):", "salario_minimo"),
            ("Empleado por contrato (S/N):", "empleado_por_contrato"),
            ("ISLR (Impuesto sobre la renta):", "islr")
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
            seguridad_val = str(emp.get('seguridad', 'No')).strip().lower() in ['s', 'si', 'sí', 'yes', 'y', 'true', '1']
            salario_minimo_val = emp.get('salario_minimo', 0) if pd.notna(emp.get('salario_minimo')) else 0
            empleado_contrato_val = emp.get('Empleado por contrato', 'No')
            islr_val = emp.get('ISLR', 0) if pd.notna(emp.get('ISLR')) else 0
            self.vars['salario_fijo'].setText('S' if salario_fijo_val else 'N')
            self.vars['empleado_fijo'].setText('S' if empleado_fijo_val else 'N')
            self.vars['seguridad'].setText('S' if seguridad_val else 'N')
            self.vars['salario_minimo'].setText(str(salario_minimo_val))
            self.vars['empleado_por_contrato'].setText('S' if str(empleado_contrato_val).strip().lower() in ['s', 'si', 'sí', 'yes', 'y', 'true', '1'] else 'N')
            self.vars['islr'].setText(str(islr_val))
            
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

        salario_fijo_val = self.vars['salario_fijo'].text().strip().upper()
        empleado_fijo_val = self.vars['empleado_fijo'].text().strip().upper()
        seguridad_val = self.vars.get('seguridad').text().strip().upper() if 'seguridad' in self.vars else 'N'
        if seguridad_val == 'S' and (salario_fijo_val == 'S' or empleado_fijo_val == 'S'):
            QMessageBox.critical(self, "Error", "Un empleado de Seguridad no puede ser 'Salario Fijo' ni 'Empleado Fijo'. Debe cobrar por hora.")
            return

        empleado_contrato_val = self.vars['empleado_por_contrato'].text().strip().upper()
        islr_val = self.vars['islr'].text().strip()
        if empleado_contrato_val == 'S':
            if not islr_val:
                QMessageBox.critical(self, "Error", "El ISLR es obligatorio para empleados por contrato")
                return
            try:
                float(islr_val)
            except ValueError:
                QMessageBox.critical(self, "Error", "El ISLR debe ser un número válido")
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
            self.vars['seguridad'].text().strip().upper() or '',
            self.vars['empleado_por_contrato'].text().strip().upper() or '',
            self.vars['islr'].text().strip() or '',
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
        adjust_window_to_screen(self, width_ratio=0.50, height_ratio=0.40, min_width_ratio=0.40, min_height_ratio=0.35)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Título
        title = QLabel("ELIMINAR EMPLEADO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {get_colors().AQUA}; margin: 10px;")
        layout.addWidget(title)
        
        # Selección de empleado
        emp_label = QLabel("Seleccione el empleado:")
        layout.addWidget(emp_label)

        self.employee_combo = QComboBox()
        self.employee_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.employee_combo)

        self.employee_info = QLabel("")
        self.employee_info.setAlignment(Qt.AlignCenter)
        self.employee_info.setStyleSheet(f"font-size: 11pt; color: {get_colors().FG_DARK};")
        layout.addWidget(self.employee_info)

        self._load_employees()
        self.employee_combo.currentIndexChanged.connect(self._update_info)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        delete_btn = QPushButton("Eliminar")
        delete_btn.clicked.connect(self.delete_employee)
        delete_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        delete_btn.setMaximumWidth(220)
        exit_color = get_colors().EXIT if hasattr(get_colors(), "EXIT") else get_colors().RED
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().BG_LIGHT};
                color: {exit_color};
                border: 2px solid {exit_color};
                border-radius: 6px;
                padding: 8px 22px;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHTER};
                color: {exit_color};
                border-color: {exit_color};
            }}
        """)
        button_layout.addWidget(delete_btn)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cancel_btn.setMaximumWidth(220)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 8px 22px;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().AQUA};
            }}
        """)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)

    def _load_employees(self):
        self.employee_combo.clear()
        try:
            df = leer_empleados_normalizado()
            if df is None or df.empty:
                self.employee_combo.addItem("No hay empleados registrados", "")
                self.employee_combo.setEnabled(False)
                self.employee_info.setText("")
                return

            # Ordenar por nombre si existe
            if "nombre" in df.columns:
                df = df.sort_values("nombre")

            for _, row in df.iterrows():
                emp_id = str(row.get("ID", "")).strip()
                nombre = str(row.get("nombre", "")).strip()
                cargo = str(row.get("cargo", "")).strip()
                if emp_id:
                    label = f"{emp_id} - {nombre}" + (f" ({cargo})" if cargo else "")
                    self.employee_combo.addItem(label, emp_id)

            self.employee_combo.setEnabled(True)
            self._update_info()
        except Exception:
            self.employee_combo.addItem("No se pudieron cargar empleados", "")
            self.employee_combo.setEnabled(False)
            self.employee_info.setText("")

    def _update_info(self):
        emp_id = str(self.employee_combo.currentData() or "").strip()
        if not emp_id:
            self.employee_info.setText("")
            return
        self.employee_info.setText(f"ID seleccionado: {emp_id}")
    
    def delete_employee(self):
        """Elimina el empleado"""
        employee_id = str(self.employee_combo.currentData() or "").strip()
        employee_label = self.employee_combo.currentText()
        if not employee_id:
            QMessageBox.critical(self, "Error", "Debe seleccionar un empleado")
            return

        resp = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar este empleado?\n\n{employee_label}",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
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


class ManageLoansWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Gestionar Préstamos")
        adjust_window_to_screen(self, width_ratio=0.90, height_ratio=0.85, min_width_ratio=0.60, min_height_ratio=0.60)
        self._is_fullscreen = False

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("GESTIONAR PRÉSTAMOS")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"font-size: 20pt; font-weight: bold; color: {get_colors().AQUA}; margin: 10px;"
        )
        layout.addWidget(title)

        # Filtro por empleado (para ver sus préstamos)
        filter_row = QHBoxLayout()
        filter_row.setAlignment(Qt.AlignCenter)
        filter_row.setSpacing(10)

        filter_label = QLabel("Empleado:")
        filter_label.setStyleSheet(f"font-size: 12pt; color: {get_colors().FG_DARK};")
        filter_row.addWidget(filter_label)

        self.employee_filter = QComboBox()
        self.employee_filter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.employee_filter.addItem("Todos", "")
        try:
            df_emp = leer_empleados_normalizado()
            if df_emp is not None and not df_emp.empty:
                for _, row in df_emp.iterrows():
                    emp_id = str(row.get("ID", "")).strip()
                    nombre = str(row.get("nombre", "")).strip()
                    if emp_id:
                        self.employee_filter.addItem(f"{emp_id} - {nombre}", emp_id)
        except Exception:
            # Si falla, dejamos el filtro en "Todos"
            pass

        self.employee_filter.currentIndexChanged.connect(self.refresh_loans)
        filter_row.addWidget(self.employee_filter, 1)

        layout.addLayout(filter_row)

        # Tabla
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setMinimumSectionSize(110)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setStyleSheet(f"""
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
        layout.addWidget(self.table)

        # Botones de acción
        actions = QHBoxLayout()
        actions.setAlignment(Qt.AlignCenter)
        actions.setSpacing(10)

        refresh_btn = QPushButton("Actualizar")
        refresh_btn.clicked.connect(self.refresh_loans)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().AQUA};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().AQUA};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().AQUA};
            }}
        """)
        actions.addWidget(refresh_btn)

        new_btn = QPushButton("Nuevo Préstamo")
        new_btn.clicked.connect(self.new_loan)
        new_btn.setStyleSheet(refresh_btn.styleSheet())
        actions.addWidget(new_btn)

        toggle_btn = QPushButton("Pausar / Reanudar")
        toggle_btn.clicked.connect(self.toggle_loan)
        toggle_btn.setStyleSheet(refresh_btn.styleSheet())
        actions.addWidget(toggle_btn)

        payments_btn = QPushButton("Ver Pagos")
        payments_btn.clicked.connect(self.view_payments)
        payments_btn.setStyleSheet(refresh_btn.styleSheet())
        actions.addWidget(payments_btn)

        manual_payment_btn = QPushButton("Registrar Pago Manual")
        manual_payment_btn.clicked.connect(self.manual_payment)
        manual_payment_btn.setStyleSheet(refresh_btn.styleSheet())
        actions.addWidget(manual_payment_btn)

        close_loan_btn = QPushButton("Cerrar Préstamo")
        close_loan_btn.clicked.connect(self.close_loan)
        close_loan_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().ORANGE};
                color: {get_colors().BUTTON_TEXT};
                border: 2px solid {get_colors().ORANGE};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().ORANGE};
            }}
        """)
        actions.addWidget(close_loan_btn)

        layout.addLayout(actions)

        # Barra inferior
        bottom = QHBoxLayout()
        bottom.setAlignment(Qt.AlignCenter)
        bottom.setSpacing(10)

        fullscreen_btn = QPushButton("Pantalla Completa")
        fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        fullscreen_btn.setStyleSheet(f"""
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
        bottom.addWidget(fullscreen_btn)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border: 2px solid {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border-radius: 6px;
                padding: 10px 30px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHTER};
                color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border-color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
            }}
        """)
        bottom.addWidget(close_btn)

        layout.addLayout(bottom)

        self._loans_df = pd.DataFrame()
        self.refresh_loans()

    def toggle_fullscreen(self):
        if self._is_fullscreen:
            self.showNormal()
            self._is_fullscreen = False
        else:
            self.showFullScreen()
            self._is_fullscreen = True

    def refresh_loans(self):
        try:
            ensure_prestamos_file()
            df = obtener_prestamos()
            if df is None or df.empty:
                self._loans_df = pd.DataFrame()
                self.table.setRowCount(0)
                self.table.setColumnCount(0)
                return

            # Preparar DF para visualización
            df = df.copy()

            # Aplicar filtro por empleado si está seleccionado
            selected_emp_id = ""
            try:
                selected_emp_id = str(self.employee_filter.currentData() or "").strip()
            except Exception:
                selected_emp_id = ""
            if selected_emp_id:
                df = df[df["employee_id"].astype(str).str.strip() == selected_emp_id].copy()
                if df.empty:
                    self._loans_df = pd.DataFrame()
                    self.table.setRowCount(0)
                    self.table.setColumnCount(0)
                    self.table.setHorizontalHeaderLabels([])
                    return

            for c in ["monto_original_centavos", "cuota_quincenal_centavos", "saldo_centavos"]:
                if c not in df.columns:
                    df[c] = 0

            df["Monto"] = df["monto_original_centavos"].fillna(0).astype(int) / 100.0
            df["Cuota Quincenal"] = df["cuota_quincenal_centavos"].fillna(0).astype(int) / 100.0
            df["Saldo"] = df["saldo_centavos"].fillna(0).astype(int) / 100.0
            if "fecha_inicio" in df.columns:
                df["Fecha Inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce").dt.strftime("%d/%m/%Y")
            else:
                df["Fecha Inicio"] = ""

            cols = [
                "loan_id",
                "employee_id",
                "employee_name",
                "estado",
                "Fecha Inicio",
                "Monto",
                "Cuota Quincenal",
                "Saldo",
                "nota",
            ]
            for c in cols:
                if c not in df.columns:
                    df[c] = ""

            df_view = df[cols].copy()
            df_view = df_view.rename(
                columns={
                    "loan_id": "Loan ID",
                    "employee_id": "ID Empleado",
                    "employee_name": "Empleado",
                    "estado": "Estado",
                    "nota": "Nota",
                }
            )

            self._loans_df = df_view

            self.table.setRowCount(len(df_view))
            self.table.setColumnCount(len(df_view.columns))
            self.table.setHorizontalHeaderLabels(df_view.columns)

            for i, row in df_view.iterrows():
                for j, col in enumerate(df_view.columns):
                    val = row[col]
                    if pd.isna(val):
                        item_text = ""
                    elif isinstance(val, (int, float)) and (("Monto" in col) or ("Cuota" in col) or ("Saldo" in col)):
                        item_text = f"${val:,.2f}"
                    else:
                        item_text = str(val)
                    item = QTableWidgetItem(item_text)
                    item.setTextAlignment(Qt.AlignCenter)
                    if ("Monto" in col) or ("Cuota" in col) or ("Saldo" in col):
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table.setItem(i, j, item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar préstamos:\n{str(e)}")

    def _get_selected_loan_id(self):
        row = self.table.currentRow()
        if row < 0 or self.table.columnCount() == 0:
            return None
        # La primera columna es Loan ID
        item = self.table.item(row, 0)
        return item.text().strip() if item else None

    def _get_selected_loan_row(self):
        loan_id = self._get_selected_loan_id()
        if not loan_id or self._loans_df is None or self._loans_df.empty:
            return None
        mask = self._loans_df["Loan ID"].astype(str).str.strip() == loan_id
        if not mask.any():
            return None
        return self._loans_df[mask].iloc[0]

    def new_loan(self):
        dlg = AddLoanDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.refresh_loans()

    def toggle_loan(self):
        selected = self._get_selected_loan_row()
        if selected is None:
            QMessageBox.information(self, "Información", "Seleccione un préstamo.")
            return
        loan_id = str(selected["Loan ID"]).strip()
        estado = str(selected.get("Estado", "")).strip().upper()
        if estado == "CERRADO":
            QMessageBox.information(self, "Información", "Este préstamo ya está cerrado.")
            return

        nuevo = "PAUSADO" if estado == "ACTIVO" else "ACTIVO"
        try:
            actualizar_estado_prestamo(loan_id, nuevo)
            self.refresh_loans()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el estado:\n{str(e)}")

    def close_loan(self):
        selected = self._get_selected_loan_row()
        if selected is None:
            QMessageBox.information(self, "Información", "Seleccione un préstamo.")
            return
        loan_id = str(selected["Loan ID"]).strip()
        estado = str(selected.get("Estado", "")).strip().upper()
        if estado == "CERRADO":
            QMessageBox.information(self, "Información", "Este préstamo ya está cerrado.")
            return

        saldo_text = str(selected.get("Saldo", "0")).replace("$", "").replace(",", "").strip()
        try:
            saldo_val = float(saldo_text) if saldo_text else 0.0
        except Exception:
            saldo_val = 0.0

        if saldo_val > 0:
            resp = QMessageBox.question(
                self,
                "Confirmar cierre",
                "Este préstamo aún tiene saldo.\n\n¿Desea CONDONAR el saldo (ponerlo en 0) y cerrar el préstamo?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if resp != QMessageBox.Yes:
                return
            condonar = True
        else:
            condonar = False

        try:
            cerrar_prestamo(loan_id, condonar=condonar)
            self.refresh_loans()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cerrar el préstamo:\n{str(e)}")

    def view_payments(self):
        selected = self._get_selected_loan_row()
        if selected is None:
            QMessageBox.information(self, "Información", "Seleccione un préstamo.")
            return
        loan_id = str(selected["Loan ID"]).strip()
        empleado = str(selected.get("Empleado", "")).strip()
        dlg = ViewLoanPaymentsWindow(self, loan_id, empleado)
        dlg.exec_()

    def manual_payment(self):
        selected = self._get_selected_loan_row()
        if selected is None:
            QMessageBox.information(self, "Información", "Seleccione un préstamo.")
            return
        loan_id = str(selected["Loan ID"]).strip()
        empleado = str(selected.get("Empleado", "")).strip()
        saldo_text = str(selected.get("Saldo", "0")).replace("$", "").replace(",", "").strip()
        try:
            saldo_val = float(saldo_text) if saldo_text else 0.0
        except Exception:
            saldo_val = 0.0

        dlg = ManualPaymentDialog(self, loan_id, empleado, saldo_val)
        if dlg.exec_() == QDialog.Accepted:
            self.refresh_loans()


class AddLoanDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Préstamo")
        adjust_window_to_screen(self, width_ratio=0.55, height_ratio=0.60, min_width_ratio=0.45, min_height_ratio=0.45)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("CREAR PRÉSTAMO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"font-size: 18pt; font-weight: bold; color: {get_colors().AQUA}; margin: 10px;"
        )
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        # Empleado
        self.employee_combo = QComboBox()
        try:
            df_emp = leer_empleados_normalizado()
            if df_emp is None or df_emp.empty:
                raise ValueError("No hay empleados registrados")
            for _, row in df_emp.iterrows():
                emp_id = str(row.get("ID", "")).strip()
                nombre = str(row.get("nombre", "")).strip()
                if emp_id:
                    self.employee_combo.addItem(f"{emp_id} - {nombre}", emp_id)
        except Exception:
            self.employee_combo.addItem("No se pudieron cargar empleados", "")
        form.addRow("Empleado:", self.employee_combo)

        self.monto_edit = QLineEdit()
        self.cuota_edit = QLineEdit()

        self.fecha_edit = QDateEdit()
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDisplayFormat("dd/MM/yyyy")
        self.fecha_edit.setDate(QDate.currentDate())

        self.nota_edit = QLineEdit()

        form.addRow("Monto préstamo ($):", self.monto_edit)
        form.addRow("Cuota quincenal ($):", self.cuota_edit)
        form.addRow("Fecha inicio:", self.fecha_edit)
        form.addRow("Nota (opcional):", self.nota_edit)

        layout.addLayout(form)

        buttons = QHBoxLayout()
        buttons.setAlignment(Qt.AlignCenter)
        buttons.setSpacing(10)

        create_btn = QPushButton("Crear")
        create_btn.clicked.connect(self._create)
        create_btn.setStyleSheet(f"""
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
        buttons.addWidget(create_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(create_btn.styleSheet())
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)

    def _create(self):
        emp_id = self.employee_combo.currentData()
        emp_text = self.employee_combo.currentText()
        if not emp_id:
            QMessageBox.critical(self, "Error", "Debe seleccionar un empleado válido.")
            return

        # Extraer nombre del texto "ID - Nombre"
        emp_name = emp_text.split(" - ", 1)[1].strip() if " - " in emp_text else ""

        monto_str = self.monto_edit.text().strip().replace(",", "")
        cuota_str = self.cuota_edit.text().strip().replace(",", "")
        try:
            monto = float(monto_str)
            cuota = float(cuota_str)
        except Exception:
            QMessageBox.critical(self, "Error", "Monto y cuota deben ser números válidos.")
            return

        fecha = self.fecha_edit.date().toPyDate()
        nota = self.nota_edit.text().strip()

        try:
            loan_id = crear_prestamo(emp_id, emp_name, monto, cuota, fecha_inicio=fecha, nota=nota)
            QMessageBox.information(self, "Éxito", f"Préstamo creado exitosamente.\n\nLoan ID: {loan_id}")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear el préstamo:\n{str(e)}")


class ViewLoanPaymentsWindow(QDialog):
    def __init__(self, parent, loan_id: str, empleado: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Pagos del Préstamo")
        adjust_window_to_screen(self, width_ratio=0.90, height_ratio=0.80, min_width_ratio=0.60, min_height_ratio=0.55)
        self._is_fullscreen = False

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("PAGOS DEL PRÉSTAMO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {get_colors().AQUA}; margin: 10px;")
        layout.addWidget(title)

        subtitle = QLabel(f"Loan ID: {loan_id}" + (f" | Empleado: {empleado}" if empleado else ""))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"font-size: 12pt; color: {get_colors().FG_DARK};")
        layout.addWidget(subtitle)

        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setMinimumSectionSize(110)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setStyleSheet(f"""
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
        layout.addWidget(self.table)

        # Botones
        btns = QHBoxLayout()
        btns.setAlignment(Qt.AlignCenter)
        btns.setSpacing(10)

        fullscreen_btn = QPushButton("Pantalla Completa")
        fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        fullscreen_btn.setStyleSheet(f"""
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
        btns.addWidget(fullscreen_btn)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors().BG_LIGHT};
                color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border: 2px solid {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border-radius: 6px;
                padding: 10px 30px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {get_colors().BG_LIGHTER};
                color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
                border-color: {get_colors().EXIT if hasattr(get_colors(), 'EXIT') else get_colors().RED};
            }}
        """)
        btns.addWidget(close_btn)

        layout.addLayout(btns)

        self._load(loan_id)

    def toggle_fullscreen(self):
        if self._is_fullscreen:
            self.showNormal()
            self._is_fullscreen = False
        else:
            self.showFullScreen()
            self._is_fullscreen = True

    def _load(self, loan_id: str):
        try:
            df = obtener_pagos_prestamo(loan_id=loan_id)
            if df is None or df.empty:
                self.table.setRowCount(0)
                self.table.setColumnCount(0)
                return

            df = df.copy()
            if "tipo_pago" in df.columns:
                df["Tipo"] = df["tipo_pago"].astype(str).str.upper().str.strip().replace({"": "NOMINA"})
            else:
                df["Tipo"] = "NOMINA"
            if "nota" in df.columns:
                df["Nota"] = df["nota"].astype(str)
            else:
                df["Nota"] = ""
            df["Fecha Pago Nómina"] = pd.to_datetime(df["fecha_pago_nomina"], errors="coerce").dt.strftime("%d/%m/%Y")
            df["Quincena Inicio"] = pd.to_datetime(df["quincena_inicio"], errors="coerce").dt.strftime("%d/%m/%Y")
            df["Quincena Fin"] = pd.to_datetime(df["quincena_fin"], errors="coerce").dt.strftime("%d/%m/%Y")
            df["Monto Pagado"] = df["monto_pagado_centavos"].fillna(0).astype(int) / 100.0
            df["Saldo Antes"] = df["saldo_antes_centavos"].fillna(0).astype(int) / 100.0
            df["Saldo Después"] = df["saldo_despues_centavos"].fillna(0).astype(int) / 100.0

            view_cols = [
                "Fecha Pago Nómina",
                "Tipo",
                "Monto Pagado",
                "Saldo Antes",
                "Saldo Después",
                "Quincena Inicio",
                "Quincena Fin",
                "Nota",
                "payment_id",
            ]
            df_view = df[view_cols].rename(columns={"payment_id": "Payment ID"})

            self.table.setRowCount(len(df_view))
            self.table.setColumnCount(len(df_view.columns))
            self.table.setHorizontalHeaderLabels(df_view.columns)

            for i, row in df_view.iterrows():
                for j, col in enumerate(df_view.columns):
                    val = row[col]
                    if pd.isna(val):
                        item_text = ""
                    elif isinstance(val, (int, float)) and ("Monto" in col or "Saldo" in col):
                        item_text = f"${val:,.2f}"
                    else:
                        item_text = str(val)
                    item = QTableWidgetItem(item_text)
                    item.setTextAlignment(Qt.AlignCenter)
                    if "Monto" in col or "Saldo" in col:
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table.setItem(i, j, item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los pagos:\n{str(e)}")


class ManualPaymentDialog(QDialog):
    def __init__(self, parent, loan_id: str, empleado: str, saldo: float):
        super().__init__(parent)
        self.setWindowTitle("Registrar Pago Manual")
        adjust_window_to_screen(self, width_ratio=0.55, height_ratio=0.55, min_width_ratio=0.45, min_height_ratio=0.45)

        self._loan_id = loan_id

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("PAGO MANUAL A PRÉSTAMO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {get_colors().AQUA}; margin: 10px;")
        layout.addWidget(title)

        info = QLabel(f"Loan ID: {loan_id}\nEmpleado: {empleado}\nSaldo actual: ${saldo:,.2f}")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet(f"font-size: 12pt; color: {get_colors().FG_DARK};")
        layout.addWidget(info)

        form = QFormLayout()
        form.setSpacing(10)

        self.amount_edit = QLineEdit()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setDate(QDate.currentDate())
        self.note_edit = QLineEdit()

        form.addRow("Monto a abonar ($):", self.amount_edit)
        form.addRow("Fecha de pago:", self.date_edit)
        form.addRow("Nota (opcional):", self.note_edit)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.setAlignment(Qt.AlignCenter)
        btns.setSpacing(10)

        save_btn = QPushButton("Registrar")
        save_btn.clicked.connect(self._save)
        save_btn.setStyleSheet(f"""
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
        btns.addWidget(save_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(save_btn.styleSheet())
        btns.addWidget(cancel_btn)

        layout.addLayout(btns)

    def _save(self):
        amount_str = self.amount_edit.text().strip().replace(",", "")
        try:
            amount = float(amount_str)
        except Exception:
            QMessageBox.critical(self, "Error", "El monto debe ser un número válido.")
            return

        fecha = self.date_edit.date().toPyDate()
        nota = self.note_edit.text().strip()

        try:
            registrar_pago_manual_prestamo(self._loan_id, amount, fecha_pago=fecha, nota=nota)
            QMessageBox.information(self, "Éxito", "Pago manual registrado exitosamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo registrar el pago manual:\n{str(e)}")


def main():
    app = QApplication(sys.argv)
    GruvboxStyle.apply_style(app, CURRENT_THEME)

    window = NominaApp(app)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()