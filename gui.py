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


class NominaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Nómina ABCOPA")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        self.main_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(
            self.main_frame,
            text="SISTEMA DE NÓMINA ABCOPA",
            font=('Arial', 24, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 30))
        
        # Botones principales
        self.create_main_buttons()
        
    def create_main_buttons(self):
        """Crea los botones principales del menú"""
        button_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        buttons = [
            ("Calcular Nómina Quincenal", self.open_calculate_payroll, '#3498db'),
            ("Gestionar Empleados", self.open_manage_employees, '#2ecc71'),
            ("Ver Información", self.show_info, '#f39c12'),
            ("Salir", self.root.quit, '#e74c3c')
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                font=('Arial', 14, 'bold'),
                bg=color,
                fg='white',
                activebackground=color,
                activeforeground='white',
                width=30,
                height=2,
                relief=tk.RAISED,
                borderwidth=3,
                cursor='hand2'
            )
            btn.pack(pady=10)
    
    def open_calculate_payroll(self):
        """Abre la ventana para calcular nómina"""
        CalculatePayrollWindow(self.root)
    
    def open_manage_employees(self):
        """Abre la ventana para gestionar empleados"""
        ManageEmployeesWindow(self.root)
    
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
• hours_worked.xlsx - Registros de asistencia

IMPORTANTE:
• Los empleados fijos reciben el mismo salario sin importar las horas
• Los empleados por horas reciben pago según horas trabajadas
• Se requiere exactamente 2 registros por día por empleado (entrada y salida)
        """
        messagebox.showinfo("Información del Sistema", info_text)


class CalculatePayrollWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Calcular Nómina Quincenal")
        self.window.geometry("700x600")
        self.window.configure(bg='#f0f0f0')
        self.window.transient(parent)
        self.window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(self.window, bg='#f0f0f0', padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = tk.Label(
            main_frame,
            text="CALCULAR NÓMINA QUINCENAL",
            font=('Arial', 18, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title.pack(pady=(0, 20))
        
        # Frame de archivos
        files_frame = tk.LabelFrame(
            main_frame,
            text="Archivos",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        files_frame.pack(fill=tk.X, pady=10)
        
        # Archivo de empleados
        tk.Label(
            files_frame,
            text="Archivo de Empleados:",
            font=('Arial', 10),
            bg='#f0f0f0'
        ).pack(anchor=tk.W)
        
        emp_frame = tk.Frame(files_frame, bg='#f0f0f0')
        emp_frame.pack(fill=tk.X, pady=5)
        
        self.emp_file_var = tk.StringVar(value="employees_information.xlsx")
        emp_entry = tk.Entry(emp_frame, textvariable=self.emp_file_var, font=('Arial', 10))
        emp_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(
            emp_frame,
            text="Buscar",
            command=lambda: self.browse_file(self.emp_file_var),
            bg='#95a5a6',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Archivo de horas
        tk.Label(
            files_frame,
            text="Archivo de Horas Trabajadas:",
            font=('Arial', 10),
            bg='#f0f0f0'
        ).pack(anchor=tk.W, pady=(10, 0))
        
        hours_frame = tk.Frame(files_frame, bg='#f0f0f0')
        hours_frame.pack(fill=tk.X, pady=5)
        
        self.hours_file_var = tk.StringVar(value="hours_worked.xlsx")
        hours_entry = tk.Entry(hours_frame, textvariable=self.hours_file_var, font=('Arial', 10))
        hours_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(
            hours_frame,
            text="Buscar",
            command=lambda: self.browse_file(self.hours_file_var),
            bg='#95a5a6',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Frame de fecha
        date_frame = tk.LabelFrame(
            main_frame,
            text="Fecha de Referencia (Opcional)",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        date_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            date_frame,
            text="Deje vacío para usar la quincena más reciente",
            font=('Arial', 9, 'italic'),
            bg='#f0f0f0',
            fg='#7f8c8d'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.date_var = tk.StringVar()
        date_entry = tk.Entry(
            date_frame,
            textvariable=self.date_var,
            font=('Arial', 10)
        )
        date_entry.pack(fill=tk.X, pady=5)
        date_entry.insert(0, "DD/MM/YYYY (ejemplo: 15/01/2026)")
        date_entry.config(fg='grey')
        
        def on_date_entry_focus_in(event):
            if date_entry.get() == "DD/MM/YYYY (ejemplo: 15/01/2026)":
                date_entry.delete(0, tk.END)
                date_entry.config(fg='black')
        
        def on_date_entry_focus_out(event):
            if not date_entry.get():
                date_entry.insert(0, "DD/MM/YYYY (ejemplo: 15/01/2026)")
                date_entry.config(fg='grey')
        
        date_entry.bind('<FocusIn>', on_date_entry_focus_in)
        date_entry.bind('<FocusOut>', on_date_entry_focus_out)
        
        # Área de mensajes
        msg_frame = tk.LabelFrame(
            main_frame,
            text="Mensajes",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        msg_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.message_text = scrolledtext.ScrolledText(
            msg_frame,
            height=10,
            font=('Consolas', 9),
            bg='#ffffff',
            fg='#2c3e50',
            wrap=tk.WORD
        )
        self.message_text.pack(fill=tk.BOTH, expand=True)
        
        # Indicador de estado
        status_frame = tk.Frame(main_frame, bg='#f0f0f0')
        status_frame.pack(pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        self.status_label.pack()
        
        # Botones
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        self.calculate_btn = tk.Button(
            button_frame,
            text="Calcular Nómina",
            command=self.calculate_payroll,
            bg='#3498db',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=20,
            height=2,
            cursor='hand2'
        )
        self.calculate_btn.pack(side=tk.LEFT, padx=10)
        
        self.continue_btn = tk.Button(
            button_frame,
            text="Continuar",
            command=self.continue_operation,
            bg='#2ecc71',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=15,
            height=2,
            cursor='hand2',
            state='disabled'
        )
        self.continue_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="Cerrar",
            command=self.window.destroy,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 12),
            width=15,
            height=2,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
    
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
        self.status_label.config(text="", fg='#2c3e50')
    
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
            messagebox.showerror("Error", "Debe especificar el archivo de horas trabajadas")
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
        self.status_label.config(text="⏳ Calculando nómina... Por favor espere.", fg='#e67e22')
        self.window.update()
        
        # Mostrar mensaje de inicio
        self.message_text.insert(tk.END, "Calculando nómina...\n")
        self.message_text.insert(tk.END, f"Archivo de empleados: {employees_file}\n")
        self.message_text.insert(tk.END, f"Archivo de horas: {hours_file}\n")
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
            self.status_label.config(text="✓ Nómina calculada exitosamente. Presione 'Continuar' para realizar otra operación.", fg='#27ae60')
            self.calculate_btn.config(state='normal')
            self.continue_btn.config(state='normal')  # Habilitar botón Continuar
            messagebox.showinfo("Éxito", "La nómina ha sido calculada exitosamente.\n\nRevise el área de mensajes para ver los detalles.\n\nPresione 'Continuar' para realizar otra operación.")
        else:
            self.status_label.config(text="✗ Error al calcular la nómina. Revise los mensajes.", fg='#e74c3c')
            self.calculate_btn.config(state='normal')
            self.continue_btn.config(state='normal')  # Habilitar botón Continuar
            messagebox.showerror("Error", "No se pudo calcular la nómina.\n\nRevise el área de mensajes para ver los errores.\n\nPresione 'Continuar' para intentar nuevamente.")
    
    def show_error(self, error_msg):
        """Muestra un error en la interfaz"""
        self.message_text.insert(tk.END, f"\nERROR: {error_msg}\n")
        self.status_label.config(text=f"✗ Error: {error_msg[:50]}...", fg='#e74c3c')
        self.calculate_btn.config(state='normal')
        self.continue_btn.config(state='normal')  # Habilitar botón Continuar
        messagebox.showerror("Error", f"Error al calcular la nómina:\n{error_msg}\n\nPresione 'Continuar' para intentar nuevamente.")


class ManageEmployeesWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Gestionar Empleados")
        self.window.geometry("800x700")
        self.window.configure(bg='#f0f0f0')
        self.window.transient(parent)
        self.window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(self.window, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = tk.Label(
            main_frame,
            text="GESTIONAR EMPLEADOS",
            font=('Arial', 18, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title.pack(pady=(0, 20))
        
        # Botones de acción
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        buttons = [
            ("Ver Lista de Empleados", self.view_employees, '#3498db'),
            ("Agregar Empleado", self.add_employee, '#2ecc71'),
            ("Modificar Empleado", self.modify_employee, '#f39c12'),
            ("Eliminar Empleado", self.delete_employee, '#e74c3c')
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                font=('Arial', 11, 'bold'),
                bg=color,
                fg='white',
                width=25,
                height=2,
                cursor='hand2',
                relief=tk.RAISED,
                borderwidth=2
            )
            btn.pack(pady=5)
        
        # Botón cerrar
        tk.Button(
            main_frame,
            text="Cerrar",
            command=self.window.destroy,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 11),
            width=15,
            height=1,
            cursor='hand2'
        ).pack(pady=20)
    
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
            
            # Frame con scrollbar
            frame = tk.Frame(view_window)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Treeview
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
        self.window.configure(bg='#f0f0f0')
        self.window.transient(parent)
        self.window.grab_set()
        
        main_frame = tk.Frame(self.window, bg='#f0f0f0', padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title = tk.Label(
            main_frame,
            text="AGREGAR NUEVO EMPLEADO",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title.pack(pady=(0, 20))
        
        # Campos
        fields = [
            ("ID (deje vacío para auto-generar):", "id"),
            ("Nombre:", "nombre"),
            ("Cargo:", "cargo"),
            ("Salario:", "salario"),
            ("Número de Cuenta:", "n_de_cuenta"),
            ("Banco:", "banco"),
            ("Tipo de Cuenta:", "tipo_de_cuenta"),
            ("Fijo (S/N):", "fijo")
        ]
        
        self.vars = {}
        
        for label_text, field_name in fields:
            tk.Label(
                main_frame,
                text=label_text,
                font=('Arial', 10),
                bg='#f0f0f0'
            ).pack(anchor=tk.W, pady=(10, 2))
            
            var = tk.StringVar()
            self.vars[field_name] = var
            
            entry = tk.Entry(main_frame, textvariable=var, font=('Arial', 10), width=40)
            entry.pack(fill=tk.X, pady=(0, 5))
        
        # Botones
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Agregar",
            command=self.add_employee,
            bg='#2ecc71',
            fg='white',
            font=('Arial', 11, 'bold'),
            width=15,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancelar",
            command=self.window.destroy,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 11),
            width=15,
            cursor='hand2'
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
        fijo_val = self.vars['fijo'].get().strip().upper()
        inputs.append('S' if fijo_val == 'S' else 'N')  # Fijo
        
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
        self.window.configure(bg='#f0f0f0')
        self.window.transient(parent)
        self.window.grab_set()
        
        main_frame = tk.Frame(self.window, bg='#f0f0f0', padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title = tk.Label(
            main_frame,
            text="MODIFICAR EMPLEADO",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title.pack(pady=(0, 20))
        
        # ID del empleado
        tk.Label(
            main_frame,
            text="ID del Empleado:",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0'
        ).pack(anchor=tk.W, pady=(10, 2))
        
        self.id_var = tk.StringVar()
        id_entry = tk.Entry(main_frame, textvariable=self.id_var, font=('Arial', 10), width=40)
        id_entry.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(
            main_frame,
            text="Buscar Empleado",
            command=self.load_employee,
            bg='#3498db',
            fg='white',
            font=('Arial', 10),
            cursor='hand2'
        ).pack(pady=5)
        
        # Campos (inicialmente deshabilitados)
        fields = [
            ("Nombre:", "nombre"),
            ("Cargo:", "cargo"),
            ("Salario:", "salario"),
            ("Número de Cuenta:", "n_de_cuenta"),
            ("Banco:", "banco"),
            ("Tipo de Cuenta:", "tipo_de_cuenta"),
            ("Fijo (S/N):", "fijo")
        ]
        
        self.vars = {}
        self.entries = []
        
        for label_text, field_name in fields:
            tk.Label(
                main_frame,
                text=label_text,
                font=('Arial', 10),
                bg='#f0f0f0'
            ).pack(anchor=tk.W, pady=(10, 2))
            
            var = tk.StringVar()
            self.vars[field_name] = var
            
            entry = tk.Entry(main_frame, textvariable=var, font=('Arial', 10), width=40, state='disabled')
            entry.pack(fill=tk.X, pady=(0, 5))
            self.entries.append(entry)
        
        # Botones
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        self.modify_btn = tk.Button(
            button_frame,
            text="Modificar",
            command=self.modify_employee,
            bg='#f39c12',
            fg='white',
            font=('Arial', 11, 'bold'),
            width=15,
            cursor='hand2',
            state='disabled'
        )
        self.modify_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancelar",
            command=self.window.destroy,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 11),
            width=15,
            cursor='hand2'
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
            self.vars['fijo'].set('S' if emp['fijo'] else 'N')
            
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
            self.vars['fijo'].get().strip().upper() or ''  # Fijo
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
        self.window.configure(bg='#f0f0f0')
        self.window.transient(parent)
        self.window.grab_set()
        
        main_frame = tk.Frame(self.window, bg='#f0f0f0', padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title = tk.Label(
            main_frame,
            text="ELIMINAR EMPLEADO",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0',
            fg='#e74c3c'
        )
        title.pack(pady=(0, 20))
        
        tk.Label(
            main_frame,
            text="ID del Empleado:",
            font=('Arial', 10),
            bg='#f0f0f0'
        ).pack(anchor=tk.W, pady=(10, 2))
        
        self.id_var = tk.StringVar()
        id_entry = tk.Entry(main_frame, textvariable=self.id_var, font=('Arial', 10), width=30)
        id_entry.pack(fill=tk.X, pady=(0, 20))
        
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack()
        
        tk.Button(
            button_frame,
            text="Eliminar",
            command=self.delete_employee,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 11, 'bold'),
            width=15,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancelar",
            command=self.window.destroy,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 11),
            width=15,
            cursor='hand2'
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
