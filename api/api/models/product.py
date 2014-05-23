# class Tag(Document):
#     name = StringField()
#
# class Images(Document):
#     id = ObjectIdField()
#     url = URLField()
#
# class Product(Document):
#     brand = StringField()
#     price = IntField()
#     deadline = IntField()
#     unit = StringField()
#     pattern = StringField()
#     sku = StringField()
#
# class ProductSerial(Document):
#     brand = StringField()
#     tags = ListField(ReferenceField(Tag))
#     cover = URLField()
#     images = ListField(EmbeddedDocumentField(Images))
#     category = StringField()
# desc = StringField()
#     products = ListField(ReferenceField(Product))

