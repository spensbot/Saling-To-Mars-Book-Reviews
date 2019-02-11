import os
import requests

from flask import Flask, session, redirect, render_template, url_for, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# A segment of code found online that updates the filepath of any static (notably .css) files when they are updated.
# This prevents browser caching so the static files update every time.
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)
def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)



#--------------HOME PAGE-------------------------------------
@app.route("/")
def index():
    if session.get('userId') != None:
        userReviews = db.execute(f"SELECT rating, review, title FROM reviews JOIN books ON reviews.book_id = books.id WHERE user_id = {session.get('userId')}").fetchall()
    else:
        userReviews = None
    return render_template("index.html", userId=session.get("userId"), username = session.get("username"), userReviews = userReviews)

#-------------------Register new user page and post method------------------------
@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html", userId=session.get("userId"), username = session.get("username"))
@app.route("/register", methods=["POST"])
def registerForm():
    username = request.form.get("username")
    password = request.form.get("password")
    db.execute(f"INSERT INTO users (username, password) VALUES ('{username}','{password}')")
    db.commit()
    return redirect("/login")

#---------------------Login page and post method.--------------------------------
@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html", userId=session.get("userId"), username = session.get("username"))
@app.route("/login", methods=["POST"])
def loginForm():
    username = request.form.get("username")
    password = request.form.get("password")
    userdata = db.execute(f"SELECT id, username FROM users WHERE username = '{username}' AND password = '{password}'").fetchone()
    session["userId"] = userdata["id"]
    session["username"] = userdata["username"]
    return redirect("/")

#--------------------Logout method.------------------------------------
@app.route("/logout")
def logout():
    session["userId"] = None
    session["username"] = None
    return redirect("/") 

#---------------------Individual Book page------------------------------------
@app.route("/book/<string:isbn>", methods=["POST"])
def bookForm(isbn):
    rating = request.form.get("rating")
    review = request.form.get("review")
    bookId = db.execute(f"SELECT id FROM books WHERE isbn = '{isbn}'").fetchone()['id']
    db.execute(f"INSERT INTO reviews (rating, review, user_id, book_id) VALUES ('{rating}', '{review}', '{session.get('userId')}', '{bookId}')")
    db.commit()
    return redirect(f"/book/{isbn}")
@app.route("/book/<string:isbn>")
def book(isbn):
    #get book data based on the isbn. User review data, and all review data for the book.
    bookData = db.execute(f"SELECT id, isbn, title, author, year FROM books WHERE isbn = '{isbn}'").fetchone()
    userReviewData = db.execute(f"SELECT rating, review FROM reviews WHERE user_id = '{session.get('userId')}' AND book_id = '{bookData['id']}'").fetchone()
    reviewData = db.execute(f"SELECT rating, review, username FROM reviews JOIN users ON reviews.user_id = users.id WHERE book_id = {bookData['id']}").fetchall()
    
    #get goodreads information for the book.
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Wa1zX6SawhSkzALxPElcw", "isbns": f"{isbn}"})
    goodreadsData = res.json()['books'][0]

    return render_template("book.html", userId=session.get("userId"), username = session.get("username"), bookData = bookData, userReviewData = userReviewData, reviewData = reviewData, goodreadsData = goodreadsData)

#---------------------Search Page--------------------------------------------
@app.route("/search")
def search():
    query = request.args.get("query")
    results = None
    if query != None:
        results = db.execute(f"SELECT isbn, title, author, year FROM books WHERE isbn LIKE '%{query}%' OR title LIKE '%{query}%' OR author LIKE '%{query}%'").fetchall()
    return render_template("search.html", userId=session.get("userId"), username = session.get("username"), query = query, results = results)