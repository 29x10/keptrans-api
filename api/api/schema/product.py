import colander


class Product(colander.MappingSchema):
    spec = colander.SchemaNode(colander.String())
    price = colander.SchemaNode(colander.Integer())
    amount = colander.SchemaNode(colander.Integer())
    dtime = colander.SchemaNode(colander.Integer())
    image = colander.SchemaNode(colander.String())


class Products(colander.SequenceSchema):
    product = Product()


class ProductSchema(colander.MappingSchema):
    brand = colander.SchemaNode(colander.String())
    category = colander.SchemaNode(colander.String())
    spec = colander.SchemaNode(colander.String())
    rows = Products()
    cover = colander.SchemaNode(colander.String())
    desc = colander.SchemaNode(colander.String())

