# coding:utf-8
import colander


class Order(colander.SequenceSchema):
    id = colander.SchemaNode(colander.String())


class OrderMasterSchema(colander.MappingSchema):
    orderStatus = colander.SchemaNode(colander.Integer())

    company = colander.SchemaNode(colander.String())
    address = colander.SchemaNode(colander.String())
    bank = colander.SchemaNode(colander.String())
    bankAccount = colander.SchemaNode(colander.String())
    tax = colander.SchemaNode(colander.String())

    legalPerson = colander.SchemaNode(colander.String())
    phone = colander.SchemaNode(colander.String())
    fax = colander.SchemaNode(colander.String())

    deliveryAddress = colander.SchemaNode(colander.String())

    orders = Order()
    client = colander.SchemaNode(colander.String())