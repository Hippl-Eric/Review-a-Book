import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

# Import enviroment varibles from .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL") #Does not raise an error, just returns None

# Check for environment variable
if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

# Import the books csv file to the books db
def main():

    try:
        # Open the file and intialize reader object
        f = open("books.csv")
        reader = csv.reader(f)

        #Skip the header row
        next(reader)

        # Insert each book into books db
        for isbn, title, author, year in reader:
            db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
            db.commit()
        print("Success, all books imported.")

    except FileNotFoundError:
        print("Error: File not found, check current directory")
    
if __name__ == "__main__":
    main()
