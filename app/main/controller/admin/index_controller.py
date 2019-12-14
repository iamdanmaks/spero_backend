from flask import redirect, url_for, flash
from flask_admin import AdminIndexView, expose
from app.main.model.user import User
from app.main import db
from flask_login import login_user, logout_user, current_user


def login_admin(form):
    user = User.query.filter_by(username=form.username.data).first()

    if not user or not user.check_password(form.password.data) or not user.admin:
        flash('Invalid username/password or you are not admin')
        return redirect(url_for('login_me'))
    login_user(user, remember=form.remember_me.data)
    user._authenticated = True
    db.session.commit()
    return redirect(url_for('admin.index'))

class MyAnalyticsView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('new_main_admin_page.html', user_count=1)
    
    def is_accessible(self):
        try:
            print(current_user.is_authenticated_admin())
            return current_user.is_authenticated_admin()
        except:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login_me'))


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
