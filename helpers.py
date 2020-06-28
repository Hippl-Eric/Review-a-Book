import os
import requests

from functools import wraps
from flask import redirect, url_for, session, render_template
from dotenv import load_dotenv

# Load api key from env file to global varible
load_dotenv()
try:
    API_KEY = os.environ["API_KEY"] #Raises a keyerror
except KeyError:
    print("ERROR: API key not found")

# Flask login wrapper
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Custom error messages for user
def apology(message):
    return render_template('apology.html', message=message)

# Get book ratings from Goodreads API
def good_reads_lookup(isbn):

    # Contact API, return NONE if no data
    try:
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": API_KEY, "isbns": isbn})
        res.raise_for_status()
    except res.RequsetException:
        return None

    # Parse response
    try:
        data = res.json()
        obj = data['books'][0]
        return {
            "avg_rating": obj['average_rating'],
            "num_ratings": obj['work_ratings_count']
        }
    except:
        return None
