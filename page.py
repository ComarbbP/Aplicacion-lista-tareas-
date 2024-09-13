import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3


conn = sqlite3.connect('tasks.db')
c = conn.cursor()


c.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    completed BOOLEAN NOT NULL,
    priority INTEGER NOT NULL
)
''')
conn.commit()
class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lista de Tareas Avanzada by Omar")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f4f7")
        
        self.setup_styles()
        
        self.create_widgets()
        self.load_tasks()

    def setup_styles(self):
        style = ttk.Style()
       
        style.theme_use('clam')
        font_large = ("Helvetica", 20, "bold")
        font_medium = ("Helvetica", 14)
        font_small = ("Helvetica", 12)

        primary_color = "#4A90E2"    
        secondary_color = "#50E3C2"  
        accent_color = "#F5A623"     
        background_color = "#f0f4f7" 
        button_color = "#007BFF"     
        button_hover_color = "#0056b3" 
        style.configure("Title.TFrame", background=primary_color)
        style.configure("Title.TLabel", font=font_large, background=primary_color, foreground="white")
        style.configure("Input.TFrame", background=background_color)
        style.configure("Input.TEntry", font=font_medium, padding=5, relief="flat", borderwidth=1, background="white")
        style.configure("Priority.TSpinbox", font=font_medium, relief="flat", background="white")
        style.configure("AddButton.TButton", background=button_color, foreground="white", font=font_small)
        style.configure("ActionButton.TButton", background=button_color, foreground="white", font=font_small)
        style.configure("Treeview", font=font_small, background=background_color, foreground="black", fieldbackground=background_color)
        style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"), background=secondary_color, foreground="white")
        style.map("AddButton.TButton", background=[('active', button_hover_color)])
        style.map("ActionButton.TButton", background=[('active', button_hover_color)])

        style.configure("TLabel", font=font_medium, background=background_color, foreground="black")
    def create_widgets(self):
       
        title_frame = ttk.Frame(self.root, padding="10", style="Title.TFrame")
        title_frame.pack(fill='x')
        title_label = ttk.Label(title_frame, text="Lista de Tareas", style="Title.TLabel")
        title_label.pack()

        input_frame = ttk.Frame(self.root, padding="20", style="Input.TFrame")
        input_frame.pack(fill='x')
        ttk.Label(input_frame, text="Nueva Tarea:", style="TLabel").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.task_entry = ttk.Entry(input_frame, style="Input.TEntry", width=40)
        self.task_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        ttk.Label(input_frame, text="Prioridad:", style="TLabel").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.priority_spinbox = ttk.Spinbox(input_frame, from_=1, to_=5, style="Priority.TSpinbox", width=5)
        self.priority_spinbox.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        add_button = ttk.Button(input_frame, text="Añadir Tarea", style="AddButton.TButton", command=self.add_task)
        add_button.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="ew")

     
        self.task_tree = ttk.Treeview(self.root, columns=("text", "priority", "completed"), show="headings", height=20, style="Treeview")
        self.task_tree.pack(fill='both', expand=True, padx=20, pady=10)
        self.task_tree.heading("text", text="Tarea")
        self.task_tree.heading("priority", text="Prioridad")
        self.task_tree.heading("completed", text="Completada")
        self.task_tree.bind("<ButtonRelease-1>", self.on_select)

  
        action_frame = ttk.Frame(self.root, padding="20")
        action_frame.pack(fill='x')
        complete_button = ttk.Button(action_frame, text="Marcar como Completa", style="ActionButton.TButton", command=self.complete_task)
        complete_button.pack(side='left', padx=10)
        delete_button = ttk.Button(action_frame, text="Eliminar Tarea", style="ActionButton.TButton", command=self.delete_task)
        delete_button.pack(side='left', padx=10)
        edit_button = ttk.Button(action_frame, text="Editar Tarea", style="ActionButton.TButton", command=self.edit_task)
        edit_button.pack(side='left', padx=10)
    def add_task(self):
        task_text = self.task_entry.get().strip()
        priority = int(self.priority_spinbox.get())

        if not task_text:
            messagebox.showwarning("Advertencia", "El campo de tarea no puede estar vacío.")
            return

        c.execute('INSERT INTO tasks (text, completed, priority) VALUES (?, ?, ?)',
                  (task_text, False, priority))
        conn.commit()
        self.load_tasks()
        self.task_entry.delete(0, tk.END)

    def load_tasks(self):
        for row in self.task_tree.get_children():
            self.task_tree.delete(row)
        c.execute('SELECT rowid, * FROM tasks')
        for task in c.fetchall():
            self.task_tree.insert("", "end", iid=task[0], values=(task[1], task[3], "Sí" if task[2] else "No"))

    def on_select(self, event):
        item = self.task_tree.selection()[0]
        self.selected_task_id = item

    def complete_task(self):
        if not hasattr(self, 'selected_task_id'):
            messagebox.showwarning("Advertencia", "Debe seleccionar una tarea para marcarla como completa.")
            return

        c.execute('UPDATE tasks SET completed = ? WHERE rowid = ?', (True, self.selected_task_id))
        conn.commit()
        self.load_tasks()

    def delete_task(self):
        if not hasattr(self, 'selected_task_id'):
            messagebox.showwarning("Advertencia", "Debe seleccionar una tarea para eliminarla.")
            return

        c.execute('DELETE FROM tasks WHERE rowid = ?', (self.selected_task_id,))
        conn.commit()
        self.load_tasks()

    def edit_task(self):
        if not hasattr(self, 'selected_task_id'):
            messagebox.showwarning("Advertencia", "Debe seleccionar una tarea para editarla.")
            return

        new_text = simpledialog.askstring("Editar Tarea", "Ingrese el nuevo texto de la tarea:")
        if new_text is not None:
            c.execute('UPDATE tasks SET text = ? WHERE rowid = ?', (new_text, self.selected_task_id))
            conn.commit()
            self.load_tasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()

