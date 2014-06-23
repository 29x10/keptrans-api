# coding:utf-8
from api.views.v_0_1_0.schema import MoneyInt
import colander


class OrderMasterSchema(colander.MappingSchema):
    status = colander.SchemaNode(colander.Integer())
    total = colander.SchemaNode(MoneyInt())
    memo = colander.SchemaNode(colander.String(), missing="")

    company = colander.SchemaNode(colander.String())

    address = colander.SchemaNode(colander.String(), missing="")
    bank = colander.SchemaNode(colander.String(), missing="")
    bankAccount = colander.SchemaNode(colander.String(), missing="")
    tax = colander.SchemaNode(colander.String(), missing="")

    legalPerson = colander.SchemaNode(colander.String(), missing="")
    phone = colander.SchemaNode(colander.String(), missing="")
    fax = colander.SchemaNode(colander.String(), missing="")

    deliveryAddress = colander.SchemaNode(colander.String(), missing="")

    client = colander.SchemaNode(colander.String())