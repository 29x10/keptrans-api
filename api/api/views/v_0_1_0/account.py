# coding:utf-8
from api.views.v_0_1_0 import password_manager
from api.views.v_0_1_0.schema.account import AccountSchema
import colander
from cornice.service import Service
from pyramid.security import remember


account = Service(name='account', path='/v0.1.0/account', description="account",
                  cors_origins=('https://admin.keptrans.com', 'https://keptrans.com'))


@account.post()
def add_user(request):
    username = request.json_body['username']
    password = request.json_body['password']
    db = request.db
    new_user = db['users'].insert({'username': username,
                                   'password': password_manager.encode(password),
                                   'groups': ['buyer'],
                                   'token': remember(request, username)})
    return {}


user_login_error = {
    'usernameNone': u'用户名不能为空',
    'passwordNone': u'密码不能为空'
}


def validate_login(request):
    try:
        schema = AccountSchema()
        user_passed = schema.deserialize(request.json_body['session'])
        db = request.db
        user = db['users'].find_one({'username': user_passed['username']})
        if user:
            if password_manager.check(user['password'], user_passed['password']):
                token = remember(request, user['username'])
                user['token'] = token
                request.validated['user'] = user
            else:
                request.errors.add('body', 'password', u'密码错误')
        else:
            request.errors.add('body', 'username', u'用户不存在')
    except colander.Invalid, e:
        errors = e.asdict()
        for error_name, error_value in errors.items():
            if error_value == 'Required':
                request.errors.add('body', error_name, user_login_error[error_name + 'None'])
            else:
                request.errors.add('body', error_name, u'发生未知错误')
    except Exception as e:
        request.errors.add('body', 'unhandled_error', e.message)


@account.put(validators=(validate_login,))
def user_login(request):
    user = request.validated['user']
    db = request.db
    db['users'].find_and_modify(query={'username': user['username']}, update={'$set': {'token': user['token']}})
    return {'session': {'token': user['token'],
            'username': user['username']}}

