import os
import requests

from flask import Flask, session, render_template, redirect, url_for, request
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
from helpers import login_required

app = Flask(__name__)
app.secret_key = os.urandom(16)

#import enviroment varibles from .env file
load_dotenv()
API_KEY = os.environ["API_KEY"] #Raises a keyerror
DATABASE_URL = os.getenv("DATABASE_URL") #Does not raise an error, just returns None
# TODO looping through all env varibles and returning error messages

# Check for environment variable
if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

#test access to API
# res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": API_KEY, "isbns": "9781632168146"})
# print(res.json())

# test access to db
# all_users = db.execute("SELECT * FROM users WHERE id = 2").first()
# print(all_users)

@app.route("/")
@login_required
def index():
    userID = session.get("user_id")
    return render_template("index.html", userID=userID)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        # Parse form input from user
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if username and password in db

            # If true store user_id in session
            # redirect to index
            # If false return error message

        return f"username = {username}, password = {password}"

    else:
        return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        session.pop('user_id', None)

        # Parse form input from user
        user_name = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        # Check database if username is already taken
        # 1:34 in lecture 3
        user_check = db.execute("SELECT * FROM users WHERE username=:username", {"username":user_name}).fetchall()

        # Return error message
        if user_check:
            return "username already taken"
        
        # Add user to db, store user_id in session, redirect to index page
        else:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": user_name, "password": password})
            db.commit()
            user_id = db.execute("SELECT id FROM users WHERE username=:username", {"username": user_name}).fetchall()
            all_users = db.execute("SELECT * FROM users").fetchall()
            session["user_id"] = user_id[0]
            return redirect(url_for("index"))


    return render_template("register.html")

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('user_id', None)
    return redirect(url_for('index'))