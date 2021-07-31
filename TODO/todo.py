from flask import Blueprint
from flask import render_template, request, redirect, url_for
from flask import g, flash, current_app
from . import db
from flask_bcrypt import Bcrypt
import datetime
import uuid

login = 0
def diff_dates(a, b):
  x_obj = datetime.datetime.strptime(a, '%Y-%m-%d %H:%M:%S')
  if b > x_obj:
    diff = b - x_obj
    duration_in_s = diff.total_seconds() 
    days = int(duration_in_s/86400)
    hours = int((duration_in_s % 86400)/3600)
    minutes = int((((duration_in_s % 86400) % 3600)/60))
    seconds = int(((duration_in_s % 86400) % 3600) % 60)
    return f"Overdue by  {days} days, {hours} hours, {minutes} minutes and {seconds} seconds"
  elif x_obj > b:
    diff = x_obj - b
    duration_in_s = diff.total_seconds() 
    days = int(duration_in_s/86400)
    hours = int((duration_in_s % 86400)/3600)
    minutes = int((((duration_in_s % 86400) % 3600)/60))
    seconds = int(((duration_in_s % 86400) % 3600) % 60)
    return f"Due, Time remaining: {days} days, {hours} hours, {minutes} minutes and {seconds} seconds"

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
        uid = str(uuid.uuid1())
        cur.execute("Insert into users(id, name, mail, pwd) values (%s, %s, %s, %s)", (uid, name, usrname, pwd))
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
            flash("Incorrect username or password, please register if you haven't already")
            return redirect(url_for("todo.user_login"), 302)
        except:
          flash("Incorrect username or password, please register if you haven't already")
          cur.close()
          return redirect(url_for("todo.user_login"), 302)
          
          
@bp.route("/<uid>")
def user_homepage(uid):
  conn = db.get_db()
  cur = conn.cursor()
  today = datetime.date.today()
  now = datetime.datetime.now()
  time = now.time()
  cur.execute("select date_time from tasks where _user = %s", (uid))
  for x in cur.fetchall():
    cur.execute("select status from tasks where _user = %s and date_time = %s", (uid, x))
    stat = cur.fetchone()[0]
    if stat == "Completed":
      continue
    else:
      diff = diff_dates(x[0], now)
      cur.execute("update tasks set status = %s where date_time = %s", (diff, x))
      conn.commit() 
  cur.execute("select count(*) from tasks where _user = %s and due_date = %s", (uid, today))
  day_tasks = cur.fetchone()[0]
  cur.execute("select count(*) from tasks where _user = %s and due_date < %s", (uid, today))
  overdue_1 = cur.fetchone()[0]
  cur.execute("select count(*) from tasks where _user = %s and due_date = %s and due_time < %s", (uid, today, time))
  overdue_2 = cur.fetchone()[0]
  overdue = overdue_1 + overdue_2
  cur.execute("select t.id, t.task_name, t.date_time, t.status from users u, tasks t where u.id = %s and t._user = u.id order by due_date, due_time",(uid,))
  tasks = (x for x in cur.fetchall())
  return render_template('homepage.html', tasks=tasks, id=uid, day_tasks=day_tasks, over_tasks=overdue)
  
  
@bp.route("/<uid>/AddTask", methods=["GET", "POST"])
def add_task(uid):
  if request.method=="GET":
    return render_template('addtask.html', id=uid)
  elif request.method=="POST":
    name = request.form.get("Taskname")
    description = request.form.get("description")
    due_date = request.form.get("date")
    due_time = request.form.get("appt")
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
  
@bp.route("/<uid>/taskdetails/<tid>")
def task_details(uid, tid):
   conn = db.get_db()
   cur = conn.cursor()
   now = datetime.datetime.now()
   cur.execute("select date_time from tasks where _user = %s and id = %s", (uid, tid))
   for x in cur.fetchall():
    diff = diff_dates(x[0], now)
    cur.execute("update tasks set status = %s where date_time = %s", (diff, x))
    conn.commit()
   cur.execute("select task_name, task_description, date_time, status from tasks where _user = %s and id = %s",(uid, tid))
   task = cur.fetchall()
   return render_template('taskdetails.html', task=task, uid=uid, tid=tid)
   
@bp.route("/<uid>/edit_task/<tid>", methods=["GET", "POST"])
def edit_task(uid, tid):
   conn = db.get_db()
   cur = conn.cursor()
   if request.method == "GET":
    cur.execute("select task_name, task_description, due_date, due_time, status from tasks where _user = %s and id = %s", (uid, tid))
    task = cur.fetchone()
    name, description, date, time, status = task
    return render_template('edittask.html', name=name, description=description, date=date, time=time, uid=uid, tid=tid, status=status)
   elif request.method == "POST":
    name = request.form.get("Taskname")
    description = request.form.get("description")
    date = request.form.get("date")
    time = request.form.get("appt")
    stat = request.form.get("options")
    cur.execute("update tasks set task_name = %s, task_description = %s, due_date = %s, due_time = %s, status = %s where _user = %s and id = %s", (name, description, date, time, stat, uid, tid))
    conn.commit()
    flash("Task edited successfully")
    return redirect(url_for('todo.user_homepage', uid=uid), 302)
    
            
