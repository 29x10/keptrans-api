# coding:utf-8
import decimal
import logging
from api.views.v_0_1_0 import convert_price
from api.views.v_0_1_0.schema.order import OrderSchema
from bson.dbref import DBRef
from bson.objectid import ObjectId
import colander
from cornice.service import Service

orders = Service(name='orders', path='/v0.1.0/orders', description='orders',
                 cors_origins=('https://admin.keptrans.com', 'https://keptrans.com'))

logger = logging.getLogger(__name__)

order_error = {

}


def validate_order(request):
    try:
        schema = OrderSchema()
        new_order = schema.deserialize(request.json_body['order'])
        _price = decimal.Decimal(100 - new_order['discount'])*decimal.Decimal(new_order['origin'])/decimal.Decimal(100 - new_order['tax'])
        new_order['serverPrice'] = int(_price.quantize(decimal.Decimal('1.'), decimal.ROUND_HALF_UP))
        new_order['serverTotalPrice'] = new_order['serverPrice']*new_order['amount']
        request.validated['order'] = new_order
    except colander.Invalid as e:
        errors = e.asdict()
        for error_name, error_value in errors.items():
            if error_value == 'Required':
                request.errors.add('body', error_name, order_error[error_name + 'None'])
            elif 'not a number' in error_value:
                request.errors.add('body', error_name, order_error[error_name + 'NotNumber'])
            else:
                request.errors.add('body', error_name, u'发生未知错误')
    except Exception as e:
        logger.error('validate order failed: ' + e.message)
        request.errors.add('body', 'unhandled_error', e.message)


@orders.post(content_type="application/json", validators=(validate_order,))
def add_order(request):
    new_order = request.validated['order']
    new_order['product'] = DBRef('product', ObjectId(new_order['product']))
    new_order['orderMaster'] = DBRef('order_master', ObjectId(new_order['orderMaster']))
    db = request.db
    db['order'].insert(new_order)
    new_order['product'] = str(new_order['product'].id)
    new_order['orderMaster'] = str(new_order['orderMaster'].id)
    new_order['id'] = str(new_order['_id'])
    del new_order['_id']
    new_order['serverPrice'] = convert_price(new_order['serverPrice'])
    new_order['serverTotalPrice'] = convert_price(new_order['serverTotalPrice'])
    return {'order': new_order}

