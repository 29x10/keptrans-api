#coding:utf-8
from cgi import FieldStorage
import json
from uuid import uuid4
from schema.product_image import ProductImageSchema
from schema.product_tag import ProductTagSchema
from bson.dbref import DBRef
from schema.product import ProductSchema
from bson.objectid import ObjectId
import colander

from cornice import Service
from webob import exc
from webob.response import Response

products_masters = Service(name='product_master', path='/productMasters', description="products master",
                          cors_origins=('*',))
products_tags = Service(name='products_tags', path='/productTags', description="products master tag",
                        cors_origins=('*',))
products = Service(name='products', path='/products', description="products", cors_origins=('*',))
product = Service(name='product', path='/products/{product_id}', description="product detail", cors_origins=('*',))
image = Service(name='image', path='/image', description="upload image", cors_origins=('*',))
product_images = Service(name='product_image', path='/productImages', description='product image', cors_origins=('*',))



@image.post()
def upload_image(request):
    up = request.up
    file = request.params.get('file')
    file_ext = '.' + file.type.split('/')[-1]
    image_url = '/products/' + uuid4().hex + file_ext
    up.put(image_url, file.file, checksum=True)
    return {'image': 'http://keptrans.b0.upaiyun.com' + image_url}


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



product_master_error = {
    'brandNone': u'品牌不能为空',
    'categoryNone': u'所属类目不能为空',
    'coverNone': u'封面地址不能为空',
    'descNone': u'描述不能为空',
    'tags': u'标签不能为空'
}


def validate_product_master(request):
    try:
        schema = ProductSchema()
        new_product = schema.deserialize(request.json_body['product'])
        request.validated['productMaster'] = new_product
    except colander.Invalid as e:
        errors = e.asdict()
        for error_name, error_value in errors.items():
            if error_value == 'Required':
                request.errors.add('body', error_name, product_master_error[error_name + 'None'])
            else:
                request.errors.add('body', error_name, u'发生未知错误')
    except Exception as e:
        request.errors.add('body', 'unhandled_error', e.message)



@products_masters.post(content_type="application/json", validators=(validate_product_master,))
def add_product_master(request):
    new_product_master = request.validated['productMaster']
    for i in range(len(new_product_master['tags'])):
        new_product_master['tags'][i] = DBRef('product_tag', ObjectId(new_product_master['tags'][i]))
    db = request.db
    db['product_master'].insert(new_product_master)
    for i in range(len(new_product_master['tags'])):
        new_product_master['tags'][i] = str(new_product_master['tags'][i].id)
    new_product_master['id'] = str(new_product_master['_id'])
    del new_product_master['_id']
    return {'productMaster': new_product_master}


def validate_product_tag(request):
    try:
        schema = ProductTagSchema()
        new_tag = schema.deserialize(request.json_body['productTag'])
        request.validated['tag'] = new_tag
    except colander.Invalid as e:
        errors = e.asdict()
        for error_name, error_value in errors.items():
            if error_value == 'Required':
                request.errors.add('body', error_name, u"标签名不能为空")
            else:
                request.errors.add('body', error_name, u'发生未知错误')
    except Exception as e:
        request.errors.add('body', 'unhandled_error', e.message)


@products_tags.post(content_type="application/json", validators=(validate_product_tag,))
def add_tag(request):
    new_tag = request.validated['tag']
    db = request.db
    result = db['product_tag'].find_and_modify(query={'name': new_tag['name']}, upsert=True, update={'$setOnInsert': {'name': new_tag['name']}}, new=True)
    result['id'] = str(result['_id'])
    del result['_id']
    return {'productTag': result}


product_error = {
    'brandNone': u'品牌不能为空',
    'patternNone': u'型号不能为空',
    'priceNone': u'价格不能为空',
    'priceNotNumber': u'价格必须是数字，单位是分',
    'deadlineNone': u'货期不能为空',
    'deadlineNotNumber': u'货期必须是数字，单位是天',
    'skuNone': u'库存数不能为空',
    'skuNotNumber': u'库存数量不能为空',
    'unitNone': u'库存单位不能为空',
    'productMaster': u'所属系列不能为空'
}


def validate_product(request):
    try:
        schema = ProductSchema()
        new_product = schema.deserialize(request.json_body['product'])
        request.validated['product'] = new_product
    except colander.Invalid as e:
        errors = e.asdict()
        for error_name, error_value in errors.items():
            if error_value == 'Required':
                request.errors.add('body', error_name, product_error[error_name + 'None'])
            elif 'not a number' in error_value:
                request.errors.add('body', error_name, product_error[error_name + 'NotNumber'])
            else:
                request.errors.add('body', error_name, u'发生未知错误')
    except Exception as e:
        request.errors.add('body', 'unhandled_error', e.message)


@products.post(content_type="application/json", validators=(validate_product,))
def add_product(request):
    new_product = request.validated['product']
    db = request.db
    new_product['productMaster'] = DBRef('product_master', ObjectId(new_product['productMaster']))
    db['product'].insert(new_product)
    new_product['productMaster'] = str(new_product['productMaster'].id)
    new_product['id'] = str(new_product['_id'])
    del new_product['_id']
    return {'product': new_product}


@product.put(content_type="application/json", validators=(validate_product,))
def update_product(request):
    product_id = ObjectId(request.matchdict['product_id'])
    product = request.validated['product']
    db = request.db
    result = db['product'].find_and_modify(query={"_id": product_id}, update=product, new=True)
    result['id'] = str(result['_id'])
    del result['_id']
    return {'product': result}

@product.delete()
def delete_product(request):
    product_id = request.matchdict['product_id']
    product_oid = ObjectId(product_id)
    db = request.db
    db['product'].remove({"_id": product_oid})
    return {'product': {'id': product_id}}


product_image_error = {
    'urlNone': u'封面地址不能为空',
    'productMasterNone': u'所属系列不能为空'
}

def validate_product_image(request):
    try:
        schema = ProductImageSchema()
        new_image = schema.deserialize(request.json_body['productImage'])
        request.validated['image'] = new_image
    except colander.Invalid, e:
        errors = e.asdict()
        for error_name, error_value in errors.items():
            if error_value == 'Required':
                request.errors.add('body', error_name, product_image_error[error_name + 'None'])
            else:
                request.errors.add('body', error_name, u'发生未知错误')
    except Exception as e:
        request.errors.add('body', 'unhandled_error', e.message)


@product_images.post()
def add_image(request):
    new_image = request.json_body['productImage']
    new_image['productMaster'] = DBRef('product_master', ObjectId(new_image['productMaster']))
    db = request.db
    db['product_image'].insert(new_image)
    new_image['productMaster'] = str(new_image['productMaster'].id)
    new_image['id'] = str(new_image['_id'])
    del new_image['_id']
    return {'productImage': new_image}
