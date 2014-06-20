# coding:utf-8
import logging
from api.views.v_0_1_0.schema.contract_info import ContractInfoSchema
from bson.dbref import DBRef
from bson.objectid import ObjectId
import colander
from cornice.service import Service


contract_infos = Service(name='contract_infos', path='/v0.1.0/contractInfos', description='contract_infos',
                         cors_origins=('https://admin.keptrans.com', 'https://keptrans.com'))

logger = logging.getLogger(__name__)


def validate_contract_info(request):
    try:
        schema = ContractInfoSchema()
        new_contract_info = schema.deserialize(request.json_body['contractInfo'])
        request.validated['contract_info'] = new_contract_info
    except colander.Invalid, e:
        errors = e.asdict()
        for error_name, error_value in errors.items():
            if error_value == 'Required':
                request.errors.add('body', error_name, u'所属客户不能为空')
            else:
                request.errors.add('body', error_name, u'发生未知错误')
    except Exception as e:
        request.errors.add('body', 'unhandled_error', e.message)


@contract_infos.post(content_type="application/json", validators=(validate_contract_info,))
def add_contract_info(request):
    new_contract_info = request.validated['contract_info']
    new_contract_info['client'] = DBRef('users', ObjectId(new_contract_info['client']))
    db = request.db
    db['contract_info'].insert(new_contract_info)

    new_contract_info['client'] = str(new_contract_info['client'].id)
    new_contract_info['id'] = str(new_contract_info['_id'])
    del new_contract_info['_id']
    return {'contractInfo': new_contract_info}