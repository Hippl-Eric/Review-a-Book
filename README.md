# Project 1

Web Programming with Python and JavaScript

### Project Name: Book-a-Review
### Project Summary:
Python/Flask application which allows users to search for ratings and reviews for up to 5,000 books.  The site accesses a postgreSQL database hosted on Heroku.  The database includes 3 tables:  
1. Users: user login information.  
2. Books: book information for 5,000 books
3. Reviews: ratings and reviews submitted by users for each book.  

In addition to user reviews, additional rating information is provided by the <a href="https://www.goodreads.com/api" target="_blank">Goodreads</a> API.

Lastly, the site is accessible via its API route, and will return book information in JSON format with a valid request.

Video Walk-through: https://www.youtube.com/watch?v=9XOoFWBmV6c

### Python
The project includes 3 python files:
1. application.py
2. helpers.py
3. import.py


application.py<br>
The main flask application.  This file initializes and configures the web application, links to the database hosted on Heroku, and handles all site routing.  The SQLAlchemy package is used to process raw SQL statements when interacting with the database.

helpers.py<br>
To help keep the main application neat, helpers.py includes a few functions used by the application.  This file handles the login_required wrapper function, custom error message template return, and parsing data from the Goodreads API.

import.py<br>
A standalone file used once to import the 5000 books provided in books.csv, into the database.  

### HTML
The project includes 7 HTML files:
1. layout.html
2. index.html
3. login.html
4. register.html
5. search-results.html
6. book-info.html
7. apology.html

layout.html<br>
Includes the page structure, all required meta tags, and navigation bar. The page is extended to all other HTML pages.

index.html<br>
Allows users to search/query the books table in the database.  Users are able to search for a book based upon the ISBN number, title, author, or any combination of the three.  Partial queries are handled so user does not need to enter the information exactly correct.  The user will be routed to search-results.html after posting.

login.html<br>
The application.py file automatically routes to the login page when user is not logged in.  Login is a simple form that posts information to the login route.  After checking the information entered is correct and matches the users table in the database, user is routed to the index page.

register.html<br>
Like the login page, register posts information to the register route.  Register allows users to register for the site, and saves their information in the users table of the database.  The user is then routed to the index page.

search-results.html<br>
Displays the results of the books search from index.html.  Results are displayed in a table, and each book can be clicked for more information.

book-info.html<br>
Displays additional information for a book when clicked on the search-results page.  Also displayed is the average rating and number of ratings received from the Goodreads API.  Lastly, users can see reviews posted by users of the site, and submit their own.

apology.html<br>
Displays custom error messages to the users.

### CSS
The project includes 1 CSS file:
1. styles.css

styles.css<br>
The main focus of the project was backend development.  This stylesheet includes only a few rules to help with UX/UI. The site was designed mobile-first, flexing elements to fit larger screens when necessary.
