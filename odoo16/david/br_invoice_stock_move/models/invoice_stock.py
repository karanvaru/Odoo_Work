# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2021-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo.exceptions import UserError
from odoo import models, fields, api, _


class InvoiceStockMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        if self.move_type in ('out_invoice',):
            if self.invoice_line_ids.filtered(lambda r: r.product_id.type in ['product', 'consu']):
                self.action_stock_move()
        return super(InvoiceStockMove, self).action_post()

    def _get_stock_type_ids(self):
        data = self.env['stock.picking.type'].search([])
        if self._context.get('default_move_type') == 'out_invoice':
            for line in data:
                if line.code == 'outgoing':
                    return line
        if self._context.get('default_move_type') == 'in_invoice':
            for line in data:
                if line.code == 'incoming':
                    return line

    picking_count = fields.Integer(string="Count", copy=False)
    invoice_picking_id = fields.Many2one('stock.picking', string="Picking Id", copy=False)

    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type',
                                      default=_get_stock_type_ids,
                                      help="This will determine picking type of incoming shipment")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('proforma', 'Pro-forma'),
        ('proforma2', 'Pro-forma'),
        ('posted', 'Posted'),
        ('post', 'Post'),
        ('cancel', 'Cancelled'),
        ('done', 'Received'),
    ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)

    @api.model
    def create(self, vals):
        id = super(InvoiceStockMove, self).create(vals)
        if id.move_type == 'out_invoice':
            if not id.picking_type_id:
                picking_type_id = self.env['stock.picking.type'].search([
                    ('code', '=', 'outgoing'),
                    ('company_id', '=', id.company_id.id)
                ], limit=1)
                if picking_type_id:
                    id.picking_type_id = picking_type_id.id
        return id


    def action_stock_move(self):
        if not self.picking_type_id:
            raise UserError(_(
                " Please select a picking type"))
        for order in self:
            if not self.invoice_picking_id:
                pick = {}
                if self.picking_type_id.code == 'outgoing':
                    pick = {
                        'picking_type_id': self.picking_type_id.id,
                        'partner_id': self.partner_id.id,
                        'origin': self.name,
                        'location_dest_id': self.partner_id.property_stock_customer.id,
                        'location_id': self.picking_type_id.default_location_src_id.id,
                        'move_type': 'direct'
                    }
                if self.picking_type_id.code == 'incoming':
                    pick = {
                        'picking_type_id': self.picking_type_id.id,
                        'partner_id': self.partner_id.id,
                        'origin': self.name,
                        'location_dest_id': self.picking_type_id.default_location_dest_id.id,
                        'location_id': self.partner_id.property_stock_supplier.id,
                        'move_type': 'direct'
                    }
                picking = self.env['stock.picking'].create(pick)
                # picking_stage = picking.action_assign
                self.invoice_picking_id = picking.id
                self.picking_count = len(picking)
                moves = order.invoice_line_ids.filtered(
                    lambda r: r.product_id.type in ['product', 'consu'])._create_stock_moves(picking)

                move_ids = moves._action_confirm()
                move_ids._action_assign()

                if self.picking_type_id.code == 'outgoing':
                    try:
                        wizard_id = self.env['stock.immediate.transfer'].with_context({
                            'button_validate_picking_ids': picking.ids
                        }).create({
                            'pick_ids': [(6, 0, picking.ids)],
                            'immediate_transfer_line_ids': [(0, 0, {
                                'picking_id': picking.id,
                                'to_immediate': True
                            })]
                        })
                        wizard_id.process()
                    except:
                        pass
                        # action = self.env.ref('br_invoice_stock_move.actions_force_done_picking_wizard').sudo().read([])[0]
                        # return action

    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_ready')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        result['domain'] = [('id', '=', self.invoice_picking_id.id)]
        pick_ids = sum([self.invoice_picking_id.id])
        if pick_ids:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids or False
        return result

    def _reverse_moves(self, default_values_list=None, cancel=False):
        ''' Reverse a recordset of account.move.
        If cancel parameter is true, the reconcilable or liquidity lines
        of each original move will be reconciled with its reverse's.
        :param default_values_list: A list of default values to consider per move.
                                    ('type' & 'reversed_entry_id' are computed in the method).
        :return:                    An account.move recordset, reverse of the current self.
        '''

        if self.picking_type_id.code == 'outgoing':
            data = self.env['stock.picking.type'].search(
                [('company_id', '=', self.company_id.id), ('code', '=', 'incoming')], limit=1)
            self.picking_type_id = data.id
        elif self.picking_type_id.code == 'incoming':
            data = self.env['stock.picking.type'].search(
                [('company_id', '=', self.company_id.id), ('code', '=', 'outgoing')], limit=1)
            self.picking_type_id = data.id
        reverse_moves = super(InvoiceStockMove, self)._reverse_moves()
        return reverse_moves


class SupplierInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            price_unit = line.price_unit
            if picking.picking_type_id.code == 'outgoing':
                template = {
                    'name': line.name or '',
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'location_id': picking.picking_type_id.default_location_src_id.id,
                    'location_dest_id': line.move_id.partner_id.property_stock_customer.id,
                    'picking_id': picking.id,
                    'state': 'draft',
                    'company_id': line.move_id.company_id.id,
                    'price_unit': price_unit,
                    'picking_type_id': picking.picking_type_id.id,
                    'route_ids': 1 and [
                        (6, 0, [x.id for x in self.env['stock.rule'].search([('id', 'in', (2, 3))])])] or [],
                    'warehouse_id': picking.picking_type_id.warehouse_id.id,
                }
            if picking.picking_type_id.code == 'incoming':
                template = {
                    'name': line.name or '',
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'location_id': line.move_id.partner_id.property_stock_supplier.id,
                    'location_dest_id': picking.picking_type_id.default_location_dest_id.id,
                    'picking_id': picking.id,
                    'state': 'draft',
                    'company_id': line.move_id.company_id.id,
                    'price_unit': price_unit,
                    'picking_type_id': picking.picking_type_id.id,
                    'route_ids': 1 and [
                        (6, 0, [x.id for x in self.env['stock.rule'].search([('id', 'in', (2, 3))])])] or [],
                    'warehouse_id': picking.picking_type_id.warehouse_id.id,
                }
            diff_quantity = line.quantity
            tmp = template.copy()
            tmp.update({
                'product_uom_qty': diff_quantity,
            })
            template['product_uom_qty'] = diff_quantity
            done += moves.create(template)
        return done
