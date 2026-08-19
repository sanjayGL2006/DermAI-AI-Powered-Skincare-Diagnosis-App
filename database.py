import os
import sqlite3
from flask import g, has_app_context

def get_db_path():
    if os.environ.get('DATABASE_PATH'):
        return os.environ['DATABASE_PATH']
    if os.environ.get('VERCEL'):
        return '/tmp/skincare.db'
    return 'data/skincare.db'

DATABASE = get_db_path()

def _ensure_tables(db):
    try:
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
        if not tables:
            init_db_schema(db)
    except Exception as e:
        print(f"[DB Schema Check] {e}")

def get_db():
    db_path = get_db_path()
    db_dir = os.path.dirname(db_path)
    if db_dir:
        try:
            os.makedirs(db_dir, exist_ok=True)
        except OSError:
            db_path = '/tmp/skincare.db'
            os.makedirs('/tmp', exist_ok=True)

    if has_app_context():
        if 'db' not in g:
            g.db = sqlite3.connect(db_path)
            g.db.row_factory = sqlite3.Row
            _ensure_tables(g.db)
        return g.db
    else:
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        _ensure_tables(db)
        return db

def close_db(e=None):
    if has_app_context():
        db = g.pop('db', None)
        if db is not None:
            db.close()

def init_db_schema(db):
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

def init_db():
    db = get_db()
    init_db_schema(db)
    if not has_app_context():
        db.close()
    print("Database initialized successfully.")


