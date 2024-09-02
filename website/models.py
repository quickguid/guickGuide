from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import  UserMixin
import datetime
from datetime import datetime



ACCESS = {
    'guest': 0,
    'user': 1,
    'admin': 2
}

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email  = db.Column(db.String(150), unique=True)
    password  = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    access = db.Column(db.Integer, default=0)

    def __init__(self, email,first_name,last_name , password ,access=ACCESS['user']):
       
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.access = access

    def is_admin(self):
        return self.access == ACCESS['admin']

    def is_user(self):
        return self.access == ACCESS['user']

    def allowed(self, access_level):
        return self.access >= access_level

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {0}>'.format(self.first_name+self.last_name)
    

class UserAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # Assuming you have a User model to reference
    session_id = db.Column(db.String(255), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)  # Foreign key to Lesson
    action_id = db.Column(db.Integer, db.ForeignKey('action.id'), nullable=False)   # Foreign key to Action
    time_clicked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    lesson = db.relationship('Lesson', backref='user_actions')
    action = db.relationship('Action', backref='user_actions')

    def __init__(self, user_id,session_id ):
        self.user_id = user_id
        self.session_id = session_id

    def __init__(self, user_id,session_id , lesson_id,action_id , time_clicked):
        self.user_id = user_id
        self.session_id = session_id
        self.lesson_id = lesson_id
        self.action_id = action_id
        self.time_clicked = time_clicked
        





class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)  # Assuming you have a User model to reference
    file_path = db.Column(db.String(255), nullable=False)

    actions = db.relationship('Action', backref='lesson', lazy=True)

    def __init__(self, name,file_path ):
        self.name = name
        self.file_path = file_path


class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    action_name = db.Column(db.String(255), nullable=False)

    def __init__(self, lesson_id, action_name):
        self.lesson_id = lesson_id
        self.action_name = action_name