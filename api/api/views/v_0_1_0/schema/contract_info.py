# coding:utf-8
import colander


class ContractInfoSchema(colander.MappingSchema):
    company = colander.SchemaNode(colander.String())
    address = colander.SchemaNode(colander.String(), missing="")
    bank = colander.SchemaNode(colander.String(), missing="")
    bankAccount = colander.SchemaNode(colander.Integer(), missing="")
    tax = colander.SchemaNode(colander.Integer(), missing="")

    legalPerson = colander.SchemaNode(colander.String(), missing="")
    phone = colander.SchemaNode(colander.String(), missing="")
    fax = colander.SchemaNode(colander.String(), missing="")

    client = colander.SchemaNode(colander.String())