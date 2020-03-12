"""Armoire"""

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, flash, redirect, session, url_for, Markup
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Clothing, Friend, Event, clothesInOutfit
from werkzeug.utils import secure_filename
import psycopg2
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.uploader import upload

UPLOAD_FOLDER = '/static/media/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])



app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined



cloudinary.config( 
  cloud_name = "lourdem", 
  api_key = os.environ.get("CLOUDINARY_API_KEY"), 
  api_secret = os.environ.get("CLOUDINARY_API_SECRET") 
)


@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')




@app.route('/register', methods = ['GET'])
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

    session["user_id"] = new_user.user_id

    return redirect(f"/users/{new_user.user_id}")




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



@app.route("/closet/<int:user_id>", methods = ["GET", "POST"])
def show_closet(user_id):
    user = User.query.filter_by(user_id=user_id).first()



    user_clothing = Clothing.query.filter_by(user_id = user_id).all()

    # for item in image_url:
    # show_image = cloudinary.CloudinaryImage(image_url).image(type="fetch")



    #app.logger.info(show_image)

    return render_template('closet.html', user=user, user_clothing = user_clothing)



@app.route("/submit_new_item", methods = ["POST"])
def add_item():
    file = request.files["new_item"]
    filename = secure_filename(file.filename)
    uploaded_file_info = cloudinary.uploader.upload(file)
    image_url = uploaded_file_info['secure_url']

    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()

    new_item = Clothing(user_id = user_id,
                        photo = image_url
                        # type_code = type_code,
                        # season_code = season_code,
                        # color = color,
                        )

    db.session.add(new_item)
    db.session.commit()

    return redirect(f"/closet/{user.user_id}")


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
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')