from couchdb.design import ViewDefinition
from couchdb.mapping import TextField, IntegerField, ListField, Document, DictField, Mapping


class Product(Document):
    db_type = TextField(default='product')
    brand = TextField()
    category = TextField()
    spec = TextField()
    cover = TextField()
    desc = TextField()
    rows = ListField(DictField(Mapping.build(
        spec=TextField(),
        price=IntegerField(),
        image=TextField()
    )))

    def __init__(self, product):
        super(Product, self).__init__()
        self.brand = product['brand']
        self.category = product['category']
        self.spec = product['spec']
        self.cover = product['cover']
        self.desc = product['desc']
        self.rows = product['rows']

    product_list = ViewDefinition('products', 'product_list', '''
        function (doc) {
            if (doc.db_type == 'product') {
                emit(doc._id, doc);
            }
        }''')
