from functools import wraps
from flask import request

from app.main.service.auth_helper import Auth
from app.main.model.user import User

from flask_babel import gettext


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        data, status = Auth.get_logged_in_user(request)
        token = data.get('data')

        if status != 200:
            return data, status

        if not token.get('active'):
            response_object = {
                'status': 'fail',
                'message': gettext('Email is not confirmed')
            }
            return response_object, 403

        if not token:
            return data, status

        return f(*args, **kwargs)

    return decorated


def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        data, status = Auth.get_logged_in_user(request)
        token = data.get('data')

        if not token:
            return data, status

        admin = token.get('admin')
        if not admin:
            response_object = {
                'status': 'fail',
                'message': gettext('Admin token required')
            }
            return response_object, 401

        return f(*args, **kwargs)

    return decorated


def token_checker(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if args[0]:
            token = args[0].split(' ')[0]
        else:
            token = ''
    
        if token:
            print('\n\n\n',token,'\n\n\n')
            resp = User.decode_auth_token(token)
            
            if isinstance(resp, str):
                user = User.query.filter_by(public_id=resp).first()
                
                if not user:
                    response_object = {
                        'status': 'fail',
                        'message': gettext('User not found, so probably they do not exist')
                    }
                    return response_object, 404

                return f(*args, **kwargs)
            
            else:
                response_object = {
                    'status': 'fail',
                    'message': gettext('Token has wrong value')
                }
                return response_object, 401
        else:
            response_object = {
                'status': 'fail',
                'message': gettext('Provide a valid auth token.')
            }
            return response_object, 403
    
    return decorated
