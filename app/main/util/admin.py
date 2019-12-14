from .views.user_admin_view import UserView
from .views.diagnosis_admin_view import DiagnosisView
from .views.blacklist_admin_view import BlacklistView
from flask_admin.contrib.sqla import ModelView

from app.main.model.user import User
from app.main.model.diagnosis import Diagnosis
from app.main.model.blacklist import BlacklistToken
from app.main import db
from flask import session, redirect, url_for, request


class AdminPanel(ModelView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_folder = 'static'

    def is_accessible(self):
        pass

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            pass
    
    @staticmethod
    def create_views(administrator):
        administrator.add_view(UserView(User, db.session))
        administrator.add_view(DiagnosisView(Diagnosis, db.session))
        administrator.add_view(BlacklistView(BlacklistToken, db.session))
