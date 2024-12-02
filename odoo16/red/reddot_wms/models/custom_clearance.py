from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class CustomClearanceInherit(models.Model):
    _inherit = "custom.clearance"
    _description = "Reddot Custom Clearance"
    _order = 'id desc'

    freight_id = fields.Many2one('freight.order', required=False)

    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('not-released', 'Not Released'),
                              ('done', 'Done')], default='draft')

    remark_not_released = fields.Text('Reason for not releasing')
    reason = fields.Text(string='Reason')
    bill_of_exit = fields.Char('Bill of Exit Number')
    picking_id = fields.Many2one('stock.picking', string="Delivery", readonly=1)

    def action_not_released(self):
        return {
            'name': _('Reason for Not Releasing'),
            'type': 'ir.actions.act_window',
            'res_model': 'custom.clearance.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id}
        }


class CustomClearanceWizard(models.TransientModel):
    _name = 'custom.clearance.wizard'
    _description = 'Custom Clearance Wizard'

    reason = fields.Text(string='Reason')

    def reason_for_not_releasing(self):
        clearance_id = self.env.context.get('active_id')
        rec = self.env['custom.clearance'].search([('id', '=', clearance_id)])
        rec.write({
            'remark_not_released': self.reason
        })
        rec.state = 'not-released'


class CustomsRestrictions(models.Model):
    _name = "customs.restrictions"
    _description = "Customs Restrictions"

    release_ref = fields.Char('Release Reference')
    agency = fields.Char('Agency')


class DutyExemptions(models.Model):
    _name = "duty.exceptions"
    _description = "Customs Restrictions"

    beneficiary = fields.Char('Beneficiary')
    sources = fields.Char('Sources')
    code = fields.Char('Code')


class CustomsDeliveries(models.TransientModel):
    _name = 'customs.clearance.wizard'
    _description = 'Customs Clearance Wizard'

    date = fields.Date('Date')
    agent_id = fields.Many2one('res.partner', 'Agent', required=True)
    bill_of_exit = fields.Char('Bill of Exit Number')

    shipper_id = fields.Many2one('res.partner', 'Shipper', required=True,
                                 help="Shipper's Details")
    transport_type = fields.Selection([('land', 'Land'), ('air', 'Air'),
                                       ('water', 'Water')], "Transport",
                                      help='Type of transportation',
                                      required=True)
    loading_port_id = fields.Many2one('freight.port', string="Loading Port",
                                      required=True,
                                      help="Loading port of the freight order")
    discharging_port_id = fields.Many2one('freight.port',
                                          string="Discharging Port",
                                          required=True,
                                          help="Discharging port of freight order")

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company.id, readonly=1)
    type = fields.Selection([('import', 'Import'), ('export', 'Export')],
                            'Import/Export', required=True,
                            help="Type of freight operation", default='export')

    warning = fields.Char(readonly=True)

    def submit(self):
        picking_id = self.env.context.get('active_ids')[0]
        if self.bill_of_exit:
            self.env['stock.picking'].search([('id', '=', picking_id)]).sudo().write({
                    'exit_number': self.bill_of_exit
                })
            freight = self.env['freight.order'].create({
                'shipper_id': self.shipper_id.id,
                'type': self.type,
                'transport_type': self.transport_type,
                'loading_port_id': self.loading_port_id.id,
                'agent_id': self.agent_id.id,
                'state': 'delivery',
                'discharging_port_id': self.discharging_port_id.id,
            })

            if freight:
                self.env['custom.clearance'].sudo().create({
                    'date': self.date,
                    'agent_id': self.agent_id.id,
                    'bill_of_exit': self.bill_of_exit,
                    'freight_id': freight.id,
                    'picking_id': picking_id,
                    'loading_port_id': self.loading_port_id.id,
                    'discharging_port_id': self.discharging_port_id.id

                })

                self.env['stock.picking'].compute_count()
