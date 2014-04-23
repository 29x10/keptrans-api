"""Main entry point
"""
from couchdb.client import Server
from pyramid.config import Configurator
from pyramid.events import NewRequest


def add_couchdb_to_request(event):
    request = event.request
    settings = request.registry.settings
    db = settings['CouchDB.server'][settings['CouchDB.db_name']]
    event.request.db = db

def main(global_config, **settings):
    config = Configurator(settings=settings)
    db_server = Server(url=settings['CouchDB.url'])
    if settings['CouchDB.db_name'] not in db_server:
        db_server.create(settings['CouchDB.db_name'])
    config.registry.settings['CouchDB.server'] = db_server
    config.add_subscriber(add_couchdb_to_request, NewRequest)
    config.include("cornice")
    config.scan("api.views")
    return config.make_wsgi_app()
