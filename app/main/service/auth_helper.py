from app.main.model.user import User
from ..service.blacklist_service import save_token

from flask.ext.babel import gettext

class Auth:

    @staticmethod
    def login_user(data):
        try:
            # fetch the user data
            user = User.query.filter_by(email=data.get('email')).first()
            if user and user.check_password(data.get('password')):
                auth_token = user.encode_auth_token(user.public_id)
                if auth_token:
                    response_object = {
                        'status': 'success',
                        'message': gettext('Successfully logged in.'),
                        'Authorization': auth_token.decode()
                    }
                    return response_object, 200
            else:
                response_object = {
                    'status': 'fail',
                    'message': gettext('Email or password does not match')
                }
                return response_object, 401

        except Exception as e:
            response_object = {
                'status': 'fail',
                'message': gettext('Try again')
            }
            return response_object, 500

    @staticmethod
    def logout_user(data):
        if data:
            auth_token = data.split(" ")[0]
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            print(resp, type(resp))
            if isinstance(resp, str):
                # mark the token as blacklisted
                return save_token(token=auth_token)
            else:
                response_object = {
                    'status': 'fail',
                    'message': resp
                }
                return response_object, 401
        else:
            response_object = {
                'status': 'fail',
                'message': gettext('Provide a valid auth token')
            }
            return response_object, 403

    @staticmethod
    def get_logged_in_user(new_request):
        # get the auth token
        auth_token = new_request.headers.get('Authorization')

        if auth_token:
            resp = User.decode_auth_token(auth_token)
            
            if isinstance(resp, str):
                user = User.query.filter_by(public_id=resp).first()
                
                if not user or resp == 'Signature expired. Please log in again.':
                    response_object = {
                        'status': 'fail',
                        'message': gettext('User not found')
                    }
                    return response_object, 404

                response_object = {
                    'status': 'success',
                    'data': {
                        'user_id': user.id,
                        'email': user.email,
                        'admin': user.admin,
                        'active': user.active,
                        'registered_on': str(user.registered_on)
                    }
                }
                return response_object, 200
            else:
                print(resp)
                response_object = {
                    'status': 'fail',
                    'message': resp
                }
                return response_object, 401
        else:
            print(auth_token)
            response_object = {
                'status': 'fail',
                'message': gettext('Provide a valid auth token')
            }
            return response_object, 401
