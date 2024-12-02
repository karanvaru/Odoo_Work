from odoo import api, fields, models, _


class CustomerNewField(models.Model):
    _inherit = 'res.partner'

    short_code = fields.Char(string='Short Code', required=True)

    contact_child_ids = fields.One2many(
        'res.partner',
        'parent_id',
        string='Contact',
        domain=[('type', '=', 'contact')]
    )

    delivery_child_ids = fields.One2many(
        'res.partner',
        'parent_id',
        string='Delivery Address',
        domain=[('type', '=', 'delivery')]
    )

    def name_get(self):
        # result = super(CustomerNewField, self).name_get()
        res = []
        for partner in self:
            res.append((partner.id, partner.name))
        # result = res
        return res
