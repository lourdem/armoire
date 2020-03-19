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
##Route for dropdown menu when you seelct a category to view in your closet##

@app.route("/show_this_category", methods = ["POST"])
def show_category():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    category = request.form["category_to_view"]
    if category == "skirts":
        return redirect(f"/show_skirts")
    elif category == "jeans":
        return redirect(f"/show_jeans")
    elif category == "dresses":
        return redirect(f"/show_dresses")
    elif category == "outerwear":
        return redirect(f"/show_outerwear")
    elif category == "shorts":
        return redirect(f"/show_shorts")
    elif category == "tops":
        return redirect(f"/show_tops")
    elif category == "shoes":
        return redirect(f"/show_shoes")
    else:
        return redirect(f"/show_accessories")
    # else:
    #     return render_template('jeans.html', user=user, user_clothing = user_clothing)
################################################################################
################################################################################



################################################################################
##Routes for displaying each category once you're on your personal closet page##

@app.route("/show_skirts", methods = ["POST", "GET"])
def show_skirts():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('skirts.html', user=user, user_clothing = user_clothing)

@app.route("/show_jeans", methods = ["POST", "GET"])
def show_jeans():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('jeans.html', user=user, user_clothing = user_clothing)

@app.route("/show_dresses", methods = ["POST", "GET"])
def show_dresses():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('dresses.html', user=user, user_clothing = user_clothing)

@app.route("/show_outerwear", methods = ["POST", "GET"])
def show_outerwear():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('outerwear.html', user=user, user_clothing = user_clothing)

@app.route("/show_shorts", methods = ["POST", "GET"])
def show_shorts():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('shorts.html', user=user, user_clothing = user_clothing)

@app.route("/show_tops", methods = ["POST", "GET"])
def show_tops():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('tops.html', user=user, user_clothing = user_clothing)

@app.route("/show_shoes", methods = ["POST", "GET"])
def show_shoes():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('shoes.html', user=user, user_clothing = user_clothing)

@app.route("/show_accessories", methods = ["POST", "GET"])
def show_accessories():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('accessories.html', user=user, user_clothing = user_clothing)
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
##Route for dropdown menu when you seelct a category to make an outfit##

@app.route("/make_outfit_category", methods = ["POST"])
def show_category_for_outfits():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    category = request.form["make_outfit_category"]
    if category == "skirts":
        return redirect(f"/make_outfit_skirts")
    elif category == "jeans":
        return redirect(f"/make_outfit_jeans")
    elif category == "dresses":
        return redirect(f"/make_outfit_dresses")
    elif category == "outerwear":
        return redirect(f"/make_outfit_outerwear")
    elif category == "shorts":
        return redirect(f"/make_outfit_shorts")
    elif category == "tops":
        return redirect(f"/make_outfit_tops")
    elif category == "shoes":
        return redirect(f"/make_outfit_shoes")
    else:
        return redirect(f"/make_outfit_accessories")
################################################################################
################################################################################


################################################################################
################################################################################
################################################################################
################################################################################

# @app.route('/categories', methods = ['POST'])
#     category = 














################################################################################
##Routes for displaying each category to make an outfit##
@app.route("/make_outfit_skirts", methods = ["POST", "GET"])
def make_outfit_skirts():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('make_outfit_skirts.html', user=user, user_clothing = user_clothing)

@app.route("/make_outfit_jeans", methods = ["POST", "GET"])
def make_outfit_jeans():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('make_outfit_jeans.html', user=user, user_clothing = user_clothing)

@app.route("/make_outfit_dresses", methods = ["POST", "GET"])
def make_outfit_dresses():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('make_outfit_dresses.html', user=user, user_clothing = user_clothing)

@app.route("/make_outfit_outerwear", methods = ["POST", "GET"])
def make_outfit_outerwear():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('make_outfit_outerwear.html', user=user, user_clothing = user_clothing)

@app.route("/make_outfit_shorts", methods = ["POST", "GET"])
def make_outfit_shorts():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('make_outfit_shorts.html', user=user, user_clothing = user_clothing)

@app.route("/make_outfit_tops", methods = ["POST", "GET"])
def make_outfit_tops():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('make_outfit_tops.html', user=user, user_clothing = user_clothing)

@app.route("/make_outfit_shoes", methods = ["POST", "GET"])
def make_outfit_shoes():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('make_outfit_shoes.html', user=user, user_clothing = user_clothing)

@app.route("/make_outfit_accessories", methods = ["POST", "GET"])
def make_outfit_accessories():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    user_clothing = Clothing.query.filter_by(user_id = user_id).all()
    return render_template('make_outfit_accessories.html', user=user, user_clothing = user_clothing)
################################################################################
################################################################################


################################################################################
##Route for after a selection is made##
@app.route("/choose_item_for_outfit", methods = ["POST"])
def choose_item_for_outfit():
    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    selected_radio_button = request.form["selected_clothing"]

    selected_clothing = Clothing.query.filter_by(clothing_id = selected_radio_button).first()

    list_of_selected_clothing = []
    if selected_clothing not in list_of_selected_clothing:
        list_of_selected_clothing.append(selected_clothing)
 

    # for item in list_of_selected_clothing:
    #     selected_id = item
    #     return selected_id

    # user_clothing = Clothing.query.filter_by(selected_id = clothing_id).all()



    return render_template("make_an_outfit.html", user = user, list_of_selected_clothing = list_of_selected_clothing, selected_clothing = selected_clothing)#, selected_id = selected_id, list_of_selected_clothing = list_of_selected_clothing)


################################################################################
################################################################################


















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