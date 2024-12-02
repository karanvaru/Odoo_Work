from odoo import fields, models


class CallsCrmSettings(models.Model):
    _inherit = 'asterisk_common.settings'

    auto_create_leads_from_calls = fields.Boolean(
        string='Create Leads on Incoming Calls')
    auto_create_leads_missed_calls_only = fields.Boolean(
        string='Only for Missed Calls', default=True)
    auto_create_leads_sales_person = fields.Many2one('res.users',
        string='Salesperson')

    def reformat_numbers(self):
        super(CallsCrmSettings, self).reformat_numbers()
        for rec in self.env['crm.lead'].with_context(
                no_clear_cache=True).search([]):
            if rec.phone:
                rec.phone = rec._format_number(
                    rec.phone, format_type='international')
        self.env['crm.lead'].pool.clear_caches()
