# app/config/settings.py

from .env import EnvConfig

class BaseConfig:
    SECRET_KEY = EnvConfig.SECRET_KEY

    MONGO_URI = EnvConfig.MONGO_URI
    MONGO_DBNAME = EnvConfig.MONGO_DBNAME
    MONGO_USERNAME = EnvConfig.MONGO_USERNAME
    MONGO_PASSWORD = EnvConfig.MONGO_PASSWORD

    SUPABASE_URL = EnvConfig.SUPABASE_URL
    SUPABASE_KEY = EnvConfig.SUPABASE_KEY
    SUPABASE_BUCKET = EnvConfig.SUPABASE_BUCKET

    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = "./flask_session"

    DEBUG = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True