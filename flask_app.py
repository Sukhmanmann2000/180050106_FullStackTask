from flask import Flask,Blueprint, render_template, redirect, url_for, request,flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_user, logout_user, login_required, current_user,UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from random import randint
from emailSender import sendVerificationEmail
import os
import time
import shutil
import numpy
import json
from datetime import datetime
# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    data = db.Column(db.String(100000))
app = Flask(__name__)

UPLOAD_FOLDER = 'upload_folder'
os.makedirs(UPLOAD_FOLDER,exist_ok=True)
ALLOWED_EXTENSIONS = {'json'}
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.jinja_env.globals.update(len=len)
premium_list=["ksmann6268@gmail.com","ssmann5122k@gmail.com","ksmann6268new@gmail.com"]
db.init_app(app)
# db.create_all(app)
login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))
user_dic={}
@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect('/enter')
    return render_template('login.html')

@app.route('/signup')
def signup():
    if current_user.is_authenticated:
        return redirect('/enter')
    return render_template('signup.html')

@app.route('/change')
def change():
    if current_user.is_authenticated:
        return redirect('/enter')
    return render_template('change.html')

@app.route('/forgot')
def forgot():
    if current_user.is_authenticated:
        return redirect('/enter')
    return render_template('forgot.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email').strip()
    password = request.form.get('password').strip()
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(email=email).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect('/login') # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect('/enter')

@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email').strip()
    name = request.form.get('name').strip()
    password = request.form.get('password').strip()

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect('/signup')
    elif len(password)<8:
        flash("Password must be atleast 8 characters long")
        return redirect('/signup')
    vcode=str(randint(100000,999999))
    user_dic[email]=[name,generate_password_hash(password, method='sha256'),vcode]
    sendVerificationEmail(email,vcode)
    return render_template('verify.html',email=email,goto="/verify")

@app.route('/fverify', methods=['POST','GET'])
def fverify_post():
    if request.method=='POST':
        code=request.form.get("VCode").strip()
        email=request.form.get('email').strip()
        rcode=user_dic[email][2]
        if code==rcode:
            user = User.query.filter_by(email=email).first()
            user.name = user_dic[email][0]
            user.password = user_dic[email][1]
            try:
                del user_dic[email]
            except:
                pass
            db.session.commit()
            flash("Registered successfully")
            return redirect('/login')
        else:
            try:
                del user_dic[email]
            except:
                pass
            flash("Wrong Verification Code")
            return redirect('/forgot')
    else:
        return redirect('/login')

@app.route('/verify', methods=['POST','GET'])
def verify_post():
    if request.method=='POST':
        code=request.form.get("VCode").strip()
        email=request.form.get('email').strip()
        rcode=user_dic[email][2]
        if code==rcode:
            new_user = User(email=email, name=user_dic[email][0], password=user_dic[email][1], data="")
            try:
                del user_dic[email]
            except:
                pass
            db.session.add(new_user)
            db.session.commit()
            flash("Registered successfully")
            return redirect('/login')
        else:
            try:
                del user_dic[email]
            except:
                pass
            flash("Wrong Verification Code")
            return redirect('/signup')
    else:
        return redirect('/login')

@app.route('/change', methods=['POST'])
def change_post():
    if request.method=='POST':
        email=request.form.get('email').strip()
        old_pass=request.form.get('old_password').strip()
        new_pass=generate_password_hash(request.form.get('new_password').strip(),method='sha256')
        user = User.query.filter_by(email=email).first()
        if user:
            if not(check_password_hash(user.password,old_pass)):
                flash("Please check your old password and try again.")
                return redirect('/change')
            else:
                user.password=new_pass
                db.session.commit()
                flash("Password changed successfully")
                return redirect('/login')
        else:
            flash("Email does not exist")
            return redirect('/change')
    else:
        return redirect('/login')

@app.route('/forgot', methods=['POST'])
def forgot_post():
    email = request.form.get('email').strip()
    name = request.form.get('name').strip()
    password = request.form.get('password').strip()
    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
    if not(user): # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address does not exist')
        return redirect('/forgot')
    elif len(password)<8:
        flash("Password must be atleast 8 characters long")
        return redirect('/forgot')
    vcode=str(randint(100000,999999))
    user_dic[email]=[name,generate_password_hash(password, method='sha256'),vcode]
    sendVerificationEmail(email,vcode)
    return render_template('verify.html',email=email,goto="/fverify")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect('/enter')
    else:
        return redirect('/login')
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def validFile(filepath):
    with open(filepath,"r") as f:
        try:
            fd = json.load(f)
            if not(isinstance(fd,list)):
                return False
            keyList = list(fd[0].keys())
            for d in fd:
                if not(isinstance(d,dict)):
                    return False
                tval = all([key in d for key in keyList])
                if not(tval):
                    return False
            return True
        except:
            return False
@app.route('/enter',methods=['GET','POST'])
@login_required
def enter():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            if not(validFile(filepath)):
                flash("Invalid file content")
                return redirect(request.url)
            return redirect(url_for('uploaded_file',filename=filename))
        else:
            flash('Invalid file format')
            return redirect(request.url)
    return render_template('upload.html',name = current_user.name)
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
	with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),"r") as f:
		current_user.data = f.read()
		db.session.commit()
	fd = json.loads(current_user.data)
	return render_template('showFile.html',data=fd,name=current_user.name)
if __name__=='__main__':
	# with app.app_context():
	# 	db.create_all()
	app.run()

