# coding:utf-8
import logging
from api.views.v_0_1_0.schema.product_image import ProductImageSchema
from bson.dbref import DBRef
from bson.objectid import ObjectId
import colander
from cornice.service import Service


product_images = Service(name='product_images', path='/v0.1.0/productImages', description='product images',
                         cors_origins=('https://admin.keptrans.com', 'https://keptrans.com'))
product_image = Service(name='product_image', path='/v0.1.0/productImages/{image_id}', description='product image',
                        cors_origins=('https://admin.keptrans.com', 'https://keptrans.com'))


product_image_error = {
    'urlNone': u'封面地址不能为空',
    'productMasterNone': u'所属系列不能为空'
}

logger = logging.getLogger(__name__)


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


@product_images.post(content_type="application/json", validators=(validate_product_image,))
def add_product_image(request):
    new_image = request.validated['image']
    new_image['productMaster'] = DBRef('product_master', ObjectId(new_image['productMaster']))
    db = request.db
    db['product_image'].insert(new_image)
    new_image['productMaster'] = str(new_image['productMaster'].id)
    new_image['id'] = str(new_image['_id'])
    del new_image['_id']
    return {'productImage': new_image}


@product_image.put(content_type="application/json", validators=(validate_product_image,))
def update_product_image(request):
    image_id = ObjectId(request.matchdict['image_id'])
    new_image = request.validated['image']
    new_image['productMaster'] = DBRef('product_master', ObjectId(new_image['productMaster']))
    db = request.db
    result = db['product_image'].find_and_modify(query={"_id": image_id}, update=new_image, new=True)
    result['productMaster'] = str(result['productMaster'].id)
    result['id'] = str(result['_id'])
    del result['_id']
    return {'productImage': result}


@product_image.delete()
def delete_product_image(request):
    image_oid = ObjectId(request.matchdict['image_id'])
    db = request.db
    db['product_image'].remove({"_id": image_oid})
    return {}
