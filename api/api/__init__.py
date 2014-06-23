"""Main entry point
"""
from auth import MozillaTokenLibForHeaderAuthenticationPolicy
from cornice.validators import DEFAULT_FILTERS
from pymongo.mongo_replica_set_client import MongoReplicaSetClient
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import NewRequest
from upyun.upyun import UpYun, ED_AUTO
import hashlib

def add_couchdb_to_request(event):
    request = event.request
    settings = request.registry.settings
    event.request.db = settings['mongodb.db']
    event.request.up = settings['UpYun.server']
    event.request.updebug = settings['UpYun.debug']


def get_user_groups(username, request):
    db = request.db
    user = db['users'].find_one({'username': username})
    if user:
        return user['groups']
    return None

def main(global_config, **settings):
    config = Configurator(settings=settings)
    auth_token = MozillaTokenLibForHeaderAuthenticationPolicy(secret='what_makes_so_secret', hashmod=hashlib.sha256, timeout=86400)
    auth_permission = ACLAuthorizationPolicy()
    config.set_authentication_policy(auth_token)
    config.set_authorization_policy(auth_permission)

    client = MongoReplicaSetClient(host=settings['mongodb.host'], replicaSet=settings['mongodb.set'])
    config.registry.settings['mongodb.db'] = client[settings['mongodb.name']]
    upyun_server = UpYun(settings['upyun.space'], settings['upyun.username'], settings['upyun.password'], timeout=30, endpoint=ED_AUTO)
    config.registry.settings['UpYun.server'] = upyun_server
    config.registry.settings['UpYun.debug'] = settings['upyun.debug']
    config.add_subscriber(add_couchdb_to_request, NewRequest)
    DEFAULT_FILTERS.pop()
    config.include("cornice")
    config.scan("api.views.v_0_1_0")
    return config.make_wsgi_app()
