from flask import Blueprint
from flask import render_template, request, redirect, url_for
from flask import g, flash, current_app
from . import db
from flask_bcrypt import Bcrypt
import datetime



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
          cur.execute("select pwd, name from users where mail=%s", (usrname,))
          usr_data = cur.fetchall()[0]
          pas = usr_data[0]
          name = usr_data[1]
          cur.close()
          bcrypt = Bcrypt(current_app)
          if bcrypt.check_password_hash(pas, pwd):
            cur = conn.cursor()
            cur.execute("select id from users where mail=%s", (usrname,))
            uid = cur.fetchone()[0]
            cur.close()
            return redirect(url_for('todo.user_homepage', uid=uid),302)  
          else:
            flash("Incorrect  or password, please register if you haven't already")
            return redirect(url_for("todo.user_login"), 302)
        except:
          flash("Incorrect username or password, please register if you haven't already")
          cur.close()
          return redirect(url_for("todo.user_login"), 302)
          
          
@bp.route("/<uid>")
def user_homepage(uid):
  conn = db.get_db()
  cur = conn.cursor()
  cur.execute("select t.id, t.task_name, t.date_time, t.status from users u, tasks t where u.id = %s and t._user = u.id",(uid,))
  tasks = (x for x in cur.fetchall())
  today = datetime.date.today()
  time = datetime.datetime.now()
  cur.execute("select count(*) from tasks where _user = %s and due_date = %s", (uid, today))
  day_tasks = cur.fetchone()[0]
  cur.execute("select count(*) from tasks where _user = %s and due_date < %s and due_time < %s", (uid, today, time))
  overdue = cur.fetchone()[0]
  return render_template('homepage.html', tasks=tasks, id=uid, day_tasks=day_tasks, over_tasks=overdue)
  
  
@bp.route("/<uid>/AddTask", methods=["GET", "POST"])
def add_task(uid):
  if request.method=="GET":
    return render_template('addtask.html', id=uid)
  elif request.method=="POST":
    name = request.form.get("Taskname")
    description = request.form.get("description")
    due_date = str(request.form.get("date"))
    due_time = request.form.get("time")
    date_time = str(datetime.datetime.strptime(due_date + " " + due_time,"%Y-%m-%d %H:%M"))
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("insert into tasks (task_name, task_description, due_date, due_time, date_time, status, _user) values (%s, %s, %s, %s, %s, 'due', %s)", (name, description, due_date, due_time, date_time, uid))
    conn.commit()
    cur.close()
    flash("Task added successfully")
    return redirect(url_for('todo.user_homepage', uid=uid), 302)
    
    
@bp.route("/<uid>/Delete/<tid>")
def del_task(uid, tid):
  conn = db.get_db()
  cur = conn.cursor()
  cur.execute("delete from tasks where _user = %s and id = %s", (uid, tid))
  conn.commit()
  cur.close()
  return redirect(url_for('todo.user_homepage', uid=uid), 302)   
            
