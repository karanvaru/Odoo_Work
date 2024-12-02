from odoo import models, fields, api


class MII_Content_required(models.Model):
    _name = 'crm.mii.content'
    _description = 'MII Content Required'

    name = fields.Char(
        "Name",
        required=True
    )
    active = fields.Boolean(
        "Active",
        default=True
    )


class crm_capture_type(models.Model):
    _name = 'crm.capture.type'
    _description = 'BID Capture Type'

    name = fields.Char(
        "Name",
        required=True
    )
    active = fields.Boolean(
        "Active",
        default=True
    )


class CRM_Category_type(models.Model):
    _name = 'crm.category.type'
    _description = 'Bid Category Type'

    name = fields.Char(
        "Name",
        required=True
    )
    active = fields.Boolean(
        "Active",
        default=True
    )


class CRM_Product_Category(models.Model):
    _name = 'crm.product.category'
    _description = 'CRM Product Category'
    _order = "sequence"

    sequence = fields.Integer(
        "Sequence"
    )
    name = fields.Char(
        "Name",
        required=True
    )
    active = fields.Boolean(
        "Active",
        default=True
    )

class CRM_BID_to_RA(models.Model):
    _name = 'crm.bid.ra'
    _description = 'CRM BID TO RA Enabled'
    _order = 'sequence'

    sequence = fields.Integer(
        "Sequence"
    )
    name = fields.Char(
        "Name",
        required=True
    )
    active = fields.Boolean(
        "Active",
        default=True
    )

class CRM_BID_Type(models.Model):
    _name = 'crm.bid.type'
    _description = 'CRM BID Type'
    _order = 'sequence'

    sequence = fields.Integer(
        "Sequence"
    )
    name = fields.Char(
        "Name",
        required=True
    )
    active = fields.Boolean(
        "Active",
        default=True
    )