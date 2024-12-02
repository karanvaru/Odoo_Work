from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    challan_number = fields.Char('Challan Number', track_visibility="always")
    bsr_code = fields.Char('BSR Code', track_visibility="always")
    tds_certificate_number = fields.Char('TDS Certificate No', track_visibility="always")
    tds_certificate = fields.Binary('TDS Certificate', track_visibility="always")
    challan_amount = fields.Char('Challan Amount', track_visibility="always")
    account_tds_paid_month_id = fields.Many2one('account.tds.paid.month', 'TDS Paid Month', track_visibility="onchange")
    account_tds_paid_year_id = fields.Many2one('account.tds.paid.year', 'TDS Paid Year', track_visibility="onchange")
    gst_returns_year_id = fields.Many2one('account.gst.returns.year', string="GST Filed Year",
                                          track_visibility="onchange")
    gst_returns_month_id = fields.Many2one('account.gst.returns.month', string="GST Filed Month",
                                           track_visibility="onchange")
    tax_type_id = fields.Many2one('account.tds.tax.type', string="Tax Type", track_visibility="onchange")
    # transaction_type_id = fields.Many2one('journal.entry.type',
    #                                       string="JE Type",
    #                                       track_visibility="onchange")

    # invoice_id = fields.Many2one('account.invoice',string="Invoice",
    #                                 compute='_compute_invoice_id',
    #                                 store=True)
    # api.depends('invoice_id')
    # def _compute_invoice_id(self):
    #     for rec in self:
    #         invoice_obj = rec.env['account.invoice'].search([('move_id.name','=',rec.name)])
    #         rec.invoice_id =invoice_obj
    #     @api.multi
    #     def write(self, vals):
    #         res = super(AccountMove, self).write(vals)
    #         # for rec in self:
    #         #     _logger.info(f"Processing record ID: {rec.id}")
    #         #     account_move_obj = rec.env['account.invoice'].search([('move_id', '=', rec.id)])
    #         #     _logger.info(f"Found {len(account_move_obj)} related records in account.invoice")

    #         #     _logger.info("Updating records...")
    #         #     account_move_obj.write({
    #         #             'challan_number': rec.challan_number,
    #         #             'bsr_code': rec.bsr_code,
    #         #             'tds_certificate_number': rec.tds_certificate_number,
    #         #             'tds_certificate': rec.tds_certificate,
    #         #             'challan_amount': rec.challan_amount,
    #         #             'account_tds_paid_month_id': rec.account_tds_paid_month_id.id,
    #         #             'account_tds_paid_year_id': rec.account_tds_paid_year_id.id,
    #         #             'gst_returns_year_id': rec.gst_returns_year_id.id,
    #         #             'gst_returns_month_id': rec.gst_returns_month_id.id,
    #         #             'tax_type_id': rec.tax_type_id.id,
    #         #         })
    #         for field, value in vals.items():
    #               if field == 'challan_number':
    #                    self.update_other_model(field, value)
    #               elif field == 'bsr_code':
    #                    self.update_other_model(field, value)
    #               elif field == 'tds_certificate_number':
    #                    self.update_other_model(field, value)
    #               elif field == 'tds_certificate':
    #                    self.update_other_model(field, value)
    #               elif field == 'challan_amount':
    #                    self.update_other_model(field, value)
    #               elif field == 'account_tds_paid_month_id':
    #                    self.update_other_model(field, value)
    #               elif field == 'account_tds_paid_year_id':
    #                    self.update_other_model(field, value)
    #               elif field == 'gst_returns_year_id':
    #                    self.update_other_model(field, value)
    #               elif field == 'gst_returns_month_id':
    #                    self.update_other_model(field, value)
    #               elif field == 'tax_type_id':
    #                    self.update_other_model(field, value)

    #         return res

    def update_other_model(self, field, value):
        account_move_obj = self.env['account.invoice'].search([('move_id', '=', self.id)])
        for record in account_move_obj:
            record.write({field: value})


# stock.picking model

# class InventoryTransfers(models.Model):
#     _inherit = 'stock.picking'
#
#     transaction_type_id = fields.Many2one('journal.entry.type', string="JE Type",
#                                           # related='move_lines.account_move_ids.transaction_type_id',
#                                           store=True,
#                                           readonly=False)


# purchase.order model
# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'
#
#     transaction_type_id = fields.Many2one('journal.entry.type', string="JE Type",
#                                           # related='picking_ids.transaction_type_id',
#                                           store=True, readonly=False)


# sale.order model
# class SaleOrder(models.Model):
#     _inherit = 'sale.order'

    # transaction_type_id = fields.Many2one('journal.entry.type', string="JE Type",
    #                                       # related='picking_ids.transaction_type_id',
    #                                       store=True, readonly=False)


# journal entery type
# class JournalEntryType(models.Model):
#     _name = 'journal.entry.type'
#
#     name = fields.Char("Name")


class AccountMove(models.Model):
    _inherit = 'account.move.line'

    account_group_id = fields.Many2one('account.group', 'Account Group', compute="compute_account_group", store=True)
    challan_number = fields.Char('Challan Number', track_visibility="always", compute="compute_tds_values")
    bsr_code = fields.Char('BSR Code', track_visibility="always", compute="compute_tds_values")
    tds_certificate_number = fields.Char('TDS Certificate No', track_visibility="always", compute="compute_tds_values")
    tds_certificate = fields.Binary('TDS Certificate', track_visibility="always", compute="compute_tds_values")
    challan_amount = fields.Char('Challan Amount', track_visibility="always", compute="compute_tds_values")
    account_tds_paid_month_id = fields.Many2one('account.tds.paid.month', 'TDS Paid Month', track_visibility="onchange",
                                                compute="compute_tds_values")
    account_tds_paid_year_id = fields.Many2one('account.tds.paid.year', 'TDS Paid Year', track_visibility="onchange",
                                               compute="compute_tds_values")
    gst_returns_year_id = fields.Many2one('account.gst.returns.year', string="GST Filed Year",
                                          track_visibility="onchange", compute="compute_tds_values")
    gst_returns_month_id = fields.Many2one('account.gst.returns.month', string="GST Filed Month",
                                           track_visibility="onchange", compute="compute_tds_values")
    tax_group_id = fields.Many2one('account.tax.group', string="Tax Group", store=True,
                                   related="tax_line_id.tax_group_id")
    gst_returns_year_id = fields.Many2one('account.gst.returns.year', string="GST Filed Year",
                                          track_visibility="onchange", compute="compute_tds_values")
    gst_returns_month_id = fields.Many2one('account.gst.returns.month', string="GST Filed Month",
                                           track_visibility="onchange", compute="compute_tds_values")
    tax_type_id = fields.Many2one('account.tds.tax.type', string="Tax Type", track_visibility="onchange",
                                  compute="compute_tds_values")

    def compute_account_group(self):
        for rec in self:
            rec.account_group_id = rec.account_id.group_id

    @api.depends('move_id')
    def compute_tds_values(self):
        for rec in self:
            rec.challan_number = rec.move_id.challan_number
            rec.bsr_code = rec.move_id.bsr_code
            rec.tds_certificate_number = rec.move_id.tds_certificate_number
            rec.tds_certificate = rec.move_id.tds_certificate
            rec.challan_amount = rec.move_id.challan_amount
            rec.account_tds_paid_month_id = rec.move_id.account_tds_paid_month_id.id
            rec.account_tds_paid_year_id = rec.move_id.account_tds_paid_year_id.id
            rec.gst_returns_year_id = rec.move_id.gst_returns_year_id.id
            rec.gst_returns_month_id = rec.move_id.gst_returns_month_id.id
            rec.tax_type_id = rec.move_id.tax_type_id.id
