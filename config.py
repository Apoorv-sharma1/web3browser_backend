import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-default')
    
    # Fix for SQLAlchemy 1.4+ (Standardizes postgres:// to postgresql://)
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Fallback to local sqlite in /tmp to prevent app crash on Vercel
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/fallback.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PORT = int(os.getenv('PORT', 5000))
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
