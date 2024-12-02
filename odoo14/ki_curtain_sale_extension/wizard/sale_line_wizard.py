from odoo import api, fields, models, _


class SaleLineWizard(models.Model):
    _name = "sale.line.wizard"

    line_ids = fields.One2many('curtain.line', 'sale_line', string="Curtain Line")
    sale_order_line_id = fields.Many2one('sale.order.line')

    def action_confirm(self):
        active_id = self._context.get('active_id')
        wizard_line = self.env['sale.order.line'].browse(active_id)
        wizard_line.curtain_line_id = [(6, 0, self.line_ids.ids)]
        curtain_line_total = 0.0
        for line in self.line_ids:
            curtain_line_multiplication = line.height * line.width
            curtain_line_total += curtain_line_multiplication
        wizard_line.write({'price_unit': curtain_line_total})

    @api.model
    def default_get(self, fields):
        res = super(SaleLineWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        wizard_line = self.env['sale.order.line'].browse(active_id)
        print("///////////////////////////wizard_line/////////////////////",wizard_line)
        res['line_ids'] = wizard_line.curtain_line_id
        return res


class CurtainLine(models.Model):
    _name = "curtain.line"

    sale_line = fields.Many2one('sale.line.wizard')
    height = fields.Float(string="Height", store=True)
    width = fields.Float(string="Width", store=True)
