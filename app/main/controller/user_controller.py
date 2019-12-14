from flask import request
from flask_restplus import Resource

from ..util.dto import UserDto, UserInfoDto
from ..service.user_service import save_new_user, get_all_users, \
    find_user, delete_user, get_user_statistics, confirm_token, \
        check_email_token
from ..util.decorator import token_required, admin_token_required

from flask_babel import gettext


api = UserDto.api
_user = UserDto.user

uapi = UserInfoDto.api
_user_info = UserInfoDto.user

@api.route('/')
class UserList(Resource):
    @api.response(404, gettext('User not found'))
    @api.doc('get a user')
    @api.marshal_with(_user_info)
    @token_required
    def get(self):
        """get a user given its identifier"""
        user = find_user(request.headers.get('Authorization'))
        if not user:
            api.abort(404)
        else:
            return user

    @api.response(201, 'User successfully created.')
    @api.doc('create a new user')
    @api.expect(_user, validate=True)
    def post(self):
        """Creates a new User """
        data = request.json
        return save_new_user(data=data)

    @api.response(200, 'User successfully deleted.')
    @api.doc('delete user')
    def delete(self):
        """Deletes user """
        return delete_user(request.headers.get('Authorization'))


@api.route('/statistics')
@api.response(404, gettext('User not found'))
class UserStatistics(Resource):
    @api.doc('get user\'s statistics')
    @token_required
    def get(self):
        return get_user_statistics(request.headers.get('Authorization'))


@api.route('/confirm')
class UserMail(Resource):
    @api.doc('confirm email')
    def get(self):
        return check_email_token(
            request.headers.get('Authorization'),
            request.args.get('token'), 
            confirm=True
        )
