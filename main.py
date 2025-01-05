import os
from flask import Flask 
from application.database import db
from application.config import LocalDevelopmentConfig

app = None 
api = None

from application.api import *   #API paths and controllers

def create_app(): 
    app = Flask(__name__)
    if os.getenv("ENV", "development") == "production": 
        print("Production version is not yet available") 
    else:
        print("Starting the local developmnet version of this app.") 
        app.config.from_object(LocalDevelopmentConfig) 
    db.init_app(app) 
    api.init_app(app)
    app.app_context().push() 
    return app 

app = create_app() 

from application.controllers import *    #Controller imports Models

if __name__=="__main__": 
    app.run()