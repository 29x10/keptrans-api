# coding:utf-8
import colander


class DeliveryAddressSchema(colander.MappingSchema):
    address = colander.SchemaNode(colander.String())
    client = colander.SchemaNode(colander.String())