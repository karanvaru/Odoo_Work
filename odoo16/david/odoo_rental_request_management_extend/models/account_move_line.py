from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    is_custom_rental_invoice = fields.Boolean(
        string='Is Rental Invoice',
        readonly=True,
    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    custom_start_datetime = fields.Datetime(
        string="Rental Start Date",
    )
    custom_end_datetime = fields.Datetime(
        string='Rental End Date'
    )
