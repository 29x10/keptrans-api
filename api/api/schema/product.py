#coding:utf-8
import colander


class ProductSchema(colander.MappingSchema):
    brand = colander.SchemaNode(colander.String())
    pattern = colander.SchemaNode(colander.String())
    price = colander.SchemaNode(colander.Integer())
    deadline = colander.SchemaNode(colander.Integer())
    sku = colander.SchemaNode(colander.Integer())
    unit = colander.SchemaNode(colander.String())
    productMaster = colander.SchemaNode(colander.String())