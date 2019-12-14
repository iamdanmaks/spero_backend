from .. import db, flask_bcrypt
import datetime
from app.main.model.blacklist import BlacklistToken

class Diagnosis(db.Model):
    """ Diagnosis Model for storing diagnosis related information """
    __tablename__ = "diagnosis"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    result = db.Column(db.Integer, nullable=False)
    public_id = db.Column(db.String(100), unique=True)
    checked_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    normal_probability = db.Column(db.Float, nullable=False)
    murmur_probability = db.Column(db.Float, nullable=False)
    extrasystole_probability = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "{0} was indicated on {1}".format(self.result, self.checked_on.strftime("%d.%m.%Y %H:%M:%S"))
