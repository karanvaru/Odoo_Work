from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class FreightOrderLine(models.Model):
    _name = 'freight.bill.entry'
    _description = 'Freight Bill Entries from Receipts and Deliveries'

    order_id = fields.Many2one('freight.order')
    product_id = fields.Many2one('product.product', domain=[('detailed_type', '=', 'product')], string='Goods '
                                                                                                       'Description')
    billing_type = fields.Selection([('weight', 'Weight'),
                                     ('volume', 'Volume')], string="Billing On")
    price = fields.Float('Unit Price')
    total_price = fields.Float('Total Price')
    volume = fields.Float('Volume')
    weight = fields.Float('Weight')
    gross = fields.Float('Gross Weight Kg(s)')
    net = fields.Float('Net Weight Kg(s)')
    hs_code = fields.Char('HS Code')
    quantity = fields.Char('Quantity in Pieces')
    unit_price = fields.Float('Unit Price')
    cif_local_value = fields.Float('CIF Local Value')
    cif_foreign_value = fields.Float('CIF Foreign Value')
    type_currency = fields.Many2one('res.currency', 'Currency Type', default=2)
    country_origin = fields.Many2one('res.country', 'Origin')
    currency_rate = fields.Float('Rate')
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id')
    purchase_order = fields.Many2one('purchase.order', 'PO')
    location_dest_id = fields.Many2one('stock.location', 'Warehouse')

    # company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    def _compute_currency_id(self):
        main_company = self.env['res.company']._get_main_company()
        for template in self:
            template.currency_id = main_company.currency_id.id or template.company_id.sudo().currency_id.id

    @api.onchange("cif_foreign_value", "currency_rate")
    def calculate_local_value(self):
        self.cif_local_value = self.cif_foreign_value * self.currency_rate
