#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер задач - главный файл приложения
Запуск: python main.py
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from task_manager import TaskManagerApp

def main():
    """Главная функция запуска приложения"""
    try:
        # Создаем главное окно
        root = tk.Tk()
        
        # Настраиваем окно
        root.title("Менеджер задач")
        root.geometry("900x700")
        root.minsize(800, 600)
        
        # Устанавливаем иконку окна (если есть)
        try:
            root.iconbitmap(default="icon.ico")
        except:
            pass  # Игнорируем ошибку если иконки нет
        
        # Создаем экземпляр приложения
        app = TaskManagerApp(root)
        
        # Запускаем главный цикл приложения
        root.mainloop()
        
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
