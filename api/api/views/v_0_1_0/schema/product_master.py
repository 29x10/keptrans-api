#coding:utf-8
import colander


class Tag(colander.SequenceSchema):
    id = colander.SchemaNode(colander.String())


class ProductMasterSchema(colander.MappingSchema):
    brand = colander.SchemaNode(colander.String())
    category = colander.SchemaNode(colander.String())
    cover = colander.SchemaNode(colander.String())
    desc = colander.SchemaNode(colander.String())
    tags = Tag()



