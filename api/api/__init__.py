"""Main entry point
"""
from cornice.validators import DEFAULT_FILTERS
from pymongo.mongo_replica_set_client import MongoReplicaSetClient
from pyramid.config import Configurator
from pyramid.events import NewRequest
from upyun.upyun import UpYun, ED_AUTO


def add_couchdb_to_request(event):
    request = event.request
    settings = request.registry.settings
    event.request.db = settings['mongodb.db']
    event.request.up = settings['UpYun.server']

def main(global_config, **settings):
    config = Configurator(settings=settings)
    client = MongoReplicaSetClient(host=settings['mongodb.host'], replicaSet=settings['mongodb.set'])
    config.registry.settings['mongodb.db'] = client[settings['mongodb.name']]
    upyun_server = UpYun(settings['upyun.space'], settings['upyun.username'], settings['upyun.password'], timeout=30, endpoint=ED_AUTO)
    config.registry.settings['UpYun.server'] = upyun_server
    config.add_subscriber(add_couchdb_to_request, NewRequest)
    DEFAULT_FILTERS.pop()
    config.include("cornice")
    config.scan("api.views")
    return config.make_wsgi_app()
