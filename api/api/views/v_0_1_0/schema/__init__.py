#coding:utf-8
import decimal
import colander


class MoneyInt(colander.Number):

    def __init__(self):
        self.quant = decimal.Decimal('.01')
        self.rounding = decimal.ROUND_HALF_UP

    def num(self, val):
        result = int((decimal.Decimal(str(val)).quantize(self.quant, self.rounding))*100)
        return result