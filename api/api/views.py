#coding:utf-8
import ast
from cgi import FieldStorage
import json
from uuid import uuid4
from bson.json_util import dumps, loads

from cornice import Service
from webob import exc
from webob.response import Response

products_master = Service(name='products', path='/productMasters', description="products master", cors_origins=('*',))
products_tags = Service(name='products', path='/product_tags', description="products master tag", cors_origins=('*',))
product = Service(name='product', path='/products/{product_id}', description="product detail", cors_origins=('*',))
image = Service(name='image', path='/image', description="upload image", cors_origins=('*.keptrans.com',))


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
        couch_data[u'rows'][0][u'value'][u'id'] = couch_data[u'rows'][0][u'value'][u'_id']
        del couch_data[u'rows'][0][u'value'][u'_id']
        payload[name] = couch_data[u'rows'][0][u'value']
    return payload


product_add_error = {
    'brandNone': u'你忘了填写品牌名称',
    'categoryNone': u'类别很重要，补上吧',
    'specNone': u'每个产品的型号都不一样，不能落下',
    'priceNone': u'必须填写价格哦，赚钱就靠它了',
    'priceNotNumber': u'价格必须是数字，单位是分',
    'descNone': u'描述随便写点什么把',
    'coverNone': u'封面是脸面',
    'imageNone': u'产品图片不能少',
    'amountNone': u'库存数量不能为空',
    'amountNotNumber': u'库存数量必须为数字',
    'dtimeNone': u'货期不能为空',
    'dtimeNotNumber': u'货期必须为数字，单位是天'
}


# def validate_product(request):
#     try:
#         schema = ProductSchema()
#         new_product = schema.deserialize(request.json_body['product'])
#         request.validated['product'] = new_product
#     except colander.Invalid, e:
#         errors = e.asdict()
#         for error_name, error_value in errors.items():
#             if error_value == 'Required':
#                 if 'rows' in error_name:
#                     index, error_name = error_name.split(".")[1:]
#                     request.errors.add('body', error_name, "#" + index + product_add_error[error_name + 'None'])
#                 else:
#                     request.errors.add('body', error_name, product_add_error[error_name + 'None'])
#             elif 'not a number' in error_value:
#                 if 'rows' in error_name:
#                     index, error_name = error_name.split(".")[1:]
#                     request.errors.add('body', error_name, "#" + index + product_add_error[error_name + 'NotNumber'])


def validate_product_master(request):
    product = request.json_body['productMaster']

@products_master.post(content_type="application/json", validators=validate_product_master)
def add_product(request):
    return {'product': True}


@products_tags.post(content_type="application/json")
def add_tag(request):
    tag = request.json_body['product_tag']
    db = request.db
    result = db['product_tag'].find_and_modify(query={'name': tag['name']}, upsert=True, update={'$setOnInsert': {'name': tag['name']}}, new=True)
    result['id'] = str(result['_id'])
    del result['_id']
    return {'product_tag': result}

# @products.get()
# def get_products(request):
#     db = request.db
#     result = db.resource('_design', 'products', '_view', 'product_list').get_json()[2]
#     return convert_to_ember_data_array(result, 'products')
#
#
# @image.post()
# def upload_image(request):
#     up = request.up
#     for file_type, file_wrapper in request.params.items():
#         if isinstance(file_wrapper, FieldStorage):
#             file_ext = '.' + file_wrapper.type.split('/')[-1]
#             image_url = '/products/' + uuid4().hex + file_ext
#             up.put(image_url, file_wrapper.file, checksum=True)
#             return {'image': image_url}
#     return {'error': True}
#
#
# def product_exists(request):
#     product_id = request.matchdict['product_id']
#     db = request.db
#     result = db.resource('_design', 'products', '_view', 'product_list').get_json(key=couchdb_json_encode(product_id))[2]
#     if not result['rows']:
#         request.errors.add('body', product_id, u'产品不存在')
#         request.errors.status = 404
#     else:
#         request.validated['result'] = result
#
#
# @product.get(validators=product_exists)
# def get_product(request):
#     product = request.validated['result']
#     return convert_to_ember_data_single(product, 'product')
#
#
# @product.put(validators=(product_exists, validate_product))
# def update_product(request):
#     product = request.validated['result']['rows'][0]
#     new_product = request.validated['product']
#     new_product['_rev'] = product['value']['_rev']
#     new_product['db_type'] = 'product'
#     db = request.db
#     result = db.resource(request.matchdict['product_id']).put_json(body=new_product)
#     return {'product': new_product}
#
# @product.delete(validators=(product_exists,))
# def delete_product(request):
#     product = request.validated['result']
#     db = request.db
#     db.resource(request.matchdict['product_id']).delete_json(rev=product['rows'][0]['value']['_rev'])
#     return convert_to_ember_data_single(product, 'product')
#