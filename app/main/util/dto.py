from flask_restplus import Namespace, fields


class UserDto:
    api = Namespace('user', description='user related operations')
    user = api.model('user', {
        'email': fields.String(required=True, description='user email address'),
        'username': fields.String(required=True, description='user username'),
        'password': fields.String(required=True, description='user password'),
        'password_repeat': fields.String(required=True, description='user password repeat'),
        'first_name': fields.String(required=True, description='user first name'),
        'second_name': fields.String(required=True, description='user second name'),
        'date_of_birth': fields.DateTime(required=True, description='user date of birth')
    })


class UserInfoDto:
    api = Namespace('user', description='user related information')
    user = api.model('user', {
        'email': fields.String(description='user email address'),
        'username': fields.String(description='user username'),
        'first_name': fields.String(description='user first name'),
        'second_name': fields.String(description='user second name'),
        'subscriber': fields.Boolean(description='user paid subscription'),
        'data_access': fields.Boolean(description='user data access'),
        'registered_on': fields.DateTime(description='user registration date'),
        'date_of_birth': fields.DateTime(description='user date of birth'),
        'height': fields.Float(description='user height'),
        'weight': fields.Float(description='user weight'),
        'avatar': fields.Boolean(description='user has avatar')
    })


class EditUserDto:
    api = Namespace('user', description='user information to edit')
    user = api.model('user', {
        'username': fields.String(description='user username'),
        'name': fields.String(description='user first name'),
        'surname': fields.String(description='user second name'),
        'height': fields.Float(description='user height'),
        'weight': fields.Float(description='user weight')
    })


class AuthDto:
    api = Namespace('auth', description='authentication related operations')
    user_auth = api.model('auth_details', {
        'email': fields.String(required=True, description='The email address'),
        'password': fields.String(required=True, description='The user password '),
    })


class DiagnosisDto:
    api = Namespace('diagnosis', description='diagnosis related operations')
    diagnosis = api.model('diagnosis_details', {
        'result': fields.String(required=True, description='The result of diagnostics'),
        'normal_proba': fields.Float(description='The probability of normal'),
        'murmur_proba': fields.Float(description='The probability of murmur'),
        'extrasystole_proba': fields.Float(description='The probability of extrasystole')
    })


class DiagnosisInfoDto:
    api = Namespace('diagnosis_info', description='diagnosis related information')
    diagnosis_info_details = api.model('diagnosis', {
        'result': fields.Integer(description='The result of diagnostics'),
        'normal_probability': fields.Float(description='The probability of normal'),
        'murmur_probability': fields.Float(description='The probability of murmur'),
        'extrasystole_probability': fields.Float(description='The probability of extrasystole'),
        'public_id': fields.String(description='The public id of diagnostics'),
        'checked_on': fields.DateTime(description='The date of diagnostics')
    })


class SubscriptionDto:
    api = Namespace('subscription', description='subscription related operations')
    subscription = api.model('subscription_details', {
        'plan': fields.String(description='Plan of subscription'),
        'stripe_id': fields.String(description='User Stripe ID')
    })


class StatisticsDto:
    api = Namespace('statistics', description='admin panel statistics related operations')
