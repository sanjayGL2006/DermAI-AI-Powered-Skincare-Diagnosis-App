import sys
import os

# Add root directory to path so app modules can be imported seamlessly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, init_db

# Initialize database tables on serverless function load
try:
    init_db()
except Exception as e:
    print(f"[Vercel Init DB Warning] {e}")

# Expose app for Vercel Serverless Function
app = app
