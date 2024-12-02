import os
import base64
import logging
import binascii
from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2 import PdfFileMerger
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError, UserError

_logger = logging.getLogger(__name__)


class BatchOrders(models.Model):
    _inherit = "stock.picking.batch"

    ready_for_download = fields.Boolean('ReadyForDownload', help="It's True when done wave.", default=False, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'Running'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('send_to_shipper', 'Send To Shipper')], default='draft',
        copy=False, track_visibility='onchange', required=True)
    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method",
                                 help="According to the provider, Visible the delivery method.", copy=False)

    def done(self):
        pickings = self.mapped('picking_ids').filtered(lambda picking: picking.state not in ('cancel', 'done'))
        for picking in pickings:
            try:
                picking.button_validate()
            except Exception as e:
                raise UserError(_("Issue While validate the picking : %s, %s" % (picking.name, e)))
        return super(BatchOrders, self).done()

    def send_to_shipper(self):
        self.ensure_one()
        pickings = self.picking_ids.filtered(lambda x: x.picking_type_code in ('outgoing') and x.state in (
            'done') and not x.carrier_tracking_ref)
        if pickings:
            for picking in pickings:
                try:
                    carrier_id = picking.carrier_id if picking.carrier_id else self.carrier_id
                    carrier_id.shiprocket_send_shipping(picking)
                    self._cr.commit()
                    if picking.shiprocket_shipment_id:
                        carrier_id.get_shiprocket_charges(picking)
                except Exception as e:
                    message = "Delivery Order : %s Description : %s" % (picking.name, e)
                    self.message_post(body=message)
                    _logger.info("Error while processing for send to Shipper - Picking : %s " % (picking.name))
        pickings = self.picking_ids.filtered(lambda x: x.picking_type_code in ('outgoing') and x.state in (
            'done') and x.carrier_id and x.shiprocket_shipment_id == False and not x.carrier_tracking_ref)

        if len(pickings) < 1:
            self.write({'state': 'send_to_shipper'})

    def generate_awd(self):
        pickings = self.picking_ids.filtered(lambda x: x.picking_type_code in ('outgoing') and x.state in (
            'done') and x.shiprocket_shipment_id)
        if pickings:
            for picking in pickings:
                try:
                    carrier_id = picking.carrier_id if picking.carrier_id else self.carrier_id
                    carrier_id.generate_shiprocket_awd(picking)
                    self._cr.commit()
                    if picking.carrier_tracking_ref:
                        carrier_id.generate_shiprocket_label(picking)
                except Exception as e:
                    message = "Delivery Order : %s Description : %s" % (picking.name, e)
                    self.message_post(body=message)
                    _logger.info("Error while processing for send to Shipper - Picking : %s " % (picking.name))

        pickings = self.picking_ids.filtered(lambda x: x.picking_type_code in ('outgoing') and x.state in (
            'done') and x.carrier_id and x.shiprocket_shipment_id == False and not x.carrier_tracking_ref)
        if len(pickings) < 1:
            self.ready_for_download = True

    def download_labels(self):
        input_path = []
        file_name = self.name
        pdf_merger = PdfFileMerger()
        file_name = file_name.replace('/', '_')
        file_path = "/tmp/waves/"
        directory = os.path.dirname(file_path)
        try:
            os.stat(directory)
        except:
            os.system("mkdir %s" % (file_path))
        pickings = self.picking_ids.filtered(lambda x: x.picking_type_code in ('outgoing') and x.state in (
            'done') and x.carrier_tracking_ref)
        for picking in pickings:
            file_name = picking.name
            file_name = file_name.replace('/', '_')
            label_attachments = self.env['ir.attachment'].search(
                [('res_model', '=', 'stock.picking'), ('res_id', '=', picking.id)])
            if not label_attachments:
                continue
            for sequence, label_attachment in enumerate(label_attachments, start=1):
                input_path.append("%s_%s.pdf" % (file_path, picking.id))
                with open("%s_%s.pdf" % (file_path, picking.id), "ab") as f:
                    f.write(base64.b64decode(label_attachment and label_attachment.datas))
        for path in input_path:
            pdf_merger.append(path)
        with open("%s_%s.pdf" % (file_path, file_name), 'wb') as fileobj:
            pdf_merger.write(fileobj)
        with open("%s_%s.pdf" % (file_path, file_name), "rb") as f1:
            f1.seek(0)
            buffer = data = f1.read()
            f1.close()
            file_data_temp = base64.b64encode(buffer)
        att_id = self.env['ir.attachment'].sudo().create({'name': "Wave_%s" % (file_name or ""),
                                                          'datas_fname': "Wave_%s.pdf" % (file_name or ""),
                                                          'type': 'binary',
                                                          'datas': file_data_temp or "",
                                                          'mimetype': 'application/pdf',
                                                          'res_model': 'stock.picking.batch',
                                                          'res_id': self.id,
                                                          'res_name': self.name})
        if os.stat(directory):
            os.system("%s" % (file_path))
            os.system("rm -R %s" % (directory))
        return {'effect': {
            'fadeout': 'slow',
            'message': "Label attached successfully..",
            'img_url': '/web/static/src/img/smile.svg',
            'type': 'rainbow_man'}}
