#coding:utf-8
import json
from formencode import validators
from formencode.api import Invalid
from formencode.schema import Schema
from mapping.products import Product

from cornice import Service
from webob import exc
from webob.response import Response



products = Service(name='products', path='/products', description="products", cors_origins=('*',))


class _401(exc.HTTPError):
    def __init__(self, msg=u'Unauthorized'):
        body = {'status': 401, 'message': msg}
        Response.__init__(self, json.dumps(body))
        self.status = 401
        self.content_type = 'application/json'


class _400(exc.HTTPError):
    def __init__(self, msg=u'Bad request, missing data.'):
        body = {'status': 400, 'message': msg}
        Response.__init__(self, json.dumps(body))
        self.status = 400
        self.content_type = 'application/json'


class ProductSchema(Schema):
     brand = validators.String(not_empty=True)
     category = validators.String(not_empty=True)
     spec = validators.String(not_empty=True)
     price = validators.Int(not_empty=True)


def validate_product(request):
    try:
        schema = ProductSchema()
        new_product = schema.to_python(request.json_body['product'])
        request.validated['product'] = new_product
    except Invalid, errors:
        for error_name, error_value in errors.unpack_errors().items():
            request.errors.add('body', error_name, error_value)

@products.post(content_type="application/json", validators=validate_product)
def add_product(request):
    product = request.validated['product']
    new_product = Product(product)
    db = request.db
    new_product.store(db)
    return {'product': {}}

