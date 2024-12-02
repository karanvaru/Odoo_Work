from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    recurring_interval = fields.Integer(
        default=1,
        string="Invoice Every",
        readonly=False,
        required=True,
    )
    recurring_rule_type = fields.Selection(
        [
            ("daily", "Day(s)"),
            ("weekly", "Week(s)"),
            ("monthly", "Month(s)"),
            ("monthlylastday", "Month(s) last day"),
            ("quarterly", "Quarter(s)"),
            ("semesterly", "Semester(s)"),
            ("yearly", "Year(s)"),
        ],
        default="monthly",
        string="Recurrence",
        required=True
    )
    date_start = fields.Date(
        string="Date Start",
        required=True,
    )
    contract_count = fields.Integer(
        string='Contract Count',
        compute='_compute_contract_count'
    )

    def _compute_contract_count(self):
        for res in self:
            contract_count = self.env['contract.contract'].search_count([('sales_order_id', '=', res.id)])
            res.contract_count = contract_count

    @api.model
    def action_confirm(self):
        rec = super(SaleOrder, self).action_confirm
        for contract_create_id in self:
            value_list = []
            contract_create = {}
            for rec_line in contract_create_id.order_line:
                contract_line_create = {}
                contract_line_create.update({
                    'product_id': rec_line.product_id.id,
                    'name': rec_line.name,
                    'quantity': rec_line.product_uom_qty,
                    'uom_id': rec_line.product_uom.id,
                    'price_unit': rec_line.price_unit,
                    'discount': rec_line.discount,
                    'location': rec_line.location,
                })
                value_list.append(contract_line_create)
            contract_create.update({
                'name': contract_create_id.name,
                'partner_id': contract_create_id.partner_invoice_id.id or False,
                'recurring_interval': contract_create_id.recurring_interval,
                'recurring_rule_type': contract_create_id.recurring_rule_type,
                'date_start': contract_create_id.date_start,
                'payment_term_id': contract_create_id.payment_term_id.id,
                'sales_order_id': contract_create_id.id,
                'fiscal_position_id': contract_create_id.fiscal_position_id.id,
            })


            resss = self.env['contract.contract'].create(contract_create)
            for i in resss:
                for j in value_list:
                    i.contract_line_fixed_ids = [(0, 0, j)]

            # print("==============================", contract_create)
        return rec

    def action_contract(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contract',
            'res_model': 'contract.contract',
            'domain': [('sales_order_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

