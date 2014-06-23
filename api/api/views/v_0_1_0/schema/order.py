# coding:utf-8
from api.views.v_0_1_0.schema import MoneyInt
import colander


class OrderSchema(colander.MappingSchema):

    origin = colander.SchemaNode(MoneyInt())
    discount = colander.SchemaNode(colander.Integer(), validator=colander.Range(0, 99))
    tax = colander.SchemaNode(colander.Integer(), validator=colander.Range(0))

    amount = colander.SchemaNode(colander.Integer(), validator=colander.Range(1))

    product = colander.SchemaNode(colander.String())
    orderMaster = colander.SchemaNode(colander.String())