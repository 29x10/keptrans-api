# coding:utf-8
from datetime import datetime
import logging
from api.views.v_0_1_0 import convert_datetime, convert_price
from api.views.v_0_1_0.schema.product_master import ProductMasterSchema
from bson.dbref import DBRef
from bson.objectid import ObjectId
import colander
from cornice.service import Service


product_masters = Service(name='product_masters', path='/v0.1.0/productMasters', description="products master",
                          cors_origins=('https://admin.keptrans.com', 'https://keptrans.com'))
product_master = Service(name='product_master', path='/v0.1.0/productMasters/{master_id}', description="product master",
                         cors_origins=('https://admin.keptrans.com', 'https://keptrans.com'))

logger = logging.getLogger(__name__)


product_master_error = {
    'brandNone': u'品牌不能为空',
    'categoryNone': u'所属类目不能为空',
    'coverNone': u'封面地址不能为空',
    'descNone': u'描述不能为空',
    'tagsNone': u'标签不能为空'
}




def validate_product_master(request):
    try:
        schema = ProductMasterSchema()
        new_product = schema.deserialize(request.json_body['productMaster'])
        request.validated['productMaster'] = new_product
    except colander.Invalid as e:
        errors = e.asdict()
        for error_name, error_value in errors.items():
            if error_value == 'Required':
                request.errors.add('body', error_name, product_master_error[error_name + 'None'])
            else:
                request.errors.add('body', error_name, u'发生未知错误')
    except Exception as e:
        logger.error('validate productMaster failed: ' + e.message)
        request.errors.add('body', 'unhandled_error', e.message)


@product_masters.post(content_type="application/json", validators=(validate_product_master,))
def add_product_master(request):
    new_product_master = request.validated['productMaster']
    for i in range(len(new_product_master['tags'])):
        new_product_master['tags'][i] = DBRef('product_tag', ObjectId(new_product_master['tags'][i]))
    db = request.db
    new_product_master['pubDate'] = new_product_master['modifiedDate'] = datetime.now()
    db['product_master'].insert(new_product_master)
    for i in range(len(new_product_master['tags'])):
        new_product_master['tags'][i] = str(new_product_master['tags'][i].id)
    new_product_master['id'] = str(new_product_master['_id'])
    del new_product_master['_id']
    new_product_master = convert_datetime(new_product_master)
    return {'productMaster': new_product_master}


@product_masters.get()
def get_all_product_master(request):
    db = request.db
    tags_list = []
    products_list = []
    images_list = []

    master_list = []

    for master in db['product_master'].find():
        tag_id_list = []
        for tag in master['tags']:
            tag = db.dereference(tag)
            tag['id'] = str(tag['_id'])
            del tag['_id']
            tag_id_list.append(tag['id'])
            tags_list.append(tag)
        master['tags'] = tag_id_list
        product_id_list = []
        for _product in db['product'].find({'productMaster.$id': master['_id']}):
            _product['id'] = str(_product['_id'])
            del _product['_id']
            del _product['productMaster']
            product_id_list.append(_product['id'])
            _product = convert_datetime(_product)
            _product['price'] = convert_price(_product['price'])
            products_list.append(_product)
        master['products'] = product_id_list
        image_id_list = []
        for img in db['product_image'].find({'productMaster.$id': master['_id']}):
            img['id'] = str(img['_id'])
            del img['_id']
            del img['productMaster']
            image_id_list.append(img['id'])
            images_list.append(img)
        master['images'] = image_id_list
        master['id'] = str(master['_id'])
        del master['_id']
        master = convert_datetime(master)
        master_list.append(master)
    return {'productMasters': master_list, 'productTags': tags_list, 'productImages': images_list,
            'products': products_list}


@product_master.put(content_type="application/json", validators=(validate_product_master,))
def update_product_master(request):
    master_id = ObjectId(request.matchdict['master_id'])
    new_product_master = request.validated['productMaster']
    for i in range(len(new_product_master['tags'])):
        new_product_master['tags'][i] = DBRef('product_tag', ObjectId(new_product_master['tags'][i]))
    db = request.db
    new_product_master['modifiedDate'] = datetime.now()
    result = db['product_master'].find_and_modify(query={"_id": master_id}, update={'$set': new_product_master},
                                                  new=True)
    for i in range(len(result['tags'])):
        result['tags'][i] = str(result['tags'][i].id)

    result['products'] = []
    result['images'] = []
    for _product in db['product'].find({'productMaster.$id': result['_id']}):
        result['products'].append(str(_product['_id']))
    for _image in db['product_image'].find({'productMaster.$id': result['_id']}):
        result['images'].append(str(_image['_id']))

    result['id'] = str(result['_id'])
    del result['_id']
    result = convert_datetime(result)
    return {'productMaster': result}


@product_master.delete()
def delete_product_master(request):
    master_id = request.matchdict['master_id']
    master_oid = ObjectId(master_id)
    db = request.db
    for pro in db['product'].find({'productMaster.$id': master_oid}):
        db['product'].remove({'_id': pro['_id']})
    for img in db['product_image'].find({'productMaster.$id': master_oid}):
        db['product_image'].remove({'_id': img['_id']})
    db['product_master'].remove({'_id': master_oid})
    return {}
