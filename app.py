from flask import Flask, render_template, request, redirect, session, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt
import secrets
from model import *
import os

# Run line below in terminal
# export MONGO_URI="mongodb+srv://admin:15112001@cluster0.v0lkc.mongodb.net/Unit4?retryWrites=true&w=majority"
# https://medium.com/@gitaumoses4/deploying-a-flask-application-on-heroku-e509e5c76524
# git add . git commit -m "heroku" git push heroku main

# -- Initialization --
app = Flask(__name__)
# Name of database
app.config['MONGO_DBNAME'] = 'Unit4'
# URI of database
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
mongo = PyMongo(app)
#Create collection for favorites


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
        # if user submit details on page
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
            users.insert_one({'name':username, 'password':hashed})

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
            # compare username in database to username submitted in form
            if bcrypt.checkpw(password, db_password):
                # store username in session
                session.clear()
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

#Favorites Route
@app.route('/index/<album>/<username>', methods=['GET', 'POST'])
def favorites(album, username):
    user = mongo.db.users_library
    username = user.find_one({"name":username})
    #ratings_lib = mongo.db['ratings_library']
    if request.method == 'GET':
        return render_template('index.html', album=album, username=username)
    elif 'favorite' in request.form:
        favorite = request.form['favorite']
        if favorite:
            collection = mongo.db['favorites']
            album = request.form['album']
            username = request.form['username']
            favorites.insert_one({'username': username, 'album': album})

        else:
            return redirect(url_for('favorites', album=album, username=username))
    
    else:
        return render_template('index.html', album=album, username=username)
        #redirect to the index route upon form submission
        return redirect('/index')