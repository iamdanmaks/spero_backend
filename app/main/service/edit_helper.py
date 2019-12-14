from ..model.user import User
from .. import db

from ..util.decorator import token_checker
from ..util.fun import password_validate
from .. import mail, serializer, salt

from flask_babel import gettext
from flask import render_template
from hashlib import sha384
from cloudinary import CloudinaryImage
from flask_mail import Message

import cloudinary.uploader
from random import seed
from random import randint


@token_checker
def edit_basic_data(token, data):
    user = User.query.filter_by(
        public_id=User.decode_auth_token(token)
    ).first()

    if data.get('name'):
        if data.get('name') == user.first_name:
            response_object = {
                'status': 'fail',
                'message': gettext('You have not changed your current name')
            }
            return response_object, 400

        user.first_name = data.get('name')
    
    if data.get('surname'):
        if data.get('surname') == user.second_name:
            response_object = {
                'status': 'fail',
                'message': gettext('You have not changed your current surname')
            }
            return response_object, 400
        
        user.second_name = data.get('surname')
    
    if data.get('height'):
        if data.get('height') == user.height:
            response_object = {
                'status': 'fail',
                'message': gettext('You have not changed your current height')
            }
            return response_object, 400
        
        user.height = float(data.get('height'))
    
    if data.get('weight'):
        if data.get('weight') == user.weight:
            response_object = {
                'status': 'fail',
                'message': gettext('You have not changed your current weight')
            }
            return response_object, 400

        user.weight = float(data.get('weight'))
    
    if data.get('username'):
        if data.get('username') == user.username:
            response_object = {
                'status': 'fail',
                'message': gettext('You have not changed your current username')
            }
            return response_object, 400

        if len(data.get('username')) < 6 and len(data.get('username')) > 25 and not any(char.isalpha() for char in data.get('username')):
            response_object = {
                'status': 'fail',
                'message': gettext('Username length should be greater than 6 and less than 25 symbols and contain letters')
            }
            return response_object, 400

        if User.query.filter_by(
            username=data.get('username')
        ).first():
            response_object = {
                'status': 'fail',
                'message': gettext('This username is already taken')
            }
            return response_object, 400
        
        user.username = data.get('username')
    
    db.session.commit()

    response_object = {
        'status': 'success',
        'message': gettext('Your data was edited')
    }
    return response_object, 200


@token_checker
def reset_password(token, data):
    user = User.query.filter_by(
        public_id=User.decode_auth_token(token)
    ).first()

    if data.get('old_pass') and data.get('new_pass') and data.get('repeat'):
        if not user.check_password(data.get('old_pass')):
            response_object = {
                'status': 'fail',
                'message': gettext('Wrong password')
            }
            return response_object, 400

        if data.get('old_pass') == data.get('new_pass'):
            response_object = {
                'status': 'fail',
                'message': gettext('You have not changed your current password')
            }
            return response_object, 400

        check_password = password_validate(data['new_pass'], data['repeat'])

        if not check_password['validity']:
            return check_password['answer'], 400

        user.password = data['new_pass']
        db.session.commit()

        response_object = {
            'status': 'success',
            'message': gettext('Password was succesfully reset')
        }
        return response_object, 200
    
    else:
        response_object = {
            'status': 'fail',
            'message': gettext('You have to fill in all the fields')
        }
        return response_object, 400


@token_checker
def save_avatar(token, avatar):
    user = User.query.filter_by(
        public_id=User.decode_auth_token(token)
    ).first()

    avatar_id = generate_avatar_name(
            user.public_id,
            user.username,
            user.registered_on
        )

    upload_data = cloudinary.uploader.upload(
        avatar,
        public_id=avatar_id
    )

    user.avatar = True
    db.session.commit()

    return {
            'status': 'success',
            'data': 'https://res.cloudinary.com/dvm82rgep/image/upload/{}.jpg'.format(
                avatar_id
            )
        }


@token_checker
def get_avatar(token):
    user = User.query.filter_by(
        public_id=User.decode_auth_token(token)
    ).first()

    seed(5)

    response_object = {
        'status': 'success',
        'message': 'https://res.cloudinary.com/dvm82rgep/image/upload/v' + str(randint(0, 100000)) + '/{}.jpg'.format(
            generate_avatar_name(
                user.public_id,
                user.username,
                user.registered_on
            )
        )
    }

    return response_object, 200


def forgot_password(email):
    user = User.query.filter_by(
        email=email
    ).first()

    if not user:
        response_object = {
            'status': 'fail',
            'message': gettext('No user with such email')
        }

    try:
        send_reset_mail(user, email)

        response_object = {
            'status': 'success',
            'message': gettext('Reset email is sent')
        }
        return response_object, 200
    except Exception as e:
        print(e)
        response_object = {
            'status': 'fail',
            'message': gettext('Error has occured')
        }
        return response_object, 400


def send_reset_mail(user, email):
    try:
        token = generate_confirmation_token(
            email + ' ' + user.public_id
        )
        msg = Message(
            gettext('Let\'s conirm your email'), 
            sender='system.spero@gmail.com', 
            html=render_email(token),
            recipients=[email]
        )
        msg.body = "Reset Flask message sent from Flask-Mail"
        mail.send(msg)
    except Exception as e:
        print(e,'\n\n\n')
        response_object = {
            'status': 'success',
            'message': gettext('Your email is not valid')
        }
        return response_object


def restore_password(email_token, data):
    print(confirm_token(email_token))
    email, public_id = confirm_token(email_token)

    print('\n\n\n',email,public_id,'\n\n\n')

    user = User.query.filter_by(
        public_id=public_id
    ).first()

    if not user:
        response_object = {
            'status': 'fail',
            'message': gettext('User not found')
        }
        return response_object, 404

    if email and public_id and user.email == email:
        if data.get('new_pass') and data.get('repeat'):
            if user.check_password(data.get('new_pass')):
                response_object = {
                    'status': 'fail',
                    'message': gettext('It is your old password')
                }
                return response_object, 400

            check_password = password_validate(data['new_pass'], data['repeat'])

            if not check_password['validity']:
                return check_password['answer'], 400

            user.password = data['new_pass']
            db.session.commit()

            response_object = {
                'status': 'success',
                'message': gettext('Your password was reset')
            }
            return response_object, 200

        else:
            response_object = {
                'status': 'fail',
                'message': gettext('Data is not complete')
            }
    
    else:
        response_object = {
            'status': 'fail',
            'message': gettext('Your link has expired or it is wrong')
        }
        return response_object, 400


def render_email(token):
    return render_template(
        'email.html',
        welcome_text=gettext('Click below to reset your password'),
        confirm_url='http://localhost:8080/edit/change?token={}'.format(
            token
        ),
        confirm_text=gettext('Click here to reset'),
        congratulations_text=gettext('Thank you for using Spero!')
    )


def generate_confirmation_token(email):
    return serializer.dumps(email, salt=salt)


def confirm_token(token, expiration=3600):
    print(token,'\n\n\n')
    try:
        result = serializer.loads(
            token,
            salt=salt,
            max_age=expiration
        ).split(' ')
    except:
        return False, False
    return result[0], result[1]


def generate_avatar_name(public_id, username, registered_on):
    return sha384(
        public_id.encode('utf-8') + username.encode('utf-8') \
         + registered_on.strftime("%d.%m.%Y %H:%M:%S").encode('utf-8')
    ).hexdigest()
