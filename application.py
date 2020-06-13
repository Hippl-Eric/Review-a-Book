import os
import requests

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

app = Flask(__name__)

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
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#test access to API
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": API_KEY, "isbns": "9781632168146"})
print(res.json())

@app.route("/")
def index():
    return "Project 1: TODO"
