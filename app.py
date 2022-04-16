from flask import Flask, render_template, request, redirect, session, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt
import secrets
from model import *
import os

# Run line below in terminal
# export MONGO_URI="mongodb+srv://admin:15112001@cluster0.v0lkc.mongodb.net/Unit4?retryWrites=true&w=majority"

# -- Initialization --
app = Flask(__name__)
# Name of database
app.config['MONGO_DBNAME'] = 'Unit4'
# URI of database
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
mongo = PyMongo(app)

# -- Session data --
app.secret_key = secrets.token_urlsafe(16)

@app.route('/')
@app.route('/index')
@app.route('/<username>')
def index(username=None):
    return render_template('index.html', username=username)

@app.route ('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        # if user submit details
        users = mongo.db.users

        # search for username in database
        existing_user = users.find_one({'name': request.form['username']})

        # if user not in database
        if not existing_user:
            username = request.form['username']

            # encode password for hashing
            password = (request.form['password']).encode('utf-8')
            # hash password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password, salt)
            users.insert_one({'name':username, 'password':password})

            # store username in session
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        else:
            return 'Username already registered. Try logging in.'

    else:
        # if loading page
        return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users

        # search for username in database
        login_user = users.find_one({'name': request.form['username']})

        #if username in database
        if login_user:
            db_password = login_user['password']

            password = request.form['password'].encode('utf-8')
            print(db_password == password)
            # compare username in database to username submitted in form
            if password == db_password: # bcrypt.checkpw(password, db_password) not working
                # store username in session
                session['username'] = request.form['username']
                return redirect("/" + request.form['username'])
            else:
                return "Invalid username/password combination."
        
        else:
            return "User not found."
    
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    # clear username from session data
    session.clear()
    return redirect('/')