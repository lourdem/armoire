"""Armoire"""

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, flash, redirect, session, url_for, Markup
from flask_debugtoolbar import DebugToolbarExtension
from model import (connect_to_db, db, User, Outfit, Clothing, Friend, Event, ClothesInOutfit)
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

################################################################################
##Route for homepage##

@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')
################################################################################
################################################################################


################################################################################
##Allows user registration##

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
################################################################################
################################################################################


################################################################################
##Allows user login##

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
################################################################################
################################################################################


################################################################################
##Shows all users and user's homepage##

@app.route("/users")
def user_list():
    users = User.query.all()
    return render_template("user_list.html", users = users)

@app.route("/users/<int:user_id>")
def user_detail(user_id):
    # username = User.username
    user = User.query.filter_by(user_id=user_id).first()
    return render_template('user.html', user =user)

@app.route("/viewoutfits/<int:user_id>")
def search_user_display_outfits(user_id):
    # username = User.username
    user = User.query.filter_by(user_id=user_id).first()
    outfits = Outfit.query.filter_by(user_id = user_id).all()

    dict_of_clothes = {}
    for outfit in outfits:
        clothes = outfit.clothes
        dict_of_clothes[outfit] = clothes
    return render_template("view_outfits_of_searched_user.html", user = user, clothes = clothes, dict_of_clothes = dict_of_clothes, outfit = outfit)


# @app.route("/view_user_after_search", methods = ["POST", "GET"])
# def view_user():
#     user = User.query.filter_by(user_id=user_id).first()
#     return render_template("view_user_from_search.html", user = user)
################################################################################
################################################################################


################################################################################
##Shows user's closet##
@app.route("/closet/<int:user_id>", methods = ["GET", "POST"])
def show_closet(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('closet.html', user=user, user_clothing = user_clothing)
################################################################################
################################################################################


################################################################################
##Handles submisison of new clothing items##

@app.route("/item_submission")
def show_submission_form():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    return render_template("item_submission.html",user =user)

@app.route("/submit_new_item", methods = ["POST"])
def add_item():
    file = request.files["new_item"]
    filename = secure_filename(file.filename)
    uploaded_file_info = cloudinary.uploader.upload(file)
    image_url = uploaded_file_info['secure_url']
    category = request.form["item_category"]
    season = request.form["item_season"]
    color = request.form["item_color"]
    size = request.form["item_size"]
    description = request.form["item_description"]

    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    new_item = Clothing(user_id = user_id,
                        category = category,
                        season = season,
                        color = color,
                        size = size,
                        description = description,
                        photo = image_url,
                        )

    db.session.add(new_item)
    db.session.commit()

    return redirect(f"/item_submission")
    # return redirect(f"/closet/{user.user_id}")
################################################################################
################################################################################


################################################################################
######################NEW WAY OF SHOWING CLOSET CATEGORIES######################
@app.route("/show_this_category", methods = ["POST"])
def show_category():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    category = request.form["category_to_view"]
    return render_template(f'{category}.html', user=user, user_clothing = user_clothing)
################################################################################
################################################################################


################################################################################
##Route to display page where you can design an outfit##
@app.route("/make_an_outfit") #, methods = ["POST"])
def make_outfit():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    # selected_clothing_to_display = selected_clothing
    # diplay_selected = Clothing.query.filter_by
    list_of_selected_clothing = []
    
    return render_template("make_an_outfit.html", user = user, list_of_selected_clothing = list_of_selected_clothing)
################################################################################
################################################################################


################################################################################
######CHANGE THE WAY YOU SELECT CATEGORY TO MAKE OUTFIT#####
@app.route("/make_outfit_category", methods = ["POST"])
def show_category_for_outfits():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    category = request.form['make_outfit_category']
    return render_template(f'make_outfit_{category}.html', user=user, user_clothing = user_clothing)
################################################################################
################################################################################


################################################################################
##Route for after a selection is made##
@app.route("/choose_item_for_outfit", methods = ["POST"])
def choose_item_for_outfit():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()

    list_of_selected_clothing = []
    selected_radio_button = request.form["selected_clothing"]
    
    if not session.get("outfit"):
        session["outfit"] = []
    
    session["outfit"].append(selected_radio_button)

    for number in session.get("outfit"):
        list_of_selected_clothing.append(Clothing.query.get(number))
    session.modified = True

    return render_template("make_an_outfit.html", user = user, list_of_selected_clothing = list_of_selected_clothing)
    #, selected_clothing = selected_clothing)#, selected_id = selected_id, list_of_selected_clothing = list_of_selected_clothing)
################################################################################
################################################################################


################################################################################
#########################Saving outfit to databse###############################
@app.route("/submit_outfit_to_database", methods = ["POST"])
def submit_outfit_to_databse():
    user_id = session["user_id"]
    clothing_list = session["outfit"]

    new_outfit = Outfit(user_id = user_id)
    db.session.add(new_outfit)
   
    for clothing_id in clothing_list:
        clothing_item = Clothing.query.filter_by(clothing_id = clothing_id).one()
        new_outfit.add_clothing_id(clothing_item)

    db.session.commit()

    return redirect(f"make_an_outfit")
################################################################################
################################################################################


@app.route("/view_outfits")
def view_outfits():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()

    outfits = Outfit.query.filter_by(user_id = user_id).all()

    dict_of_clothes = {}
    for outfit in outfits:
        clothes = outfit.clothes
        dict_of_clothes[outfit] = clothes

    # print("\n\n\n", dict_of_clothes, "\n\n\n")

    return render_template("view_outfits.html", user = user, clothes = clothes, dict_of_clothes = dict_of_clothes, outfit = outfit)
################################################################################
################################################################################


@app.route("/search_user", methods = ["POST"])
def search_user():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()

    user_input = request.form["search"]
    search = "%{}%".format(user_input)

    found_users = User.query.filter(User.username.like(search)).all()


    return render_template("display_searches.html", found_users = found_users, user =user)










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