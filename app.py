from os import environ
from flask import Flask, Response, flash, request, render_template, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import jwt
import json
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["SECRET_KEY"] = environ.get("SECRET_KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://tris0n:@localhost/api"

db = SQLAlchemy(app)


#class usuario connection for database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    group = db.Column(db.String(50))


#functions
def check_token(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.cookies.get("token")
        if not token:
            return redirect("/login")
        
        user_data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        return func(*args, **kwargs, user_data=user_data)
    return decorated

def check_isadmin(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.cookies.get("token")
        if not token:
            return redirect("/login")
        
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        if(data["is_admin"] == True):
            return func(*args, **kwargs, isadmin=True)
        else:
            return func(*args, **kwargs, isadmin=False)
    return decorated

#routes
@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods=["GET"])
def login_front():
    return render_template("login.html")


@app.route("/register", methods=["GET"])
def register_front():
    template = render_template("register.html")
    return Response(template, status=200)


@app.route("/register", methods=["POST"])
def register_back():
    name = request.form.get("name")
    password = request.form.get("password")

    #if(request.form.get("group")):
    #    group = request.form.get("group")
    #else:
    #    group = "guest"

    try:
        user = User(name=name, password=password, group="guest")
        db.session.add(user)
        db.session.commit()
        return redirect("/login")

    except Exception as e:
        print(e)
        return Response("Error!")


@app.route("/login", methods=["POST"])
def login_back():
    name = request.form.get("name")
    password = request.form.get("password")

    user = User.query.filter_by(name=name).first()
    if(not user or user.password != password):
        flash("Please check your credentials and try again.", "error")
        return redirect("/login")
    
    if(user.group == "admin"):
        token = jwt.encode({
                "user": user.name,
                "is_admin": True,
                "expiration": str(datetime.utcnow() + timedelta(seconds=3600))
            }, app.config["SECRET_KEY"])
        resp = make_response(redirect("/admin"))
        resp.set_cookie("token", token, max_age=3600)
        return resp
    else:
        token = jwt.encode({
            "user": user.name,
            "is_admin": False,
            "expiration": str(datetime.utcnow() + timedelta(seconds=3600))
        }, app.config["SECRET_KEY"])
        resp = make_response(redirect("/admin"))
        resp.set_cookie("token", token, max_age=3600)
        return resp

@app.route("/admin")
@check_isadmin
def auth(isadmin):
    if(isadmin):
        return render_template("admin.html")
    else:
        return Response("Welcome!")

@app.route("/admin", methods=["POST"])
@check_isadmin
def set_admin(isadmin):
    if(isadmin):
        if(request.form.get("setadmin")):
            try:
                name = request.form.get("user")
                user = User.query.filter_by(name=name).first()
                user.group = "admin"
                db.session.add(user)
                db.session.commit()
                return Response("Success!")
            except Exception as e:
                print(e)
                return Response("Error!")

        elif(request.form.get("unsetadmin")):
            try:
                name = request.form.get("user")
                user = User.query.filter_by(name=name).first()
                user.group = "guest"
                db.session.add(user)
                db.session.commit()
                return Response("Success!")
            except Exception as e:
                print(e)
                return Response("Error!")

        elif(request.form.get("deluser")):
            try:
                name = request.form.get("user")
                user = User.query.filter_by(name=name).first()
                db.session.delete(user)
                db.session.commit()
                return Response("Success!")
            except Exception as e:
                print(e)
                return Response("Error!")

        return Response("Sucess!")

app.run(host="127.0.0.1", port=5000, debug=False)