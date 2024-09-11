from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from geoalchemy2 import Geometry
import os
from flask import current_app
from datetime import datetime



class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    job = db.Column(db.String, nullable=True)
    city = db.Column(db.String, nullable=True)
    sdt = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.String, default="False", nullable=False)
    comments = db.relationship("Comment",backref="user",cascade="all, delete-orphan", lazy=True) 

    def set_password(self, password_input):
        self.password = generate_password_hash(password_input)


    def check_password(self, password_input):
        return check_password_hash(self.password, password_input)
    

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))
    

class Motel(db.Model):
    __tablename__ = 'motels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    name_master = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False, unique=True)
    address = db.Column(db.String, nullable=False)
    describe = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)
    geom = db.Column(Geometry('POINT'))
    comments = db.relationship("Comment",backref="motel",cascade="all, delete-orphan", lazy=True)


    def save_image(self, image, motel_id):
        filename = str(motel_id) + '.jpg'
        path = os.path.join(current_app.static_folder,'images', filename)
        with open(path, 'wb') as f:
            f.write(image)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"),nullable=False)
    motel_id = db.Column(db.Integer, db.ForeignKey("motels.id"),nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)