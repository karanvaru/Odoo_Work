from odoo.exceptions import UserError
from odoo import api, fields, models, _
from dateutil.relativedelta import *
from odoo.exceptions import UserError, ValidationError


class EmployeeProfileUpdateRequest(models.Model):
    _inherit = "hr.employee"

    is_agent = fields.Boolean(
        string="Is Agent",
    )
    commission_taxes_id = fields.Many2one(
        "account.tax",
        string="Commission Taxes",
    )
    direct_commission = fields.Float(
        string="Direct Commission",
    )

    @api.model
    def _get_commission_users(self, company=False):
        if not self:
            return {}
        if not company:
            company = self.company_id

        query = """
               WITH RECURSIVE parents AS (
                SELECT id, parent_id, 0 as depth
                FROM hr_employee
                WHERE id = %s
               UNION
                SELECT op.id, op.parent_id, depth + 1
                FROM hr_employee op
                JOIN parents p ON op.id = p.parent_id
               )
               SELECT *
               FROM parents ;
           """
        self._cr.execute(query % (self.id))
        res = self._cr.dictfetchall()

        company_config = {
            c.level_no: c.percentage
            for c in company.commission_level_ids
        }
        commission_users = {}
        for r in res:
            if r['depth'] in company_config:
                commission_users[self.sudo().browse(r['id'])] = {
                    'level_no': r['depth'],
                    'percentage': company_config[r['depth']],
                    'commission_user_id': r['id']
                }

        commission_users.update({self: {
            'level_no': 0,
            'percentage': self.direct_commission,
            'commission_user_id': self.id
        }})
        return commission_users

    @api.model
    def _prepare_commission_history_vals(self, commission_date=False, company=False):
        if not company:
            company = self.company_id
        if not commission_date:
            commission_date = fields.Date.today()

        date_start = commission_date.replace(day=1)
        date_end = date_start + relativedelta(day=31)
        values = {
            'date_start': date_start,
            'date_end': date_end,
            'commission_user_id': self.id,
            'company_id': company.id,
        }
        return values

    def _compute_commission_amount_count(self):
        jobcost = self.env['commission.history.line'].search([
            ('commission_user_id', '=', self.name)
        ])
        amount = 0.0
        for rec in jobcost:
            amount += rec.commission_amount
        for project in self:
            project.commission_amount_count = amount

    commission_amount_count = fields.Integer(
        compute='_compute_commission_amount_count'
    )
    commission_rule_count = fields.Integer(
        compute='_compute_commission_rules_count'
    )
    def _compute_commission_rules_count(self):
#         res = self.env['commission.rule'].search_count(
#                 [('employee_id', '=', self.id)])
        self.commission_rule_count = 0

    def action_commission_rule(self):
        act = self.env.ref('reddot_commission.action_commission_rule')
        act_read = act.read([])[0]
        act_read['domain'] = [('employee_id', '=', self.id)]
        return act_read

    def action_commission_history_line(self):
        act = self.env.ref('ki_agent_commission.action_commission_history_line')
        act_read = act.read([])[0]
        act_read['domain'] = [('commission_user_id', '=', self.name)]
        act_read['context'] = {'search_default_group_by_commission_type': True, }
        return act_read

    @api.model
    def _get_commission_history(self, commission_date=False, company=False):
        if not company:
            company = self.company_id
        if not commission_date:
            commission_date = fields.Date.today()

        domain = [
            ('commission_user_id', '=', self.id),
            ('date_start', '<=', commission_date),
            ('date_end', '>=', commission_date),
            # ('state', 'in', ('new', 'invoiced')),
            ('state', '=', 'new'),
            ('company_id', '=', company.id),
        ]
        sheet = self.env['commission.history'].sudo().search(domain)
        if not sheet:
            values = self._prepare_commission_history_vals(
                commission_date, company
            )
            sheet = self.env['commission.history'].sudo().create(values)
        return sheet

    def get_commission_amount(self, payslip):
        commission_sheet = self.env['commission.history'].sudo().search([
            ('payslip_id', '=', False),
            ('state', '=', 'confirm'),
            ('date_start', '<', payslip.date_from),
            ('commission_user_id', '=', self.id)
        ])
        total_commission = sum(commision.total_amount for commision in commission_sheet)
        commission_sheet.write({
            'payslip_id': payslip.id
        })
        return total_commission


class AccountMove(models.Model):
    _inherit = "account.move"

    commission_sheet_id = fields.Many2one(
        'commission.history',
        string="Commission Sheet",
        copy=False,
        readonly=True
    )
# 
#     def button_cancel(self):
#         super_res = super(AccountMove, self).button_cancel()
#         source_orders = self.env['sale.order'].search([('invoice_ids', '=', self.id)])
#         for commission in source_orders:
#             if commission:
#                 self.env['commission.history.line'].search([
#                     ('commission_type', 'in', ('direct', 'level', 'product', 'department_commission')),
#                     ('sale_id', '=', commission.id),
#                     ('commission_history_id.state', 'not in', ('invoiced', 'paid'))
#                 ]).unlink()
#         return super_res
