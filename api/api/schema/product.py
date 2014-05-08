import colander


class ProductSchema(colander.MappingSchema):
    brand = colander.SchemaNode(colander.String())
    category = colander.SchemaNode(colander.String())
    spec = colander.SchemaNode(colander.String())
    price = colander.SchemaNode(colander.Int())
    desc = colander.SchemaNode(colander.String())
    cover = colander.SchemaNode(colander.String())