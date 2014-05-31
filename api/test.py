#coding:utf-8
import colander

__author__ = 'binlei'





class Tag(colander.SequenceSchema):
    id = colander.SchemaNode(colander.String())

class ProductMasterSchema(colander.MappingSchema):
    tags = Tag()


schema = ProductMasterSchema()
result = schema.deserialize({'tags': 123})
print result



