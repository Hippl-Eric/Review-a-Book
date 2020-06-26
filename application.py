import os
import requests
import json

from flask import Flask, session, render_template, redirect, url_for, request, abort
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
from helpers import login_required, apology, good_reads_lookup

app = Flask(__name__)
app.secret_key = os.urandom(16)

#import enviroment varibles from .env file
load_dotenv()
# API_KEY = os.environ["API_KEY"] #Raises a keyerror
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

    # Return apology when user submits no search information
    if not isbn and not title and not author:
        return apology("Please provide at least one search criteria.")

    # Initialize result lists
    isbn_results = title_results = author_results = []

    # Query books db for partial strings if value provided by user
    if isbn:
        isbn_results = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn LIMIT 10", {"isbn": f'%{isbn}%'}).fetchall()
    if title:
        title_results = db.execute("SELECT * FROM books WHERE title LIKE :title LIMIT 10", {"title": f'%{title}%'}).fetchall()
    if author:
        author_results = db.execute("SELECT * FROM books WHERE author LIKE :author LIMIT 10", {"author": f'%{author}%'}).fetchall()

    # Combine results and check total number of results
    results = isbn_results + title_results + author_results
    length = len(results)
   
    # TODO add string formatting to highlight partial strings in results

    return render_template("search-results.html", results=results, length=length)

@app.route("/book_info/<isbn>", methods = ["GET", "POST"])
@login_required
def book_info(isbn):

    # User is posting a review to book
    if request.method == "POST":

        # Ensure rating and review provided
        rating = request.form.get("rating")
        review = request.form.get("review")
        if not rating or not review:
            return apology("Please provide a rating and review.")

        # Get current user_name
        user_query = db.execute("SELECT username FROM users WHERE id = :user_id", {"user_id": session.get("user_id")}).fetchone()
        user_name = user_query[0]

        # Ensure user has not submitted review previously
        review_check = db.execute("SELECT * FROM reviews WHERE book_isbn = :isbn AND reviewer_username = :user_name", {"isbn": isbn, "user_name": user_name}).fetchall()
        if review_check:
            return apology("Sorry, you can only submit one review per book")
        
        # Submit review to db
        db.execute("INSERT INTO reviews (book_isbn, reviewer_username, rating, review) VALUES (:isbn, :user_name, :rating, :review)", {"isbn": isbn, "user_name": user_name, "rating": rating, "review": review})
        db.commit()

        return redirect(url_for("book_info", isbn=isbn))

    # User is accessing book page and review results
    else:

        # Query books database for book details
        book_info = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

        # Grab reviews (if any) from GoodReads
        good_info = good_reads_lookup(isbn)
        
        # Query review database for reviews if any
        reviews = db.execute("SELECT * FROM reviews WHERE book_isbn = :isbn", {"isbn": isbn}).fetchall()

        # return book info, GoodReads, and review data (3)
        return render_template("book-info.html", book_info=book_info, good_info=good_info, reviews=reviews)

@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):

    # Query books and reviews tables and join results
    query = db.execute("SELECT books.title, books.author, books.year, books.isbn, COUNT(reviews.review), AVG(reviews.rating) FROM books INNER JOIN reviews ON books.isbn = reviews.book_isbn WHERE books.isbn = :isbn GROUP BY books.title, books.author, books.year, books.isbn", {"isbn": isbn}).fetchall()

    # Return error code if no results
    if not query:
        return abort(404)

    # Parse data
    else:
        data = query[0]

    # Return JSON
    return json.dumps({
        "title": data[0],
        "author": data[1],
        "year": int(data[2]),
        "isbn": data[3],
        "review_count": data[4],
        "average_score": float(data[5])
    })