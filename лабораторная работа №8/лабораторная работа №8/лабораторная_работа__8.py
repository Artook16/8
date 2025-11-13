import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import os

class Hexagon:
    def __init__(self, center_x=200, center_y=200, size=50, color="blue", name="Шестиугольник"):
        self.center_x = center_x
        self.center_y = center_y
        self.size = size
        self.color = color
        self.name = name
    
    def calculate_vertices(self):
        vertices = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            x = self.center_x + self.size * math.cos(angle_rad)
            y = self.center_y + self.size * math.sin(angle_rad)
            vertices.append((x, y))
        return vertices
    
    def copy(self, new_name=None):
        if new_name is None:
            new_name = f"{self.name}_копия"
        return Hexagon(self.center_x, self.center_y, self.size, self.color, new_name)
    
    def resize(self, new_size):
        if new_size > 0:
            self.size = new_size
            return True
        return False
    
    def move(self, new_x, new_y):
        self.center_x = new_x
        self.center_y = new_y
    
    def get_info(self):
        return f"{self.name},{self.center_x},{self.center_y},{self.size},{self.color}"


class HexagonManager:
    def __init__(self):
        self.hexagons = []
        self.selected_index = -1
    
    def add_hexagon(self, hexagon):
        self.hexagons.append(hexagon)
    
    def copy_hexagon(self, index, new_name=None):
        if 0 <= index < len(self.hexagons):
            copy_hex = self.hexagons[index].copy(new_name)
            self.add_hexagon(copy_hex)
            return True
        return False
    
    def delete_hexagon(self, index):
        if 0 <= index < len(self.hexagons):
            del self.hexagons[index]
            if self.selected_index >= len(self.hexagons):
                self.selected_index = len(self.hexagons) - 1
            return True
        return False
    
    def resize_hexagon(self, index, new_size):
        if 0 <= index < len(self.hexagons):
            return self.hexagons[index].resize(new_size)
        return False
    
    def save_to_file(self, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                for hexagon in self.hexagons:
                    file.write(hexagon.get_info() + '\n')
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
            return False
    
    def load_from_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            new_hexagons = []
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    parts = line.split(',')
                    if len(parts) != 5:
                        raise ValueError("Неверное количество параметров")
                    
                    name = parts[0].strip()
                    center_x = float(parts[1])
                    center_y = float(parts[2])
                    size = float(parts[3])
                    color = parts[4].strip()
                    
                    if size <= 0:
                        raise ValueError("Размер должен быть положительным числом")
                    
                    new_hexagon = Hexagon(center_x, center_y, size, color, name)
                    new_hexagons.append(new_hexagon)
                    
                except ValueError as e:
                    messagebox.showwarning("Предупреждение", 
                                         f"Ошибка в строке {i}: {str(e)}\nСтрока пропущена.")
            
            self.hexagons = new_hexagons
            self.selected_index = -1
            return True
            
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл не найден")
            return False
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
            return False


class HexagonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор шестиугольников")
        self.root.geometry("800x600")
        
        self.manager = HexagonManager()
        self.setup_gui()
        
        self.manager.add_hexagon(Hexagon())
        self.update_hexagon_list()
        self.draw_hexagons()
    
    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        control_frame = ttk.LabelFrame(main_frame, text="Управление", padding="5")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(control_frame, text="Добавить", command=self.add_hexagon).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Копировать", command=self.copy_hexagon).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Удалить", command=self.delete_hexagon).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="Изменить размер", command=self.resize_dialog).grid(row=0, column=3, padx=5)
        
        params_frame = ttk.LabelFrame(main_frame, text="Параметры", padding="5")
        params_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        ttk.Label(params_frame, text="X:").grid(row=0, column=0, sticky=tk.W)
        self.x_var = tk.StringVar(value="200")
        ttk.Entry(params_frame, textvariable=self.x_var, width=10).grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(params_frame, text="Y:").grid(row=1, column=0, sticky=tk.W)
        self.y_var = tk.StringVar(value="200")
        ttk.Entry(params_frame, textvariable=self.y_var, width=10).grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(params_frame, text="Размер:").grid(row=2, column=0, sticky=tk.W)
        self.size_var = tk.StringVar(value="50")
        ttk.Entry(params_frame, textvariable=self.size_var, width=10).grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(params_frame, text="Цвет:").grid(row=3, column=0, sticky=tk.W)
        self.color_var = tk.StringVar(value="blue")
        color_combo = ttk.Combobox(params_frame, textvariable=self.color_var, width=8)
        color_combo['values'] = ('blue', 'red', 'green', 'yellow', 'purple', 'orange', 'pink')
        color_combo.grid(row=3, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(params_frame, text="Имя:").grid(row=4, column=0, sticky=tk.W)
        self.name_var = tk.StringVar(value="Шестиугольник")
        ttk.Entry(params_frame, textvariable=self.name_var).grid(row=4, column=1, sticky=(tk.W, tk.E))
        
        ttk.Button(params_frame, text="Применить", command=self.apply_changes).grid(row=5, column=0, columnspan=2, pady=5)
        
        list_frame = ttk.LabelFrame(main_frame, text="Шестиугольники", padding="5")
        list_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.hexagon_list = tk.Listbox(list_frame)
        self.hexagon_list.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.hexagon_list.bind('<<ListboxSelect>>', self.on_hexagon_select)
        
        canvas_frame = ttk.LabelFrame(main_frame, text="Просмотр", padding="5")
        canvas_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white", width=600, height=300)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(file_frame, text="Сохранить", command=self.save_file).grid(row=0, column=0, padx=5)
        ttk.Button(file_frame, text="Загрузить", command=self.load_file).grid(row=0, column=1, padx=5)
        
        params_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(4, weight=1)
    
    def add_hexagon(self):
        """Добавляет новый шестиугольник"""
        try:
            x = float(self.x_var.get())
            y = float(self.y_var.get())
            size = float(self.size_var.get())
            color = self.color_var.get()
            name = self.name_var.get()
            
            if size <= 0:
                messagebox.showerror("Ошибка", "Размер должен быть положительным числом")
                return
            
            hexagon = Hexagon(x, y, size, color, name)
            self.manager.add_hexagon(hexagon)
            self.update_hexagon_list()
            self.draw_hexagons()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения")
    
    def copy_hexagon(self):
        """Копирует выбранный шестиугольник"""
        if self.manager.selected_index == -1:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите шестиугольник для копирования")
            return
        
        new_name = f"{self.manager.hexagons[self.manager.selected_index].name}_копия"
        self.manager.copy_hexagon(self.manager.selected_index, new_name)
        self.update_hexagon_list()
        self.draw_hexagons()
    
    def delete_hexagon(self):
        """Удаляет выбранный шестиугольник"""
        if self.manager.selected_index == -1:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите шестиугольник для удаления")
            return
        
        self.manager.delete_hexagon(self.manager.selected_index)
        self.update_hexagon_list()
        self.draw_hexagons()
    
    def resize_dialog(self):
        """Открывает диалог изменения размера"""
        if self.manager.selected_index == -1:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите шестиугольник для изменения размера")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Изменение размера")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Новый размер:").pack(pady=5)
        size_var = tk.StringVar()
        size_entry = ttk.Entry(dialog, textvariable=size_var)
        size_entry.pack(pady=5)
        
        def apply_resize():
            try:
                new_size = float(size_var.get())
                if new_size <= 0:
                    messagebox.showerror("Ошибка", "Размер должен быть положительным числом")
                    return
                
                if self.manager.resize_hexagon(self.manager.selected_index, new_size):
                    self.update_hexagon_list()
                    self.draw_hexagons()
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось изменить размер")
            
            except ValueError:
                messagebox.showerror("Ошибка", "Пожалуйста, введите корректное числовое значение")
        
        ttk.Button(dialog, text="Применить", command=apply_resize).pack(pady=5)
    
    def apply_changes(self):
        """Применяет изменения к выбранному шестиугольнику"""
        if self.manager.selected_index == -1:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите шестиугольник для изменения")
            return
        
        try:
            x = float(self.x_var.get())
            y = float(self.y_var.get())
            size = float(self.size_var.get())
            color = self.color_var.get()
            name = self.name_var.get()
            
            if size <= 0:
                messagebox.showerror("Ошибка", "Размер должен быть положительным числом")
                return
            
            hexagon = self.manager.hexagons[self.manager.selected_index]
            hexagon.center_x = x
            hexagon.center_y = y
            hexagon.size = size
            hexagon.color = color
            hexagon.name = name
            
            self.update_hexagon_list()
            self.draw_hexagons()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения")
    
    def on_hexagon_select(self, event):
        """Обрабатывает выбор шестиугольника в списке"""
        selection = self.hexagon_list.curselection()
        if selection:
            index = selection[0]
            self.manager.selected_index = index
            hexagon = self.manager.hexagons[index]
            
            self.x_var.set(str(hexagon.center_x))
            self.y_var.set(str(hexagon.center_y))
            self.size_var.set(str(hexagon.size))
            self.color_var.set(hexagon.color)
            self.name_var.set(hexagon.name)
    
    def update_hexagon_list(self):
        """Обновляет список шестиугольников"""
        self.hexagon_list.delete(0, tk.END)
        for hexagon in self.manager.hexagons:
            self.hexagon_list.insert(tk.END, f"{hexagon.name} (размер: {hexagon.size})")
    
    def draw_hexagons(self):
        """Рисует все шестиугольники на холсте"""
        self.canvas.delete("all")
        
        for i, hexagon in enumerate(self.manager.hexagons):
            vertices = hexagon.calculate_vertices()
            
            points = []
            for x, y in vertices:
                points.extend([x, y])
            
            fill_color = hexagon.color
            outline_color = "black"
            width = 2
            
            self.canvas.create_polygon(points, fill=fill_color, outline=outline_color, width=width)
            
            self.canvas.create_oval(
                hexagon.center_x - 3, hexagon.center_y - 3,
                hexagon.center_x + 3, hexagon.center_y + 3,
                fill="black"
            )
    
    def save_file(self):
        """Сохраняет шестиугольники в файл"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            if self.manager.save_to_file(filename):
                messagebox.showinfo("Успех", "Файл успешно сохранен")
    
    def load_file(self):
        """Загружает шестиугольники из файла"""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            if self.manager.load_from_file(filename):
                self.update_hexagon_list()
                self.draw_hexagons()
                messagebox.showinfo("Успех", "Файл успешно загружен")


if __name__ == "__main__":
    root = tk.Tk()
    app = HexagonApp(root)
    root.mainloop()
