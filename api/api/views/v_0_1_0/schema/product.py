#coding:utf-8
import decimal
import colander


class MoneyInt(colander.Number):

    def __init__(self):
        self.quant = decimal.Decimal('.01')
        self.rounding = decimal.ROUND_UP

    def num(self, val):
        result = int((decimal.Decimal(str(val)).quantize(self.quant, self.rounding))*100)
        return result

class ProductSchema(colander.MappingSchema):
    brand = colander.SchemaNode(colander.String())
    pattern = colander.SchemaNode(colander.String())
    price = colander.SchemaNode(MoneyInt())
    deadline = colander.SchemaNode(colander.Integer())
    sku = colander.SchemaNode(colander.Integer())
    unit = colander.SchemaNode(colander.String())
    productMaster = colander.SchemaNode(colander.String())