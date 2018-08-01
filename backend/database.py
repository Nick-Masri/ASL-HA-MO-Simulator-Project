from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
# from sqlalchemy.dialects.postgresql import JSONB
# from sqlalchemy.ext.mutable import MutableDict

#--- Global objects ---
migrate = Migrate()
db = SQLAlchemy()

#--- Helper function ---
def session_commit():
	try:
		db.session.commit()
	except SQLAlchemyError as e:
		db.session.rollback()
		reason = str(e)
		return reason

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))


    def as_dict(self):
    	return {
    		'id': self.id,
    		'username': self.username
    	}

    def __init__(self, username, password):
    	self.username = username
    	self.set_password(password)

    def set_password(self, password):
    	self.password_hash = generate_password_hash(password)

    def check_password(self, password):
    	return check_password_hash(self.password_hash, password)

    @staticmethod
    def add(user):
    	db.session.add(user)
    	return session_commit()

    @staticmethod
    def update():
    	return session_commit()

    @staticmethod
    def delete(user):
    	db.session.delete(user)
    	return session_commit()


