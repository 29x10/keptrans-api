# coding:utf-8
from api.views.v_0_1_0 import password_manager
from cornice.service import Service
from pyramid.security import remember


clients = Service(name='clients', path='/v0.1.0/clients', description='clients',
                  cors_origins=('https://admin.keptrans.com', 'https://keptrans.com'))


@clients.post(content_type="application/json")
def add_client(request):
    mobile = request.json_body['client']['mobile']
    name = request.json_body['client']['name']
    db = request.db
    new_user = db['users'].insert({'username': mobile,
                                   'name': name,
                                   'orders': [],
                                   'password': password_manager.encode('keptrans'),
                                   'groups': ['buyer'],
                                   'staff': False,
                                   'token': remember(request, mobile)})
    return {'client': {'mobile': mobile, 'name': name, 'id': str(new_user)}}


@clients.get()
def get_all_clients(request):
    db = request.db
    order_list = []
    contract_info_list = []
    delivery_address_list = []

    client_list = []

    for _client in db['users'].find({'staff': False}):
        order_id_list = []
        for _order in _client['orders']:
            #get
            _order = db.dereference(_order)
            #deal with id
            _order['id'] = str(_order['_id'])
            del _order['_id']
            #generate id list
            order_id_list.append(_order['id'])
            #generate list
            order_list.append(_order)

        contract_info_id_list = []
        for _contract_info in db['contract_info'].find({'client.$id': _client['_id']}):
            #deal with id
            _contract_info['id'] = str(_contract_info['_id'])
            del _contract_info['_id']
            del _contract_info['client']
            #generate id list
            contract_info_id_list.append(_contract_info['id'])
            #generate list
            contract_info_list.append(_contract_info)

        delivery_address_id_list = []
        for _address in db['delivery_address'].find({'client.$id': _client['_id']}):
            #deal with id
            _address['id'] = str(_address['_id'])
            del _address['_id']
            del _address['client']
            #generate id list
            delivery_address_id_list.append(_address['id'])
            #generate list
            delivery_address_list.append(_address)

        client_list.append({'id': str(_client['_id']),
                            'mobile': _client['username'],
                            'name': _client['name'],
                            'orders': order_id_list,
                            'contractInfos': contract_info_id_list,
                            'deliveryAddresses': delivery_address_id_list})
    return {'clients': client_list, 'orders': order_list, 'contractInfos': contract_info_list,
            'deliveryAddresses': delivery_address_list}




