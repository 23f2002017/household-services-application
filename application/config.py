import os
curr_dir = os.path.dirname(__file__)

class config: 
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(config): 
    SQLITE_DB_DIR = os.path.join(curr_dir, "../db_directory")  
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "database.sqlite3") 
    DEBUG = True    