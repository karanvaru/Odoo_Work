from odoo import models, fields


class order_return_config(models.Model):
    _name = "order.return.config"
    _description = "Order Return Configuration"
    _order = 'id desc'

    instance_id = fields.Many2one('amazon.instance.ept', string='Instance')
    location_id = fields.Many2one('stock.location', string='Location', required=False,
                                  domain=[('usage', 'in', ['internal', 'inventory'])])
    condition = fields.Selection([
        ('SELLABLE', 'SELLABLE'), ('DAMAGED', 'DAMAGED'),
        ('CUSTOMER_DAMAGED', 'CUSTOMER DAMAGED'), ('DEFECTIVE', 'DEFECTIVE'),
        ('CARRIER_DAMAGED', 'CARRIER DAMAGED'), ('EXPIRED', 'EXPIRED'),
        ('CUSTOMERDAMAGED', 'CUSTOMERDAMAGED')],
        string='Condition', required=True, copy=False)
    is_reimbursed = fields.Boolean("Is Reimbursed ?", default=False, help="Is Reimbursed?",
                                   copy=False)

    _sql_constraints = [
        ('order_return_unique_constraint', 'unique(condition)', "Condition must be unique.")
    ]
