from ..model.user import User

from flask.ext.babel import gettext
from .. import db

import stripe

from ..util.decorator import token_checker


@token_checker
def enter_subscribction(token, data):
    user = User.query.filter_by(
        public_id=User.decode_auth_token(token)
    ).first()

    stripe.api_key = 'sk_test_KkGEJemEelBHxdDIVLKkpfgo00OELhzQhM'

    ADVANCED_PLAN = 'plan_G8q6hcSY0O28k1'
    MAX_PLAN = 'plan_G8q5R7P8EzA3Wh'

    print(data)
    if data['plan'] not in ['Spero Advanced', 'Spero Max']:
        response_object = {
            'status': 'fail',
            'message': gettext('Plan does not exist')
        }
        return response_object, 400

    try:
        if user.stripe_id and user.stripe_id:
            if not user.data_access and data['plan'] == 'Spero Max':
                response_object = {
                    'status': 'fail',
                    'message': gettext('You are already subscribed for Spero Max')
                }
                return response_object, 400
            
            if user.data_access and user.subscriber and data['plan'] == 'Spero Advanced':
                response_object = {
                    'status': 'fail',
                    'message': gettext('You are already subscribed for Spero Advanced')
                }
                return response_object, 400
            
            if not user.data_access and data['plan'] == 'Spero Advanced':
                try:
                    finish_payment(user.stripe_id, mode=False)
                except:
                    print('can not')
                customer = stripe.Customer.create(
                    email=user.email,
                    plan=ADVANCED_PLAN,
                    card=data['stripe_id']
                )

                user.data_access = True
                user.subscriber = True
                user.stripe_id = customer.stripe_id
            
            if user.data_access and user.subscriber and data['plan'] == 'Spero Max':
                try:
                    finish_payment(user.stripe_id, mode=False)
                except:
                    print('can not')
                customer = stripe.Customer.create(
                    email=user.email,
                    plan=MAX_PLAN,
                    card=data['stripe_id']
                )

                user.data_access = False
                user.subscriber = True
                user.stripe_id = customer.stripe_id

        else:
            customer = stripe.Customer.create(
                email=user.email,
                plan=MAX_PLAN if data['plan'] == 'Spero Max' else ADVANCED_PLAN,
                card=data['stripe_id']
            )

            user.subscriber = True
            user.stripe_id = customer.stripe_id

            if data['plan'] == 'Spero Max':
                user.data_access = False

        if user.stripe_id != None:
            user.subscriber = True
            db.session.commit()

        response_object = {
            'status': 'success',
            'message': gettext('You have succesfully subscriped to ') + data['plan'] + gettext(' plan')
        }

        return response_object, 200
    
    except Exception as e:
        print(e)
        response_object = {
            'status': 'fail',
            'message': gettext('Your card has been declined')
        }
        return response_object, 400


@token_checker
def cancel_subscription(token):
    user = User.query.filter_by(
        public_id=User.decode_auth_token(token)
    ).first()
    
    stripe.api_key = 'sk_test_KkGEJemEelBHxdDIVLKkpfgo00OELhzQhM'

    try:
        finish_payment(user.stripe_id, mode=True)

        if user.data_access and user.subscriber:
            user.subscriber = False
        
        if not user.data_access:
            user.subscriber = False
            user.data_access = True
        
        user.stripe_id = None
        db.session.commit()

        response_object = {
            'status': 'success',
            'message': 'Subscription was canceled'
        }

        return response_object, 200

    except Exception as e:
        print(e)
        response_object = {
            'status': 'fail',
            'message': gettext('Error has occured')
        }
        return response_object, 400


def finish_payment(stripe_id, mode):
    customer = stripe.Customer.retrieve(stripe_id)
    print(len(customer.subscriptions))
    customer.subscriptions.retrieve(
        customer.subscriptions.data[0].id
    ).delete()
