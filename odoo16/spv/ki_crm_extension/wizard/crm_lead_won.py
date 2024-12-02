from odoo import api, fields, models


class CrmLeadWon(models.TransientModel):
    _name = 'crm.lead.won.wizard'
    _description = 'Crm Lead Won wizard'

    def _get_sale_domain(self):
        print("=============================")
        active_id = self._context.get('active_id', False)
        print("============================active_id=",active_id)

        return [('opportunity_id', '=', active_id), ('state', 'in', ['draft', 'sent'])]

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order",
        required=True,
        domain=_get_sale_domain,

    )

    def action_submit(self):
        self.sale_order_id.action_confirm
        active_model = self._context.get('active_model', False)
        active_id = self._context.get('active_id', False)
        if active_model == 'crm.lead':
            crm_id = self.env[active_model].browse(active_id)
            crm_id.action_set_won_rainbowman()
