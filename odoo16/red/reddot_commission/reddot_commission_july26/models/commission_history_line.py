# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class CommissionHistoryLine(models.Model):
    _name = 'commission.history.line'
    _description = "Commission History Lines"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Number",
        readonly=True
    )
    date_commission = fields.Date(
        string="Date",
        # required=True,
        default=fields.Date.today
    )
    move_id = fields.Many2one(
        'account.move',
        string="Journal Entry",
    )
    approval_date = fields.Date(
        string="Approval Date",
        readonly=True,
        # default=fields.Date.today
    )

    commission_user_id = fields.Many2one(
        'hr.employee',
        string="User",
    )
    commission_history_id = fields.Many2one(
        'commission.history',
        string="Sheet",
    )
    sale_order_line_ids = fields.Many2many(
        'sale.order',
        string='Sale Order',
        required=False
    )

    responsible_user_id = fields.Many2one(
        'hr.employee',
        string="Responsible Employee",
    )

    customer_user_id = fields.Many2one(
        'res.partner',
        related="sale_id.partner_id",
        string="Customer"
    )
#     agent_user_id = fields.Many2one(
#         'hr.employee',
#         string="Agent name"
#     )
    percentage = fields.Float(
        string="Percentage(%)",
    )
    base_amount = fields.Float(
        string="Base Amount",
    )
#     sale_order_amount = fields.Float(
#         string="Sale Order Amount",
#     )
    commission_amount = fields.Float(
        string="Amount",
        compute ="_compute_commission_amount",
        store=True
    )
    calculation_types = fields.Selection(
        selection=[
            ('bu_level', 'Bu Level'),
            ('company_level', 'Company Level'),
            ('region_level', 'Region Level'),
            ('bu_group_level', 'Bu Group Level'),
            ('self', 'Self'),
        ],
        string='Calculation Type',
        tracking=1,
    )
    company_id = fields.Many2one(
        'res.company',
        related="commission_history_id.company_id",
        string="Company",
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related="company_id.currency_id",
        string="Currency",
        store=True
    )
#     level_no = fields.Integer(
#         string="Level",
#     )
    invoice_id = fields.Many2one(
        'account.move',
        string="Invoice",
    )
    sale_id = fields.Many2one(
        'sale.order',
        string="Sale",
    )

#     product_id = fields.Many2one(
#         'product.template',
#         string="Product",
#     )

#     is_manual_commission = fields.Boolean(
#         string="Manual",
#         default=False,copy=False
#     )
#     pos_id = fields.Many2one(
#         'pos.order',
#         string="POS",
#     )
    origin = fields.Char(
        string="Source"
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('approve', 'Approved'),
            ('reject', 'Reject'),
            ('invoiced', 'Invoiced')
        ],
        default='draft',
        copy=False
    )
#     special_target_type = fields.Selection(
#         [
#             ('monthly', 'Monthly'),
#             ('date_range', 'Date Range'),
#         ],
#         copy=False
#     )
    business_unit_id = fields.Many2one(
        'business.unit',
        string='Business Unit',
#         required=True
    )
    target_amount = fields.Float(
        string="Target Amount",
    )
    target_achieved_amount = fields.Float(
        string="Target Achieved Amount",
    )
    commission_type = fields.Selection(
        selection=[
            ('gp', 'GP(Gross Profit)'),
            ('customer_invoice', 'Customer Invoice'),
            # ('revenue', 'Revenue'),

        ],
        string='Commission Type',
        tracking=1,
    )
    origin_ref = fields.Reference(string="Origin", selection="_selection_target_model")

    @api.model
    def _selection_target_model(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]


    def view_source(self):
        for rec in self:
            if rec.sale_id:
                act = self.env.ref('sale.action_quotations_with_onboarding')
                act_read = act.read([])[0]
                act_read['domain'] = [('id', '=', self.sale_id.id)]
                return act_read
#             if rec.pos_id:
#                 act = self.env.ref('point_of_sale.action_pos_pos_form')
#                 act_read = act.read([])[0]
#                 act_read['domain'] = [('id', '=', self.pos_id.id)]
#                 return act_read

    def approved(self):
        for rec in self:
            sale_obj = self.env['sale.order'].search([('id', '=', rec.sale_id.id)])
            commission_date1 = [(rec.date_commission - relativedelta(day=1)).strftime('%Y-%m-01'),
            (rec.date_commission + relativedelta(day=31)).strftime('%Y-%m-%d')]
            target_Saleobj = self.env['sale.order'].search([
                ('date_order', '>=', commission_date1[0]),
                ('date_order', '<=', commission_date1[1]),
                ('agent_id', '=', rec.responsible_user_id.id),
                ('payment_status', '=', 'fully_paid'),
                ('target_commission_line_id', '=', False),
                ('state', 'not in', ('draft', 'sent', 'cancel'))
            ])
            specialtarget_Saleobj = self.env['sale.order'].search([('date_order', '>=', commission_date1[0]),
                                                                   ('date_order', '<=', commission_date1[1]),
                                                                   ('agent_id', '=', rec.responsible_user_id.id),
                                                                   ('special_target_commission_line_id', '=', False),
                                                                   ('payment_status', '=', 'fully_paid'),
                                                                   ('state', 'not in', ('draft', 'sent', 'cancel'))])
            target_line1 = self.env['commission.history.line'].search(
                [('commission_type', '=', 'target'), ('sale_order_line_ids', 'in', target_Saleobj.ids)], limit=1)

            specialtargetline2 = self.env['commission.history.line'].search(
                [('commission_type', '=', 'special_commission'), ('sale_order_line_ids', 'in', specialtarget_Saleobj.ids)], limit=1)
            sheet = self.env['commission.history'].search([('id', '=', rec.commission_history_id.id)])
            approval_date = fields.Date.today()
            sale_obj.commission_sheet_id = sheet.id
            rec.write({'state': "approve",
                       'approval_date': approval_date})
            for target in target_Saleobj:
                if target_line1.state == 'approve':
                        target.target_commission_line_id = target_line1.id
            for specialtarget in specialtarget_Saleobj:
                if specialtargetline2.state == 'approve':
                        specialtarget.special_target_commission_line_id = specialtargetline2.id

    def reject(self):
        for rec in self:
            rec.write({'state': "reject",
                       'approval_date': ''})

    @api.depends(
        'base_amount',
        'percentage',
        'currency_id'
    )
    def _compute_commission_amount(self):
        for line in self:
#             if line.is_manual_commission == True:
#                 line.commission_amount = line.commission_amount
#             else:
            line.commission_amount = (line.base_amount * line.percentage) / 100.0

    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
    #     # TDE FIXME: strange
    #     if self._context.get('filter_state'):
    #         domain = domain.copy()
    #         domain.append((('state', 'in', self._context['filter_state'])))
    #     return super()._search(domain, offset, limit, order, access_rights_uid)

    @api.model_create_multi
    def create(self, vals_list):
        seq_obj = self.env['ir.sequence']
        for vals in vals_list:
            vals['name'] = seq_obj.next_by_code('commission.history.line')
        return super(CommissionHistoryLine, self).create(vals_list)

    def name_get(self):
        result = []
        for line in self:
            if line != False:
                name = line.name
                if line._origin.commission_history_id and line._origin.commission_history_id.display_name:
                    name = line._origin.commission_history_id.display_name + '/' + line._origin.name
                result.append((line._origin.id, name))
        return result

    @api.constrains('percentage')
    def _check_percentage(self):
        for rec in self:
#             if rec.percentage > 100.00 or rec.percentage < 0.0:
#                 raise ValidationError("greater then 0.0 and less then 100.0...")

            if rec.percentage < 0.0:
                raise ValidationError("greater then 0.00...")

    def unlink(self):
        for commission in self:
            if commission.state != 'draft':
                raise UserError(
                    _('You cannot delete an commission line which is not draft.')
                )
        return super(CommissionHistoryLine, self).unlink()