#coding:utf-8
from api.mapping.products import Product
from couchdb.client import Server

__author__ = 'binlei'

server = Server("http://admin:qweasdzxc@localhost:5984/")
db = server['keptrans']
# result = db.view('products/product_list')
result = db.resource('_design', 'products', '_view', 'product_list').get_json()[2]['rows']

for k in result:
    print k['value']

