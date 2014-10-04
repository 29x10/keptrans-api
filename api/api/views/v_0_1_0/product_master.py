# coding:utf-8
from datetime import datetime
import logging
from api.views.v_0_1_0 import convert_datetime, convert_price, get_id_from_ref, PRODUCT_COLLECTION, \
    PRODUCT_IMAGE_COLLECTION, PRODUCT_MASTER_COLLECTION
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





def generate_master_item(db, _master):
    #标签ID列表
    _master['tags'] = map(get_id_from_ref, _master['tags'])

    #产品ID列表
    product_id_list = []
    for _product in db[PRODUCT_COLLECTION].find({'productMaster.$id': _master['_id']}):
        product_id_list.append(str(_product['_id']))
    _master['products'] = product_id_list

    #产品图片列表
    image_id_list = []
    for _image in db[PRODUCT_IMAGE_COLLECTION].find({'productMaster.$id': _master['_id']}):
        image_id_list.append(str(_image['_id']))
    _master['images'] = image_id_list

    #ID变换
    _master['id'] = str(_master['_id'])
    del _master['_id']

    #变更时间
    _master = convert_datetime(_master)
    return _master


@product_masters.get()
def get_all_product_master(request):
    db = request.db
    master_list = []

    if request.GET:
        master_id_list = [ObjectId(master_id) for _, master_id in request.GET.items()]
        for _master in db[PRODUCT_MASTER_COLLECTION].find({'_id': {'$in': master_id_list}}):
            #转变master
            _master = generate_master_item(db, _master)

            #加入列表
            master_list.append(_master)
    else:
        for _master in db[PRODUCT_MASTER_COLLECTION].find():
            #转变master
            _master = generate_master_item(db, _master)

            #加入列表
            master_list.append(_master)
    return {'productMasters': master_list}


@product_master.get()
def get_product_master(request):
    master_id = ObjectId(request.matchdict['master_id'])
    db = request.db

    _master = db[PRODUCT_MASTER_COLLECTION].find_one({'_id': master_id})

    #master转换
    _master = generate_master_item(db, _master)

    return {'productMaster': _master}


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
