from odoo import api, fields, models, _


class BOESmartButton(models.Model):
    _inherit = 'account.invoice'

    boe_submit_count_id = fields.Integer('cash request count', compute="boe_settlement_count")

    @api.multi
    def boe_settlement_count(self):
        count_values = self.env['boe.settlement'].search_count([('boe_submit_id', '=', self.id)])
        self.boe_submit_count_id = count_values

    @api.multi
    def action_to_boe_submit(self, vals):
        boe_submit_details = self.env['boe.settlement']

        vals = {
            'boe_submit_id': self.id,
            'partner_id': self.partner_id.id,
            'number': self.number,
            'bill_date': self.date_invoice,
            'amount_untaxed': self.amount_untaxed,
            'amount_tax': self.amount_tax,
            'amount_total': self.amount_total,
        }
        new_val = boe_submit_details.create(vals)
        # self.state = 'bill_submit'
        return new_val

    @api.multi
    def action_boe_settlement_button(self):
        self.ensure_one()
        return {
            'name': 'BOE Settlement',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'boe.settlement',
            'domain': [('boe_submit_id', '=', self.id)],
        }


class BOESubmitButton(models.Model):
    _inherit = "boe.settlement"

    boe_submit_id = fields.Many2one('account.invoice', string="BOE Submit")



