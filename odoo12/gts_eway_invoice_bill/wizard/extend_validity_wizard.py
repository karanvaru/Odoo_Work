
from odoo import api, models, fields, _
from odoo.exceptions import UserError, Warning

import json


class ExtendEwayValidity(models.TransientModel):
    _name = 'extend.eway.validity'

    vehicle_no = fields.Char('vehicle No')
    reason = fields.Selection([('1', 'Natural Calamity'),
                               ('2', 'Law and Order Situation'),
                               ('4', 'Transshipment'),
                               ('5', 'Accident'),
                               ('6', 'Others')], string='Reason')
    remark = fields.Text('Remark')
    transporter_doc_no = fields.Char("Transporter Document No.", size=16)
    transportation_doc_date = fields.Date('Transport Document Date', track_visibility="onchange")
    vehicle_type = fields.Selection([('R', 'Regular'),
                                     ('O', 'ODC')], string="Vechicle Type", track_visibility="onchange")
    transportation_mode = fields.Selection([('1', 'Road'),
                                            ('2', 'Rail'),
                                            ('3', 'Air'),
                                            ('4', 'Ship'),
                                            ('5', 'In Transit')
                                            ], string="Transportation Mode")
    street = fields.Char('Address1')
    street2 = fields.Char('Address2')
    street3 = fields.Char('Address3')
    city = fields.Char('From Place/City')
    state_id = fields.Many2one("res.country.state", string='State', domain="[('country_id.code', '=', 'IN')]")
    zip = fields.Char('Pincode', change_default=True)
    transportation_distance = fields.Float("Remaining Distance(Km)", tracking=2,
                                           help='If entered, we will use this distance')
    transit_type = fields.Selection([('R', 'Road'),
                                     ('W', 'Warehouse'),
                                     ('O', 'Others')], string="Transit Type")
    consignment_status = fields.Selection([('M', 'In Movement'),
                                           ('T', 'In Transit')], string="Consignment Status")

    @api.model
    def default_get(self, fields):
        vals = super(ExtendEwayValidity, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        order = self.env['account.invoice'].browse(active_id)
        if 'transporter_doc_no' in fields:
            vals['transporter_doc_no'] = order.transporter_doc_no or ''
        if 'transportation_doc_date' in fields:
            vals['transportation_doc_date'] = order.transportation_doc_date
        if 'vehicle_type' in fields:
            vals['vehicle_type'] = order.vehicle_type
        if 'transportation_mode' in fields:
            vals['transportation_mode'] = order.transportation_mode
        # if 'street' in fields:
        #     vals['street'] = order.street or ''
        # if 'street2' in fields:
        #     vals['street2'] = order.street2 or ''
        # if 'city' in fields:
        #     vals['city'] = order.city or ''
        # if 'state_id' in fields:
        #     vals['state_id'] = order.state_id.id or False
        # if 'zip' in fields:
        #     vals['zip'] = order.zip or ''
        # if 'transportation_distance' in fields:
        #     vals['transportation_distance'] = order.transportation_distance
        return vals

    def update_vehicle(self):
        if not (self.transportation_distance > 0):
            raise UserError(_('Remaining Distance should be greater than 0 !'))
        active_id = self.env.context.get('active_id')
        order = self.env['account.invoice'].browse(active_id)
        if order.doc_date and self.transportation_doc_date:
            if not (self.transportation_doc_date >= order.doc_date):
                raise UserError(_('Document Date can not be greater then today!'))
        if order.transportation_distance > 0 and self.transportation_distance > 0:
            if self.transportation_distance >= order.transportation_distance:
                raise UserError(_('Remaining Distance can not be greater than or equal to the actual distance!'))
        if order.ewaybill_no and not order.cancel_date:
            vehicle_dic = {
                'ewbNo': order.ewaybill_no,
                'transDocNo ': self.transporter_doc_no,
                'transDocDate ': str(order.format_date(self.transportation_doc_date))
                    if self.transportation_doc_date else '',
                'transMode': self.transportation_mode,
                'vehicleType': self.vehicle_type,
                'remainingDistance': int(self.transportation_distance),
                'extnRsnCode': int(self.reason),
                'extnRemarks': self.remark or '',
                'fromPincode': self.zip,
                'fromPlace': self.city,
                'fromState': self.state_id.port_code,
            }
            if self.transportation_mode == '1':
                vehicle_dic.update({'vehicleNo': order.vehicle_no})
            elif self.transportation_mode in ('2', '3', '4'):
                if not self.transporter_doc_no:
                    raise UserError(_('Transporter Document Number is required !'))
                vehicle_dic.update({'transDocNo': self.transporter_doc_no})
            elif self.transportation_mode == '5':
                vehicle_dic.update({
                    'addressLine1': self.street or '',
                    'addressLine2': self.street2 or '',
                    'addressLine3': self.street3 or '',
                })
            if self.transportation_mode == '5':
                vehicle_dic.update({
                    'consignmentStatus': 'T',
                    'transitType': self.transit_type or 'R',
                })
            elif self.transportation_mode != '5':
                vehicle_dic.update({
                    'consignmentStatus': 'M',
                    'transitType': '',
                })
            print('vehicle_dic...', vehicle_dic)
            data_base64 = json.dumps(vehicle_dic)
            print(data_base64)
            configuration = order.get_configuration()
            picking_id = self.env['account.invoice'].browse(active_id)
            warehouse_id = picking_id.warehouse_id
            response = configuration.generate_eway(
                warehouse_id, data_base64, 'EXTENDVALIDITY')
            print('response..', response, response.json())
            if 'status_cd' in response.json() and response.json().get('status_cd') == '0':
                if 'error' in response.json():
                    order.message_post(body=_(str(response.json().get('error').get('message'))))
                    # raise Warning(_((str(response.json().get('error').get('message')))))
            else:
                print(response.json())
                order.message_post(body=_(
                    "E-Way Bill Validity Extended: '" + dict(
                        self._fields['reason'].selection).get(self.reason) +
                    "', Remark: '" + self.remark + "'. Vehicle Details valid from " + str(
                        response.json().get('validUpto')) +
                    ' and Update Date is: '
                    + str(response.json().get('vehUpdDate'))))
        else:
            raise UserError(_('E-Way Bill is already cancelled !'))
