#coding:utf-8
from api.views.v_0_1_0.schema import MoneyInt
import colander




class ProductSchema(colander.MappingSchema):
    brand = colander.SchemaNode(colander.String())
    pattern = colander.SchemaNode(colander.String())
    price = colander.SchemaNode(MoneyInt())
    deadline = colander.SchemaNode(colander.Integer())
    sku = colander.SchemaNode(colander.Integer())
    unit = colander.SchemaNode(colander.String())
    productMaster = colander.SchemaNode(colander.String())