from odoo import api, models, fields, _
from odoo.exceptions import UserError

import json


class UpdatevehicleNO(models.TransientModel):
    _name = 'update.vehicle.no'

    vehicle_no = fields.Char('vehicle No')
    reason = fields.Selection([('1', 'Due To Break Down'),
                               ('2', 'Due To Transhipment'),
                               ('3', 'Others'),
                               ('VEHEWB4', 'First time'), ], string='Reason')
    remark = fields.Text('Remark')
    transporter_doc_no = fields.Char("Transporter Document No.", size=16)
    transportation_doc_date = fields.Date('Transport Document Date', track_visibility="onchange")
    vehicle_type = fields.Selection([('R', 'Regular'),
                                     ('O', 'ODC')], string="Vechicle Type", track_visibility="onchange")
    transportation_mode = fields.Selection([('1', 'Road'),
                                            ('2', 'Rail'),
                                            ('3', 'Air'),
                                            ('4', 'Ship'),
                                            ], string="Transportation Mode")

    @api.model
    def default_get(self, fields):
        vals = super(UpdatevehicleNO, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        order = self.env['account.invoice'].browse(active_id)
        if 'vehicle_no' in fields:
            vals['vehicle_no'] = order.vehicle_no or ''
        if 'transporter_doc_no' in fields:
            vals['transporter_doc_no'] = order.transporter_doc_no or ''
        if 'transportation_doc_date' in fields:
            vals['transportation_doc_date'] = order.transportation_doc_date
        if 'vehicle_type' in fields:
            vals['vehicle_type'] = order.vehicle_type
        if 'transportation_mode' in fields:
            vals['transportation_mode'] = order.transportation_mode
        return vals

    def update_vehicle(self):
        active_id = self.env.context.get('active_id')
        order = self.env['account.invoice'].browse(active_id)
        if order.ewaybill_no and not order.cancel_date:
            vehicle_dic = {
                'ewbNo': order.ewaybill_no,
                'vehicleNo': self.vehicle_no,
                'fromPlace': order.city,
                'fromState': order.state_id.port_code,
                'reasonCode': self.reason,
                'reasonRem': self.remark,
                'transDocNo ': self.transporter_doc_no,
                'transDocDate ': str(self.transportation_doc_date) if self.transportation_doc_date else '',
                'transMode': self.transportation_mode,
                'vehicleType': self.vehicle_type
            }
            data_base64 = json.dumps(vehicle_dic)
            configuration = self.env['eway.configuration'].search([])
            if configuration:
                response = configuration.generate_eway(order.warehouse_id, data_base64, 'VEHEWB')
                print('response..', response, response.json())
                if response.json().get('status_cd', '') != 0:
                    order.message_post(body=_(
                        "Vehicle Details Updated: Reason is '" + dict(
                                    self._fields['reason'].selection).get(self.reason) +
                        "', Remark: '" + self.remark + "'. Vehicle Details valid from " + str(response.json().get('validUpto')) +
                        ' and Update Date is: '
                        + str(response.json().get('vehUpdDate'))))
                    order.write({
                        'valid_ebill_date': str(response.json().get('validUpto')),
                        'vehicle_no': self.vehicle_no,
                        'transporter_doc_no': self.transporter_doc_no,
                        'transportation_doc_date': self.transportation_doc_date,
                        'transportation_mode': self.transportation_mode,
                        'vehicle_type': self.vehicle_type
                    })
                else:
                    order.message_post(body=_("Error: " + str(response.json().get('message', ''))))
        else:
            raise UserError(_('Eway Bill is already cancelled !'))
