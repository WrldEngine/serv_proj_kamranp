from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from conf import *

app = Flask(__name__)
db = SQLAlchemy()

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String)
    username = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.Integer)
    password = db.Column(db.String)

    def __repr__(self, id):
        return '<Client %r>' % self.id

class Messages(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    msg_author = db.Column(db.String())
    msg_content = db.Column(db.Text())
    chat_room = db.Column(db.String())

    def __repr__(self, id):
        return '<Messages %r>' % self.id

class Chat_rooms(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    msg_author = db.Column(db.String())

    def __repr__(self, id):
        return '<Chat %r>' % self.id

def set_adm():
    USERNAME_CHECKER = Client.query.filter(Client.username == ADMIN_CONF_NAME).all()
    PASSWORD_CHECKER = Client.query.filter(Client.password == ADMIN_CONF_PASSWORD).all()

    if not USERNAME_CHECKER and not PASSWORD_CHECKER:
        set_admin = Client(
            username=ADMIN_CONF_NAME,
            fullname=ADMIN_CONF_FULL_NAME,
            phone=ADMIN_CONF_PHONE, 
            password=ADMIN_CONF_PASSWORD
        )
        db.session.add(set_admin)
        db.session.commit()