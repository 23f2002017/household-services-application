from datetime import date, datetime
from flask import request, render_template, redirect
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from flask import current_app as app
from .models import Customers, Professionals, Service, Request, Request_Response
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
                return redirect(f"/customer/{customer.User_ID}")
            else:
                return render_template("error.html", error_message = "Invalid Password " , back_to = "/login")
            
        professional = Professionals.query.filter(Professionals.Email == request.form["email"]).first() 
        print(professional) 
        if professional != None:
            if professional.Password == request.form["password"]:
                return redirect(f"/professional/{professional.Professional_ID}")   
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
        else: 
            try:                                                                                                                                                                                                                                              
                professional = Professionals(First_Name = request.form["first_name"] , Last_Name = request.form["last_name"] , Email = request.form["email"] , Password = request.form["password"] , Service_Type = request.form["service_type"] , Experience = request.form["experience"] , Pincode = request.form["pincode"] , Join_Date = date.today() , Reviews = 0 , Ratings = 0 , Status = "Registered" )
                db.session.add(professional)
                db.session.commit()
            except:
                return render_template("error.html" , error_message = "Something went wrong !! ", back_to = "/professional_signup")
            else:
                return redirect("/login")
                #return render_template("error.html" , error_message = "Something went really wrong !! ", back_to = "/professional_signup")

        
#Admin Portal 
@app.route("/admin_portal")
def Admin():
    users = Customers.query.all()
    professionals = Professionals.query.all()
    services = Service.query.all()
    service_requests = Request.query.order_by(Request.Request_ID.desc()).all()
    return render_template("admin_dashboard.html", services=services, professionals=professionals, service_requests=service_requests, users=users) 


#Admin Summary
@app.route("/admin_summary")
def Admin_Summary():
    service_requests = Request.query.all()
    sum_of_ratings, total_rating = 0, 0
    for request in service_requests:
        if request.Rating_to_Prof!=None:
            total_rating+=1
            sum_of_ratings+=request.Rating_to_Prof
    avg_cust_rating = (sum_of_ratings/total_rating) 
    sum_of_ratings, total_rating = 0, 0
    for request in service_requests:
        if request.Rating_to_Cust!=None:
            total_rating+=1
            sum_of_ratings+=request.Rating_to_Cust 
    avg_prof_rating = (sum_of_ratings/total_rating) 
    total_requests, open_requests, accepted_requests, closed_requests = 0, 0, 0, 0
    for request in service_requests:
        total_requests+=1
        if request.Status == "Open":
            open_requests+=1
        elif  request.Status == "Accepted":
            accepted_requests+=1
        else:
            closed_requests+=1  
    data = {"Total Requests":total_requests, "Open":open_requests, "Assigned":accepted_requests, "Closed":closed_requests}
    plt.figure(figsize=(10,6))
    plt.bar(list(data.keys()), list(data.values()), edgecolor="white", width = 0.5, color=['deepskyblue', 'seagreen', 'crimson', 'goldenrod'])   
    plt.title("Service Bookings") 
    plt.xlabel("Booking Statuses")
    plt.ylabel("No. of bookings") 
    plt.savefig("./static/request_status.png")
    return render_template("admin_summary.html", avg_cust_rating=avg_cust_rating, avg_prof_rating=avg_prof_rating)


#Admin Search 
@app.route("/admin/search", methods = ["GET", "POST"])
def Admin_Search():
    if request.method == "GET":
        return render_template("admin_search_form.html")
    else:
        try:
            if request.form["search_by"] == "professional_id":
                field = int(request.form["field"])
                professional = [Professionals.query.filter(Professionals.Professional_ID == field).first()]
                print(professional)
                return render_template("search_result.html", professionals = professional, type = "professional")
            if request.form["search_by"] == "professional_name":
                field = request.form["field"]
                query = Professionals.query.filter(db.func.concat(Professionals.First_Name, " ", Professionals.Last_Name).like(f"%{field}%"))
                if query.count() != 0:
                    professionals = query.all()
                else:
                    professionals = [None]    
                return render_template("search_result.html", professionals = professionals, type = "professional")
            if request.form["search_by"] == "professional_type":
                field = request.form["field"]
                query = Professionals.query.filter(Professionals.Service_Type.like(f"%{field}%"))
                if query.count() != 0:
                    professionals = query.all()
                else:
                    professionals = [None]    
                return render_template("search_result.html", professionals = professionals, type = "professional")
            if request.form["search_by"] == "customer_id":
                field = int(request.form["field"])
                customer = [Customers.query.filter(Customers.User_ID == field).first()]
                return render_template("search_result.html", users = customer, type = "customer")
            if request.form["search_by"] == "customer_name":
                field = request.form["field"]
                query = Customers.query.filter(db.func.concat(Customers.First_Name, " ", Customers.Last_Name).like(f"%{field}%"))
                if query.count() != 0:
                    customers = query.all()
                else:
                    customers = [None]    
                return render_template("search_result.html", users = customers, type = "customer")
            if request.form["search_by"] == "service_id":
                field = int(request.form["field"])
                service = [Service.query.filter(Service.Service_ID == field).first()]
                return render_template("search_result.html", services = service, type = "service")
            if request.form["search_by"] == "service_type": 
                field = request.form["field"]
                query = Service.query.filter(Service.Type.like(f"%{field}%"))
                if query.count() != 0:
                    services = query.all()
                else:
                    services = [None]    
                return render_template("search_result.html", services = services, type = "service")
        except:
            return render_template("error.html", error_message = "Something went wrong !! ", back_to = "/admin/search")    


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
        requests = Request.query.filter(Request.Professional_ID == professional_id).all()
        for request in requests:
            if request.Status == "Accepted":
                return render_template("error.html", error_message="Error !! You can't block a professional who has accepted for a service. Please try again later ", back_to = "/admin_portal")
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
        requests = Request.query.filter(Request.Professional_ID == professional_id).all()
        for request in requests:
            if request.Status == "Accepted":
                return render_template("error.html", error_message="Error !! You can't delete a professional who has accepted for a service. Please try again later ", back_to = "/admin_portal")
        db.session.delete(professional)
        db.session.commit()
    except:
        return render_template("error.html", error_message="Something went Wrong !!", back_to = "/admin_portal")    
    else:
        return redirect("/admin_portal")  


#Get details of a Professional
@app.route("/get_details_professional/<int:professional_id>")
def Professional_Details(professional_id):
    professional = Professionals.query.filter(Professionals.Professional_ID == professional_id).first()
    return render_template("professional_details.html", professional=professional)


#Block a User
@app.route("/block_user/<int:user_id>")     
def Block_User(user_id):
    user = Customers.query.filter(Customers.User_ID == user_id).first()
    try:
        requests = Request.query.filter(Request.User_ID == user_id).all()
        for request in requests:
            if request.Status == "Open" or request.Status == "Accepted":
                return render_template("error.html", error_message="Error !! You can't block a customer whose service is not yet closed. Please try again later ", back_to = "/admin_portal")
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


#User Dashboard
@app.route("/customer/<int:user_id>")  
def User_Portal(user_id):
    user =  Customers.query.filter(Customers.User_ID == user_id).first()
    service_types = set([service_tuple[0] for service_tuple in Professionals.query.filter(db.or_(Professionals.Pincode == (user.Pincode-1), Professionals.Pincode == user.Pincode, Professionals.Pincode == (user.Pincode+1))).with_entities(Professionals.Service_Type).all()])
    services = []
    for service in service_types:
        services = services + Service.query.filter(Service.Type == service).all()
    bookings = Request.query.filter(Request.User_ID == user_id).all()
    request_history = []
    for booking in bookings:
        fields = {"Request ID":"", "Service Description":"", "Request Time":"" , "Professional Name":"", "Email":"", "Status":""}
        service_description = Service.query.filter(Service.Service_ID == booking.Service_ID).first().Description
        professional = Professionals.query.filter(Professionals.Professional_ID == booking.Professional_ID).first()
        fields["Request ID"] = booking.Request_ID
        fields["Service Description"] = service_description
        fields["Request Time"] = str(booking.Request_time)[:-7]
        if professional != None:
            fields["Professional Name"] = professional.First_Name +" "+ professional.Last_Name
            fields["Email"] = professional.Email 
        fields["Status"] = booking.Status
        request_history.append(fields) 
    return render_template("customer_dashboard.html", user = user, services = services, request_history = request_history)


#Summary of a Customer
@app.route("/customer_summary/<int:user_id>")
def Customer_Summary(user_id):
    user = Customers.query.filter(Customers.User_ID == user_id).first()
    requests = Request.query.filter(Request.User_ID == user_id).all() 
    total_requests, open_requests, accepted_requests, closed_requests = 0, 0, 0, 0
    for request in requests:
        total_requests+=1
        if request.Status == "Open":
            open_requests+=1
        elif  request.Status == "Accepted":
            accepted_requests+=1
        else:
            closed_requests+=1  
    data = {"Total Requests":total_requests, "Open":open_requests, "Assigned":accepted_requests, "Closed":closed_requests}
    plt.figure(figsize=(10,6))
    plt.bar(list(data.keys()), list(data.values()), edgecolor="white", width = 0.5, color=['deepskyblue', 'seagreen', 'crimson', 'goldenrod'])   
    plt.title("Service Bookings") 
    plt.xlabel("Booking Statuses")
    plt.ylabel("No. of bookings") 
    plt.savefig("./static/booking_status.png")
    return render_template("customer_summary.html", user=user)


#Search in User
@app.route("/customer_search/<int:user_id>", methods = ["GET", "POST"])
def Customer_Search(user_id):
    user = Customers.query.filter(Customers.User_ID == user_id).first()
    if request.method == "GET": 
        return render_template("customer_search_form.html", user = user) 
    else:
        try:
            if request.form["search_by"] == "service_id":
                id = int(request.form["field"])
                query = Service.query.filter(Service.Service_ID == id)
                if query.count() == 0:
                    return render_template("error.html", error_message="Error!! The following service does not exist ", back_to = f"/customer_search/{user_id}")
                service = query.first()
                service_types = set([service_tuple[0] for service_tuple in Professionals.query.filter(db.or_(Professionals.Pincode == (user.Pincode-1), Professionals.Pincode == user.Pincode, Professionals.Pincode == (user.Pincode+1))).with_entities(Professionals.Service_Type).all()])
                services = []
                if service.Type in service_types:
                    services = [service]
                return render_template("searched_service.html", services=services, user=user)    
            if request.form["search_by"] == "service_type":
                type = request.form["field"]
                query = Service.query.filter(Service.Type.like(f"%{type}%"))
                if query.count() == 0:
                    return render_template("error.html", error_message="Error!! The following service either does not exist or there is typo in your search ", back_to = f"/customer_search/{user_id}")
                services = query.all()
                service_types = set([service_tuple[0] for service_tuple in Professionals.query.filter(db.or_(Professionals.Pincode == (user.Pincode-1), Professionals.Pincode == user.Pincode, Professionals.Pincode == (user.Pincode+1))).with_entities(Professionals.Service_Type).all()])
                for service in services:
                    if service.Type not in service_types:
                        services.remove(service)
                return render_template("searched_service.html", services=services, user=user)
            if request.form["search_by"] == "search_description":  
                description = request.form["field"]
                query = Service.query.filter(Service.Description.like(f"%{description}%"))
                if query.count() == 0:
                    return render_template("error.html", error_message="Error!! The following service either does not exist or there is typo in your search ", back_to = f"/customer_search/{user_id}")
                services = query.all()
                service_types = set([service_tuple[0] for service_tuple in Professionals.query.filter(db.or_(Professionals.Pincode == (user.Pincode-1), Professionals.Pincode == user.Pincode, Professionals.Pincode == (user.Pincode+1))).with_entities(Professionals.Service_Type).all()])
                for service in services:
                    if service.Type not in service_types:
                        services.remove(service)
                return render_template("searched_service.html", services=services, user=user) 
        except:
            return render_template("error.html", error_message="Something went Wrong !!", back_to = f"/customer_search/{user_id}")


#Update User Profile
@app.route("/update_user_profile/<int:user_id>", methods = ["GET", "POST"])
def Update_User_Profile(user_id):
    user =  Customers.query.filter(Customers.User_ID == user_id).first()
    if request.method == "GET":
        return render_template("update_user_profile.html", user = user)
    if request.method == "POST":
        try:
            user.First_Name = request.form["first_name"]
            user.Last_Name = request.form["last_name"]
            user.Phone_No = request.form["phone"]
            user.Password = request.form["password"]
            user.Address = request.form["address"]
            user.Pincode = request.form["pincode"]
            db.session.commit()
        except:
            return render_template("error.html", error_message="Something went Wrong !!", back_to = f"/update_user_profile/{user_id}" )    
        else:
            return redirect(f"/customer/{user_id}")
        

#User Service Booking
@app.route("/<int:user_id>/book_service/<int:service_id>")
def Service_Booking(user_id, service_id):
    check = Request.query.filter(db.and_(Request.User_ID == user_id, Request.Service_ID == service_id, (db.or_(Request.Status == "Open", Request.Status == "Accepted")))).first()
    if check != None:
        return render_template("error.html", error_message="Error !! You've already booked this service ", back_to = f"/customer/{user_id}") 
    service = Service.query.filter(Service.Service_ID == service_id).first()
    user = Customers.query.filter(Customers.User_ID == user_id).first() 
    professionals = Professionals.query.filter(db.or_(Professionals.Pincode == (user.Pincode-1), Professionals.Pincode == user.Pincode, Professionals.Pincode == (user.Pincode+1))).filter(Professionals.Service_Type == service.Type).all()
    try:
        booking = Request(User_ID = user_id, Service_ID = service_id, Request_time = datetime.now(), Status = "Open") 
        db.session.add(booking) 
        db.session.flush() 
        for professional in professionals:
            notify_professional = Request_Response(Request_ID = booking.Request_ID, Service_ID = service_id , User_ID = user_id, Professional_ID = professional.Professional_ID, Action = "No Action") 
            db.session.add(notify_professional)   
        db.session.commit()  
    except: 
        return render_template("error.html", error_message="Something went Wrong !!", back_to = f"/customer/{user_id}")       
    else:
        return redirect(f"/customer/{user_id}")
    

#Closing a Service Request by User
@app.route("/<int:user_id>/customer_close_request/<int:request_id>", methods = ["GET", "POST"])
def User_Close_Request(user_id, request_id):
    s_request = Request.query.filter(Request.Request_ID == request_id).first()
    service = Service.query.filter(Service.Service_ID == s_request.Service_ID).first()
    professional = Professionals.query.filter(Professionals.Professional_ID == s_request.Professional_ID).first()
    if request.method == "GET":
        return render_template("user_request_closure.html", request = s_request, professional = professional, service = service)
    if request.method == "POST":
        try:
            s_request.Completion_time = datetime.now()
            s_request.Rating_to_Prof = int(request.form["rating"])
            s_request.Remark = request.form["remarks"]
            s_request.Status = "User Closed"
            professional.Reviews = professional.Reviews + 1
            professional.Ratings = ((professional.Ratings*(professional.Reviews-1)) + int(request.form["rating"]))/(professional.Reviews)
            db.session.commit()
        except:
            return render_template("error.html", error_message="Something went Wrong !!", back_to = f"/{user_id}/customer_close_request/{request_id}")    
        else:
            return redirect(f"/customer/{user_id}")
        

#Get Details of a service request
@app.route("/get_service_request_details/<int:request_id>")  
def Service_Request_Details(request_id):
    request = Request.query.filter(Request.Request_ID == request_id).first()   
    user = Customers.query.filter(Customers.User_ID == request.User_ID).first()
    service = Service.query.filter(Service.Service_ID == request.Service_ID).first()
    professional = None
    if request.Professional_ID != None:
        professional = Professionals.query.filter(Professionals.Professional_ID == request.Professional_ID).first()
    return render_template("service_request_details.html", request=request, user=user, professional=professional, service=service)
        

#Professional Dashboard
@app.route("/professional/<int:professional_id>")  
def Professional_Portal(professional_id): 
    professional = Professionals.query.filter(Professionals.Professional_ID == professional_id).first()    
    accepted_request  = Request.query.filter(db.and_(Request.Professional_ID == professional_id, Request.Status == "Accepted")).first()
    user_requested = None
    service_requested = None
    if accepted_request != None:
        user_requested = Customers.query.filter(Customers.User_ID == accepted_request.User_ID).first()
        service_requested = Service.query.filter(Service.Service_ID == accepted_request.Service_ID).first()    
    services_provided = [id_tup[0] for id_tup in Service.query.filter(Service.Type == professional.Service_Type).with_entities(Service.Service_ID).all()]
    open_requests = Request.query.filter(Request.Service_ID.in_(services_provided)).filter(Request.Status == "Open").all()
    open_lst = []
    for request in open_requests:
        if Request_Response.query.filter(db.and_(Request_Response.Request_ID == request.Request_ID, Request_Response.Professional_ID == professional_id)).first()!= None: 
            if Request_Response.query.filter(db.and_(Request_Response.Request_ID == request.Request_ID, Request_Response.Professional_ID == professional_id)).first().Action != "Rejected":
                fields = {"ID":"", "Request Type":"","Base Fare":"", "Customer Name":"", "Phone No.":"", "Address":"", "Pincode":""}
                user = Customers.query.filter(Customers.User_ID == request.User_ID).first()
                service = Service.query.filter(Service.Service_ID == request.Service_ID).first()
                fields["ID"] = request.Request_ID
                fields["Request Type"] = service.Description
                fields["Base Fare"] = service.Base_Price
                fields["Customer Name"] = user.First_Name +" "+ user.Last_Name
                fields["Phone No."] = user.Phone_No
                fields["Address"] = user.Address
                fields["Pincode"] = user.Pincode
                open_lst.append(fields)
    closed_requests = Request.query.filter(db.and_(Request.Professional_ID == professional_id, (db.or_(Request.Status == "User Closed", Request.Status == "Closed")))).all()
    close_lst = []
    for request in closed_requests:
        fields = {"ID":"", "Customer Name":"", "Phone No.":"", "Address":"", "Pincode":"", "Request Date":"", "Rating":"", "Remark":"", "Status":""}
        user = Customers.query.filter(Customers.User_ID == request.User_ID).first()
        fields["ID"] = request.Request_ID
        fields["Customer Name"] = user.First_Name +" "+ user.Last_Name
        fields["Phone No."] = user.Phone_No
        fields["Address"] = user.Address
        fields["Pincode"] = user.Pincode
        fields["Request Date"] = str(request.Request_time)[:-7]
        fields["Rating"] = request.Rating_to_Prof
        fields["Remark"] = request.Remark
        fields["Status"] = request.Status
        close_lst.append(fields)
    return render_template("professional_dashboard.html", accepted_request = accepted_request, user_requested = user_requested, service_requested = service_requested, professional = professional, open_requests = open_lst, closed_requests = close_lst)     


#Summary of a Professional
@app.route("/professional_summary/<int:professional_id>")
def Professional_Summary(professional_id):
    professional = Professionals.query.filter(Professionals.Professional_ID == professional_id).first()
    request_responses = Request_Response.query.filter(Request_Response.Professional_ID == professional_id).all() 
    total_requests, accepted_requests, rejected_requests, no_actions = 0, 0, 0, 0
    for request in request_responses:
        total_requests+=1
        if request.Action == "Accepted":
            accepted_requests+=1
        elif  request.Action == "Rejected":
            rejected_requests+=1
        else:
            no_actions+=1  
    data = {"Total Requests":total_requests, "Accepted":accepted_requests, "Rejected":rejected_requests, "No Action":no_actions}
    plt.figure(figsize=(10,6))
    plt.bar(list(data.keys()), list(data.values()), edgecolor="white", width = 0.5, color=['deepskyblue', 'seagreen', 'crimson', 'goldenrod'])   
    plt.title("Service Requests") 
    plt.xlabel("Response to requests")
    plt.ylabel("No. of requests") 
    plt.savefig("./static/request_actions.png")
    return render_template("professional_summary.html", professional=professional)     


#Search in Professional 
@app.route("/professional_search/<int:professional_id>", methods = ["GET", "POST"])
def Professional_Search(professional_id):
    professional = Professionals.query.filter(Professionals.Professional_ID == professional_id).first()
    closed_requests = Request.query.filter(db.and_(Request.Professional_ID == professional_id, (db.or_(Request.Status == "User Closed", Request.Status == "Closed")))).all()
    if request.method == "GET":
        return render_template("professional_search_form.html", professional=professional)
    else:
        try:
            if request.form["search_by"] == "request_id":
                id = int(request.form["field"]) 
                searched_request = []
                for s_request in closed_requests:
                    if s_request.Request_ID == id:
                        fields = {"ID":"", "Customer Name":"", "Phone No.":"", "Address":"", "Pincode":"", "Request Date":"", "Rating":"", "Remark":"", "Status":""}
                        user = Customers.query.filter(Customers.User_ID == s_request.User_ID).first()
                        fields["ID"] = s_request.Request_ID
                        fields["Customer Name"] = user.First_Name +" "+ user.Last_Name
                        fields["Phone No."] = user.Phone_No
                        fields["Address"] = user.Address
                        fields["Pincode"] = user.Pincode
                        fields["Request Date"] = str(s_request.Request_time)[:-7]
                        fields["Rating"] = s_request.Rating_to_Prof
                        fields["Remark"] = s_request.Remark
                        fields["Status"] = s_request.Status
                        searched_request.append(fields) 
                return render_template("searched_request.html", professional=professional, searched_request = searched_request)    
            if request.form["search_by"] == "customer_name":
                name = request.form["field"]
                searched_request = []
                for s_request in closed_requests:
                    user = Customers.query.filter(Customers.User_ID == s_request.User_ID).first()
                    if name in (user.First_Name+" "+user.Last_Name).lower():
                        fields = {"ID":"", "Customer Name":"", "Phone No.":"", "Address":"", "Pincode":"", "Request Date":"", "Rating":"", "Remark":"", "Status":""}
                        fields["ID"] = s_request.Request_ID 
                        fields["Customer Name"] = user.First_Name +" "+ user.Last_Name
                        fields["Phone No."] = user.Phone_No
                        fields["Address"] = user.Address
                        fields["Pincode"] = user.Pincode
                        fields["Request Date"] = str(s_request.Request_time)[:-7]
                        fields["Rating"] = s_request.Rating_to_Prof
                        fields["Remark"] = s_request.Remark
                        fields["Status"] = s_request.Status
                        searched_request.append(fields) 
                return render_template("searched_request.html", professional=professional, searched_request = searched_request)    
            if request.form["search_by"] == "pincode":
                pincode = int(request.form["field"])
                searched_request = []
                for s_request in closed_requests:
                    user = Customers.query.filter(Customers.User_ID == s_request.User_ID).first()
                    if pincode == user.Pincode:
                        fields = {"ID":"", "Customer Name":"", "Phone No.":"", "Address":"", "Pincode":"", "Request Date":"", "Rating":"", "Remark":"", "Status":""}
                        fields["ID"] = s_request.Request_ID
                        fields["Customer Name"] = user.First_Name +" "+ user.Last_Name
                        fields["Phone No."] = user.Phone_No
                        fields["Address"] = user.Address
                        fields["Pincode"] = user.Pincode
                        fields["Request Date"] = str(s_request.Request_time)[:-7]
                        fields["Rating"] = s_request.Rating_to_Prof
                        fields["Remark"] = s_request.Remark
                        fields["Status"] = s_request.Status
                        searched_request.append(fields) 
                return render_template("searched_request.html", professional=professional, searched_request = searched_request)    
            if request.form["search_by"] == "date":
                date = request.form["field"]
                searched_request = []
                for s_request in closed_requests:
                    user = Customers.query.filter(Customers.User_ID == s_request.User_ID).first()
                    if date in str(s_request.Request_time):
                        fields = {"ID":"", "Customer Name":"", "Phone No.":"", "Address":"", "Pincode":"", "Request Date":"", "Rating":"", "Remark":"", "Status":""}
                        fields["ID"] = s_request.Request_ID
                        fields["Customer Name"] = user.First_Name +" "+ user.Last_Name
                        fields["Phone No."] = user.Phone_No
                        fields["Address"] = user.Address
                        fields["Pincode"] = user.Pincode
                        fields["Request Date"] = str(s_request.Request_time)[:-7]
                        fields["Rating"] = s_request.Rating_to_Prof
                        fields["Remark"] = s_request.Remark
                        fields["Status"] = s_request.Status
                        searched_request.append(fields) 
                return render_template("searched_request.html", professional=professional, searched_request = searched_request) 
        except:  
            return render_template("error.html", error_message="Something went Wrong !!", back_to = f"/professional_search/{professional_id}")  
    


#Update Professionals Profile
@app.route("/update_professional_profile/<int:professional_id>", methods = ["GET", "POST"])
def Update_Professional_Profile(professional_id):
    professional = Professionals.query.filter(Professionals.Professional_ID == professional_id).first()
    services = [service[0] for service in set(Service.query.with_entities(Service.Type).all())]
    if request.method == "GET":
        return render_template("update_professional_profile.html", professional = professional, service_lst = services)
    if request.method == "POST":
        try:
            professional.First_Name = request.form["first_name"]
            professional.Last_Name = request.form["last_name"]
            professional.Password = request.form["password"]
            professional.Service_Type = request.form["service_type"]
            professional.Experience = request.form["experience"]
            professional.Pincode = request.form["pincode"]
            db.session.commit()
        except:
            return render_template("error.html", error_message="Something went Wrong !!", back_to = f"/update_professional_profile/{professional_id}" )    
        else:
            return redirect(f"/professional/{professional_id}")


#Accepting a Service
@app.route("/<int:professional_id>/accepts/<int:request_id>")
def Accept_Service(professional_id, request_id):
    response = Request_Response.query.filter(db.and_(Request_Response.Request_ID == request_id, Request_Response.Professional_ID == professional_id)).first()
    request = Request.query.filter(Request.Request_ID == request_id).first()
    try: 
        response.Action = "Accepted" 
        request.Professional_ID = professional_id 
        request.Status = "Accepted" 
        db.session.commit() 
    except:
        return render_template("error.html", error_message="Something went Wrong !!", back_to = f"/professional/{professional_id}")   
    else:
        return redirect(f"/professional/{professional_id}")        


#Rejecting a Service 
@app.route("/<int:professional_id>/rejects/<int:request_id>")       
def Reject_Service(professional_id, request_id):        
    response = Request_Response.query.filter(db.and_(Request_Response.Request_ID == request_id, Request_Response.Professional_ID == professional_id)).first()
    try:
        response.Action = "Rejected"
        db.session.flush()
        all_reponses = Request_Response.query.filter(Request_Response.Request_ID == request_id).all()
        c = False
        for a_reponse in all_reponses:
            if a_reponse.Action != "Rejected":
                c = True
        if not c:
            request = Request.query.filter(Request.Request_ID == request_id).first()
            db.session.delete(request)
        db.session.commit()
    except:
        return render_template("error.html", error_message="Something went Wrong !!", back_to = f"/professional/{professional_id}")   
    else:
        return redirect(f"/professional/{professional_id}")
    

#Closing a Service Request by Professional
@app.route("/<int:professional_id>/professional_close_request/<int:request_id>", methods = ["GET", "POST"])
def Professional_Close_Request(professional_id, request_id):
    s_request = Request.query.filter(Request.Request_ID == request_id).first()
    service = Service.query.filter(Service.Service_ID == s_request.Service_ID).first()
    user = Customers.query.filter(Customers.User_ID == s_request.User_ID).first()
    if request.method == "GET":
        return render_template("professional_request_closure.html", request = s_request, user = user, service = service)
    if request.method == "POST":
        try:
            s_request.Rating_to_Cust = int(request.form["rating"])
            s_request.Status = "Closed"
            user.Reviews = user.Reviews + 1
            user.Ratings = ((user.Ratings * (user.Reviews - 1)) + int(request.form["rating"]))/(user.Reviews)                
            db.session.commit()
        except:
            return render_template("error.html", error_message="Something went Wrong !!", back_to = f"/{professional_id}/customer_close_request/{request_id}")    
        else:
            return redirect(f"/professional/{professional_id}")     