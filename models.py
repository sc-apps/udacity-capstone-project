from flask_sqlalchemy import SQLAlchemy
import os
from os import environ as env
from dotenv import find_dotenv, load_dotenv
	

ENV_FILE = find_dotenv()
if ENV_FILE:
	load_dotenv(ENV_FILE)

database_name = env.get("database_name")
database_path = "postgresql://{}/{}".format('localhost:5432', database_name)


db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = env.get("APP_SECRET_KEY")
    db.app = app
    db.init_app(app)
    db.create_all()



class Event(db.Model):
	__tablename__ = 'event'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(), nullable=False)
	date = db.Column(db.DateTime(), nullable=False)
	requests = db.relationship("Request", backref = "event", lazy = True)

	def insert(self):
		db.session.add(self)
		db.session.commit()


    
class Request(db.Model):
	__tablename__ = 'request'	
	id = db.Column(db.Integer, primary_key=True)
	child_name = db.Column(db.String(), nullable=False)
	child_age = db.Column(db.Integer, nullable=False)
	gift_name = db.Column(db.String(), nullable=False)
	gift_link = db.Column(db.String(), nullable=False)
	price = db.Column(db.Integer, nullable=False)
	shipping_address = db.Column(db.String(), nullable=False)
	phone = db.Column(db.String(), nullable=False)
	recipient_email = db.Column(db.String(), nullable=False)
	taken = db.Column(db.Boolean, nullable=False)
	event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable = False)
	event_name = db.Column(db.String(), nullable=False)

	def insert(self):
		db.session.add(self)
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def update(self):
		db.session.commit()
