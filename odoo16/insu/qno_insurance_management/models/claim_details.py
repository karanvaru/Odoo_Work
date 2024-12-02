# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ClaimDetails(models.Model):
    _name = 'insurance.claim.details'
    _inherit = ["mail.thread", 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )
    name_2 = fields.Char(
        string='Name 2',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )
    insurance_id = fields.Many2one(
        'insurance.policy',
        required=True,
        string='Policy',
        help="Confirmed orders can be selected"
    )
    partner_id = fields.Many2one(
        'res.partner',
        # related='insurance_id.partner_id',
        # store=True,
        string='Customer',
        readonly=True
    )
    policy_id = fields.Many2one(
        related='insurance_id.policy_product_id',
        string='Policy Product',
        readonly=True
    )
    employee_id = fields.Many2one(
        related='insurance_id.agent_id',
        string='Agent',
        readonly=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id.id
    )
    amount = fields.Monetary(
        related='insurance_id.sum_assured',
        string='Sum Assured',
        copy=False
    )
    date_claimed = fields.Date(
        string='Date Applied',
        default=fields.Date.context_today,
        copy=False
    )
    claimed_passed_date = fields.Date(
        string='Claim Passed Date',
        copy=False
    )
    file_sub_date = fields.Date(
        string='File Submission Date',
        copy=False
    )
    qry_sub_date = fields.Date(
        string='Query Submission Date',
        copy=False
    )
    invoice_id = fields.Many2one(
        'account.move',
        string='Invoiced',
        readonly=True,
        copy=False
    )
    note_field = fields.Html(
        string='Comment'
    )

    claimed_amount = fields.Float(
        string='Claimed Amount',
        copy=False
    )
    passed_amount = fields.Float(
        string='Passed Amount',
        copy=False
    )

    state = fields.Selection(
        selection=[
            ('new', 'new'),
            ('in_process', 'In Process'),
            ('query', 'Query'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ],
        default='new',
        copy=False,
        tracking=True
    )
    policy_number = fields.Char(
        string="Policy Number",
        related='insurance_id.policy_number'
    )

    def claim_cancel(self):
        self.update({
            'state': 'cancelled'
        })

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'claim.details'
                ) or 'New'
            vals.update({
                'state': 'new',
            })
        return super(ClaimDetails, self).create(vals_list)

    def action_create_bill(self):
        if not self.invoice_id:
            invoice_val = self.env['account.move'].sudo().create({
                'move_type': 'in_invoice',
                'invoice_date': fields.Date.context_today(self),
                'partner_id': self.partner_id.id,
                'invoice_user_id': self.env.user.id,
                'claim_id': self.id,
                'invoice_origin': self.name,
                'invoice_line_ids': [(0, 0, {
                    'name': 'Invoice For Insurance Claim',
                    'quantity': 1,
                    'price_unit': self.amount,
                    'account_id': 41,
                })],
            })
            self.invoice_id = invoice_val

