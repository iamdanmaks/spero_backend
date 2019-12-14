from flask import request
from flask_restplus import Resource

from ..util.dto import SubscriptionDto
from ..service.subscription_helper import enter_subscribction, \
     cancel_subscription
from ..util.decorator import token_required

from flask.ext.babel import gettext


api = SubscriptionDto.api
_subscription = SubscriptionDto.subscription


@api.route('/')
class Subscription(Resource):
    @api.response(200, 'Subscription was entered.')
    @api.doc('suscribe for a plan')
    @api.expect(_subscription, validate=True)
    def post(self):
        data = request.json
        return enter_subscribction(request.headers.get('Authorization'), data)

    @api.response(200, 'Subscription was canceled.')
    @api.doc('cancel subscription')
    def delete(self):
        return cancel_subscription(request.headers.get('Authorization'))
