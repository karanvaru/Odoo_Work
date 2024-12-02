# -*- coding: utf-8 -*-

from odoo import api, fields, models


class sale_order(models.Model):
    _inherit = "sale.order"

    attachment_number = fields.Integer(
        compute='_get_attachment_number',
        string="Number of Attachments"
    )
    attachment_ids = fields.One2many(
        'ir.attachment',
        'res_id',
        domain=[('res_model', '=', 'sale.order')],
        string='Attachments'
    )

    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'sale.order'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)

    def action_get_attachment_tree_view(self):
        attachment_action = self.env.ref('base.action_attachment')
        action = attachment_action.read()[0]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0]
        }
        action['domain'] = str([
            '&', ('res_model', '=', self._name),
            ('res_id', 'in', self.ids)
        ])
        return action

    @api.model
    def website_get_attachments(self):
        documents = self.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'sale.order'),
            ('res_id', 'in', self.ids)
        ])

        return documents

    @api.model
    def website_upload_attach(self,vals):
        self.env['ir.attachment'].sudo().create(vals)

    @api.model
    def website_delete_attach(self,id):
        id = int(id)
        attach_id = self.env['ir.attachment'].sudo().browse(id)
        attach_id.sudo().unlink()
