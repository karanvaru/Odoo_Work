# Copyright (C) 2019 - TODAY, Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models,api


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    parent_id = fields.Many2one('helpdesk.ticket', string="Parent")
    child_ids = fields.One2many('helpdesk.ticket',
                                'parent_id', string="Children")
    child_count = fields.Integer('child count',compute='child_count_values')

    def child_count_values(self):
        child_count_ids = self.env['helpdesk.ticket'].search_count([('parent_id', '=', self.id)])
        self.child_count = child_count_ids







    def action_child_count(self):
            self.ensure_one()
            return {
                'name': 'Child tickets',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'helpdesk.ticket',
                'domain': [('parent_id', '=', self.id)],
            }




    def create_child_ticket(self,vals):
        help_ticket = self.env['helpdesk.ticket']
        vals = {
            'name': self.name,
            'team_id':self.team_id.id,
            'user_id':self.user_id.id,
            'priority' :self.priority,
            # 'x_studio_model_name' :self.x_studio_model_name,
            'x_studio_attached_os' :self.x_studio_attached_os,
            'close_hours':self.close_hours,
            'deadline':self.deadline,
            'create_date':self.create_date,
            'x_studio_sales_channel':self.x_studio_sales_channel,
            'partner_id':self.partner_id.id,
            'partner_email':self.partner_email,
            'x_studio_field_w3gK7':self.x_studio_field_w3gK7,
            'x_studio_customer_mobile':self.x_studio_customer_mobile,
            'x_studio_partner':self.x_studio_partner.id,
            # 'parent_ticket_id':self.id,
            # 'ticket_type_id':self.ticket_type_id.id,
            # 'x_studio_serial_no':self.x_studio_serial_no,
            'x_studio_bill_date':self.x_studio_bill_date,
            'x_studio_scope':self.x_studio_scope,
            # 'tag_ids':self.tag_ids
            'parent_id':self.id,
            'description':self.description,

        }

        new_val = help_ticket.create(vals)
        # help_ticket.create({})

        return new_val
