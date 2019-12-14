import uuid, os

from app.main.model.user import User
from app.main import db

from flask import render_template
from flask_babel import gettext
from flask_mail import Message

from .. import mail, serializer, salt
from ..service.blacklist_service import save_token
from ..util.fun import age, group_diagnoses, stats, password_validate
from ..util.decorator import token_checker

import datetime
from datetime import datetime
from datetime import date
from dateutil.parser import parse

from .diagnosis_service import generate_name


def save_new_user(data):
    """ Create new user in database """
    user = User.query.filter_by(email=data['email']).first()
    user1 = User.query.filter_by(username=data['username']).first()
    if not user and not user1:
        check_password = password_validate(data['password'], data['password_repeat'])
        born = parse(data['date_of_birth'])
        user_age = age(born)
        name_len = len(data['username'])

        if not check_password['validity']:
            return check_password['answer'], 400

        elif user_age < 18 and user_age > 120:
            response_object = {
                'status': 'fail',
                'message': gettext('User age should be greater than 18')
            }
            return response_object, 400

        elif len(data['first_name']) != 0 and not any(char.isalpha() for char in data['first_name']):
            response_object = {
                'status': 'fail',
                'message': gettext('Name is not valid')
            }
            return response_object, 400

        elif len(data['second_name']) != 0 and not any(char.isalpha() for char in data['second_name']):
            response_object = {
                'status': 'fail',
                'message': gettext('Surname is not valid')
            }
            return response_object, 400

        elif name_len < 6 and name_len > 25 and not any(char.isalpha() for char in data['username']):
            response_object = {
                'status': 'fail',
                'message': gettext('Username length should be greater than 6 and less than 25 symbols')
            }
            return response_object, 400

        else:
            new_user = User(
                public_id=str(uuid.uuid4()),
                email=data['email'],
                username=data['username'],
                first_name=data['first_name'],
                second_name=data['second_name'],
                password=data['password'],
                date_of_birth=born
            )

            if data.get('height'):
                new_user.height = float(data.get('height'))
            
            if data.get('weight'):
                new_user.weight = float(data.get('weight'))

            save_changes(new_user)
            send_confirmation_email(new_user)
            return generate_token(new_user)

    else:
        response_object = {
            'status': 'fail',
            'message': gettext('User already exists. Please Log in.'),
        }
        return response_object, 409


@token_checker
def delete_user(token):
    """ Delete user from database """
    user = User.query.filter_by(
        public_id=User.decode_auth_token(token)
    ).first()

    for diagnosis in user.diagnoses:
        filename = './app/main/uploads/' + generate_name(diagnosis.public_id, 
            diagnosis.checked_on) + '.wav'
        os.remove(filename)
        db.session.delete(diagnosis)
    
    temp_name = '@' + user.username
    db.session.delete(user)
    
    # mark the token as blacklisted
    save_token(token=token)

    db.session.commit()

    response_object = {
        'status': 'success',
        'message': gettext('User was deleted')
    }

    return response_object, 200


@token_checker
def get_user_statistics(token):
    user = User.query.filter_by(
        public_id=User.decode_auth_token(token)
    ).first()
    grouped = group_diagnoses(user.diagnoses)
    response_object = {
        'status': 'success',
        'message': gettext('Statistics is gathered'),
        'result': stats(grouped)
    }

    return response_object, 200


@token_checker
def find_user(token):
    return User.query.filter_by(
        public_id=User.decode_auth_token(token)
    ).first()


def send_confirmation_email(user):
    try:
        token = generate_confirmation_token(
            user.email + ' ' + user.public_id
        )
        msg = Message(
            gettext('Let\'s conirm your email'), 
            sender='system.spero@gmail.com', 
            html=render_email(token),
            recipients=[user.email]
        )
        msg.body = "Hello Flask message sent from Flask-Mail"
        mail.send(msg)
    except Exception as e:
        response_object = {
            'status': 'success',
            'message': gettext('Your email is not valid')
        }
        return response_object


def check_email_token(token, email_token, confirm=False):
    email, public_id = confirm_token(email_token)

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
        user.active = True
        db.session.commit()

        response_object = {
            'status': 'success',
            'message': gettext('Your email was confirmed')
        }
        return response_object, 200
    
    else:
        response_object = {
            'status': 'fail',
            'message': gettext('Your link has expired or it is wrong')
        }
        return response_object, 400


def render_email(token):
    return render_template(
        'email.html',
        welcome_text=gettext('Welcome! You\'ve just signed up for Spero.\
             If it is your email than follow the confiramtion link below \
                 to finish registration'),
        confirm_url='http://localhost:8080/confirm?token={}'.format(
            token
        ),
        confirm_text=gettext('Click here to confirm'),
        congratulations_text=gettext('Thank you!')
    )

def generate_confirmation_token(email):
    return serializer.dumps(email, salt=salt)


def confirm_token(token, expiration=3600):
    try:
        result = serializer.loads(
            token,
            salt=salt,
            max_age=expiration
        ).split(' ')
    except:
        return False, False
    return result[0], result[1]


def get_all_users():
    return User.query.all()


def get_a_user(pub_id):
    return User.query.filter_by(public_id=pub_id).first()


def save_changes(data):
    db.session.add(data)
    db.session.commit()


def generate_token(user):
    try:
        # generate the auth token
        auth_token = user.encode_auth_token(user.public_id)
        response_object = {
            'status': 'success',
            'message': gettext('Successfully registered'),
            'Authorization': auth_token.decode()
        }
        return response_object, 201
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': gettext('Some error occurred. Please try again.')
        }
        return response_object, 401
