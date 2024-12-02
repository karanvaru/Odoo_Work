from odoo import models, fields, api


class MaterialPurchaseRequisitionInherit(models.Model):
    _inherit = 'material.purchase.requisition'

    @api.model
    def default_get(self, fields):
        location_id = self.env.ref('stock.stock_location_stock')
        picking_type = self.env['stock.picking.type'].sudo().search([('code', '=', 'internal')], limit=1)
        rec = super(MaterialPurchaseRequisitionInherit, self).default_get(fields)
        rec.update({
            'dest_location_id': self.env.ref('stock.stock_location_locations').id,
            'location_id': location_id.id,
            'custom_picking_type_id': picking_type.id,
        })
        return rec

    def requisition_confirm(self):
        res = super(MaterialPurchaseRequisitionInherit, self).requisition_confirm()
        self.user_approve()
        return res

    @api.onchange('employee_id')
    def set_department(self):
        for rec in self:
            rec.department_id = rec.employee_id.sudo().department_id.id
            location = rec.employee_id.sudo().dest_location_id
            if not location:
                location = rec.employee_id.sudo().department_id.dest_location_id
            if location:
                rec.dest_location_id = location.id 


class MaterialPurchaseRequisitionLine(models.Model):
    _inherit = "material.purchase.requisition.line"

    requisition_type = fields.Selection(
        default='internal',
    )
