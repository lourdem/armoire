from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_imageattach.entity import Image, image_attachment
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy_imageattach.entity import Image, image_attachment
# import psycopg2
# from config import Config


#added in order to be able to implement login
from werkzeug.security import generate_password_hash, check_password_hash
# from SQLAlchemy import Table, Column, Integer, ForeignKey
# from sqlalchemy.orm import relationship

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()



#added to implement login

# def create_password(self, password):
#     self.password = generate_password_hash(password)

# def login(self, password):
#     check_password_hash(password, self.password)




##############################################################################
# Model definitions

class User(db.Model):
    """User of Armoire."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    username = db.Column(db.String(64), nullable = False)
    password = db.Column(db.String(64), nullable=False)
    # picture = image_attachment('UserPicture')
    # age = db.Column(db.Integer, nullable=True)
    # zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        return f"<User user_id={self.user_id} email = {self.email} username = {self.username} password={self.password}>"


class Clothing(db.Model):
    """User's clothing'."""

    __tablename__ = "clothing"

    clothing_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    type_code = db.Column(db.String(10), nullable=True)
    season_code = db.Column(db.String(10), nullable = True)
    color = db.Column(db.String(20), nullable = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
    photo = db.Column(db.String(), nullable = True)
    # picture = image_attachment('UserPicture')
    # picture = image_attachment('UserPicture')

    def __repr__(self):
        return f"<Clothing clothing_id={self.clothing_id} type_code ={self.type_code} season_code={self.season_code} color = {self.color}>"


# class UserPicture(db.Model, Image):
#     """User picture model."""

#     __tablename__ = "user_picture"

#     picture_id = Column(Integer, ForeignKey('clothing.clothing_id'), primary_key=True)
#     user = relationship('clothing')

#     clothingPictures = db.relationship("Clothing",
#                            backref=db.backref("clothingPictures", order_by=picture_id))




#IS A TABLE WITH OUTFIT NUMBERS AND NO ITEMS COLUMN
class Outfit(db.Model):
    """User's outfits."""

    __tablename__ = "outfits"

    outfit_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    day_of_week = db.Column(db.String(10), nullable =True)

    def __repr__(self):
        return f"<Outfit outfit_id={self.outfit_id} day_of_week={self.day_of_week}>"


class Friend(db.Model):
    """User's friends."""

    __tablename__="friends"

    friend_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    friend_name = db.Column(db.String(70), nullable=False)

    def __repr__(self):
        return f"<Friend friend_id={self.friend_id} friend_name={self.friend_name}>"


class Event(db.Model):
    """User's events."""

    __tablename__="events"

    event_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('users.user_id'),index=True)
    event_outfit_id = db.Column(db.Integer, db.ForeignKey('outfits.outfit_id'), index =True)

#defining relationship to user and outfit
    guest = db.relationship("User",
                           backref=db.backref("eventGuest", order_by=event_id))
    outfit = db.relationship("Outfit",
                           backref=db.backref("eventOutfit", order_by=event_id))

    def __repr__(self):
        return f"<Friend friend_id={self.friend_id} friend_name={self.friend_name}>"    


#create table to make outfits --> an outfit_id can appear numerous times and have a
#corresponding clothing_id, so that you can add multiple clothing items to an outfit
#but there is no minimum or maximum this way

clothesInOutfit = db.Table('clothesInOutfit', db.Column('outfit_id', db.Integer, db.ForeignKey('outfits.outfit_id')),
                db.Column('clothing_id', db.Integer, db.ForeignKey('clothing.clothing_id')))

#HOW TO PRINT CONTENTS OF THE TABLE ABOVE
    # def __repr__(self):
    #     return f"<Outfit outfit_id={self.outfit_id} day_of_week={self.day_of_week}>"



#TABLE IF AN OUTFITS TABLE IS MADE
# clothesInOutfit = db.Table('clothesInOutfit', db.Column('outfit_id', db.Integer, db.ForeignKey('outfit_id')),
#                 db.Column('clothing_id', db.Integer, db.ForeignKey('clothing_id')))


# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///project'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")
