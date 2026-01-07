import sqlite3
import os

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'teacher'
        )
    ''')
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            class TEXT NOT NULL,
            email TEXT,
            phone TEXT
        )
    ''')
    
    # Create results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            marks INTEGER NOT NULL,
            max_marks INTEGER NOT NULL DEFAULT 100,
            grade TEXT,
            semester TEXT,
            year INTEGER,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    ''')
    
    # Insert default admin user if not exists
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, role) 
        VALUES ('admin', 'admin123', 'admin')
    ''')
    
    conn.commit()
    conn.close()