"""Main entry point
"""
from cornice.validators import DEFAULT_FILTERS
from couchdb.client import Server
from pyramid.config import Configurator
from pyramid.events import NewRequest
from upyun.upyun import UpYun, ED_AUTO


def add_couchdb_to_request(event):
    request = event.request
    settings = request.registry.settings
    db = settings['CouchDB.server'][settings['CouchDB.db_name']]
    event.request.db = db
    event.request.up = settings['UpYun.server']

def main(global_config, **settings):
    config = Configurator(settings=settings)
    db_server = Server(url=settings['CouchDB.url'])
    if settings['CouchDB.db_name'] not in db_server:
        db_server.create(settings['CouchDB.db_name'])
    config.registry.settings['CouchDB.server'] = db_server
    upyun_server = UpYun(settings['upyun.space'], settings['upyun.username'], settings['upyun.password'], timeout=30, endpoint=ED_AUTO)
    config.registry.settings['UpYun.server'] = upyun_server
    config.add_subscriber(add_couchdb_to_request, NewRequest)
    DEFAULT_FILTERS.pop()
    config.include("cornice")
    config.scan("api.views")
    return config.make_wsgi_app()
