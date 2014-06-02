#coding:utf-8
import colander

__author__ = 'binlei'





class Tag(colander.SequenceSchema):
    id = colander.SchemaNode(colander.String())

class ProductMasterSchema(colander.MappingSchema):
    brand = colander.SchemaNode(colander.String())
    category = colander.SchemaNode(colander.String)
    cover = colander.SchemaNode(colander.String())
    desc = colander.SchemaNode(colander.String())
    tags = Tag()

cstruct = {u'category': u'1', u'brand': u'1', u'tags': [u'53895d780b2f42bd464cec0f', u'53895d790b2f42bd464cec10', u'53895d790b2f42bd464cec11', u'53896cae0b2f42bd464cec12'], u'cover': u'http://keptrans.b0.upaiyun.com/products/a3bbf92c6a864d3d9a809cc0b431dbc1.jpeg', u'desc': u'adfasdfasdf'}
schema = ProductMasterSchema()
result = schema.deserialize(cstruct)
print result



