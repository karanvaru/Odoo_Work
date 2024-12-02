from odoo import api, fields, models, _


class CustomerVendorGroup(models.Model):
    _name = "customer.vendor.group"
    _description = "Customer Vendor Group"

    name = fields.Char(
        string="Name",
        required=True
    )
    code = fields.Char(
        string="Code",
    )
