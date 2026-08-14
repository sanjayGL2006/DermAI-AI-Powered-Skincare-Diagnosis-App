import os
import sqlite3

DATABASE = 'data/skincare.db'

def get_db():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    # Migration queries to support local authentication on existing databases
    try:
        db.execute("ALTER TABLE users ADD COLUMN username TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        db.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    except sqlite3.OperationalError:
        pass
    
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            google_id TEXT UNIQUE,
            username TEXT UNIQUE,
            name TEXT,
            email TEXT UNIQUE,
            avatar TEXT,
            password_hash TEXT,
            created_at TEXT,
            analysis_count INTEGER DEFAULT 0,
            is_premium INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            skin_type TEXT,
            conditions TEXT,
            recommendations TEXT,
            diet_tips TEXT,
            lifestyle_tips TEXT,
            overall_score INTEGER,
            see_doctor INTEGER DEFAULT 0,
            doctor_reason TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id TEXT,
            role TEXT,
            message TEXT,
            created_at TEXT,
            FOREIGN KEY(analysis_id) REFERENCES analyses(id)
        );
    ''')
    db.commit()
    db.close()
    print("Database initialized successfully.")
