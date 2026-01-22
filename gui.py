import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from datetime import datetime
import pandas as pd
import os
import threading
from main import (
    calculate_payroll_quincenal, 
    agregar_empleado, 
    eliminar_empleado, 
    modificar_empleado,
    leer_empleados_normalizado
)

# Paleta de colores: Negro, Cyan, Gris oscuro, Celeste
COLOR_BG_DARK = '#1e1e1e'  # Fondo oscuro
COLOR_BG_FRAME = '#2d2d2d'  # Gris oscuro para frames
COLOR_TEXT = '#ffffff'  # Texto blanco
COLOR_CYAN = '#00bcd4'  # Cyan
COLOR_CELESTE = '#87ceeb'  # Celeste
COLOR_BLACK = '#000000'  # Negro
COLOR_GRAY_DARK = '#3d3d3d'  # Gris oscuro adicional


class NominaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Nómina ABCOPA")
        self.root.geometry("900x700")
        self.root.configure(bg=COLOR_BG_DARK)
        
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TScrollbar', background=COLOR_BG_FRAME, troughcolor=COLOR_BG_DARK)
        
        # Canvas con scrollbar para permitir desplazamiento
        canvas = tk.Canvas(root, bg=COLOR_BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLOR_BG_DARK)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Centrar el contenido horizontalmente en el canvas
        def center_content(event=None):
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            if canvas_width > 1 and frame_width > 0:
                x = (canvas_width - frame_width) // 2
                canvas.coords(canvas.find_all()[0] if canvas.find_all() else None, max(0, x), 0)
        
        canvas.bind("<Configure>", center_content)
        scrollable_frame.bind("<Configure>", center_content)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Habilitar scroll con rueda del mouse (Windows)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Vincular scroll a la ventana cuando el mouse está sobre ella
        def _bind_mousewheel(event):
            self.root.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            self.root.unbind_all("<MouseWheel>")
        
        self.root.bind("<Enter>", _bind_mousewheel)
        self.root.bind("<Leave>", _unbind_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame principal centrado con ancho máximo
        center_container = tk.Frame(scrollable_frame, bg=COLOR_BG_DARK)
        center_container.pack(expand=True, fill=tk.BOTH)
        
        self.main_frame = tk.Frame(center_container, bg=COLOR_BG_DARK, padx=20, pady=15)
        self.main_frame.pack(expand=True)
        
        # Título centrado
        title_label = tk.Label(
            self.main_frame,
            text="SISTEMA DE NÓMINA ABCOPA",
            font=('Arial', 20, 'bold'),
            bg=COLOR_BG_DARK,
            fg=COLOR_CYAN
        )
        title_label.pack(pady=(0, 15), anchor=tk.CENTER)
        
        # Botones principales
        self.create_main_buttons()
        
    def create_main_buttons(self):
        """Crea los botones principales del menú"""
        # Contenedor para centrar los botones
        button_container = tk.Frame(self.main_frame, bg=COLOR_BG_DARK)
        button_container.pack(expand=True, fill=tk.X, pady=10)
        
        button_frame = tk.Frame(button_container, bg=COLOR_BG_DARK)
        button_frame.pack(anchor=tk.CENTER)
        
        buttons = [
            ("Calcular Nómina Quincenal", self.open_calculate_payroll, COLOR_CYAN),
            ("Gestionar Empleados", self.open_manage_employees, COLOR_CELESTE),
            ("Ver Nómina", self.view_payroll, COLOR_CELESTE),
            ("Ver Información", self.show_info, COLOR_GRAY_DARK),
            ("Salir", self.root.quit, COLOR_BLACK)
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                font=('Arial', 12, 'bold'),
                bg=color,
                fg=COLOR_TEXT,
                activebackground=color,
                activeforeground=COLOR_TEXT,
                width=28,
                height=1,
                relief=tk.RAISED,
                borderwidth=2,
                cursor='hand2'
            )
            btn.pack(pady=5)
    
    def open_calculate_payroll(self):
        """Abre la ventana para calcular nómina"""
        CalculatePayrollWindow(self.root)
    
    def open_manage_employees(self):
        """Abre la ventana para gestionar empleados"""
        ManageEmployeesWindow(self.root)
    
    def view_payroll(self):
        """Permite seleccionar y ver un archivo de nómina"""
        # Abrir diálogo para seleccionar archivo
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de nómina",
            filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
            initialdir=os.getcwd()
        )
        
        if not file_path:
            return  # Usuario canceló
        
        try:
            # Leer el archivo de nómina
            df = pd.read_excel(file_path)
            
            if df.empty:
                messagebox.showinfo("Información", "El archivo de nómina está vacío.")
                return
            
            # Reorganizar columnas: mover "Pago Quincenal" al final y renombrarlo
            if 'Pago Quincenal' in df.columns:
                # Guardar el valor antes de renombrar
                df = df.rename(columns={'Pago Quincenal': 'Total Pago a Empleados'})
                
                # Obtener todas las columnas excepto "Total Pago a Empleados"
                other_cols = [col for col in df.columns if col != 'Total Pago a Empleados']
                # Reorganizar: otras columnas primero, luego "Total Pago a Empleados" al final
                df = df[other_cols + ['Total Pago a Empleados']]
            
            # Calcular total general
            if 'Total Pago a Empleados' in df.columns:
                total_general = df['Total Pago a Empleados'].sum()
            else:
                # Si no existe la columna renombrada, buscar "Pago Quincenal"
                if 'Pago Quincenal' in df.columns:
                    total_general = df['Pago Quincenal'].sum()
                else:
                    total_general = 0
            
            # Crear ventana para mostrar nómina
            view_window = tk.Toplevel(self.root)
            view_window.title("Nómina Quincenal")
            view_window.geometry("1200x600")
            view_window.configure(bg=COLOR_BG_DARK)
            
            # Título
            title = tk.Label(
                view_window,
                text="NÓMINA QUINCENAL",
                font=('Arial', 16, 'bold'),
                bg=COLOR_BG_DARK,
                fg=COLOR_CYAN
            )
            title.pack(pady=10)
            
            # Mostrar información del archivo
            file_info = tk.Label(
                view_window,
                text=f"Archivo: {os.path.basename(file_path)}",
                font=('Arial', 10),
                bg=COLOR_BG_DARK,
                fg=COLOR_TEXT
            )
            file_info.pack(pady=5)
            
            # Frame con scrollbar para la tabla
            table_frame = tk.Frame(view_window, bg=COLOR_BG_DARK)
            table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Treeview con estilo oscuro
            style = ttk.Style()
            style.theme_use('clam')
            style.configure("Treeview", background=COLOR_GRAY_DARK, foreground=COLOR_TEXT, 
                          fieldbackground=COLOR_GRAY_DARK, borderwidth=0)
            style.configure("Treeview.Heading", background=COLOR_BG_FRAME, foreground=COLOR_CYAN,
                          borderwidth=1, relief=tk.SOLID)
            style.map("Treeview", background=[('selected', COLOR_CYAN)])
            
            # Frame para treeview y scrollbar
            tree_container = tk.Frame(table_frame, bg=COLOR_BG_DARK)
            tree_container.pack(fill=tk.BOTH, expand=True)
            
            tree = ttk.Treeview(tree_container)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Scrollbar vertical
            v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=tree.yview)
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.configure(yscrollcommand=v_scrollbar.set)
            
            # Scrollbar horizontal
            h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            tree.configure(xscrollcommand=h_scrollbar.set)
            
            # Columnas
            columns = list(df.columns)
            tree['columns'] = columns
            tree['show'] = 'headings'
            
            # Configurar columnas
            for col in columns:
                tree.heading(col, text=col)
                # Ajustar ancho según el tipo de columna
                if 'Total' in col or 'Pago' in col:
                    tree.column(col, width=150, anchor=tk.E)  # Alineado a la derecha para números
                elif col == 'ID':
                    tree.column(col, width=100, anchor=tk.CENTER)
                elif col == 'Nombre':
                    tree.column(col, width=180, anchor=tk.W)
                else:
                    tree.column(col, width=120, anchor=tk.CENTER)
            
            # Insertar datos
            for _, row in df.iterrows():
                values = []
                for col in columns:
                    val = row[col]
                    if pd.isna(val):
                        values.append('')
                    elif isinstance(val, (int, float)) and ('Pago' in col or 'Total' in col or 'Salario' in col or 'Bono' in col):
                        # Formatear números monetarios
                        values.append(f"${val:,.2f}")
                    else:
                        values.append(str(val))
                tree.insert('', tk.END, values=values)
            
            # Frame para el total general (resaltado)
            total_frame = tk.Frame(view_window, bg=COLOR_BG_DARK, pady=15)
            total_frame.pack(fill=tk.X, padx=10)
            
            # Etiqueta de total general con estilo resaltado
            total_label = tk.Label(
                total_frame,
                text="TOTAL GENERAL A PAGAR:",
                font=('Arial', 14, 'bold'),
                bg=COLOR_BG_DARK,
                fg=COLOR_CYAN
            )
            total_label.pack(side=tk.LEFT, padx=10)
            
            # Valor del total con estilo muy resaltado
            total_value = tk.Label(
                total_frame,
                text=f"${total_general:,.2f}",
                font=('Arial', 18, 'bold'),
                bg=COLOR_CYAN,
                fg=COLOR_BLACK,
                relief=tk.RAISED,
                borderwidth=3,
                padx=20,
                pady=10
            )
            total_value.pack(side=tk.LEFT, padx=10)
            
            # Información adicional
            info_label = tk.Label(
                total_frame,
                text=f"({len(df)} empleados)",
                font=('Arial', 10),
                bg=COLOR_BG_DARK,
                fg=COLOR_TEXT
            )
            info_label.pack(side=tk.LEFT, padx=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al leer el archivo de nómina:\n{str(e)}")
    
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
        messagebox.showinfo("Información del Sistema", info_text)


class CalculatePayrollWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Calcular Nómina Quincenal")
        self.window.geometry("700x600")
        self.window.configure(bg=COLOR_BG_DARK)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Canvas con scrollbar para permitir desplazamiento
        canvas = tk.Canvas(self.window, bg=COLOR_BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLOR_BG_DARK)
        
        # Centrar el contenido horizontalmente en el canvas
        def center_content(event=None):
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            if canvas_width > 1 and frame_width > 0:
                x = (canvas_width - frame_width) // 2
                if canvas.find_all():
                    canvas.coords(canvas.find_all()[0], max(0, x), 0)
        
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            center_content()
        
        scrollable_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", center_content)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Habilitar scroll con rueda del mouse (Windows)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Vincular scroll a la ventana cuando el mouse está sobre ella
        def _bind_mousewheel(event):
            self.window.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            self.window.unbind_all("<MouseWheel>")
        
        self.window.bind("<Enter>", _bind_mousewheel)
        self.window.bind("<Leave>", _unbind_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame contenedor para centrar el contenido
        center_container = tk.Frame(scrollable_frame, bg=COLOR_BG_DARK)
        center_container.pack(expand=True, fill=tk.BOTH)
        
        # Frame principal dentro del canvas
        main_frame = tk.Frame(center_container, bg=COLOR_BG_DARK, padx=20, pady=15)
        main_frame.pack(expand=True)
        
        # Título centrado
        title = tk.Label(
            main_frame,
            text="CALCULAR NÓMINA QUINCENAL",
            font=('Arial', 16, 'bold'),
            bg=COLOR_BG_DARK,
            fg=COLOR_CYAN
        )
        title.pack(pady=(0, 10), anchor=tk.CENTER)
        
        # Botones principales al inicio para mejor accesibilidad (centrados)
        button_container = tk.Frame(main_frame, bg=COLOR_BG_DARK)
        button_container.pack(expand=True, fill=tk.X, pady=10)
        
        button_frame_top = tk.Frame(button_container, bg=COLOR_BG_DARK)
        button_frame_top.pack(anchor=tk.CENTER)
        
        self.calculate_btn = tk.Button(
            button_frame_top,
            text="Calcular Nómina",
            command=self.calculate_payroll,
            bg=COLOR_CYAN,
            fg=COLOR_TEXT,
            font=('Arial', 11, 'bold'),
            width=18,
            height=1,
            cursor='hand2'
        )
        self.calculate_btn.pack(side=tk.LEFT, padx=5)
        
        self.continue_btn = tk.Button(
            button_frame_top,
            text="Continuar",
            command=self.continue_operation,
            bg=COLOR_CELESTE,
            fg=COLOR_TEXT,
            font=('Arial', 11, 'bold'),
            width=15,
            height=1,
            cursor='hand2',
            state='disabled'
        )
        self.continue_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame_top,
            text="Cerrar",
            command=self.window.destroy,
            bg=COLOR_GRAY_DARK,
            fg=COLOR_TEXT,
            font=('Arial', 11),
            width=15,
            height=1,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        # Frame de archivos
        files_frame = tk.LabelFrame(
            main_frame,
            text="Archivos",
            font=('Arial', 11, 'bold'),
            bg=COLOR_BG_FRAME,
            fg=COLOR_CYAN,
            padx=12,
            pady=10
        )
        files_frame.pack(fill=tk.X, pady=5)
        
        # Archivo de empleados
        tk.Label(
            files_frame,
            text="Archivo de Empleados:",
            font=('Arial', 10),
            bg=COLOR_BG_FRAME,
            fg=COLOR_TEXT
        ).pack(anchor=tk.W)
        
        emp_frame = tk.Frame(files_frame, bg=COLOR_BG_FRAME)
        emp_frame.pack(fill=tk.X, pady=5)
        
        self.emp_file_var = tk.StringVar(value="employees_information.xlsx")
        emp_entry = tk.Entry(emp_frame, textvariable=self.emp_file_var, font=('Arial', 10), bg=COLOR_GRAY_DARK, fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
        emp_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(
            emp_frame,
            text="Buscar",
            command=lambda: self.browse_file(self.emp_file_var),
            bg=COLOR_GRAY_DARK,
            fg=COLOR_TEXT,
            font=('Arial', 9),
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Archivo de horas
        tk.Label(
            files_frame,
            text="Archivo de Reporte de Asistencia:",
            font=('Arial', 10),
            bg=COLOR_BG_FRAME,
            fg=COLOR_TEXT
        ).pack(anchor=tk.W, pady=(10, 0))
        
        hours_frame = tk.Frame(files_frame, bg=COLOR_BG_FRAME)
        hours_frame.pack(fill=tk.X, pady=5)
        
        self.hours_file_var = tk.StringVar(value="Reporte de Asistencia.xlsx")
        hours_entry = tk.Entry(hours_frame, textvariable=self.hours_file_var, font=('Arial', 10), bg=COLOR_GRAY_DARK, fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
        hours_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(
            hours_frame,
            text="Buscar",
            command=lambda: self.browse_file(self.hours_file_var),
            bg=COLOR_GRAY_DARK,
            fg=COLOR_TEXT,
            font=('Arial', 9),
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Frame de fecha
        date_frame = tk.LabelFrame(
            main_frame,
            text="Fecha de Referencia (Opcional)",
            font=('Arial', 11, 'bold'),
            bg=COLOR_BG_FRAME,
            fg=COLOR_CYAN,
            padx=12,
            pady=10
        )
        date_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            date_frame,
            text="Deje vacío para usar la quincena más reciente",
            font=('Arial', 9, 'italic'),
            bg=COLOR_BG_FRAME,
            fg=COLOR_CELESTE
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.date_var = tk.StringVar()
        date_entry = tk.Entry(
            date_frame,
            textvariable=self.date_var,
            font=('Arial', 10),
            bg=COLOR_GRAY_DARK,
            fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT
        )
        date_entry.pack(fill=tk.X, pady=5)
        date_entry.insert(0, "DD/MM/YYYY (ejemplo: 15/01/2026)")
        date_entry.config(fg=COLOR_CELESTE)
        
        def on_date_entry_focus_in(event):
            if date_entry.get() == "DD/MM/YYYY (ejemplo: 15/01/2026)":
                date_entry.delete(0, tk.END)
                date_entry.config(fg=COLOR_TEXT)
        
        def on_date_entry_focus_out(event):
            if not date_entry.get():
                date_entry.insert(0, "DD/MM/YYYY (ejemplo: 15/01/2026)")
                date_entry.config(fg=COLOR_CELESTE)
        
        date_entry.bind('<FocusIn>', on_date_entry_focus_in)
        date_entry.bind('<FocusOut>', on_date_entry_focus_out)
        
        # Área de mensajes
        msg_frame = tk.LabelFrame(
            main_frame,
            text="Mensajes",
            font=('Arial', 11, 'bold'),
            bg=COLOR_BG_FRAME,
            fg=COLOR_CYAN,
            padx=12,
            pady=10
        )
        msg_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.message_text = scrolledtext.ScrolledText(
            msg_frame,
            height=8,
            font=('Consolas', 9),
            bg=COLOR_GRAY_DARK,
            fg=COLOR_TEXT,
            wrap=tk.WORD,
            insertbackground=COLOR_TEXT
        )
        self.message_text.pack(fill=tk.BOTH, expand=True)
        
        # Indicador de estado (centrado)
        status_frame = tk.Frame(main_frame, bg=COLOR_BG_DARK)
        status_frame.pack(pady=5)
        
        self.status_label = tk.Label(
            status_frame,
            text="",
            font=('Arial', 10, 'bold'),
            bg=COLOR_BG_DARK,
            fg=COLOR_CYAN
        )
        self.status_label.pack()
    
    def browse_file(self, var):
        """Abre diálogo para buscar archivo"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            var.set(filename)
    
    def continue_operation(self):
        """Permite continuar después de calcular la nómina"""
        self.calculate_btn.config(state='normal')
        self.continue_btn.config(state='disabled')
        self.status_label.config(text="", fg=COLOR_CYAN)
    
    def calculate_payroll(self):
        """Calcula la nómina"""
        # Validaciones previas
        employees_file = self.emp_file_var.get().strip()
        hours_file = self.hours_file_var.get().strip()
        date_str = self.date_var.get().strip()
        
        # Limpiar placeholder si está presente
        if date_str == "DD/MM/YYYY (ejemplo: 15/01/2026)":
            date_str = ""
        
        # Validar archivos
        if not employees_file:
            messagebox.showerror("Error", "Debe especificar el archivo de empleados")
            return
        
        if not hours_file:
            messagebox.showerror("Error", "Debe especificar el archivo de reporte de asistencia")
            return
        
        if not os.path.exists(employees_file):
            messagebox.showerror("Error", f"El archivo de empleados no existe: {employees_file}")
            return
        
        if not os.path.exists(hours_file):
            messagebox.showerror("Error", f"El archivo de horas no existe: {hours_file}")
            return
        
        # Preparar fecha
        quincena_fecha = None
        if date_str:
            try:
                # Validar formato de fecha
                datetime.strptime(date_str, '%d/%m/%Y')
                quincena_fecha = date_str
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/YYYY (ejemplo: 15/01/2026)")
                return
        
        # Limpiar mensajes anteriores y preparar interfaz
        self.message_text.delete(1.0, tk.END)
        self.calculate_btn.config(state='disabled')
        self.continue_btn.config(state='disabled')
        self.status_label.config(text="⏳ Calculando nómina... Por favor espere.", fg=COLOR_CELESTE)
        self.window.update()
        
        # Mostrar mensaje de inicio
        self.message_text.insert(tk.END, "Calculando nómina...\n")
        self.message_text.insert(tk.END, f"Archivo de empleados: {employees_file}\n")
        self.message_text.insert(tk.END, f"Archivo de reporte de asistencia: {hours_file}\n")
        if quincena_fecha:
            self.message_text.insert(tk.END, f"Fecha de referencia: {quincena_fecha}\n")
        self.message_text.insert(tk.END, "-" * 60 + "\n\n")
        self.window.update()
        
        # Ejecutar cálculo en un hilo separado para no bloquear la interfaz
        def run_calculation():
            try:
                # Redirigir print a la caja de texto
                import sys
                from io import StringIO
                
                old_stdout = sys.stdout
                sys.stdout = output = StringIO()
                
                result = calculate_payroll_quincenal(
                    employees_file=employees_file,
                    hours_file=hours_file,
                    output_file=None,
                    quincena_fecha=quincena_fecha
                )
                
                sys.stdout = old_stdout
                output_text = output.getvalue()
                
                # Actualizar interfaz en el hilo principal
                self.window.after(0, self.update_result, result, output_text)
            
            except Exception as e:
                # Actualizar interfaz con error en el hilo principal
                self.window.after(0, self.show_error, str(e))
        
        # Iniciar cálculo en hilo separado
        thread = threading.Thread(target=run_calculation, daemon=True)
        thread.start()
    
    def update_result(self, result, output_text):
        """Actualiza la interfaz con el resultado del cálculo"""
        # Mostrar salida
        self.message_text.insert(tk.END, output_text)
        self.message_text.see(tk.END)
        
        if result is not None:
            self.message_text.insert(tk.END, "\n" + "=" * 60 + "\n")
            self.message_text.insert(tk.END, "✓ NÓMINA CALCULADA EXITOSAMENTE\n")
            self.message_text.insert(tk.END, "=" * 60 + "\n")
            self.status_label.config(text="✓ Nómina calculada exitosamente. Presione 'Continuar' para realizar otra operación.", fg=COLOR_CYAN)
            self.calculate_btn.config(state='normal')
            self.continue_btn.config(state='normal')  # Habilitar botón Continuar
            messagebox.showinfo("Éxito", "La nómina ha sido calculada exitosamente.\n\nRevise el área de mensajes para ver los detalles.\n\nPresione 'Continuar' para realizar otra operación.")
        else:
            self.status_label.config(text="✗ Error al calcular la nómina. Revise los mensajes.", fg=COLOR_CELESTE)
            self.calculate_btn.config(state='normal')
            self.continue_btn.config(state='normal')  # Habilitar botón Continuar
            messagebox.showerror("Error", "No se pudo calcular la nómina.\n\nRevise el área de mensajes para ver los errores.\n\nPresione 'Continuar' para intentar nuevamente.")
    
    def show_error(self, error_msg):
        """Muestra un error en la interfaz"""
        self.message_text.insert(tk.END, f"\nERROR: {error_msg}\n")
        self.status_label.config(text=f"✗ Error: {error_msg[:50]}...", fg=COLOR_CELESTE)
        self.calculate_btn.config(state='normal')
        self.continue_btn.config(state='normal')  # Habilitar botón Continuar
        messagebox.showerror("Error", f"Error al calcular la nómina:\n{error_msg}\n\nPresione 'Continuar' para intentar nuevamente.")


class ManageEmployeesWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Gestionar Empleados")
        self.window.geometry("800x700")
        self.window.configure(bg=COLOR_BG_DARK)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Canvas con scrollbar para permitir desplazamiento
        canvas = tk.Canvas(self.window, bg=COLOR_BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLOR_BG_DARK)
        
        # Centrar el contenido horizontalmente en el canvas
        def center_content(event=None):
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            if canvas_width > 1 and frame_width > 0:
                x = (canvas_width - frame_width) // 2
                if canvas.find_all():
                    canvas.coords(canvas.find_all()[0], max(0, x), 0)
        
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            center_content()
        
        scrollable_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", center_content)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Habilitar scroll con rueda del mouse (Windows)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Vincular scroll a la ventana cuando el mouse está sobre ella
        def _bind_mousewheel(event):
            self.window.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            self.window.unbind_all("<MouseWheel>")
        
        self.window.bind("<Enter>", _bind_mousewheel)
        self.window.bind("<Leave>", _unbind_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame contenedor para centrar el contenido
        center_container = tk.Frame(scrollable_frame, bg=COLOR_BG_DARK)
        center_container.pack(expand=True, fill=tk.BOTH)
        
        # Frame principal
        main_frame = tk.Frame(center_container, bg=COLOR_BG_DARK, padx=20, pady=15)
        main_frame.pack(expand=True)
        
        # Título centrado
        title = tk.Label(
            main_frame,
            text="GESTIONAR EMPLEADOS",
            font=('Arial', 16, 'bold'),
            bg=COLOR_BG_DARK,
            fg=COLOR_CYAN
        )
        title.pack(pady=(0, 10), anchor=tk.CENTER)
        
        # Botones de acción centrados
        button_frame = tk.Frame(main_frame, bg=COLOR_BG_DARK)
        button_frame.pack(pady=5, anchor=tk.CENTER)
        
        buttons = [
            ("Ver Lista de Empleados", self.view_employees, COLOR_CYAN),
            ("Agregar Empleado", self.add_employee, COLOR_CELESTE),
            ("Modificar Empleado", self.modify_employee, COLOR_GRAY_DARK),
            ("Eliminar Empleado", self.delete_employee, COLOR_BLACK)
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                font=('Arial', 10, 'bold'),
                bg=color,
                fg=COLOR_TEXT,
                width=23,
                height=1,
                cursor='hand2',
                relief=tk.RAISED,
                borderwidth=2,
                activebackground=color,
                activeforeground=COLOR_TEXT
            )
            btn.pack(pady=3)
        
        # Botón cerrar centrado
        tk.Button(
            main_frame,
            text="Cerrar",
            command=self.window.destroy,
            bg=COLOR_GRAY_DARK,
            fg=COLOR_TEXT,
            font=('Arial', 10),
            width=15,
            height=1,
            cursor='hand2',
            activebackground=COLOR_GRAY_DARK,
            activeforeground=COLOR_TEXT
        ).pack(pady=10, anchor=tk.CENTER)
    
    def view_employees(self):
        """Muestra la lista de empleados"""
        try:
            df = leer_empleados_normalizado()
            if df is None or df.empty:
                messagebox.showinfo("Información", "No hay empleados registrados.")
                return
            
            # Crear ventana para mostrar empleados
            view_window = tk.Toplevel(self.window)
            view_window.title("Lista de Empleados")
            view_window.geometry("900x500")
            view_window.configure(bg=COLOR_BG_DARK)
            
            # Título centrado
            title = tk.Label(
                view_window,
                text="LISTA DE EMPLEADOS",
                font=('Arial', 14, 'bold'),
                bg=COLOR_BG_DARK,
                fg=COLOR_CYAN
            )
            title.pack(pady=10)
            
            # Frame con scrollbar
            frame = tk.Frame(view_window, bg=COLOR_BG_DARK)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Treeview con estilo oscuro
            style = ttk.Style()
            style.theme_use('clam')
            style.configure("Treeview", background=COLOR_GRAY_DARK, foreground=COLOR_TEXT, 
                          fieldbackground=COLOR_GRAY_DARK, borderwidth=0)
            style.configure("Treeview.Heading", background=COLOR_BG_FRAME, foreground=COLOR_CYAN,
                          borderwidth=1, relief=tk.SOLID)
            style.map("Treeview", background=[('selected', COLOR_CYAN)])
            
            tree = ttk.Treeview(frame)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # Columnas
            columns = list(df.columns)
            tree['columns'] = columns
            tree['show'] = 'headings'
            
            for col in columns:
                tree.heading(col, text=col.replace('_', ' ').title())
                tree.column(col, width=120, anchor=tk.CENTER)
            
            # Datos
            for _, row in df.iterrows():
                values = [str(row[col]) if pd.notna(row[col]) else '' for col in columns]
                tree.insert('', tk.END, values=values)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al leer empleados:\n{str(e)}")
    
    def add_employee(self):
        """Abre ventana para agregar empleado"""
        AddEmployeeWindow(self.window)
    
    def modify_employee(self):
        """Abre ventana para modificar empleado"""
        ModifyEmployeeWindow(self.window)
    
    def delete_employee(self):
        """Elimina un empleado"""
        DeleteEmployeeWindow(self.window)


class AddEmployeeWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Agregar Empleado")
        self.window.geometry("500x550")
        self.window.configure(bg=COLOR_BG_DARK)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Canvas con scrollbar para permitir desplazamiento
        canvas = tk.Canvas(self.window, bg=COLOR_BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLOR_BG_DARK)
        
        # Centrar el contenido horizontalmente en el canvas
        def center_content(event=None):
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            if canvas_width > 1 and frame_width > 0:
                x = (canvas_width - frame_width) // 2
                if canvas.find_all():
                    canvas.coords(canvas.find_all()[0], max(0, x), 0)
        
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            center_content()
        
        scrollable_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", center_content)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Habilitar scroll con rueda del mouse (Windows)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Vincular scroll a la ventana cuando el mouse está sobre ella
        def _bind_mousewheel(event):
            self.window.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            self.window.unbind_all("<MouseWheel>")
        
        self.window.bind("<Enter>", _bind_mousewheel)
        self.window.bind("<Leave>", _unbind_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame contenedor para centrar el contenido
        center_container = tk.Frame(scrollable_frame, bg=COLOR_BG_DARK)
        center_container.pack(expand=True, fill=tk.BOTH)
        
        main_frame = tk.Frame(center_container, bg=COLOR_BG_DARK, padx=25, pady=15)
        main_frame.pack(expand=True)
        
        # Título centrado
        title = tk.Label(
            main_frame,
            text="AGREGAR NUEVO EMPLEADO",
            font=('Arial', 14, 'bold'),
            bg=COLOR_BG_DARK,
            fg=COLOR_CYAN
        )
        title.pack(pady=(0, 10), anchor=tk.CENTER)
        
        # Campos
        fields = [
            ("ID (deje vacío para auto-generar):", "id"),
            ("Nombre:", "nombre"),
            ("Cargo:", "cargo"),
            ("Salario (por hora):", "salario"),
            ("Número de Cuenta:", "n_de_cuenta"),
            ("Banco:", "banco"),
            ("Tipo de Cuenta:", "tipo_de_cuenta"),
            ("Salario Fijo (S/N) - Cobra lo mismo sin importar horas:", "salario_fijo"),
            ("Empleado Fijo (S/N) - Tiene sueldo mínimo + bono:", "empleado_fijo"),
            ("Salario Mínimo (mensual, solo si es Empleado Fijo):", "salario_minimo")
        ]
        
        self.vars = {}
        
        for label_text, field_name in fields:
            tk.Label(
                main_frame,
                text=label_text,
                font=('Arial', 9),
                bg=COLOR_BG_DARK,
                fg=COLOR_TEXT
            ).pack(anchor=tk.W, pady=(5, 2))
            
            var = tk.StringVar()
            self.vars[field_name] = var
            
            entry = tk.Entry(main_frame, textvariable=var, font=('Arial', 9), width=40, 
                           bg=COLOR_GRAY_DARK, fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
            entry.pack(fill=tk.X, pady=(0, 3))
        
        # Botones centrados
        button_frame = tk.Frame(main_frame, bg=COLOR_BG_DARK)
        button_frame.pack(pady=10, anchor=tk.CENTER)
        
        tk.Button(
            button_frame,
            text="Agregar",
            command=self.add_employee,
            bg=COLOR_CYAN,
            fg=COLOR_TEXT,
            font=('Arial', 11, 'bold'),
            width=15,
            cursor='hand2',
            activebackground=COLOR_CYAN,
            activeforeground=COLOR_TEXT
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancelar",
            command=self.window.destroy,
            bg=COLOR_GRAY_DARK,
            fg=COLOR_TEXT,
            font=('Arial', 11),
            width=15,
            cursor='hand2',
            activebackground=COLOR_GRAY_DARK,
            activeforeground=COLOR_TEXT
        ).pack(side=tk.LEFT, padx=5)
    
    def add_employee(self):
        """Agrega el empleado"""
        # Simular input() usando los valores de los campos
        import sys
        from io import StringIO
        import builtins
        
        # Guardar inputs originales
        original_input = builtins.input
        
        inputs = []
        id_val = self.vars['id'].get().strip()
        inputs.append(id_val if id_val else '')  # ID
        inputs.append(self.vars['nombre'].get().strip())  # Nombre
        inputs.append(self.vars['cargo'].get().strip())  # Cargo
        inputs.append(self.vars['salario'].get().strip())  # Salario
        inputs.append(self.vars['n_de_cuenta'].get().strip())  # Número de cuenta
        inputs.append(self.vars['banco'].get().strip())  # Banco
        inputs.append(self.vars['tipo_de_cuenta'].get().strip())  # Tipo de cuenta
        salario_fijo_val = self.vars['salario_fijo'].get().strip().upper()
        inputs.append('S' if salario_fijo_val == 'S' else 'N')  # Salario Fijo
        empleado_fijo_val = self.vars['empleado_fijo'].get().strip().upper()
        inputs.append('S' if empleado_fijo_val == 'S' else 'N')  # Empleado Fijo
        # Validar que no sean ambos
        if salario_fijo_val == 'S' and empleado_fijo_val == 'S':
            messagebox.showerror("Error", "Un empleado no puede ser 'Salario Fijo' y 'Empleado Fijo' al mismo tiempo")
            return
        # Si es empleado_fijo, validar salario_minimo
        if empleado_fijo_val == 'S':
            salario_minimo_val = self.vars['salario_minimo'].get().strip()
            if not salario_minimo_val:
                messagebox.showerror("Error", "El salario mínimo es obligatorio para empleados fijos")
                return
            try:
                float(salario_minimo_val)
            except ValueError:
                messagebox.showerror("Error", "El salario mínimo debe ser un número válido")
                return
            inputs.append(salario_minimo_val)  # Salario Mínimo
        else:
            inputs.append('')  # Salario Mínimo vacío si no es empleado fijo
        
        input_index = [0]
        
        def mock_input(prompt=''):
            if input_index[0] < len(inputs):
                result = inputs[input_index[0]]
                input_index[0] += 1
                return result
            return ''
        
        # Validar campos requeridos
        if not self.vars['nombre'].get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        if not self.vars['salario'].get().strip():
            messagebox.showerror("Error", "El salario es obligatorio")
            return
        
        try:
            float(self.vars['salario'].get().strip())
        except ValueError:
            messagebox.showerror("Error", "El salario debe ser un número válido")
            return
        
        try:
            builtins.input = mock_input
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            result = agregar_empleado()
            
            sys.stdout = old_stdout
            builtins.input = original_input
            
            if result is not None:
                messagebox.showinfo("Éxito", "Empleado agregado exitosamente")
                self.window.destroy()
            else:
                messagebox.showerror("Error", "No se pudo agregar el empleado.\nVerifique los datos e intente nuevamente.")
        
        except Exception as e:
            builtins.input = original_input
            sys.stdout = old_stdout
            messagebox.showerror("Error", f"Error al agregar empleado:\n{str(e)}")


class ModifyEmployeeWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Modificar Empleado")
        self.window.geometry("500x600")
        self.window.configure(bg=COLOR_BG_DARK)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Canvas con scrollbar para permitir desplazamiento
        canvas = tk.Canvas(self.window, bg=COLOR_BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLOR_BG_DARK)
        
        # Centrar el contenido horizontalmente en el canvas
        def center_content(event=None):
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            if canvas_width > 1 and frame_width > 0:
                x = (canvas_width - frame_width) // 2
                if canvas.find_all():
                    canvas.coords(canvas.find_all()[0], max(0, x), 0)
        
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            center_content()
        
        scrollable_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", center_content)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Habilitar scroll con rueda del mouse (Windows)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Vincular scroll a la ventana cuando el mouse está sobre ella
        def _bind_mousewheel(event):
            self.window.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            self.window.unbind_all("<MouseWheel>")
        
        self.window.bind("<Enter>", _bind_mousewheel)
        self.window.bind("<Leave>", _unbind_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame contenedor para centrar el contenido
        center_container = tk.Frame(scrollable_frame, bg=COLOR_BG_DARK)
        center_container.pack(expand=True, fill=tk.BOTH)
        
        main_frame = tk.Frame(center_container, bg=COLOR_BG_DARK, padx=25, pady=15)
        main_frame.pack(expand=True)
        
        # Título centrado
        title = tk.Label(
            main_frame,
            text="MODIFICAR EMPLEADO",
            font=('Arial', 14, 'bold'),
            bg=COLOR_BG_DARK,
            fg=COLOR_CYAN
        )
        title.pack(pady=(0, 10), anchor=tk.CENTER)
        
        # ID del empleado
        tk.Label(
            main_frame,
            text="ID del Empleado:",
            font=('Arial', 9, 'bold'),
            bg=COLOR_BG_DARK,
            fg=COLOR_TEXT
        ).pack(anchor=tk.W, pady=(5, 2))
        
        self.id_var = tk.StringVar()
        id_entry = tk.Entry(main_frame, textvariable=self.id_var, font=('Arial', 9), width=40,
                          bg=COLOR_GRAY_DARK, fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
        id_entry.pack(fill=tk.X, pady=(0, 5))
        
        tk.Button(
            main_frame,
            text="Buscar Empleado",
            command=self.load_employee,
            bg=COLOR_CYAN,
            fg=COLOR_TEXT,
            font=('Arial', 9),
            cursor='hand2',
            activebackground=COLOR_CYAN,
            activeforeground=COLOR_TEXT
        ).pack(pady=3, anchor=tk.CENTER)
        
        # Campos (inicialmente deshabilitados)
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
        
        self.vars = {}
        self.entries = []
        
        for label_text, field_name in fields:
            tk.Label(
                main_frame,
                text=label_text,
                font=('Arial', 9),
                bg=COLOR_BG_DARK,
                fg=COLOR_TEXT
            ).pack(anchor=tk.W, pady=(5, 2))
            
            var = tk.StringVar()
            self.vars[field_name] = var
            
            entry = tk.Entry(main_frame, textvariable=var, font=('Arial', 9), width=40, 
                           state='disabled', bg=COLOR_GRAY_DARK, fg=COLOR_TEXT, 
                           insertbackground=COLOR_TEXT, disabledbackground=COLOR_BG_FRAME,
                           disabledforeground=COLOR_CELESTE)
            entry.pack(fill=tk.X, pady=(0, 3))
            self.entries.append(entry)
        
        # Botones centrados
        button_frame = tk.Frame(main_frame, bg=COLOR_BG_DARK)
        button_frame.pack(pady=10, anchor=tk.CENTER)
        
        self.modify_btn = tk.Button(
            button_frame,
            text="Modificar",
            command=self.modify_employee,
            bg=COLOR_CELESTE,
            fg=COLOR_TEXT,
            font=('Arial', 11, 'bold'),
            width=15,
            cursor='hand2',
            state='disabled',
            activebackground=COLOR_CELESTE,
            activeforeground=COLOR_TEXT
        )
        self.modify_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancelar",
            command=self.window.destroy,
            bg=COLOR_GRAY_DARK,
            fg=COLOR_TEXT,
            font=('Arial', 11),
            width=15,
            cursor='hand2',
            activebackground=COLOR_GRAY_DARK,
            activeforeground=COLOR_TEXT
        ).pack(side=tk.LEFT, padx=5)
    
    def load_employee(self):
        """Carga los datos del empleado"""
        employee_id = self.id_var.get().strip()
        if not employee_id:
            messagebox.showerror("Error", "Debe ingresar un ID")
            return
        
        try:
            df = leer_empleados_normalizado()
            if df is None or df.empty:
                messagebox.showerror("Error", "No hay empleados en la base de datos")
                return
            
            # Buscar empleado
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
                messagebox.showerror("Error", f"No se encontró un empleado con ID: {employee_id}")
                return
            
            emp = employee.iloc[0]
            
            # Llenar campos
            self.vars['nombre'].set(str(emp['nombre']))
            self.vars['cargo'].set(str(emp.get('cargo', '')))
            self.vars['salario'].set(str(emp['salario']))
            self.vars['n_de_cuenta'].set(str(emp.get('n_de_cuenta', '')))
            self.vars['banco'].set(str(emp.get('banco', '')))
            self.vars['tipo_de_cuenta'].set(str(emp.get('tipo_de_cuenta', '')))
            salario_fijo_val = bool(emp.get('salario_fijo', False))
            empleado_fijo_val = bool(emp.get('empleado_fijo', False))
            salario_minimo_val = emp.get('salario_minimo', 0) if pd.notna(emp.get('salario_minimo')) else 0
            self.vars['salario_fijo'].set('S' if salario_fijo_val else 'N')
            self.vars['empleado_fijo'].set('S' if empleado_fijo_val else 'N')
            self.vars['salario_minimo'].set(str(salario_minimo_val))
            
            # Habilitar campos
            for entry in self.entries:
                entry.config(state='normal')
            self.modify_btn.config(state='normal')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar empleado:\n{str(e)}")
    
    def modify_employee(self):
        """Modifica el empleado"""
        employee_id = self.id_var.get().strip()
        if not employee_id:
            messagebox.showerror("Error", "Debe ingresar un ID")
            return
        
        # Simular inputs
        import sys
        from io import StringIO
        import builtins
        
        original_input = builtins.input
        
        inputs = [
            employee_id,  # ID
            self.vars['nombre'].get().strip() or '',  # Nombre (Enter para mantener)
            self.vars['cargo'].get().strip() or '',  # Cargo
            self.vars['salario'].get().strip() or '',  # Salario
            self.vars['n_de_cuenta'].get().strip() or '',  # Número de cuenta
            self.vars['banco'].get().strip() or '',  # Banco
            self.vars['tipo_de_cuenta'].get().strip() or '',  # Tipo de cuenta
            self.vars['salario_fijo'].get().strip().upper() or '',  # Salario Fijo
            self.vars['empleado_fijo'].get().strip().upper() or '',  # Empleado Fijo
            self.vars['salario_minimo'].get().strip() or ''  # Salario Mínimo
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
                messagebox.showinfo("Éxito", "Empleado modificado exitosamente")
                self.window.destroy()
            else:
                messagebox.showerror("Error", "No se pudo modificar el empleado.\nVerifique los datos e intente nuevamente.")
        
        except Exception as e:
            builtins.input = original_input
            sys.stdout = old_stdout
            messagebox.showerror("Error", f"Error al modificar empleado:\n{str(e)}")


class DeleteEmployeeWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Eliminar Empleado")
        self.window.geometry("400x200")
        self.window.configure(bg=COLOR_BG_DARK)
        self.window.transient(parent)
        self.window.grab_set()
        
        main_frame = tk.Frame(self.window, bg=COLOR_BG_DARK, padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título centrado
        title = tk.Label(
            main_frame,
            text="ELIMINAR EMPLEADO",
            font=('Arial', 16, 'bold'),
            bg=COLOR_BG_DARK,
            fg=COLOR_CYAN
        )
        title.pack(pady=(0, 20), anchor=tk.CENTER)
        
        tk.Label(
            main_frame,
            text="ID del Empleado:",
            font=('Arial', 10),
            bg=COLOR_BG_DARK,
            fg=COLOR_TEXT
        ).pack(anchor=tk.W, pady=(10, 2))
        
        self.id_var = tk.StringVar()
        id_entry = tk.Entry(main_frame, textvariable=self.id_var, font=('Arial', 10), width=30,
                          bg=COLOR_GRAY_DARK, fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
        id_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Botones centrados
        button_frame = tk.Frame(main_frame, bg=COLOR_BG_DARK)
        button_frame.pack(anchor=tk.CENTER)
        
        tk.Button(
            button_frame,
            text="Eliminar",
            command=self.delete_employee,
            bg=COLOR_BLACK,
            fg=COLOR_TEXT,
            font=('Arial', 11, 'bold'),
            width=15,
            cursor='hand2',
            activebackground=COLOR_BLACK,
            activeforeground=COLOR_TEXT
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancelar",
            command=self.window.destroy,
            bg=COLOR_GRAY_DARK,
            fg=COLOR_TEXT,
            font=('Arial', 11),
            width=15,
            cursor='hand2',
            activebackground=COLOR_GRAY_DARK,
            activeforeground=COLOR_TEXT
        ).pack(side=tk.LEFT, padx=5)
    
    def delete_employee(self):
        """Elimina el empleado"""
        employee_id = self.id_var.get().strip()
        if not employee_id:
            messagebox.showerror("Error", "Debe ingresar un ID")
            return
        
        # Simular inputs
        import sys
        from io import StringIO
        import builtins
        
        original_input = builtins.input
        
        inputs = [employee_id, 'S']  # ID y confirmación
        
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
                messagebox.showinfo("Éxito", "Empleado eliminado exitosamente")
                self.window.destroy()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el empleado.\nVerifique el ID e intente nuevamente.")
        
        except Exception as e:
            builtins.input = original_input
            sys.stdout = old_stdout
            messagebox.showerror("Error", f"Error al eliminar empleado:\n{str(e)}")


def main():
    root = tk.Tk()
    app = NominaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
