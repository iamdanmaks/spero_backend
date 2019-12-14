from flask import request
from flask_restplus import Resource

from ..service.edit_helper import edit_basic_data, reset_password, \
    save_avatar, get_avatar, forgot_password, restore_password
from ..util.dto import EditUserDto
from ..util.decorator import token_required


api = EditUserDto.api
user_edit = EditUserDto.user


@api.route('/')
class UserEdit(Resource):
    """
        User Edit Resource
    """
    @api.doc('save avatar')
    def post(self):
        # get the post data
        return save_avatar(
            request.headers.get('Authorization'),
            request.files['avatar']
        )

    @api.doc('edit user data')
    @api.expect(user_edit, validate=True)
    def put(self):
        # get the post data
        return edit_basic_data(
            request.headers.get('Authorization'),
            request.json
        )
    
    @api.doc('get user avatar')
    def get(self):
        # get the post data
        return get_avatar(
            request.headers.get('Authorization')
        )


@api.route('/reset')
class ResetPassword(Resource):
    """
    User Password Reset Resource
    """
    @api.doc('reset a password')
    @token_required
    def post(self):
        # get auth token
        return reset_password(
            request.headers.get('Authorization'),
            request.json
        )
    
    @api.doc('forgot a password')
    def get(self):
        return forgot_password(
            request.args.get('email')
        )
    
    @api.doc('restore a password')
    def put(self):
        return restore_password(
            request.args.get('token'),
            request.json
        )
