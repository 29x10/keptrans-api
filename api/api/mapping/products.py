from couchdb.design import ViewDefinition
from couchdb.mapping import TextField, IntegerField, ListField, Document


class Product(Document):
    db_type = TextField(default='product')
    brand = TextField()
    spec = TextField()
    category = TextField()
    price = IntegerField()
    desc = TextField()
    cover = TextField()

    def __init__(self, product):
        super(Product, self).__init__()
        self.brand = product['brand']
        self.spec = product['spec']
        self.category = product['category']
        self.price = product['price']
        self.desc = product['desc']
        self.cover = product['cover']

    product_list = ViewDefinition('products', 'product_list', '''
        function (doc) {
            if (doc.db_type == 'product') {
                emit(doc._id, doc);
            }
        }''')
