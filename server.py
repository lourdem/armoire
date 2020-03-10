"""Armoire"""

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Clothing, Friend, Event, clothesInOutfit
import cloudinary
import cloudinary.uploader
import cloudinary.api


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')




@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods = ['POST'])
def register_user():
    email = request.form["register_email"]
    username = request.form["register_username"]
    password = request.form["register_password"]

    new_user = User(username = username, password = password, email = email)

    db.session.add(new_user)
    db.session.commit()

    return redirect(f"/users/{new_user.user_id}")




# @app.route('/login')
# def login():
#     return redirect(f"/users/{user.user_id}") 

@app.route('/login', methods = ['POST'])
def login_user():
    username = request.form["username_for_login"]
    password = request.form["password_for_login"]

# query is like select, here you are looking for the username by using filter_by(...)
# the first return only the first result of the query, or none if it's not found
    
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("Account not found, please try again.")
        return render_template('homepage.html')
    if user.password != password:
        flash("Incorrect password. Please try again.")
        return render_template('homepage.html')

    session["user_id"] = user.user_id

    return redirect(f"/users/{user.user_id}")




@app.route("/users")
def user_list():
    users = User.query.all()
    return render_template("user_list.html", users = users)



@app.route("/users/<int:user_id>")
def user_detail(user_id):
    # username = User.username
    user = User.query.filter_by(user_id=user_id).first()
    return render_template('user.html', user =user)



@app.route("/closet/<int:user_id>")
def show_closet(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    return render_template('closet.html', user=user)



@app.route('/friends/<int:user_id>')
def show_friends(user_id):
    return render_template('friends.html')

@app.route('/requests/<int:user_id>')
def show_requests(user_id):
    return render_template('requests.html')

@app.route('/recommendations/<int:user_id>')
def show_recommendations(user_id):
    return render_template('recommendations.html')

@app.route('/events/<int:user_id>')
def sholw_events(user_id):
    return render_template('events.html')


    

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')