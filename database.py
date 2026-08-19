import os
import sqlite3
from flask import g, has_app_context

def get_db_path():
    if os.environ.get('DATABASE_PATH'):
        return os.environ['DATABASE_PATH']
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        return '/tmp/skincare.db'
    return 'data/skincare.db'

def _connect_db():
    path = get_db_path()
    try:
        db_dir = os.path.dirname(path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(path)
    except Exception as e:
        print(f"[DB Warning] Could not open database at '{path}': {e}. Falling back to '/tmp/skincare.db'")
        path = '/tmp/skincare.db'
        os.makedirs('/tmp', exist_ok=True)
        conn = sqlite3.connect(path)
    
    conn.row_factory = sqlite3.Row
    return conn

def init_db_schema(db):
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

    try:
        db.execute("ALTER TABLE users ADD COLUMN username TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        db.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    except sqlite3.OperationalError:
        pass
    db.commit()

def _ensure_tables(db):
    try:
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
        if not tables:
            init_db_schema(db)
    except Exception as e:
        print(f"[DB Schema Check Error] {e}")
        try:
            init_db_schema(db)
        except Exception as err2:
            print(f"[DB Init Schema Error] {err2}")

def get_db():
    if has_app_context():
        if 'db' not in g:
            g.db = _connect_db()
            _ensure_tables(g.db)
        return g.db
    else:
        conn = _connect_db()
        _ensure_tables(conn)
        return conn

def close_db(e=None):
    if has_app_context():
        db = g.pop('db', None)
        if db is not None:
            db.close()

def init_db():
    db = get_db()
    init_db_schema(db)
    if not has_app_context():
        db.close()
    print("Database initialized successfully.")
