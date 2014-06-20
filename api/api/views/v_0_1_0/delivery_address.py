# coding:utf-8
from api.views.v_0_1_0.schema.delivery_address import DeliveryAddressSchema
from bson.dbref import DBRef
from bson.objectid import ObjectId
import colander
from cornice.service import Service


delivery_addresses = Service(name='delivery_addresses', path='/v0.1.0/deliveryAddresses',
                             description='delivery_addresses',
                             cors_origins=('https://admin.keptrans.com', 'https://keptrans.com'))


def validate_delivery_address(request):
    try:
        schema = DeliveryAddressSchema()
        new_address = schema.deserialize(request.json_body['deliveryAddress'])
        request.validated['delivery_address'] = new_address
    except colander.Invalid, e:
        errors = e.asdict()
        for error_name, error_value in errors.items():
            if error_value == 'Required':
                request.errors.add('body', error_name, u'送货地址不能为空')
            else:
                request.errors.add('body', error_name, u'发生未知错误')
    except Exception as e:
        request.errors.add('body', 'unhandled_error', e.message)


@delivery_addresses.post(content_type="application/json", validators=(validate_delivery_address,))
def add_address(request):
    new_address = request.validated['delivery_address']
    new_address['client'] = DBRef('users', ObjectId(new_address['client']))
    db = request.db
    db['delivery_address'].insert(new_address)

    new_address['client'] = str(new_address['client'].id)
    new_address['id'] = str(new_address['_id'])
    del new_address['_id']
    return {'deliveryAddress': new_address}