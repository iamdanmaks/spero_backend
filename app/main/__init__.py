from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_alchemydumps import AlchemyDumps
from flask_cors import CORS
from flask_mail import Mail
from flask_babel import Babel
from flask_login import LoginManager, current_user

import stripe
import cloudinary

from itsdangerous import URLSafeTimedSerializer

#from .util.checker_usage import define_checker_model

from .config import config_by_name


db = SQLAlchemy()
flask_bcrypt = Bcrypt()
cors = CORS(resources={r"/api/*": {"origins": "*"}})
mail = Mail()
babel = Babel()
login = LoginManager()
stripe_module = stripe

serializer = URLSafeTimedSerializer('my_secret_key')
salt = 'my_secret_password'

#checker_model, graph = define_checker_model()

from app.main.controller.admin.index_controller import MyAnalyticsView, \
    login_admin, LoginForm
admin = Admin(
    name='Spero', 
    index_view = MyAnalyticsView(endpoint='admin'), 
    template_mode='bootstrap3'
)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    flask_bcrypt.init_app(app)
    admin.init_app(app)
    cors.init_app(app)
    mail.init_app(app)
    babel.init_app(app)
    login.init_app(app)

    stripe_module.api_key = app.config['STRIPE_KEY']

    cloudinary.config(cloud_name=app.config['CLOUD_NAME'],
                  api_key=app.config['KEY'],
                  api_secret=app.config['SECRET']
                )

    from app.main.util.admin import AdminPanel

    AdminPanel.create_views(admin)

    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys())
    
    @app.route('/login', methods=['GET', 'POST'])
    def login_me():
        if current_user.is_authenticated:
            return redirect('admin.index')
        form = LoginForm()
        if form.validate_on_submit():
            login_admin(form)
        return render_template('login_to_admin.html', title='Sign In', form=form)
    
    @app.route('/logout')
    def logout():
        pass

    return app
