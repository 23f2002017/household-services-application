from flask_restful import Api, Resource, fields, marshal_with
from flask import request
from datetime import date
from .validation import NotFoundError, ValidationError
from .database import db
from .models import *

api = Api()

customer_output_fields = {
    "User_ID" : fields.Integer ,
    "First_Name" : fields.String ,
    "Last_Name" : fields.String ,
    "Phone_No" : fields.Integer ,
    "Email" : fields.String ,
    "Password" : fields.String ,
    "Address" : fields.String ,
    "Pincode" : fields.Integer ,
    "Reviews" : fields.Integer ,
    "Ratings" : fields.Float ,
    "Status" : fields.String 
}

professional_output_fields = {
    "Professional_ID" : fields.Integer ,
    "First_Name" : fields.String ,
    "Last_Name" : fields.String ,
    "Email" : fields.String ,
    "Password" : fields.String ,
    "Join_Date" : fields.String ,
    "Service_Type" : fields.String ,
    "Experience" : fields.Integer ,
    "Pincode" : fields.Integer ,
    "Reviews" : fields.Integer ,
    "Ratings" : fields.Float ,
    "Status" : fields.String 
}

service_output_fields = {
    "Service_ID" : fields.Integer ,
    "Type" : fields.String ,
    "Description" : fields.String ,
    "Base_Price" : fields.Float ,
    "Time_required" : fields.Integer
}

class CustomerAPI(Resource):            #Resource Class
    @marshal_with(customer_output_fields)
    def get(self, user_id):             #For Read operation of CRUD
        customer = Customers.query.filter(Customers.User_ID == user_id).first()
        if customer is None:
            raise NotFoundError(404)
        else:
            return customer, 201

    @marshal_with(customer_output_fields)
    def post(self):                     #For Create operation of CRUD
        first_name = request.json.get("first_name", None)
        last_name = request.json.get("last_name", None)
        phone = request.json.get("phone", None)
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        address = request.json.get("address", None)
        pincode = request.json.get("pincode", None)

        if None in [first_name, last_name, phone, email, password, address, pincode]:
            raise ValidationError(400, "Missing Information !!")
        
        if len(phone) != 10:
            raise ValidationError(422, "phone no. is not valid")

        if "@" not in email:
            raise ValidationError(422, "email id is not valid")
        another_cust = Customers.query.filter(Customers.Email == email).first()
        another_prof = Professionals.query.filter(Professionals.Email == email).first()
        if another_cust != None or another_prof != None:
            raise ValidationError(422, "email already exists in the system")
        
        if len(password) < 6:
            raise ValidationError(422, "password length should be greater than 6")
        
        if len(pincode) != 6:
            raise ValidationError(422, "pincode is not valid")
        
        customer = Customers(First_Name = first_name, Last_Name = last_name, Phone_No = int(phone), Email = email, Password = password, Address = address, Pincode = int(pincode), Reviews = 0, Ratings = 0, Status = "Registered")
        db.session.add(customer)
        db.session.commit()

        return customer, 201

    @marshal_with(customer_output_fields)
    def put(self, user_id):                    #For Update operation of CRUD
        customer = Customers.query.filter(Customers.User_ID == user_id).first()
        if customer is None:
            raise NotFoundError(404)
        
        first_name = request.json.get("first_name", None)
        last_name = request.json.get("last_name", None)
        phone = request.json.get("phone", None)
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        address = request.json.get("address", None)
        pincode = request.json.get("pincode", None)

        if first_name is not None:
            customer.First_Name = first_name

        if last_name is not None:
            customer.Last_Name = last_name

        if phone is not None:
            if len(phone) != 10:
                raise ValidationError(422, "phone no. is not valid")
            another_cust = Customers.query.filter(Customers.Phone_No == phone).first()
            if another_cust != None:
                raise ValidationError(422, "phone no. already exists in the system")
            customer.Phone_No = phone
 
        if email is not None:
            if "@" not in email:
                raise ValidationError(422, "email id is not valid")
            another_cust = Customers.query.filter(Customers.Email == email).first()
            another_prof = Professionals.query.filter(Professionals.Email == email).first()
            if another_cust != None or another_prof != None:
                raise ValidationError(422, "email already exists in the system")
            customer.Email = email

        if password is not None:
            if len(password) < 6:
                raise ValidationError(422, "password length should be greater than 6")
            customer.Password = password

        if address is not None:
            customer.Address = address

        if pincode is not None:
            if len(pincode) != 6:
                raise ValidationError(422, "pincode is not valid")
            customer.Pincode = pincode

        db.session.commit()

        return customer, 201

    @marshal_with(customer_output_fields)
    def delete(self, user_id):
        customer = Customers.query.filter(Customers.User_ID == user_id).first()
        if customer is None:
            raise NotFoundError(404)
        
        db.session.delete(customer)
        db.session.commit()
        return customer, 201

api.add_resource(CustomerAPI, "/api/customer/<int:user_id>/", "/api/customer/")    


class ProfessionalAPI(Resource):            #Resource Class
    @marshal_with(professional_output_fields)
    def get(self, prof_id):             #For Read operation of CRUD
        professional = Professionals.query.filter(Professionals.Professional_ID == prof_id).first()
        if professional is None:
            raise NotFoundError(404)
        else:
            return professional, 201

    @marshal_with(professional_output_fields)
    def post(self):                     #For Create operation of CRUD
        service_types = [service[0] for service in set(Service.query.with_entities(Service.Type).all())]

        first_name = request.json.get("first_name", None)
        last_name = request.json.get("last_name", None)
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        service_type = request.json.get("service_type", None)
        experience = request.json.get("experience", None)
        pincode = request.json.get("pincode", None)

        if None in [first_name, last_name, email, password, service_type, experience, pincode]:
            raise ValidationError(400, "Missing Information !!")

        if "@" not in email:
            raise ValidationError(422, "email id is not valid")
        another_cust = Customers.query.filter(Customers.Email == email).first()
        another_prof = Professionals.query.filter(Professionals.Email == email).first()
        if another_cust != None or another_prof != None:
            raise ValidationError(422, "email already exists in the system")
        
        if len(password) < 6:
            raise ValidationError(422, "password length should be greater than 6")
        
        if len(pincode) != 6:
            raise ValidationError(422, "pincode is not valid")
        
        if service_type not in service_types:
            raise ValidationError(422, "service type not valid")
        
        if int(experience) < 0:
            raise ValidationError(422, "experience cannot be negative")

        professional = Professionals(First_Name = first_name, Last_Name = last_name, Email = email, Password = password, Join_Date = date.today(), Service_Type = service_type, Experience = int(experience), Pincode = int(pincode), Reviews = 0, Ratings = 0, Status = "Registered")
        db.session.add(professional)
        db.session.commit()

        return professional, 201

    @marshal_with(professional_output_fields)
    def put(self, prof_id):                    #For Update operation of CRUD
        professional = Professionals.query.filter(Professionals.Professional_ID == prof_id).first()
        if professional is None:
            raise NotFoundError(404)
        
        service_types = [service[0] for service in set(Service.query.with_entities(Service.Type).all())]

        first_name = request.json.get("first_name", None)
        last_name = request.json.get("last_name", None)
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        service_type = request.json.get("service_type", None)
        experience = request.json.get("experience", None)
        pincode = request.json.get("pincode", None)

        if first_name is not None:
            professional.First_Name = first_name

        if last_name is not None:
            professional.Last_Name = last_name
 
        if email is not None:
            if "@" not in email:
                raise ValidationError(422, "email id is not valid")
            another_cust = Customers.query.filter(Customers.Email == email).first()
            another_prof = Professionals.query.filter(Professionals.Email == email).first()
            if another_cust != None or another_prof != None:
                raise ValidationError(422, "email already exists in the system")
            professional.Email = email

        if password is not None:
            if len(password) < 6:
                raise ValidationError(422, "password length should be greater than 6")
            professional.Password = password

        if service_type is not None:
            if service_type not in service_types:
                raise ValidationError(422, "service type not valid")
            professional.Service_Type = service_type

        if experience is not None:
            if int(experience) < 0:
                raise ValidationError(422, "experience cannot be negative")
            professional.Experience = experience    

        if pincode is not None:
            if len(pincode) != 6:
                raise ValidationError(422, "pincode is not valid")
            professional.Pincode = pincode

        db.session.commit()

        return professional, 201

    @marshal_with(professional_output_fields)
    def delete(self, prof_id):
        professional = Professionals.query.filter(Professionals.Professional_ID == prof_id).first()
        if professional is None:
            raise NotFoundError(404)
        
        db.session.delete(professional)
        db.session.commit()
        return professional, 201

api.add_resource(ProfessionalAPI, "/api/professional/<int:prof_id>/", "/api/professional/") 


class ServiceAPI(Resource):
    @marshal_with(service_output_fields)
    def get(self, service_id):
        service = Service.query.filter(Service.Service_ID == service_id).first()
        if service is None:
            raise NotFoundError(404)
        else:
            return service, 201

    @marshal_with(service_output_fields)
    def post(self):
        type = request.json.get("type", None)
        description = request.json.get("description", None)
        base_price = request.json.get("base_price", None)
        time_required = request.json.get("time_required", None)

        if None in [type, description, base_price, time_required]:
            raise ValidationError(422, "Missing Information !!")
        
        if float(base_price) < 0:
            raise ValidationError(422, "base price cannot be negative")
        
        if int(time_required) < 0:
            raise ValidationError(422, "time required cannot be negative")
        
        service = Service(Type = type, Description = description, Base_Price = float(base_price), Time_required = int(time_required))
        db.session.add(service)
        db.session.commit()

        return service, 201

    @marshal_with(service_output_fields)
    def put(self, service_id):
        service = Service.query.filter(Service.Service_ID == service_id).first()
        if service is None:
            raise NotFoundError(404)
        
        type = request.json.get("type", None)
        description = request.json.get("description", None)
        base_price = request.json.get("base_price", None)
        time_required = request.json.get("time_required", None)

        if type is not None:
            service.Type = type

        if description is not None:   
            service.Description = description

        if base_price is not None:
            if float(base_price) < 0:
                raise ValidationError(422, "base price cannot be negative")
            service.Base_Price = float(base_price)

        if time_required is not None: 
            if int(time_required) < 0:
                raise ValidationError(422, "time required cannot be negative")
            service.Time_required = int(time_required)

        db.session.commit()

        return service, 201    

    @marshal_with(service_output_fields)
    def delete(self, service_id):
        service = Service.query.filter(Service.Service_ID == service_id).first()
        if service is None:
            raise NotFoundError(404)
        
        db.session.delete(service)
        db.session.commit()

        return service, 201

api.add_resource(ServiceAPI, "/api/service/<int:service_id>/", "/api/service/")    