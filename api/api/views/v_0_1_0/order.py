# coding:utf-8
from cornice.service import Service


orders = Service(name='orders', path='/v0.1.0/orders/{order_id}', description='orders',
                 cors_origins=('https://admin.keptrans.com', 'https://keptrans.com'))