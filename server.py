"""Armoire"""

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Clothing, Friend, Event, clothesInOutfit


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



@app.route('/login')
def login():
    return render_template('userhome.html')   

@app.route('/login', methods = ['POST'])
def login_user():
    username = request.form.get("username_for_login")
    password = request.form.get("password_for_login")


    user = User(username = username, password = password)

    db.session.add(user)
    db.session.commit()

    return render_template('userhome.html')



@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods = ['POST'])
def register_user():
    email = request.form["register_email"]
    username = request.form["register_username"]
    password = request.form["register_password"]

    user = User(username = username, password = password, email = email)

    db.session.add(user)
    db.session.commit()

    return render_template('userhome.html')



@app.route('/userhome')
def user_info():
    # username = request.form["username_for_login"]
    return render_template('userhome.html', username_for_login=username)





@app.route('/closet')
def show_closet():
    return render_template('closet.html')

@app.route('/friends')
def show_friends():
    return render_template('friends.html')

@app.route('/requests')
def show_requests():
    return render_template('requests.html')

@app.route('/recommendations')
def show_recommendations():
    return render_template('recommendations.html')

@app.route('/events')
def sholw_events():
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