from odoo import api, fields, models, _


class PartnerChildrenDetails(models.Model):
    _name = 'partner.children.details'
    _description = "Partner Children Details"

    child_name = fields.Char(
        string="Name",
    )
    child_age = fields.Float(
        string="Age",
    )
    child_living = fields.Boolean(
        string="Is Living?",
        copy=False
    )
    child_edu = fields.Char(
        string="Educational Years",
    )
    child_marital = fields.Selection([
        ('SINGLE', 'Single'),
        ('STEADY', 'Steady'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
    ], string='Marital Status')

    partner_children_partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
    )
