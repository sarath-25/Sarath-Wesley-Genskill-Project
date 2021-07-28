from flask import Blueprint
from flask import render_template, request, redirect, url_for
from flask import g, flash, current_app
from . import db
from flask_bcrypt import Bcrypt



bp = Blueprint("todo", "todo", url_prefix="/todo")

@bp.route("/register", methods=["GET", "POST"])
def user_register():
    if request.method=="GET":
        return render_template('register.html')
    elif request.method=="POST":
        usrname = request.form.get('mailid')
        name = request.form.get('name')
        p = request.form.get('pwd')
        conn = db.get_db()
        cur = conn.cursor()
        bcrypt = Bcrypt(current_app)
        hashed_pwd = bcrypt.generate_password_hash(p).decode('utf-8')
        pwd = hashed_pwd
        cur.execute("Insert into users(name, mail, pwd) values (%s, %s, %s)", (name, usrname, pwd))
        cur.close()
        conn.commit()
        flash(f"Welcome {name}, You are registered successfully")
        return render_template('index.html')
        

@bp.route("/login", methods=["GET", "POST"])
def user_login():
    if request.method=="GET":
        return render_template('login.html')
    elif request.method=="POST":
        usrname = request.form.get("mailid")
        pwd = request.form.get("pwd")
        conn = db.get_db()
        cur = conn.cursor()
        try:
          cur.execute("select pwd from users where mail=%s", (usrname,))
          pas = cur.fetchall()[0]
          cur.close()
          bcrypt = Bcrypt(current_app)
          if bcrypt.check_password_hash(pas[0], pwd):
            return "Success"
          else:
            return "wrong password"
        except:
          flash("Wrong username, register if you haven't already")
          return render_template('login.html')
        
            
