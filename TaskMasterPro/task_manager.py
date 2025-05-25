#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Основной модуль менеджера задач с GUI на tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date
import json
from data_storage import DataStorage

class Task:
    """Класс для представления задачи"""
    
    def __init__(self, title, description="", deadline=None, completed=False):
        self.id = None  # Будет установлен при сохранении
        self.title = title
        self.description = description
        self.deadline = deadline
        self.completed = completed
        self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def to_dict(self):
        """Преобразование задачи в словарь для сохранения"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.strftime("%Y-%m-%d") if self.deadline else None,
            'completed': self.completed,
            'created_date': self.created_date
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создание задачи из словаря"""
        task = cls(
            title=data['title'],
            description=data.get('description', ''),
            completed=data.get('completed', False)
        )
        task.id = data.get('id')
        task.created_date = data.get('created_date', datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        if data.get('deadline'):
            try:
                task.deadline = datetime.strptime(data['deadline'], "%Y-%m-%d").date()
            except:
                task.deadline = None
        
        return task

class TaskManagerApp:
    """Главный класс приложения менеджера задач"""
    
    def __init__(self, root):
        self.root = root
        self.storage = DataStorage()
        self.tasks = []
        self.selected_task_id = None
        
        # Красно-бордовая цветовая схема
        self.colors = {
            'bg_main': '#8B0000',        # Темно-красный
            'bg_secondary': '#A0001A',    # Бордовый
            'bg_light': '#F5F0F0',       # Светло-розовый
            'fg_main': '#FFFFFF',        # Белый текст
            'fg_dark': '#2F0000',        # Темный текст
            'accent': '#DC143C',         # Яркий красный
            'success': '#228B22',        # Зеленый для выполненных
            'warning': '#FF6347'         # Оранжево-красный для предупреждений
        }
        
        self.setup_ui()
        self.load_tasks()
        self.refresh_task_list()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Настройка стилей
        self.setup_styles()
        
        # Главный контейнер
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Менеджер задач", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Верхняя панель с кнопками
        button_frame = ttk.Frame(main_frame, style='Button.TFrame')
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки управления
        ttk.Button(button_frame, text="Добавить задачу", 
                  command=self.add_task, style='Action.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Редактировать", 
                  command=self.edit_task, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", 
                  command=self.delete_task, style='Delete.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отметить выполненной", 
                  command=self.toggle_completion, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        # Фильтры
        filter_frame = ttk.Frame(main_frame, style='Filter.TFrame')
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Показать:", style='Filter.TLabel').pack(side=tk.LEFT)
        
        self.filter_var = tk.StringVar(value="Все")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                   values=["Все", "Активные", "Выполненные", "Просроченные"],
                                   state="readonly", width=15)
        filter_combo.pack(side=tk.LEFT, padx=(5, 0))
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_task_list())
        
        # Список задач
        self.setup_task_list(main_frame)
        
        # Панель деталей задачи
        self.setup_details_panel(main_frame)
    
    def setup_styles(self):
        """Настройка стилей ttk"""
        style = ttk.Style()
        
        # Основные стили
        style.configure('Main.TFrame', background=self.colors['bg_light'])
        style.configure('Button.TFrame', background=self.colors['bg_light'])
        style.configure('Filter.TFrame', background=self.colors['bg_light'])
        
        # Заголовок
        style.configure('Title.TLabel', 
                       font=('Arial', 18, 'bold'),
                       foreground=self.colors['bg_main'],
                       background=self.colors['bg_light'])
        
        # Кнопки
        style.configure('Action.TButton',
                       font=('Arial', 10),
                       foreground=self.colors['fg_main'])
        style.map('Action.TButton',
                 background=[('active', self.colors['accent']),
                           ('!active', self.colors['bg_main'])])
        
        style.configure('Delete.TButton',
                       font=('Arial', 10),
                       foreground=self.colors['fg_main'])
        style.map('Delete.TButton',
                 background=[('active', '#B22222'),
                           ('!active', self.colors['bg_secondary'])])
        
        style.configure('Success.TButton',
                       font=('Arial', 10),
                       foreground=self.colors['fg_main'])
        style.map('Success.TButton',
                 background=[('active', '#32CD32'),
                           ('!active', self.colors['success'])])
        
        # Метки фильтра
        style.configure('Filter.TLabel',
                       font=('Arial', 10),
                       foreground=self.colors['fg_dark'],
                       background=self.colors['bg_light'])
    
    def setup_task_list(self, parent):
        """Настройка списка задач"""
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Создаем Treeview для списка задач
        columns = ('Задача', 'Дедлайн', 'Статус', 'Создано')
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # Настройка заголовков
        self.task_tree.heading('Задача', text='Задача')
        self.task_tree.heading('Дедлайн', text='Дедлайн')
        self.task_tree.heading('Статус', text='Статус')
        self.task_tree.heading('Создано', text='Создано')
        
        # Настройка ширины колонок
        self.task_tree.column('Задача', width=300)
        self.task_tree.column('Дедлайн', width=100)
        self.task_tree.column('Статус', width=100)
        self.task_tree.column('Создано', width=120)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение элементов
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Обработка выбора задачи
        self.task_tree.bind('<<TreeviewSelect>>', self.on_task_select)
        self.task_tree.bind('<Double-1>', self.edit_task)
    
    def setup_details_panel(self, parent):
        """Настройка панели деталей задачи"""
        details_frame = ttk.LabelFrame(parent, text="Детали задачи", padding=10)
        details_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Поле описания
        self.description_text = tk.Text(details_frame, height=4, width=80,
                                       background=self.colors['bg_light'],
                                       foreground=self.colors['fg_dark'],
                                       font=('Arial', 10))
        self.description_text.pack(fill=tk.X)
        self.description_text.config(state=tk.DISABLED)
    
    def load_tasks(self):
        """Загрузка задач из хранилища"""
        try:
            tasks_data = self.storage.load_tasks()
            self.tasks = [Task.from_dict(task_data) for task_data in tasks_data]
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить задачи: {e}")
            self.tasks = []
    
    def save_tasks(self):
        """Сохранение задач в хранилище"""
        try:
            tasks_data = [task.to_dict() for task in self.tasks]
            self.storage.save_tasks(tasks_data)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить задачи: {e}")
    
    def refresh_task_list(self):
        """Обновление списка задач"""
        # Очищаем список
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Фильтрация задач
        filtered_tasks = self.get_filtered_tasks()
        
        # Добавляем задачи в список
        for task in filtered_tasks:
            # Определяем статус
            status = "Выполнена" if task.completed else "Активна"
            
            # Проверяем просроченность
            if not task.completed and task.deadline and task.deadline < date.today():
                status = "Просрочена"
            
            # Форматируем дедлайн
            deadline_str = task.deadline.strftime("%d.%m.%Y") if task.deadline else "Не установлен"
            
            # Добавляем в дерево
            item_id = self.task_tree.insert('', tk.END, values=(
                task.title,
                deadline_str,
                status,
                task.created_date.split()[0] if task.created_date else ""
            ))
            
            # Сохраняем ID задачи в элементе
            self.task_tree.set(item_id, '#0', task.id)
            
            # Цветовое кодирование
            if task.completed:
                self.task_tree.set(item_id, '#1', 'completed')
            elif not task.completed and task.deadline and task.deadline < date.today():
                self.task_tree.set(item_id, '#1', 'overdue')
    
    def get_filtered_tasks(self):
        """Получение отфильтрованного списка задач"""
        filter_value = self.filter_var.get()
        
        if filter_value == "Все":
            return self.tasks
        elif filter_value == "Активные":
            return [task for task in self.tasks if not task.completed]
        elif filter_value == "Выполненные":
            return [task for task in self.tasks if task.completed]
        elif filter_value == "Просроченные":
            return [task for task in self.tasks 
                   if not task.completed and task.deadline and task.deadline < date.today()]
        
        return self.tasks
    
    def on_task_select(self, event):
        """Обработка выбора задачи"""
        selection = self.task_tree.selection()
        if selection:
            item = selection[0]
            task_id = self.task_tree.item(item)['values']
            if task_id:
                # Находим задачу по заголовку (так как ID может быть None)
                task_title = self.task_tree.item(item)['values'][0]
                selected_task = next((task for task in self.tasks if task.title == task_title), None)
                
                if selected_task:
                    self.selected_task_id = selected_task.id if selected_task.id else id(selected_task)
                    self.show_task_details(selected_task)
    
    def show_task_details(self, task):
        """Отображение деталей задачи"""
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete(1.0, tk.END)
        
        details = f"Название: {task.title}\n"
        details += f"Описание: {task.description or 'Не указано'}\n"
        details += f"Дедлайн: {task.deadline.strftime('%d.%m.%Y') if task.deadline else 'Не установлен'}\n"
        details += f"Статус: {'Выполнена' if task.completed else 'Активна'}\n"
        details += f"Создано: {task.created_date}"
        
        self.description_text.insert(tk.END, details)
        self.description_text.config(state=tk.DISABLED)
    
    def add_task(self):
        """Добавление новой задачи"""
        dialog = TaskDialog(self.root, "Добавить задачу")
        result = dialog.result
        
        if result:
            task = Task(
                title=result['title'],
                description=result['description'],
                deadline=result['deadline']
            )
            
            # Присваиваем уникальный ID
            task.id = len(self.tasks) + 1
            
            self.tasks.append(task)
            self.save_tasks()
            self.refresh_task_list()
            messagebox.showinfo("Успех", "Задача добавлена успешно!")
    
    def edit_task(self):
        """Редактирование выбранной задачи"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите задачу для редактирования")
            return
        
        # Находим выбранную задачу
        item = selection[0]
        task_title = self.task_tree.item(item)['values'][0]
        selected_task = next((task for task in self.tasks if task.title == task_title), None)
        
        if selected_task:
            dialog = TaskDialog(self.root, "Редактировать задачу", selected_task)
            result = dialog.result
            
            if result:
                selected_task.title = result['title']
                selected_task.description = result['description']
                selected_task.deadline = result['deadline']
                
                self.save_tasks()
                self.refresh_task_list()
                messagebox.showinfo("Успех", "Задача обновлена успешно!")
    
    def delete_task(self):
        """Удаление выбранной задачи"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите задачу для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту задачу?"):
            # Находим выбранную задачу
            item = selection[0]
            task_title = self.task_tree.item(item)['values'][0]
            self.tasks = [task for task in self.tasks if task.title != task_title]
            
            self.save_tasks()
            self.refresh_task_list()
            
            # Очищаем панель деталей
            self.description_text.config(state=tk.NORMAL)
            self.description_text.delete(1.0, tk.END)
            self.description_text.config(state=tk.DISABLED)
            
            messagebox.showinfo("Успех", "Задача удалена успешно!")
    
    def toggle_completion(self):
        """Переключение статуса выполнения задачи"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите задачу для изменения статуса")
            return
        
        # Находим выбранную задачу
        item = selection[0]
        task_title = self.task_tree.item(item)['values'][0]
        selected_task = next((task for task in self.tasks if task.title == task_title), None)
        
        if selected_task:
            selected_task.completed = not selected_task.completed
            status = "выполненной" if selected_task.completed else "активной"
            
            self.save_tasks()
            self.refresh_task_list()
            self.show_task_details(selected_task)
            
            messagebox.showinfo("Успех", f"Задача отмечена как {status}!")

class TaskDialog:
    """Диалог для добавления/редактирования задачи"""
    
    def __init__(self, parent, title, task=None):
        self.result = None
        
        # Создаем диалоговое окно
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем окно
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Создаем интерфейс
        self.setup_ui(task)
        
        # Ожидаем закрытия диалога
        self.dialog.wait_window()
    
    def setup_ui(self, task):
        """Настройка интерфейса диалога"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Название задачи
        ttk.Label(main_frame, text="Название задачи:").pack(anchor=tk.W)
        self.title_entry = ttk.Entry(main_frame, width=50)
        self.title_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Описание задачи
        ttk.Label(main_frame, text="Описание:").pack(anchor=tk.W)
        self.description_text = tk.Text(main_frame, height=6, width=50)
        self.description_text.pack(fill=tk.X, pady=(5, 10))
        
        # Дедлайн
        deadline_frame = ttk.Frame(main_frame)
        deadline_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(deadline_frame, text="Дедлайн:").pack(side=tk.LEFT)
        self.deadline_var = tk.StringVar()
        self.deadline_entry = ttk.Entry(deadline_frame, textvariable=self.deadline_var, width=15)
        self.deadline_entry.pack(side=tk.LEFT, padx=(10, 5))
        ttk.Label(deadline_frame, text="(дд.мм.гггг)").pack(side=tk.LEFT)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Сохранить", command=self.save_task).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT)
        
        # Заполняем поля если редактируем
        if task:
            self.title_entry.insert(0, task.title)
            self.description_text.insert(tk.END, task.description or "")
            if task.deadline:
                self.deadline_var.set(task.deadline.strftime("%d.%m.%Y"))
        
        # Фокус на поле названия
        self.title_entry.focus()
    
    def save_task(self):
        """Сохранение задачи"""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("Ошибка", "Введите название задачи")
            return
        
        description = self.description_text.get(1.0, tk.END).strip()
        
        # Парсинг даты
        deadline = None
        deadline_str = self.deadline_var.get().strip()
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, "%d.%m.%Y").date()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте дд.мм.гггг")
                return
        
        self.result = {
            'title': title,
            'description': description,
            'deadline': deadline
        }
        
        self.dialog.destroy()
