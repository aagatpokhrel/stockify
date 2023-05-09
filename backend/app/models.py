from app import db
from flask_login import UserMixin

class Subscribers(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True)
    username = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)

    def __init__(self,email,username,password):
        self.email = email
        self.username = username
        self.password = password
    
    @property
    def serialize(self):
        return {
           'user_id':int(self.id),       
           'email':self.email,
           'username':self.username,
           'password':self.password,
        }