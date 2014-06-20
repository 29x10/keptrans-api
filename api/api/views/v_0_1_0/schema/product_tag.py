import colander


class ProductTagSchema(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())