from werkzeug.exceptions import HTTPException
from flask import make_response
import json

class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)   

class ValidationError(HTTPException):
    def __init__(self, error_code, error_message):
        message = {"Error Code" : error_code, "Error Message" : error_message}  
        self.response = make_response(json.dumps(message), error_code)          