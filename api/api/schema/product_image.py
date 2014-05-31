#coding:utf-8
import colander


class ProductImageSchema(colander.MappingSchema):
    url = colander.SchemaNode(colander.String())
    productMaster = colander.SchemaNode(colander.String())