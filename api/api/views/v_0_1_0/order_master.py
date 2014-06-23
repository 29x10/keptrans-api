# coding:utf-8
from datetime import datetime
import logging
from api.views.v_0_1_0 import BadRequestView, convert_datetime, convert_price
from api.views.v_0_1_0.schema.order_master import OrderMasterSchema
from bson.dbref import DBRef
from bson.objectid import ObjectId
import colander
from cornice.service import Service

order_masters = Service(name='order_masters', path='/v0.1.0/orderMasters', description='order_masters',
                        cors_origins=('https://admin.keptrans.com', 'https://keptrans.com'))

logger = logging.getLogger(__name__)

order_master_error = {
    'orderStatusNone': u'订单状态不能为空',
    'orderStatusNotNumber': u'订单状态必须为数字',
    'companyNone': u'公司名称不能为空',
    'clientNone': u'客户不能为空',
}


def validate_order_master(request):
    try:
        schema = OrderMasterSchema()
        new_order = schema.deserialize(request.json_body['orderMaster'])
        request.validated['orderMaster'] = new_order
    except colander.Invalid as e:
        errors = e.asdict()
        for error_name, error_value in errors.items():
            if error_value == 'Required':
                request.errors.add('body', error_name, order_master_error[error_name + 'None'])
            elif 'not a number' in error_value:
                request.errors.add('body', error_name, order_master_error[error_name + 'NotNumber'])
            else:
                request.errors.add('body', error_name, u'发生未知错误')
    except Exception as e:
        logger.error('validate orderMaster failed: ' + e.message)
        request.errors.add('body', 'unhandled_error', e.message)

@order_masters.post(content_type="application/json", validators=(validate_order_master,))
def add_order_master(request):
    new_order_master = request.validated['orderMaster']
    if new_order_master['status'] != 1:
        raise BadRequestView(u'订单状态非法')
    new_order_master['client'] = DBRef('users', ObjectId(new_order_master['client']))
    db = request.db
    new_order_master['pubDate'] = new_order_master['modifiedDate'] = datetime.now()
    db['order_master'].insert(new_order_master)
    new_order_master['client'] = str(new_order_master['client'].id)
    new_order_master['id'] = str(new_order_master['_id'])
    del new_order_master['_id']
    new_order_master = convert_datetime(new_order_master)
    new_order_master['total'] = convert_price(new_order_master['total'])
    return {'orderMaster': new_order_master}


@order_masters.get()
def all_order_master(request):
    order_list = []
    client_list = []

    master_list = []

    db = request.db

    for _order_master in db['order_master'].find():
        order_id_list = []
        for _order in db['order'].find({'orderMaster.$id': _order_master['_id']}):
            _order['id'] = str(_order['_id'])
            del _order['_id']
            del _order['orderMaster']
            order_id_list.append(_order['id'])
            _order['origin'] = convert_price(_order['origin'])
            _order['serverPrice'] = convert_price(_order['serverPrice'])
            _order['serverTotalPrice'] = convert_price(_order['serverTotalPrice'])
            _order['product'] = str(_order['product'].id)
            order_list.append(_order)

        _order_master['orders'] = order_id_list

        _order_master = convert_datetime(_order_master)
        _order_master['total'] = convert_price(_order_master['total'])

        _order_master['id'] = str(_order_master['_id'])
        del _order_master['_id']

        _client = db.dereference(_order_master['client'])
        client_list.append({'id': str(_client['_id']), 'mobile': _client['username'], 'name': _client['name']})
        _order_master['client'] = str(_order_master['client'].id)

        master_list.append(_order_master)
    return {'orderMasters': master_list, 'orders': order_list, 'clients': client_list}

