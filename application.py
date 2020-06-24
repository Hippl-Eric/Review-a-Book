import os
import requests

from flask import Flask, session, render_template, redirect, url_for, request
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
from helpers import login_required, apology

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

        # Log form values
        user_name = request.form.get('username')
        password = request.form.get('password')

        # Ensure username provided
        if not user_name:
            return apology("Please provide username.")

        # Ensure password provided
        if not password:
            return apology("Please provide password.")

        # Check if username and password in db
        valid_user = db.execute("SELECT * FROM users WHERE username=:username AND password=:password", {"username":user_name, "password":password}).first()

        # Store user_id in session, redirect to index
        if valid_user:
            session["user_id"] = valid_user[0]
            return redirect(url_for("index"))

        # Return error message
        else:
            return apology("Incorrect username or password")

    else:
        return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        # Remove active user if any
        session.pop('user_id', None)

        # Log form values
        user_name = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        # Ensure username provided
        if not user_name:
            return apology("Please provide username.")

        # Ensure password provided
        if not password:
            return apology("Please provide password.")

        # Ensure passwords match
        if password != confirmation:
            return apology("Passwords must match.")

        # Check database if username is already taken
        user_check = db.execute("SELECT * FROM users WHERE username=:username", {"username":user_name}).fetchall()

        # Return error message if user_check returns a value
        if user_check:
            return apology("Username already taken.  Please try another")
        
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

@app.route('/search', methods = ["POST"])
@login_required
def search():

    # Retreive form values
    isbn = request.form.get("isbn")
    title = request.form.get("title")
    author = request.form.get("author")

    # Initialize result lists
    isbn_results = []
    title_results = []
    author_results = []

    # Query books db for partial strings if value provided by user
    if isbn != "":
        isbn_results = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn LIMIT 10", {"isbn": f'%{isbn}%'}).fetchall()
    if title != "":
        title_results = db.execute("SELECT * FROM books WHERE title LIKE :title LIMIT 10", {"title": f'%{title}%'}).fetchall()
    if author != "":
        author_results = db.execute("SELECT * FROM books WHERE author LIKE :author LIMIT 10", {"author": f'%{author}%'}).fetchall()

    # Combine results and check total number of results
    results = isbn_results + title_results + author_results
    length = len(results)
   
    # TODO add string formatting to highlight partial strings in results

    return render_template("search-results.html", results=results, length=length)