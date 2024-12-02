import base64
from odoo import models, fields, api, _
from odoo.modules.module import get_module_resource
from odoo.exceptions import Warning
from odoo import tools


class ShippingPartner(models.Model):
    _name = "shipping.partner"
    _description = "Shipping Partner"


    @api.multi
    def find_pickings(self):
        self.ensure_one()
        picking_obj = self.env['stock.picking']
        waiting_picking_ids = picking_obj
        ready_picking_ids = picking_obj
        delivery_method = self.env['delivery.carrier'].search([('shipping_partner_id', '=', self.id)])
        if delivery_method:
            picking_ids = self.env['stock.picking'].search([('carrier_id', 'in', delivery_method.ids)])
            waiting_picking_ids = waiting_picking_ids + picking_obj.search([('id', 'in', picking_ids.ids),('state', 'in', ['confirmed','waiting'])])
            ready_picking_ids = ready_picking_ids + picking_obj.search([('id', 'in', picking_ids.ids), ('state', '=', 'assigned')])
        return waiting_picking_ids,ready_picking_ids

    @api.multi
    def _count_pickings(self):
        for record in self:
            waiting_picking_ids,ready_picking_ids = record.find_pickings()
            record.count_waiting_picking = len(waiting_picking_ids)
            record.count_ready_picking = len(ready_picking_ids)

    name = fields.Char(required=True, help="Shipping Partner", string="Name")
    color = fields.Integer(string='Color Index', help="select color")
    provider_company = fields.Selection(selection=[], string='Partner', required=False, help="Select Shipping Partner.")
    count_waiting_picking = fields.Integer('Waiting Pickings',compute='_count_pickings')
    count_ready_picking = fields.Integer('Ready Pickings',compute='_count_pickings')
    active = fields.Boolean('Active', help="If the active field is set to False, then can not access the Instance.",
                            default=True)

    image = fields.Binary("Photo", attachment=True, help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized photo", attachment=True,
        help="Medium-sized photo of the employee. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized photo", attachment=True,
        help="Small-sized photo of the employee. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")

    @api.onchange('provider_company')
    def _onchange_provider_company(self):
        pass

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(ShippingPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(ShippingPartner, self).write(vals)

    @api.multi
    def action_delivery_method(self):
        self.ensure_one()
        action = self.env.ref('delivery.action_delivery_carrier_form').read()[0]
        action['context'] = {'default_shipping_partner_id': self.id, 'default_delivery_type': self.provider_company}
        action['domain'] = [('shipping_partner_id', '=', self.id)]
        return action

    @api.model
    def action_dashboard_redirect(self):
        if self.env.user.has_group('base.group_system'):
            return self.env.ref('base_shipping_partner.backend_shipping_dashboard').read()[0]
        return self.env.ref('base_shipping_partner.action_website').read()[0]

    @api.multi
    def unlink(self):
        delivery_carrier_obj = self.env['delivery.carrier']
        for instance in self:
            delivery_methods = delivery_carrier_obj.search([('shipping_partner_id', '=', instance.id)])
            inactive_delivery_methods = delivery_carrier_obj.search(
                [('shipping_partner_id', '=', instance.id), ('active', '=', False)])
            if delivery_methods or inactive_delivery_methods:
                raise Warning(_("You can not delete %s shipping instance because method is exist.") % instance.name)
        return super(ShippingPartner, self).unlink()

    @api.multi
    def toggle_active(self):
        delivery_carrier_obj = self.env['delivery.carrier']
        delivery_methods = delivery_carrier_obj.search([('shipping_partner_id', '=', self.id)])
        if delivery_methods:
            delivery_methods.write({'active': False})
        for record in self:
            record.active = not record.active

    @api.multi
    def open_pickings(self):
        self.ensure_one()
        waiting_picking_ids, ready_picking_ids = self.find_pickings()
        picking_ids = self.env['stock.picking']
        if self._context.get('picking_type',False) and self._context.get('picking_type') == 'waiting':
            picking_ids = picking_ids + waiting_picking_ids
        if self._context.get('picking_type',False) and self._context.get('picking_type') == 'ready':
            picking_ids = picking_ids + ready_picking_ids

        vals = {
            'name': _('Picking'),
            'view_type': 'tree',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'views': [[self.env.ref('stock.vpicktree').id, 'list'], [self.env.ref('stock.view_picking_form').id, 'form']],
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', picking_ids.ids)],
            'target': 'current'
        }
        return vals


