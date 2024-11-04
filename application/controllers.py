from datetime import date, datetime
from flask import request, render_template, redirect
from flask import current_app as app
from .models import Customers, Professionals, Service, Request
from .database import db


admin_email = "khanikram6519@gmail.com"
admin_password = "Ikram744"


#Controllers 

#Login 
@app.route("/login", methods = ["GET", "POST"]) 
def Home():
    if request.method == "GET":
        return render_template("login_page.html")
    elif request.method=="POST": 
        if request.form["email"] == admin_email and request.form["password"] == admin_password:
            return render_template("admin_dashboard.html")
        
        customer = Customers.query.filter(Customers.Email == request.form["email"]).first()   
        if customer != None: 
            if customer.Password == request.form["password"]:
                return redirect(f"/customer/{customer.User_ID}/")
            else:
                return render_template("error.html", error_message = "Invalid Password " , back_to = "/login")
            
        professional = Professionals.query.filter(Professionals.Email == request.form["email"]).first() 
        print(professional) 
        if professional != None:
            if professional.Password == request.form["password"]:
                return redirect(f"/professional/{professional.Professional_ID}/")   
            else:
                return render_template("error.html", error_message = "Invalid Password " , back_to = "/login")
        else:
            return render_template("error.html", error_message = "Invalid Email ", back_to = "/login") 


#Customer Registration 
@app.route("/user_signup", methods=["GET", "POST"])
def User_Signup():
    if request.method=="GET":
        return render_template("user_signup.html")
    elif request.method=="POST":
        try:
            professional = Professionals.query.filter(Professionals.Email == request.form["email"]).first()
            customer = Customers.query.filter(Customers.Email == request.form["email"]).first()

            if professional == None and customer == None and request.form["email"] != admin_email:
                user = Customers(First_Name=request.form["first_name"], Last_Name=request.form["last_name"], Phone_No=request.form["phone"], Email=request.form["email"] , Password=request.form["password"] , Address=request.form["address"] , Pincode=request.form["pincode"] , Reviews=0 , Ratings=0 , Status="Registered" )
                db.session.add(user)
                db.session.commit()
            else:
                return render_template("error.html", error_message = "Error !! Account already exists with this Email ", back_to = "/user_signup")    
        except:
            return render_template("error.html" , error_message = "Something went wrong !! ", back_to = "/user_signup") 
        else:
            return redirect("/login") 
        

#Professional Registration  
@app.route("/professional_signup", methods=["GET", "POST"])
def Professional_Signup():
    services = [service[0] for service in list(set(Service.query.with_entities(Service.Type).all()))]
    if request.method == "GET":
        return render_template("professional_signup.html", service_lst = services)  
    if request.method == "POST":
        professional = Professionals.query.filter(Professionals.Email == request.form["email"]).first()
        customer = Customers.query.filter(Customers.Email == request.form["email"]).first()
        if (professional != None) or (customer != None) or (request.form["email"] == admin_email):
            return render_template("error.html", error_message = "Error !! Account already exists with this Email ", back_to = "/professional_signup")
        elif (str(request.form["resume"])[-4:]) != ".pdf":
            return render_template("error.html" , error_message = "Error !! Upload the valid PDF file ", back_to = "/professional_signup")
        else: 
            try:  
                #file = request.files["resume"]                                                                                                                                                                                                                               # , Resume = request.form["resume"]                   
                professional = Professionals(First_Name = request.form["first_name"] , Last_Name = request.form["last_name"] , Email = request.form["email"] , Password = request.form["password"] , Service_Type = request.form["service_type"] , Experience = request.form["experience"] , Pincode = request.form["pincode"] , Join_Date = date.today() , Reviews = 0 , Ratings = 0 , Status = "Registered" )
                db.session.add(professional)
                #print(type(file))
                db.session.commit()
            except:
                return render_template("error.html" , error_message = "Something went wrong !! ", back_to = "/professional_signup")
            else:
                return redirect("/login")
                #return render_template("error.html" , error_message = "Something went wrong !! ", back_to = "/professional_signup")

        

#Admin Portal 
@app.route("/admin_portal")
def Admin():
    users = Customers.query.all()
    professionals = Professionals.query.all()
    services = Service.query.all()
    return render_template("admin_dashboard.html", services=services, professionals=professionals, users=users) 

#Adding a new service
@app.route("/create_service", methods = ["GET", "POST"])
def Create_Service():
    if request.method == "GET" :
        return render_template("create_service.html")
    elif request.method == "POST" :
        try:
            service = Service(Type = request.form["type"], Description = request.form["description"] , Base_Price = request.form["base_price"] , Time_required = request.form["time"])
            db.session.add(service)
            db.session.commit()
        except:
            return render_template("error.html", error_message = "Something went wrong !! ", back_to = "/create_service")   
        else:
            return redirect("/admin_portal") 

#Editing an existing service
@app.route("/edit_service/<int:service_id>", methods = ["GET", "POST"])   
def Edit_Service(service_id):
    service = Service.query.filter(Service.Service_ID == service_id).first()
    if request.method == "GET" :
        return render_template("update_service.html", service = service)  
    if request.method == "POST" :
        try:
            service.Type = request.form["type"]
            service.Description = request.form["description"]
            service.Base_Price = request.form["base_price"]
            service.Time_required = request.form["time"]
            db.session.commit()
        except:
            return render_template("error.html", error_message = "Something went Wrong !!", back_to = f"/edit_service/{service.Service_ID}" )    
        else:
            return redirect("/admin_portal")

#Deleting an existing service       
@app.route("/delete_service/<int:service_id>")
def Delete_Service(service_id):
    service = Service.query.filter(Service.Service_ID == service_id).first()
    try:
        db.session.delete(service)
        db.session.commit()
    except:
        return render_template("error.html", error_message="Something went Wrong !!", back_to = "/admin_portal")    
    else:
        return redirect("/admin_portal")
   
#Approve a Professional 
@app.route("/approve_professional/<int:professional_id>") 
def Approve_Professional(professional_id):
    professional = Professionals.query.filter(Professionals.Professional_ID == professional_id).first()
    try:
        professional.Status = "Approved"
        db.session.commit()
    except:
        return render_template("error.html", error_message="Something went Wrong !!", back_to = "/admin_portal")    
    else:
        return redirect("/admin_portal")  
 
#Blocking a Professional
@app.route("/block_professional/<int:professional_id>") 
def Block_Professional(professional_id):
    professional = Professionals.query.filter(Professionals.Professional_ID == professional_id).first()
    try:
        professional.Status = "Blocked"
        db.session.commit()
    except:
        return render_template("error.html", error_message="Something went Wrong !!", back_to = "/admin_portal")    
    else:
        return redirect("/admin_portal")   
    
#Deleting a Professional
@app.route("/delete_professional/<int:professional_id>") 
def Delete_Professional(professional_id):
    professional = Professionals.query.filter(Professionals.Professional_ID == professional_id).first()
    try:
        db.session.delete(professional)
        db.session.commit()
    except:
        return render_template("error.html", error_message="Something went Wrong !!", back_to = "/admin_portal")    
    else:
        return redirect("/admin_portal")   
    
#Block a User
@app.route("/block_user/<int:user_id>")     
def Block_User(user_id):
    user = Customers.query.filter(Customers.User_ID == user_id).first()
    try:
        user.Status = "Blocked"
        db.session.commit()
    except:
        return render_template("error.html", error_message="Something went Wrong !!", back_to = "/admin_portal")    
    else:
        return redirect("/admin_portal")
    
#Unblock a User
@app.route("/unblock_user/<int:user_id>")   
def Unblock_User(user_id):
    user = Customers.query.filter(Customers.User_ID == user_id).first()
    try:
        user.Status = "Registered"
        db.session.commit()
    except:
        return render_template("error.html", error_message="Something went Wrong !!", back_to = "/admin_portal")    
    else:
        return redirect("/admin_portal")   