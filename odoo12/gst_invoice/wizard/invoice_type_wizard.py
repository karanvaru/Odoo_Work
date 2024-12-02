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

from odoo import api, fields, models

class InvoiceTypeWizard(models.TransientModel):
    _name = "invoice.type.wizard"
    _description = "Invoice type wizard"

    gst_status = fields.Selection([
                                ('not_uploaded', 'Not Uploaded'),
                                ('ready_to_upload', 'Ready to upload'),
                                ('uploaded', 'Uploaded to govt'),
                                ('filed', 'Filed')
                            ],
                            string='GST Status',
                            help="status will be consider during gst import, "
            )
    invoice_type = fields.Selection([
                                ('b2b', 'B2B'),
                                ('b2cl', 'B2CL'),
                                ('b2cs', 'B2CS'),
                                ('export', 'Export')
                            ], string='Invoice Type')
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
                            help='When goods will be kept in bonded warehouses and later cleared from there',
            )
    itc_eligibility = fields.Selection([
                                ('Inputs', 'Inputs'),
                                ('Capital goods', 'Capital goods'),
                                ('Input services', 'Input services'),
                                ('Ineligible', 'Ineligible'),
                            ],
                            string='ITC Eligibility',
            )
    gst_invoice_type = fields.Selection([
                                ('Regular', 'Regular'),
                                ('SEZ supplies with payment', 'SEZ supplies with payment'),
                                ('SEZ supplies without payment', 'SEZ supplies without payment'),
                                ('Deemed Exp', 'Deemed Exp'),
                            ],
                            string='GST Invoice Type',
            )
    reverse_charge = fields.Boolean(
                        string='Reverse Charge',
                        help="Allow reverse charges for b2b invoices")
    portcode_id = fields.Many2one('port.code', 'Port Code', help="Enter the six digit code of port through which goods were imported")

    @api.model
    def updateInvoiceType(self):
        partial = self.create({})
        ctx = dict(self._context or {})
        return {'name': ("Bulk Action"),
                'view_mode': 'form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'invoice.type.wizard',
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': ctx,
                'domain': '[]',
                }

    @api.multi
    def updateAccountInvoiceType(self):
        count = 0
        model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        export = self.export
        for active_id in active_ids:
            invoiceObj = self.env[model].browse(active_id)
            data = {}
            if self.invoice_type:
                data['invoice_type'] = self.invoice_type
            if self.gst_status:
                data['gst_status'] = self.gst_status
            if self.export:
                data['export'] = self.export
            if self.bonded_wh:
                data['bonded_wh'] = self.bonded_wh
            if self.itc_eligibility:
                data['itc_eligibility'] = self.itc_eligibility
            if self.gst_invoice_type:
                data['gst_invoice_type'] = self.gst_invoice_type
            if self.reverse_charge:
                data['reverse_charge'] = self.reverse_charge
            if self.portcode_id:
                data['portcode_id'] = self.portcode_id
            if data:
                invoiceObj.write(data)
            count = count + 1
        text = 'Invoice data of %s record(s) has been successfully updated.' % (count)
        partial = self.env['message.wizard'].create({'text': text})
        return {'name': ("Information"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'message.wizard',
                'view_id': self.env.ref('gst_invoice.message_wizard_form1').id,
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                }
