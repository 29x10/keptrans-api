# coding:utf-8
import json
from cryptacular.bcrypt import BCRYPTPasswordManager
from webob import exc
from webob.response import Response


def convert_datetime(model_object):
    model_object['pubDate'] = model_object['pubDate'].strftime("%Y-%m-%d %H:%M:%S")
    model_object['modifiedDate'] = model_object['modifiedDate'].strftime("%Y-%m-%d %H:%M:%S")
    return model_object


def convert_price(model_object):
    model_object['price'] = "{0:.2f}".format(model_object['price'] / 100.0)
    return model_object


class UnauthorizedView(exc.HTTPError):
    def __init__(self, msg=u'Unauthorized'):
        body = {'status': 401, 'message': msg}
        Response.__init__(self, json.dumps(body))
        self.status = 401
        self.content_type = 'application/json'


class BadRequestView(exc.HTTPError):
    def __init__(self, msg=u'Bad request, missing data.'):
        body = {'status': 400, 'message': msg}
        Response.__init__(self, json.dumps(body))
        self.status = 400
        self.content_type = 'application/json'


class NotFoundView(exc.HTTPError):
    def __init__(self, msg=u'Not Found.'):
        body = {'status': 404, 'message': msg}
        Response.__init__(self, json.dumps(body))
        self.status = 404
        self.content_type = 'application/json'


password_manager = BCRYPTPasswordManager()