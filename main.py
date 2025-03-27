import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
from tkcalendar import Calendar  # Requires pip install tkcalendar

class TaskManager:
    def __init__(self, root):
        """
        Initialize the Task Manager application.
        
        Args:
            root (tk.Tk): The root window of the application.
        """
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("800x600")
        
        # Initialize database
        self.init_db()
        
        # Create GUI
        self.create_widgets()
        
        # Load tasks from database
        self.load_tasks()
        
        # Bind window close event to save tasks
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def init_db(self):
        """
        Initialize the SQLite database and create tasks table if it doesn't exist.
        """
        self.conn = sqlite3.connect('task_manager.db')
        self.cursor = self.conn.cursor()
        
        # Create tasks table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT NOT NULL,
                deadline TEXT,
                completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def create_widgets(self):
        """
        Create all the GUI widgets for the application.
        """
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        ttk.Label(self.main_frame, text="Task Manager", font=('Helvetica', 16, 'bold')).pack(pady=10)
        
        # Control buttons frame
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Add task button
        ttk.Button(control_frame, text="Add Task", command=self.open_add_task_window).pack(side=tk.LEFT, padx=5)
        
        # Edit task button
        self.edit_btn = ttk.Button(control_frame, text="Edit Task", command=self.edit_task, state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete task button
        self.delete_btn = ttk.Button(control_frame, text="Delete Task", command=self.delete_task, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Mark complete button
        self.complete_btn = ttk.Button(control_frame, text="Mark Complete", command=self.toggle_complete, state=tk.DISABLED)
        self.complete_btn.pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(self.main_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_entry.bind('<KeyRelease>', self.search_tasks)
        
        # Task list treeview
        self.tree = ttk.Treeview(self.main_frame, columns=('title', 'priority', 'deadline', 'completed'), selectmode='browse')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure treeview columns
        self.tree.heading('#0', text='ID')
        self.tree.column('#0', width=50, stretch=tk.NO)
        
        self.tree.heading('title', text='Title')
        self.tree.column('title', width=200)
        
        self.tree.heading('priority', text='Priority')
        self.tree.column('priority', width=100)
        
        self.tree.heading('deadline', text='Deadline')
        self.tree.column('deadline', width=100)
        
        self.tree.heading('completed', text='Completed')
        self.tree.column('completed', width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_task_select)
        
        # Status bar
        self.status_bar = ttk.Label(self.main_frame, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def on_task_select(self, event):
        """
        Handle task selection event to enable/disable buttons.
        """
        selected = self.tree.selection()
        if selected:
            self.edit_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
            self.complete_btn.config(state=tk.NORMAL)
            
            # Update complete button text based on current state
            item = self.tree.item(selected)
            if item['values'][3] == 'Yes':
                self.complete_btn.config(text="Mark Incomplete")
            else:
                self.complete_btn.config(text="Mark Complete")
        else:
            self.edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)
            self.complete_btn.config(state=tk.DISABLED)
    
    def open_add_task_window(self):
        """
        Open a new window for adding a task.
        """
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Add New Task")
        self.add_window.grab_set()  # Make window modal
        
        # Task title
        ttk.Label(self.add_window, text="Title:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.title_entry = ttk.Entry(self.add_window, width=40)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
        
        # Task description
        ttk.Label(self.add_window, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.desc_entry = tk.Text(self.add_window, width=40, height=5)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5, columnspan=2)
        
        # Priority
        ttk.Label(self.add_window, text="Priority:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.priority_var = tk.StringVar(value="Medium")
        ttk.Radiobutton(self.add_window, text="Low", variable=self.priority_var, value="Low").grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(self.add_window, text="Medium", variable=self.priority_var, value="Medium").grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(self.add_window, text="High", variable=self.priority_var, value="High").grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Deadline
        ttk.Label(self.add_window, text="Deadline:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.deadline_cal = Calendar(self.add_window, selectmode='day', date_pattern='yyyy-mm-dd')
        self.deadline_cal.grid(row=4, column=1, padx=5, pady=5, columnspan=2)
        
        # Buttons
        ttk.Button(self.add_window, text="Add Task", command=self.add_task).grid(row=5, column=1, padx=5, pady=10)
        ttk.Button(self.add_window, text="Cancel", command=self.add_window.destroy).grid(row=5, column=2, padx=5, pady=10)
    
    def add_task(self):
        """
        Add a new task to the database and refresh the task list.
        """
        title = self.title_entry.get().strip()
        description = self.desc_entry.get("1.0", tk.END).strip()
        priority = self.priority_var.get()
        deadline = self.deadline_cal.get_date()
        
        if not title:
            messagebox.showerror("Error", "Task title cannot be empty!")
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO tasks (title, description, priority, deadline)
                VALUES (?, ?, ?, ?)
            ''', (title, description, priority, deadline))
            self.conn.commit()
            
            self.add_window.destroy()
            self.load_tasks()
            self.status_bar.config(text="Task added successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add task: {str(e)}")
    
    def edit_task(self):
        """
        Open a window to edit the selected task.
        """
        selected = self.tree.selection()
        if not selected:
            return
            
        task_id = self.tree.item(selected)['text']
        task_data = self.get_task_by_id(task_id)
        
        if not task_data:
            messagebox.showerror("Error", "Selected task not found!")
            return
            
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Edit Task")
        self.edit_window.grab_set()
        
        # Task title
        ttk.Label(self.edit_window, text="Title:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.edit_title_entry = ttk.Entry(self.edit_window, width=40)
        self.edit_title_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
        self.edit_title_entry.insert(0, task_data[1])
        
        # Task description
        ttk.Label(self.edit_window, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.edit_desc_entry = tk.Text(self.edit_window, width=40, height=5)
        self.edit_desc_entry.grid(row=1, column=1, padx=5, pady=5, columnspan=2)
        self.edit_desc_entry.insert("1.0", task_data[2])
        
        # Priority
        ttk.Label(self.edit_window, text="Priority:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.edit_priority_var = tk.StringVar(value=task_data[3])
        ttk.Radiobutton(self.edit_window, text="Low", variable=self.edit_priority_var, value="Low").grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(self.edit_window, text="Medium", variable=self.edit_priority_var, value="Medium").grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(self.edit_window, text="High", variable=self.edit_priority_var, value="High").grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Deadline
        ttk.Label(self.edit_window, text="Deadline:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.edit_deadline_cal = Calendar(self.edit_window, selectmode='day', date_pattern='yyyy-mm-dd')
        self.edit_deadline_cal.grid(row=4, column=1, padx=5, pady=5, columnspan=2)
        if task_data[4]:
            # Correct way to set the date in tkcalendar
            self.edit_deadline_cal.selection_set(task_data[4])
        
        # Store task ID for update
        self.editing_task_id = task_id
        
        # Buttons
        ttk.Button(self.edit_window, text="Update Task", command=self.update_task).grid(row=5, column=1, padx=5, pady=10)
        ttk.Button(self.edit_window, text="Cancel", command=self.edit_window.destroy).grid(row=5, column=2, padx=5, pady=10)
    
    def update_task(self):
        """
        Update the selected task in the database.
        """
        title = self.edit_title_entry.get().strip()
        description = self.edit_desc_entry.get("1.0", tk.END).strip()
        priority = self.edit_priority_var.get()
        deadline = self.edit_deadline_cal.get_date()
        
        if not title:
            messagebox.showerror("Error", "Task title cannot be empty!")
            return
        
        try:
            self.cursor.execute('''
                UPDATE tasks 
                SET title = ?, description = ?, priority = ?, deadline = ?
                WHERE id = ?
            ''', (title, description, priority, deadline, self.editing_task_id))
            self.conn.commit()
            
            self.edit_window.destroy()
            self.load_tasks()
            self.status_bar.config(text="Task updated successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update task: {str(e)}")
    
    def delete_task(self):
        """
        Delete the selected task after confirmation.
        """
        selected = self.tree.selection()
        if not selected:
            return
            
        task_id = self.tree.item(selected)['text']
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            return
            
        try:
            self.cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            self.conn.commit()
            
            self.load_tasks()
            self.status_bar.config(text="Task deleted successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete task: {str(e)}")
    
    def toggle_complete(self):
        """
        Toggle the completed status of the selected task.
        """
        selected = self.tree.selection()
        if not selected:
            return
            
        task_id = self.tree.item(selected)['text']
        current_status = self.tree.item(selected)['values'][3]
        new_status = 0 if current_status == 'Yes' else 1
        
        try:
            self.cursor.execute('''
                UPDATE tasks 
                SET completed = ?
                WHERE id = ?
            ''', (new_status, task_id))
            self.conn.commit()
            
            self.load_tasks()
            self.status_bar.config(text="Task status updated")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update task status: {str(e)}")
    
    def get_task_by_id(self, task_id):
        """
        Retrieve a task by its ID from the database.
        
        Args:
            task_id (int): The ID of the task to retrieve.
            
        Returns:
            tuple: The task data or None if not found.
        """
        self.cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        return self.cursor.fetchone()
    
    def load_tasks(self):
        """
        Load tasks from the database and display them in the treeview.
        """
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get search term
        search_term = self.search_entry.get().strip()
        
        # Build query based on search
        if search_term:
            query = '''
                SELECT id, title, priority, deadline, completed 
                FROM tasks 
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY 
                    CASE priority 
                        WHEN 'High' THEN 1 
                        WHEN 'Medium' THEN 2 
                        WHEN 'Low' THEN 3 
                        ELSE 4 
                    END,
                    deadline
            '''
            params = (f'%{search_term}%', f'%{search_term}%')
        else:
            query = '''
                SELECT id, title, priority, deadline, completed 
                FROM tasks 
                ORDER BY 
                    CASE priority 
                        WHEN 'High' THEN 1 
                        WHEN 'Medium' THEN 2 
                        WHEN 'Low' THEN 3 
                        ELSE 4 
                    END,
                    deadline
            '''
            params = ()
        
        self.cursor.execute(query, params)
        tasks = self.cursor.fetchall()
        
        # Add tasks to treeview
        for task in tasks:
            completed = 'Yes' if task[4] else 'No'
            deadline = task[3] if task[3] else ''
            
            # Strike through completed tasks
            tags = ('completed',) if task[4] else ()
            
            self.tree.insert('', tk.END, text=task[0], values=(task[1], task[2], deadline, completed), tags=tags)
        
        # Configure tag for completed tasks
        self.tree.tag_configure('completed', font=('Helvetica', 10, 'overstrike'))
    
    def search_tasks(self, event=None):
        """
        Search tasks based on the search term.
        """
        self.load_tasks()
    
    def on_close(self):
        """
        Handle application close event.
        """
        self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()
