from flask_restplus import Api
from flask import Blueprint

from .main.controller.user_controller import api as user_ns
from .main.controller.auth_controller import api as auth_ns
from .main.controller.diagnosis_controller import api as diagnosis_ns
from .main.controller.subscription_controller import api as subscription_ns
from .main.controller.edit_controller import api as edit_ns


blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='FLASK RESTPLUS API BOILER-PLATE WITH JWT',
          version='1.0',
          description='a boilerplate for flask restplus web service'
          )

api.add_namespace(user_ns, path='/api/user')
api.add_namespace(auth_ns, path='/api/account')
api.add_namespace(diagnosis_ns, path='/api/diagnosis')
api.add_namespace(subscription_ns, path='/api/subscription')
api.add_namespace(edit_ns, path='/api/edit')
