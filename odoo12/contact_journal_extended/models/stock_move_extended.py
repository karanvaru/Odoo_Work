from odoo import fields, models, api,_

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    company = fields.Many2one('res.company', string="Company", compute="compute_company", store=True)

    @api.depends('move_id')
    def compute_company(self):
        for rec in self:
            rec.company = rec.move_id.company_id.id