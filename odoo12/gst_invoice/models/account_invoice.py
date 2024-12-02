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

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    gst_status = fields.Selection([
                                ('not_uploaded', 'Not Uploaded'),
                                ('ready_to_upload', 'Ready to upload'),
                                ('uploaded', 'Uploaded to govt'),
                                ('filed', 'Filed')
                            ],
                            string='GST Status',
                            default="not_uploaded",
                            copy=False,
                            help="status will be consider during gst import, "
            )
    invoice_type = fields.Selection([
                                ('b2b', 'B2B'),
                                ('b2cl', 'B2CL'),
                                ('b2cs', 'B2CS'),
                                ('b2bur', 'B2BUR'),
                                ('import', 'IMPS/IMPG'),
                                ('export', 'Export')
                            ],
                            copy=False,
                            string='Invoice Type'
            )
    export = fields.Selection([
                                ('WPAY', 'WPay'),
                                ('WOPAY', 'WoPay')
                            ],
                            string='Export'
            )
    bonded_wh = fields.Selection([
                                ('Y', 'Yes'),
                                ('N', 'No')
                            ],
                            string='Sale from Bonded WH',
                            default='N',
                            help='When goods will be kept in bonded warehouses and later cleared from there',
            )
    itc_eligibility = fields.Selection([
                                ('Inputs', 'Inputs'),
                                ('Capital goods', 'Capital goods'),
                                ('Input services', 'Input services'),
                                ('Ineligible', 'Ineligible'),
                            ],
                            string='ITC Eligibility',
                            default='Ineligible'
            )
    gst_invoice_type = fields.Selection([
                                ('Regular', 'Regular'),
                                ('SEZ supplies with payment', 'SEZ supplies with payment'),
                                ('SEZ supplies without payment', 'SEZ supplies without payment'),
                                ('Deemed Exp', 'Deemed Exp'),
                            ],
                            copy=False,
                            string='GST Invoice Type',
                            default='Regular'
            )
    reverse_charge = fields.Boolean(
                        string='Reverse Charge',
                        help="Allow reverse charges for b2b invoices")
    portcode_id = fields.Many2one('port.code', 'Port Code', help="Enter the six digit code of port through which goods were imported")
    inr_total = fields.Float(string='INR Total')
    port_code = fields.Char(
        string='Port Code',
        copy=False,
        help='Enter the six digit code of port through which goods were exported. Please refer to the list of port codes available on the GST common portal.')
    shipping_bill_number = fields.Char(
        string='Shipping Bill Number',
        copy=False,
        help='Enter the unique reference number of shipping bill. This information if not available at the timing of submitting the return the same may be left blank and provided later.')
    shipping_bill_date = fields.Date(
        string='Shipping Bill Date',
        copy=False,
        help="Enter date of shipping bill in DD-MMM-YYYY. E.g. 24-May-2017.")

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        taxes_grouped = self.get_hsn_taxes_values()
        tax_lines = self.tax_line_ids.browse([])
        for yo in taxes_grouped.values():
            for tax in yo.values():
                tax_lines += tax_lines.new(tax)
            self.tax_line_ids = tax_lines
        return

    @api.multi
    def get_hsn_taxes_values(self):
        tax_hsn_grouped = {}
        tax_grouped = {}
        for line in self.invoice_line_ids:
            hsn =line.product_id.l10n_in_hsn_code
            hsnVal = hsn
            if not hsnVal:
                hsnVal = 'false'
            if hsnVal not in tax_hsn_grouped:
                tax_hsn_grouped[hsnVal] = {}
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
                if key not in tax_hsn_grouped[hsnVal]:
                    val['hsn_code'] = hsn
                    tax_hsn_grouped[hsnVal][key] = val
                else:
                    tax_hsn_grouped[hsnVal][key]['amount'] += val['amount']
                    tax_hsn_grouped[hsnVal][key]['base'] += val['base']
        return tax_hsn_grouped

    class AccountInvoiceTax(models.Model):
        _inherit = "account.invoice.tax"
    
        hsn_code = fields.Char(string='HSN', copy=False)
