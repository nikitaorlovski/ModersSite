import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'salaries.db')

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS salaries
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
     nickname TEXT NOT NULL,
     role TEXT NOT NULL,
     project TEXT NOT NULL,
     server TEXT NOT NULL,
     online_hours INTEGER,
     questions INTEGER,
     complaints INTEGER,
     severe_complaints INTEGER,
     attached_moderators INTEGER,
     interviews INTEGER,
     online_top INTEGER,
     questions_top INTEGER,
     gma_review INTEGER,
     total_salary REAL,
     month TEXT NOT NULL,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     UNIQUE(nickname, project, server, month))
    ''')
    
    conn.commit()
    conn.close()

def save_salary(data):
    """Сохранение или обновление зарплаты модератора"""
    try:
        print("Получены данные:", data)  # Логируем входные данные
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Проверяем существует ли запись за этот месяц
        cursor.execute('''SELECT id FROM salaries 
                         WHERE nickname = ? AND project = ? AND server = ? AND month = ?''', 
                      (data['nickname'], data['project'], data['server'], data['month']))
        existing_record = cursor.fetchone()
        
        print("Существующая запись:", existing_record)  # Логируем результат проверки
        
        if existing_record:
            # Обновляем существующую запись
            cursor.execute('''UPDATE salaries 
                             SET role = ?,
                                 online_hours = ?,
                                 questions = ?,
                                 complaints = ?,
                                 severe_complaints = ?,
                                 attached_moderators = ?,
                                 interviews = ?,
                                 online_top = ?,
                                 questions_top = ?,
                                 gma_review = ?,
                                 total_salary = ?
                             WHERE nickname = ? AND project = ? AND server = ? AND month = ?''',
                          (data['role'], data['online_hours'],
                           data['questions'], data['complaints'],
                           data['severe_complaints'], data['attached_moderators'],
                           data['interviews'], data['online_top'],
                           data['questions_top'], data['gma_review'],
                           data['total_salary'], data['nickname'], 
                           data['project'], data['server'], data['month']))
            print("Запись обновлена")  # Логируем успешное обновление
        else:
            # Создаем новую запись
            cursor.execute('''INSERT INTO salaries 
                             (nickname, role, project, server, online_hours, questions, complaints,
                              severe_complaints, attached_moderators, interviews,
                              online_top, questions_top, gma_review, total_salary, month)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                              (data['nickname'], data['role'], data['project'], data['server'],
                               data['online_hours'], data['questions'], data['complaints'],
                               data['severe_complaints'], data['attached_moderators'],
                               data['interviews'], data['online_top'], data['questions_top'],
                               data['gma_review'], data['total_salary'], data['month']))
            print("Создана новая запись")  # Логируем создание новой записи
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Ошибка при сохранении:", str(e))  # Логируем ошибку
        raise e

def get_salary(nickname, project, server, month=None):
    """Получение зарплаты модератора за конкретный месяц"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if month:
        cursor.execute('''
        SELECT * FROM salaries 
        WHERE nickname = ? AND project = ? AND server = ? AND month = ?
        ORDER BY created_at DESC LIMIT 1
        ''', (nickname, project, server, month))
    else:
        cursor.execute('''
        SELECT * FROM salaries 
        WHERE nickname = ? AND project = ? AND server = ?
        ORDER BY created_at DESC LIMIT 1
        ''', (nickname, project, server))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'nickname': row[1],
            'role': row[2],
            'project': row[3],
            'server': row[4],
            'online_hours': row[5],
            'questions': row[6],
            'complaints': row[7],
            'severe_complaints': row[8],
            'attached_moderators': row[9],
            'interviews': row[10],
            'online_top': row[11],
            'questions_top': row[12],
            'gma_review': row[13],
            'total_salary': row[14],
            'month': row[15]
        }
    return None


def delete_salary_record(nickname, project, server, month):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM salaries WHERE nickname = ? AND project = ? AND server = ? AND month = ?''',
                       (nickname, project, server, month))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Ошибка удаления:", e)
        return False

def get_all_salaries(project, server, month=None):
    """Получение всех зарплат за конкретный месяц"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if month:
        cursor.execute('''
        SELECT * FROM salaries 
        WHERE project = ? AND server = ? AND month = ? 
        ORDER BY created_at DESC
        ''', (project, server, month))
    else:
        cursor.execute('''
        SELECT * FROM salaries 
        WHERE project = ? AND server = ? 
        ORDER BY created_at DESC
        ''', (project, server))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        'nickname': row[1],
        'role': row[2],
        'project': row[3],
        'server': row[4],
        'online_hours': row[5],
        'questions': row[6],
        'complaints': row[7],
        'severe_complaints': row[8],
        'attached_moderators': row[9],
        'interviews': row[10],
        'online_top': row[11],
        'questions_top': row[12],
        'gma_review': row[13],
        'total_salary': row[14],
        'month': row[15]
    } for row in rows] 