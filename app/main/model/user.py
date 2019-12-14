from ..import db, flask_bcrypt, login
import datetime
import jwt
from app.main.model.blacklist import BlacklistToken
from ..config import key
from .diagnosis import Diagnosis
from .role import Role, roles_users
from flask_security import SQLAlchemyUserDatastore
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """ User Model for storing user related details """
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    public_id = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(100))
    stripe_id = db.Column(db.String(255))

    registered_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    
    active = db.Column(db.Boolean, nullable=False, default=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    subscriber = db.Column(db.Boolean, nullable=False, default=False)
    data_access = db.Column(db.Boolean, nullable=False, default=True)
    avatar = db.Column(db.Boolean, default=False)

    first_name = db.Column(db.String(150))
    second_name = db.Column(db.String(150))
    avatar_pass = db.Column(db.String(150))

    height = db.Column(db.Float)
    weight = db.Column(db.Float)

    _authenticated = db.Column(db.Boolean, default=False)

    diagnoses = db.relationship("Diagnosis")
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = flask_bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return flask_bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User '{}'>".format(self.username)
   
    def is_authenticated_admin(self):
        return self._authenticated

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                key,
                algorithm='HS256'
            )
        except Exception as e:
            return e
    
    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            print(auth_token, type(auth_token))
            payload = jwt.decode(auth_token, key)
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
