#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для работы с данными задач
Сохранение и загрузка в JSON формате
"""

import json
import os
from datetime import datetime

class DataStorage:
    """Класс для управления сохранением и загрузкой данных задач"""
    
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.ensure_data_file()
    
    def ensure_data_file(self):
        """Создание файла данных если он не существует"""
        if not os.path.exists(self.filename):
            try:
                with open(self.filename, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Ошибка создания файла данных: {e}")
    
    def load_tasks(self):
        """Загрузка списка задач из файла"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except FileNotFoundError:
            # Создаем пустой файл если его нет
            self.ensure_data_file()
            return []
        except json.JSONDecodeError:
            print(f"Ошибка чтения JSON из файла {self.filename}")
            # Создаем резервную копию поврежденного файла
            backup_name = f"{self.filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                os.rename(self.filename, backup_name)
                print(f"Поврежденный файл переименован в {backup_name}")
            except:
                pass
            
            # Создаем новый пустой файл
            self.ensure_data_file()
            return []
        except Exception as e:
            print(f"Ошибка загрузки задач: {e}")
            return []
    
    def save_tasks(self, tasks):
        """Сохранение списка задач в файл"""
        try:
            # Создаем резервную копию перед сохранением
            if os.path.exists(self.filename):
                backup_name = f"{self.filename}.bak"
                try:
                    import shutil
                    shutil.copy2(self.filename, backup_name)
                except:
                    pass  # Игнорируем ошибки резервного копирования
            
            # Сохраняем данные
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения задач: {e}")
            # Пытаемся восстановить из резервной копии
            backup_name = f"{self.filename}.bak"
            if os.path.exists(backup_name):
                try:
                    import shutil
                    shutil.copy2(backup_name, self.filename)
                    print("Данные восстановлены из резервной копии")
                except:
                    pass
            
            return False
    
    def backup_data(self):
        """Создание резервной копии данных"""
        if not os.path.exists(self.filename):
            return False
        
        try:
            backup_name = f"{self.filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            import shutil
            shutil.copy2(self.filename, backup_name)
            return backup_name
        except Exception as e:
            print(f"Ошибка создания резервной копии: {e}")
            return False
    
    def get_data_stats(self):
        """Получение статистики по файлу данных"""
        try:
            if os.path.exists(self.filename):
                stat = os.stat(self.filename)
                return {
                    'file_size': stat.st_size,
                    'modified_time': datetime.fromtimestamp(stat.st_mtime),
                    'created_time': datetime.fromtimestamp(stat.st_ctime)
                }
        except:
            pass
        return None
