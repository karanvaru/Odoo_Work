#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models, _
from odoo.osv import expression
from datetime import timedelta
from odoo.exceptions import UserError, RedirectWarning

class AccountPeriod(models.Model):
    _name = "account.period"
    _description = "Account period"

    @api.depends('date_stop')
    def _get_special(self):
        from_dt = fields.Date.today() - timedelta(days=30)
        for obj in self:
            if obj.date_stop and obj.date_stop < from_dt:
                obj.special = True

    name = fields.Char('Period Name', required=True)
    code = fields.Char('Code', size=12)
    special = fields.Boolean('Opening/Closing Period',help="These periods can overlap.", compute='_get_special')
    date_start = fields.Date('Start of Period', required=True)
    date_stop = fields.Date('End of Period', required=True)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Fiscal Year', required=True)
    company_id = fields.Many2one('res.company', string='Company',
        related='fiscalyear_id.company_id', store=True, readonly=True)

    _order = "date_start, special desc"

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)', 'The name of the period must be unique per company!'),
    ]

    @api.multi
    def _check_duration(self):
        if self.date_stop < self.date_start:
            return False
        return True

    @api.multi
    def _check_year_limit(self):
        for obj_period in self:
            if obj_period.special:
                continue
            if obj_period.fiscalyear_id.date_stop < obj_period.date_stop or \
               obj_period.fiscalyear_id.date_stop < obj_period.date_start or \
               obj_period.fiscalyear_id.date_start > obj_period.date_start or \
               obj_period.fiscalyear_id.date_start > obj_period.date_stop:
                return False
            pidObjs = self.search(
                [('date_stop','>=',obj_period.date_start),
                ('date_start','<=',obj_period.date_stop),
                ('id','<>',obj_period.id)
                ]
            )
            for period in pidObjs:
                pastMonth = fields.Date.today() - timedelta(days=30)
                dateStop = period.date_stop
                if dateStop > pastMonth and dateStop < fields.Date.today():
                    continue
                if period.fiscalyear_id.company_id.id==obj_period.fiscalyear_id.company_id.id:
                    return False
        return True

    _constraints = [
        (_check_duration, 'Error!\nThe duration of the Period(s) is/are invalid.', ['date_stop']),
        (_check_year_limit, 'Error!\nThe period is invalid. Either some periods are overlapping or the period\'s dates are not matching the scope of the fiscal year.', ['date_stop'])
    ]

    @api.returns('self')
    def next(self, period, step):
        ids = self.search([('date_start','>',period.date_start)])
        if len(ids)>=step:
            return ids[step-1]
        return False

    @api.returns('self')
    def find(self, dt=None):
        context = self._context
        if context is None: context = {}
        if not dt:
            dt = fields.date.context_today(self)
        args = [('date_start', '<=' ,dt), ('date_stop', '>=', dt)]
        if context.get('company_id', False):
            args.append(('company_id', '=', context['company_id']))
        else:
            company_id = self.env['res.users'].browse(self._uid).company_id.id
            args.append(('company_id', '=', company_id))
        result = []
        if context.get('account_period_prefer_normal', True):
            # look for non-special periods first, and fallback to all if no result is found
            result = self.search(args + [('special', '=', False)])
        if not result:
            result = self.search(args)
        if not result:
            model, action_id = self.env['ir.model.data'].get_object_reference('account', 'action_account_period')
            msg = _('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.') % dt
            raise odoo.exceptions.RedirectWarning(msg, action_id, _('Go to the configuration panel'))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            domain = [('code', operator, name), ('name', operator, name)]
        else:
            domain = ['|', ('code', operator, name), ('name', operator, name)]
        objs = self.search(expression.AND([domain, args]), limit=limit)
        return objs.name_get()

    @api.multi
    def write(self, vals):
        if 'company_id' in vals:
            move_lines = self.env['account.move.line'].search([('period_id', 'in', self.ids)])
            if move_lines:
                raise UserError(_('Warning!'), _('This journal already contains items for this period, therefore you cannot modify its company field.'))
        return super(AccountPeriod, self).write(vals)

    @api.model
    def build_ctx_periods(self, period_from_id, period_to_id):
        if period_from_id == period_to_id:
            return [period_from_id]
        period_from = self.browse(period_from_id)
        period_date_start = period_from.date_start
        company1_id = period_from.company_id.id
        period_to = self.browse(period_to_id)
        period_date_stop = period_to.date_stop
        company2_id = period_to.company_id.id
        if company1_id != company2_id:
            raise UserError(_('Error!'), _('You should choose the periods that belong to the same company.'))
        if period_date_start > period_date_stop:
            raise UserError(_('Error!'), _('Start period should precede then end period.'))

        if period_from.special:
            return self.search([('date_start', '>=', period_date_start), ('date_stop', '<=', period_date_stop)])
        return self.search([('date_start', '>=', period_date_start), ('date_stop', '<=', period_date_stop), ('special', '=', False)])
