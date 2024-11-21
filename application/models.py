from .database import db

#Models 
class Customers(db.Model):
    __tablename__ = "Users"
    User_ID = db.Column(db.Integer, primary_key = True, autoincrement = True)
    First_Name = db.Column(db.Text, nullable = False)
    Last_Name = db.Column(db.Text, nullable = False)
    Phone_No = db.Column(db.BigInteger, unique = True, nullable = False) 
    Email = db.Column(db.String, unique = True, nullable = False) 
    Password = db.Column(db.String, nullable = False) 
    Address = db.Column(db.String, nullable = False) 
    Pincode = db.Column(db.Integer, nullable = False) 
    Reviews = db.Column(db.Integer, nullable = False)
    Ratings = db.Column(db.Float, nullable = False) 
    Status = db.Column(db.String, nullable = False) 

class Professionals(db.Model):
    __tablename__ = "Professionals"
    Professional_ID = db.Column(db.Integer, primary_key = True, autoincrement = True)
    First_Name = db.Column(db.Text, nullable = False)
    Last_Name = db.Column(db.Text, nullable = False) 
    Email = db.Column(db.String, unique = True, nullable = False) 
    Password = db.Column(db.String, nullable = False)
    Join_Date = db.Column(db.Date, nullable = False) 
    Service_Type = db.Column(db.Text, nullable = False )
    Experience = db.Column(db.Integer, nullable = False)
    Pincode = db.Column(db.Integer, nullable = False) 
    Reviews = db.Column(db.Integer, nullable = False)
    Ratings = db.Column(db.Float, nullable = False) 
    Status = db.Column(db.Text, nullable = False) 

class Service(db.Model): 
    __tablename__ = "Services"
    Service_ID = db.Column(db.Integer, primary_key = True, autoincrement = True)
    Type = db.Column(db.String, nullable = False)
    Description = db.Column(db.String, unique = True, nullable = False)
    Base_Price = db.Column(db.Float, nullable = False)
    Time_required = db.Column(db.Integer, nullable = False)

class Request(db.Model): 
    __tablename__ = "Service_Requests"   
    Request_ID =  db.Column(db.Integer, primary_key = True, autoincrement = True)
    User_ID = db.Column(db.Integer, nullable = False)
    Professional_ID = db.Column(db.Integer)
    Service_ID = db.Column(db.Integer, db.ForeignKey("Services.Service_ID"), nullable = False)
    Request_time = db.Column(db.DateTime, nullable = False)
    Completion_time = db.Column(db.DateTime)
    Rating_to_Prof = db.Column(db.Integer)
    Remark = db.Column(db.Text)
    Rating_to_Cust = db.Column(db.Integer)
    Status = db.Column(db.Text, nullable = False) 

class Request_Response(db.Model):
    __tablename__ = "Service_Professional_Response" 
    Request_ID = db.Column(db.Integer, primary_key = True)
    Service_ID = db.Column(db.Integer, nullable = False)
    User_ID = db.Column(db.Integer, nullable = False)
    Professional_ID = db.Column(db.Integer, primary_key = True)
    Action = db.Column(db.Text, nullable = False)