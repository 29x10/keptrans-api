#coding:utf-8
from cgi import FieldStorage
import json
from uuid import uuid4
from schema.product import ProductSchema
import colander
from mapping.products import Product

from cornice import Service
from webob import exc
from webob.response import Response
from couchdb.json import encode as couchdb_json_encode


products = Service(name='products', path='/products', description="products", cors_origins=('*',))
product = Service(name='product', path='/products/{product_id}', description="product detail", cors_origins=('*',))
image = Service(name='image', path='/image', description="upload image", cors_origins=('*',))


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


def convert_to_ember_data_array(couch_data, name):
    payload = {name: []}
    for item in couch_data['rows']:
        item[u'value'][u'id'] = item[u'value'][u'_id']
        del item[u'value'][u'_id']
        payload[name].append(item[u'value'])
    return payload

def convert_to_ember_data_single(couch_data, name):
    payload = {name: {}}
    if couch_data[u'rows']:
        couch_data[u'rows'][u'value'][u'id'] = couch_data[u'rows'][u'value'][u'_id']
        del couch_data[u'rows'][u'value'][u'_id']
        payload[name] = couch_data[u'rows'][u'value']
    return payload


product_add_error = {
    'brandNone': u'你忘了填写品牌名称',
    'categoryNone': u'类别很重要，补上吧',
    'specNone': u'每个产品的型号都不一样，不能落下',
    'priceNone': u'必须填写价格哦，赚钱就靠它了',
    'priceNotNumber': u'价格必须是数字，单位是分',
    'descNone': u'描述随便写点什么把',
    'coverNone': u'封面是脸面'
}


def validate_product(request):
    try:
        schema = ProductSchema()
        new_product = schema.deserialize(request.json_body['product'])
        request.validated['product'] = new_product
    except colander.Invalid, e:
        errors = e.asdict()
        for error_name, error_value in errors.items():
            if error_value == 'Required':
                request.errors.add('body', error_name, product_add_error[error_name + 'None'])
            elif 'not a number' in error_value:
                request.errors.add('body', error_name, product_add_error[error_name + 'NotNumber'])


@products.post(content_type="application/json", validators=validate_product)
def add_product(request):
    product = request.validated['product']
    new_product = Product(product)
    db = request.db
    result = new_product.store(db)
    product['id'] = result.id
    return {'product': product}

@products.get()
def get_products(request):
    db = request.db
    result = db.resource('_design', 'products', '_view', 'product_list').get_json()[2]
    return convert_to_ember_data_array(result, 'products')


@image.post()
def upload_image(request):
    up = request.up
    for file_type, file_wrapper in request.params.items():
        if isinstance(file_wrapper, FieldStorage):
            file_ext = '.' + file_wrapper.type.split('/')[-1]
            image_url = '/products/' + uuid4().hex + file_ext
            up.put(image_url, file_wrapper.file, checksum=True)
            return {'image': image_url}
    return {'error': True}


@product.get()
def get_product(request):
    product_id = request.matchdict['product_id']
    db = request.db
    result = db.resource('_design', 'products', '_view', 'product_list').get_json(key=couchdb_json_encode(product_id))[2]
    return convert_to_ember_data_single(result, 'product')