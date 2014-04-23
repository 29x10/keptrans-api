from couchdb.mapping import TextField, IntegerField, ListField, Document


class Product(Document):
    db_type = TextField(default='product')
    brand = TextField()
    spec =  TextField()
    category = TextField()
    price = IntegerField()


    def __init__(self, product):
        super(Product, self).__init__()
        self.brand = product['brand']
        self.spec = product['spec']
        self.category = product['category']
        self.price = product['price']
