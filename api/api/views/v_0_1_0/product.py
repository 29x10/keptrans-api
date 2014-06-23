# coding:utf-8
from datetime import datetime
import logging
from api.views.v_0_1_0 import convert_datetime, convert_price
from api.views.v_0_1_0.schema.product import ProductSchema
from bson.dbref import DBRef
from bson.objectid import ObjectId
import colander
from cornice.service import Service


products = Service(name='products', path='/v0.1.0/products', description="products",
                   cors_origins=('https://admin.keptrans.com', 'https://keptrans.com'))
product = Service(name='product', path='/v0.1.0/products/{product_id}', description="product detail",
                  cors_origins=('https://admin.keptrans.com', 'https://keptrans.com'))

logger = logging.getLogger(__name__)

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
    'productMasterNone': u'所属系列不能为空'
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
        logger.error('validate product failed: ' + e.message)
        request.errors.add('body', 'unhandled_error', e.message)


@products.post(content_type="application/json", validators=(validate_product,))
def add_product(request):
    new_product = request.validated['product']
    db = request.db
    new_product['productMaster'] = DBRef('product_master', ObjectId(new_product['productMaster']))
    new_product['pubDate'] = new_product['modifiedDate'] = datetime.now()
    db['product'].insert(new_product)
    new_product['productMaster'] = str(new_product['productMaster'].id)
    new_product['id'] = str(new_product['_id'])
    del new_product['_id']
    new_product = convert_datetime(new_product)
    new_product['price'] = convert_price(new_product['price'])
    return {'product': new_product}


@products.get()
def get_all_products(request):
    db = request.db

    product_list = []
    product_master_list = []

    for _product in db['product'].find():
        master_relevant = db.dereference(_product['productMaster'])
        _product['productMaster'] = str(_product['productMaster'].id)
        _product['id'] = str(_product['_id'])
        del _product['_id']
        _product = convert_datetime(_product)
        _product['price'] = convert_price(_product['price'])
        product_list.append(_product)
        del master_relevant['tags']
        master_relevant['id'] = str(master_relevant['_id'])
        del master_relevant['_id']
        master_relevant = convert_datetime(master_relevant)
        product_master_list.append(master_relevant)
    return {'products': product_list, 'productMasters': product_master_list}


@product.put(content_type="application/json", validators=(validate_product,))
def update_product(request):
    product_id = ObjectId(request.matchdict['product_id'])
    new_product = request.validated['product']
    new_product['productMaster'] = DBRef('product_master', ObjectId(new_product['productMaster']))
    db = request.db
    new_product['modifiedDate'] = datetime.now()
    result = db['product'].find_and_modify(query={"_id": product_id}, update={'$set': new_product}, new=True)
    result['productMaster'] = str(result['productMaster'].id)
    result['id'] = str(result['_id'])
    del result['_id']
    result = convert_datetime(result)
    result['price'] = convert_price(result['price'])
    return {'product': result}


@product.delete()
def delete_product(request):
    product_id = request.matchdict['product_id']
    product_oid = ObjectId(product_id)
    db = request.db
    db['product'].remove({"_id": product_oid})
    return {}