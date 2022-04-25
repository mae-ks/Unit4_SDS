from flask import Flask, render_template, request, redirect, session, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt
import secrets
from model import stage_names
import os

# For flask -->
# export MONGO_URI="mongodb+srv://admin:15112001@cluster0.v0lkc.mongodb.net/Unit4?retryWrites=true&w=majority"
# FLASK_DEBUG=1
# For heroku -->
# git add ., git commit -m "heroku", git push heroku main, git push

# -- Initialization --
app = Flask(__name__)
# Name of database
app.config['MONGO_DBNAME'] = 'Unit4'
# URI of database
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
mongo = PyMongo(app)

albums = mongo.db['albums']

# -- Session data --
app.secret_key = secrets.token_urlsafe(16)

@app.route('/')
@app.route('/index')
@app.route('/<username>')
def index(username=None):
    """
    Homepage
    """
    return render_template('index.html', username=username)

@app.route ('/signup', methods=['GET','POST'])
def signup():
    """
    User signup
    """
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
        return render_template('signup.html', session=session)

@app.route('/login', methods=['GET','POST'])
def login():
    """
    User login
    """
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
        return render_template('login.html', session=session)

@app.route('/logout')
def logout():
    # clear username from session data
    session.clear()
    return redirect('/')

@app.route('/<username>/profile', methods=['GET', 'POST'])
def profile(username):
    """
    Retrieve user's profile where they can choose to change password.
    """
    user = mongo.db.users.find_one({'name':username})
    if request.method == 'POST':
        return redirect(url_for('changepassword', username=username, password=request.form['newpassword']))
    return render_template('profile.html', username=username)

@app.route('/changepassword/<username>/<password>', methods=['GET', 'POST'])
def changepassword(username, password):
    """
    Updating password in database.
    """
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    mongo.db.users.update_one({'name':username}, {'$set':{'password':hashed}})
    return redirect("/" + username)

"""@app.route('/<stage_name>')
def album_view():
    songs = mongo.db.albums
    albums = songs.find({"stage_name": stage_name})
    return render_template('album.html', albums = albums, stage_names = stage_names)"""


@app.route('/index/ <albumID>')
def album_view(albumID):
    collection = mongo.db.albums
    album = collection.find_one({"_id":ObjectId(albumID)})
    return render_template('album.html', album = album)


@app.route('/index/<albumID>/add_image', methods=['GET','POST'])
def add_cover(albumID): 
    if request.method == "GET":
        collection = mongo.db.albums 

        album = collection.find_one({"_id":ObjectID(albumID)})

        return render_template('add_cover.html', album=album)
    else: 

        #assigning form data to variable 
        url = request.form['url']
        collection = mongo.db.albums

        album = {"_id":ObjectId(albumID)}
        newcovers = {"$set": {"image": url}}

        collection.update_one(album, newcovers)

        return redirect('/index/<albumID>/'+albumID)