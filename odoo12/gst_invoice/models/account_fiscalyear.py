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

import odoo
from odoo import api, fields, models, _
from odoo.osv import expression
import time
from dateutil.relativedelta import relativedelta

class AccountFiscalyear(models.Model):
    _name = "account.fiscalyear"
    _description = "Fiscal Year"

    name = fields.Char('Fiscal Year', required=True)
    code = fields.Char('Code', size=6, required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    date_start = fields.Date('Start Date', required=True, default=lambda * a: time.strftime('%Y-%m-01 %H:59:%S'))
    date_stop = fields.Date('End Date', required=True, default=lambda * a: time.strftime('%Y-12-31 %H:59:%S'))
    period_ids = fields.One2many('account.period', 'fiscalyear_id', 'Periods')

    _order = "date_start, id"

    @api.multi
    def _check_duration(self):
        if self.date_stop < self.date_start:
            return False
        return True

    _constraints = [
        (_check_duration, 'Error!\nThe start date of a fiscal year must precede its end date.', ['date_start','date_stop'])
    ]

    @api.multi
    def create_period3(self):
        return self.create_period(3)

    @api.multi
    def create_period1(self):
        return self.create_period(1)

    @api.multi
    def create_period(self, interval=1):
        period_obj = self.env['account.period']
        for fy in self:
            ds = fy.date_start
            period_obj.create({
                    'name':  "%s %s" % (_('Opening Period'), ds.strftime('%Y')),
                    'code': ds.strftime('00/%Y'),
                    'date_start': ds,
                    'date_stop': ds,
                    'special': True,
                    'fiscalyear_id': fy.id,
                })
            while ds < fy.date_stop:
                de = ds + relativedelta(months=interval, days=-1)

                if de > fy.date_stop:
                    de = fy.date_stop

                period_obj.create({
                    'name': ds.strftime('%b-%Y'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds,
                    'date_stop': de,
                    'fiscalyear_id': fy.id,
                })
                ds = ds + relativedelta(months=interval)
        return True

    @api.model
    def find(self, dt=None, exception=True):
        res = self.finds(dt, exception)
        return res and res[0] or False

    @api.model
    def finds(self, dt=None, exception=True):
        context = self._context
        if context is None: context = {}
        if not dt:
            dt = fields.date.context_today(self)
        args = [('date_start', '<=' ,dt), ('date_stop', '>=', dt)]
        if context.get('company_id', False):
            company_id = context['company_id']
        else:
            company_id = self.env['res.users'].browse(self._uid).company_id.id
        args.append(('company_id', '=', company_id))
        objs = self.search(args)
        if not objs:
            if exception:
                model, action_id = self.env['ir.model.data'].get_object_reference('account', 'action_account_fiscalyear')
                msg = _('There is no period defined for this date: %s.\nPlease go to Configuration/Periods and configure a fiscal year.') % dt
                raise odoo.exceptions.RedirectWarning(msg, action_id, _('Go to the configuration panel'))
            else:
                return []
        ids = objs.ids
        return ids

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
