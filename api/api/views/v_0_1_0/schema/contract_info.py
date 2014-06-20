# coding:utf-8
import colander


class ContractInfoSchema(colander.MappingSchema):
    company = colander.SchemaNode(colander.String(), missing="")
    address = colander.SchemaNode(colander.String(), missing="")
    bank = colander.SchemaNode(colander.String(), missing="")
    bankAccount = colander.SchemaNode(colander.String(), missing="")
    tax = colander.SchemaNode(colander.String(), missing="")

    legalPerson = colander.SchemaNode(colander.String(), missing="")
    phone = colander.SchemaNode(colander.String(), missing="")
    fax = colander.SchemaNode(colander.String(), missing="")

    client = colander.SchemaNode(colander.String())