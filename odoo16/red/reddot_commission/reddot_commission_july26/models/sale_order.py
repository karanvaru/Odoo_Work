from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
import datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    agent_id = fields.Many2one(
        'hr.employee',
        string="Agent employee",
        required=False,
        domain=[("is_agent", "=", True)]
    )

    is_create_commission = fields.Boolean(
        string="Create Commission?",
        default=True,
        copy=False,
    )

    commission_sheet_id = fields.Many2one(
        'commission.history',
        string="Commission Sheet",
        readonly=True,
        copy=False,
    )
    payment_status = fields.Selection(
        [('not_paid', 'Not Paid'), ('partial_paid', 'Partial Paid'), ('fully_paid', 'Full Paid'),
         ('nothing', 'Invoice Not Created')],
        string="Payment Status",
        compute="_compute_payment_status",
        copy=False,
        store=True,
        readonly=True,
        default="not_paid"
    )
    fully_paid_date = fields.Date(
        string="Fully Paid Date",
        compute="_compute_payment_status",
        copy=False,
        store=True,
        readonly=True,
    )

    @api.depends('invoice_ids.payment_state', 'invoice_ids.amount_residual')
    def _compute_payment_status(self):
        for rec in self:
            if rec.invoice_ids:
                total_paid_amt = 0
                for lines in rec.invoice_ids:
                    total_paid_amt += (lines.amount_total - lines.amount_residual)

                if total_paid_amt >= rec.amount_total:
                    rec.payment_status = 'fully_paid'
                    rec.fully_paid_date = fields.Date.today()
                #                     self.action_generate_sheet()
                # rec.fully_paid_date = lines.invoice_date
                elif total_paid_amt < rec.amount_total:
                    rec.payment_status = 'partial_paid'
                else:
                    rec.payment_status = 'not_paid'
            else:
                rec.payment_status = 'nothing'

