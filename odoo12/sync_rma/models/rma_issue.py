# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class RmaIssue(models.Model):
    _name = 'rma.issue'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _order = 'id desc'
    _description = 'RMA Issue'

    @api.multi
    def _get_invoice_ids(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids) if record.invoice_ids else 0

    @api.multi
    @api.depends('issue_line_ids', 'issue_line_ids.return_type_id')
    def check_return_purpose(self):
        """
            Set return purpose depends on RMA lines
        """
        for rec in self:
            rec.is_credit = False
            rec.is_replace = False
            rec.is_repair = False
            if rec.issue_line_ids.filtered(lambda l: l.return_type_id.return_purpose == 'credit'):
                rec.is_credit = True
            if rec.issue_line_ids.filtered(lambda l: l.return_type_id.return_purpose == 'replace'):
                rec.is_replace = True
            if rec.issue_line_ids.filtered(lambda l: l.return_type_id.return_purpose == 'repair'):
                rec.is_repair = True

    @api.multi
    def _repair_count(self):
        """
            Count repair orders
        """
        for repair in self:
            repair.repair_count = len(repair.repair_ids) if repair.repair_ids else 0
            repair_ref = []
            for repair_id in repair.repair_ids:
                if repair_id.name:
                    repair_ref.append(repair_id.name)
            repair.repair_order = (', '.join(repair_ref))

    @api.multi
    def _delivery_count(self):
        """
            Count delivery orders
        """
        for repair in self:
            picking_ids = self.env['stock.picking'].search(['|', ('return_rma_issue_id', '=', repair.id), ('rma_issue_id', '=', repair.id)])
            repair.return_delivery_count = len(picking_ids) if picking_ids else 0

    @api.model
    def default_get(self, fields):
        """
            Override method for set default values
        """
        line_vals = []
        rec = super(RmaIssue, self).default_get(fields)
        if self._context.get('rma_sale_id', False) and self._context.get('sale_order', False):
            order = self.env['sale.order'].browse(self._context.get('rma_sale_id'))
            for order_line in order.order_line:
                if order_line.product_id.type != 'service':
                    if order_line.product_uom_qty > 0 and order_line.qty_delivered:
                        line_vals.append((0, 0, {
                            'order_id': self.id,
                            'product_id': order_line.product_id.id,
                            'name': order_line.name,
                            'quantity': order_line.product_uom_qty,
                            'qty_delivered': order_line.qty_delivered,
                            'product_uom': order_line.product_uom.id,
                            'product_uom_qty': order_line.product_uom_qty,
                            'qty_invoiced': order_line.qty_invoiced,
                            'price_unit': order_line.price_unit,
                            'price_tax': order_line.price_tax,
                            'discount': order_line.discount,
                            'price_subtotal': order_line.price_subtotal,
                            'price_total': order_line.price_total,
                            }))
            rec['issue_line_ids'] = line_vals
            rec['partner_id'] = order.partner_id.id
            rec['associated_so'] = order.id
        return rec

    @api.model
    def _default_source_location(self):
        """
            Get defaule source location
        """
        partner_location = self.env.ref('stock.stock_location_customers')
        if partner_location:
            return partner_location
        return False

    @api.model
    def _default_dest_location(self):
        """
            Get default destination location
        """
        warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        if warehouse_id:
            return warehouse_id.lot_stock_id
        return False

    @api.multi
    @api.depends('return_picking_ids', 'return_picking_ids.state')
    def check_done_pickings(self):
        for rec in self:
            rec.is_done_receipt = False
            if rec.return_picking_ids and all('done' == state for state in rec.return_picking_ids.mapped('state')):
                rec.is_done_receipt = True

    is_receipt = fields.Boolean(string='Is Receipt', copy=False)
    is_done_receipt = fields.Boolean(string='Is Done Receipt', copy=False, compute="check_done_pickings", store=True)
    return_picking_ids = fields.One2many('stock.picking', 'return_rma_issue_id', string="Return Pickings", copy=False)
    subject = fields.Char(string="Subject", required=True, track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    name = fields.Char(string='Name', default=lambda self: _('New'), copy=False, readonly=True, states={'draft': [('readonly', False)]})
    repair_order = fields.Char(string="Repair Order", invisible=True, compute="_repair_count")
    issue_date = fields.Datetime(string='Date', default=fields.Datetime.now, required=True, readonly=True, states={'draft': [('readonly', False)]})
    rma_note = fields.Text(string="RMA Note", copy=False)
    rma_reject_note = fields.Text(string="RMA Rejection Note", copy=False)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    partner_invoice_id = fields.Many2one('res.partner', string='Invoice Address', readonly=True, required=True, states={'draft': [('readonly', False)]}, help="Invoice address for current RMA.")
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address', readonly=True, required=True, states={'draft': [('readonly', False)]}, help="Delivery address for current RMA.")
    associated_so = fields.Many2one('sale.order', string='Sale Order', copy=False, track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', string='Responsible', track_visibility='onchange', default=lambda self: self.env.user, readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('rma.issue'), track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    invoice_ref_id = fields.Many2one('account.invoice', string="Credit Invoice", copy=False, readonly=True, states={'draft': [('readonly', False)]})
    order_ref_id = fields.Many2one('sale.order', string="Replace Order", copy=False, readonly=True, states={'draft': [('readonly', False)]})
    issue_line_ids = fields.One2many('rma.issue.line', 'order_id', string='Order Lines', copy=False)
    repair_count = fields.Float(string='# Repair', compute="_repair_count")
    return_delivery_count = fields.Float(string='# Return Delivery', compute="_delivery_count", copy=False)
    priority = fields.Selection([('0', 'All'), ('1', 'Low Priority'), ('2', 'High Priority'), ('3', 'Urgent')], 'Priority', default='0', copy=False, readonly=True, states={'draft': [('readonly', False)]})
    repair_ids = fields.One2many('repair.order', 'issue_id', string="Repair", copy=False)
    is_credit = fields.Boolean(string="Is Credit", compute='check_return_purpose', store=True, copy=False)
    is_replace = fields.Boolean(string="Is Replace", compute='check_return_purpose', store=True, copy=False)
    is_repair = fields.Boolean(string="Is Repair", compute='check_return_purpose', store=True, copy=False)
    state = fields.Selection([
                ('draft', 'Draft'),
                ('confirm', 'Confirmed'),
                ('approve', 'Approved'),
                ('cancel', 'Cancelled'),
                ('reject', 'Reject'),
                ('done', 'Done'),
            ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    location_id = fields.Many2one('stock.location', string="Source Location", default=_default_source_location, readonly=True, states={'draft': [('readonly', False)]}, domain=[('usage', '=', 'customer')])
    location_dest_id = fields.Many2one('stock.location', string="Destination Location", default=_default_dest_location, readonly=True, states={'draft': [('readonly', False)]}, domain=[('usage', '=', 'internal')])
    invoice_ids = fields.Many2many('account.invoice', string='Invoice')
    # invoice_ids = fields.Many2many('account.move', compute="_get_invoice_ids", string='Invoice')
    invoice_count = fields.Integer(compute="_get_invoice_ids", string='Invoice')
    approved_by = fields.Many2one('res.users', string="Approved By", readonly=True, copy=False)
    approved_date = fields.Datetime(string="Approved Date", readonly=True, copy=False)
    reject_by = fields.Many2one('res.users', string="Rejected By", readonly=True, copy=False)
    reject_date = fields.Datetime(string="Rejected Date", readonly=True, copy=False)
    confirm_by = fields.Many2one('res.users', string="Confirmed By", readonly=True, copy=False)
    confirm_date = fields.Datetime(string="Confirmed Date", readonly=True, copy=False)
    cancel_by = fields.Many2one('res.users', string="Cancelled By", readonly=True, copy=False)
    cancel_date = fields.Datetime(string="Cancelled Date", readonly=True, copy=False)
    done_by = fields.Many2one('res.users', string="Repaired By", readonly=True, copy=False)
    done_date = fields.Datetime(string="Repaired Date", readonly=True, copy=False)
    is_refund_done = fields.Boolean('Refund Done', compute="check_refund_done")

    @api.multi
    def check_refund_done(self):
        for rec in self:
            line_ids = rec.issue_line_ids.filtered(lambda l: l.return_type_id.return_purpose == 'credit' and not l.invoice_id)
            rec.is_refund_done = False
            if not line_ids:
                rec.is_refund_done = True

    @api.multi
    def unlink(self):
        """
            Override method for apply constraint on delete record
        """
        for rma in self:
            if rma.state not in ('draft', 'cancel'):
                raise UserError(_('You can not delete a RMA which are not in draft or cancel state! Try to cancel it before.'))
        return super(RmaIssue, self).unlink()

    @api.multi
    def confirm_rma(self):
        """
            Confirm RMA record
        """
        for rec in self:
            if not rec.partner_id:
                raise UserError(_('Please Select Customer for create replacement order!'))
            if not rec.issue_line_ids:
                raise UserError(_('Please create some return lines!'))
            rec.confirm_by = self.env.uid
            rec.confirm_date = fields.Datetime.now()
            rec.state = 'confirm'

    @api.multi
    def approve_rma(self):
        """
            Approve RMA record
        """
        for rec in self:
            if not rec.issue_line_ids:
                raise UserError(_('Please create some return Lines!'))
            if rec.issue_line_ids.filtered(lambda l: not l.return_type_id or not l.reason_id):
                raise UserError(_('Please Select Return Type/Reason in Return lines!'))
            rec.approved_by = self.env.uid
            rec.approved_date = fields.Datetime.now()
            rec.state = 'approve'

    @api.multi
    def reject_rma(self):
        """
            Reject RMA record
        """
        for rec in self:
            rec.reject_by = self.env.uid
            rec.reject_date = fields.Datetime.now()
            rec.state = 'reject'

    @api.multi
    def done_rma(self):
        """
            Set to done RMA record
        """
        try:
            done_template_id = self.env.ref('sync_rma.email_template_done_rma_issue')
        except ValueError:
            done_template_id = False

        for rec  in self:
            rec.done_by = self.env.uid
            rec.done_date = fields.Datetime.now()
            rec.state = 'done'
            if done_template_id:
                done_template_id.send_mail(rec.id, force_send=True, raise_exception=True)

    @api.multi
    def set_to_draft(self):
        """
            Set to draft RMA record
        """
        for rec in self:
            rec.state = 'draft'

    @api.multi
    def rma_cancel(self):
        """
            Set to cancel RMA record
        """
        for rec in self:
            rec.state = 'cancel'
            rec.cancel_by = self.env.uid
            rec.cancel_date = fields.Datetime.now()

    @api.model
    def create(self, vals):
        """
            Override method for generate sequence
        """
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('rma.issue') or _('New')
        return super(RmaIssue, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
            Set partner invoice and shipping ids
        """
        for rec in self:
            if rec.partner_id:
                addr = rec.partner_id.address_get(['delivery', 'invoice'])
                rec.partner_invoice_id = addr['invoice']
                rec.partner_shipping_id = addr['delivery']

    @api.multi
    def action_generate_receipt(self):
        """
            Rma issue return qty when generating return picking receipt.
        """
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        move_line_obj = self.env['stock.move.line']
        for rec in self:
            rec.is_receipt = True
            if rec.associated_so and rec.associated_so.picking_ids:
                for pick in rec.associated_so.picking_ids.filtered(lambda l: l.state == 'done' and l.picking_type_id.code in ['outgoing', 'internal']):
                    if rec.associated_so.name in pick.origin:
                        default_values = self.env['stock.return.picking'].with_context(active_id=pick.id, return_line=self.issue_line_ids.ids).default_get(['product_return_moves', 'move_dest_exists', 'original_location_id', 'parent_location_id', 'location_id'])
                        stock_return_picking_id = self.env['stock.return.picking'].with_context(active_id=pick.id).create(default_values)
                        return_picking_id = stock_return_picking_id.with_context(return_rma_issue_id=self.id)._create_returns()
            else:
                picking_type_id = self.env['stock.picking.type'].search([('warehouse_id.company_id', '=', self.company_id.id), ('code', '=', 'incoming')], limit=1)
                # if rec.picking_id and rec.picking_id.picking_type_id and rec.picking_id.picking_type_id.return_picking_type_id:
                #     picking_type_id = rec.picking_id.picking_type_id.return_picking_type_id
                if not picking_type_id:
                    raise UserError(_("There are not any return picking type is available!"))
                picking_id = picking_obj.create({
                        'partner_id': rec.partner_id.id,
                        'location_id': rec.location_id.id,
                        'location_dest_id': rec.location_dest_id.id,
                        'picking_type_id': picking_type_id.id,
                        'company_id': rec.company_id.id,
                        'origin': rec.name,
                        'move_type': 'direct',
                        'return_rma_issue_id': rec.id
                    })
                for line in rec.issue_line_ids:
                    move_id = move_obj.create({
                            'picking_id': picking_id.id,
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.to_return,
                            'product_uom': line.product_uom.id,
                            'location_id': picking_id.location_id.id,
                            'location_dest_id': picking_id.location_dest_id.id,
                            'name': line.product_id.name,
                            'serial_id': line.serial_id.id,
                            'origin': rec.name,
                            'warehouse_id': picking_id.picking_type_id.warehouse_id.id,
                            'picking_type_id': picking_id.picking_type_id.id,
                            })
                    line.move_id = move_id.id
                picking_id.action_assign()
                for line in rec.issue_line_ids.filtered(lambda l: l.serial_id):
                    move_line_id = picking_id.move_line_ids.filtered(lambda l: l.move_id.id == line.move_id.id)
                    if move_line_id:
                        move_line_id[0].lot_id = line.serial_id.id
                    else:
                        move_line_obj.create({
                            'picking_id': picking_id.id,
                            'move_id': line.move_id.id,
                            'product_id': line.product_id.id,
                            'product_uom_id': line.product_uom.id,
                            'qty_done': line.to_return,
                            'location_id': picking_id.location_id.id,
                            'location_dest_id': picking_id.location_dest_id.id,
                            'lot_id': line.serial_id.id,
                        })
            form_view = self.env.ref('stock.view_picking_form')
            tree_view = self.env.ref('stock.vpicktree')
            picking_id = picking_obj.search([('return_rma_issue_id', '=', rec.id)])
            picking_dict = {
                'name': 'Picking',
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'domain': [('return_rma_issue_id', '=', rec.id)],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'nodestroy': True
            }
            if len(picking_id) == 1:
                picking_dict.update({
                    'views': [(form_view.id, 'form')],
                    'res_id': picking_id.id,
                })
            else:
                picking_dict.update({
                    'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
                })
            return picking_dict

    @api.multi
    def action_rma_replace(self):
        """
            Create so based on rma replace product.
        """
        self.ensure_one()
        reasons = self.issue_line_ids.filtered(lambda l: l.return_type_id.return_purpose == 'replace' and l.to_return > 0).mapped('return_type_id').mapped('name')
        sale_id = self.env['sale.order'].create({
                                         'partner_id': self.partner_id.id,
                                         'partner_invoice_id': self.partner_invoice_id.id,
                                         'partner_shipping_id': self.partner_shipping_id.id,
                                         'date_order': fields.Datetime.now(),
                                         'origin': self.name,
                                         'rma_issue_id': self.id,
                                         'note': 'Create replacement sale order because of the : ' + ', '.join(reasons) + 'reasons of ' + self.name + ' issue.',
                                         'user_id': self.env.uid
                                     })
        sale_id.onchange_partner_id()
        for rec in self.issue_line_ids:
            if rec.return_type_id.return_purpose == 'replace' and rec.to_return > 0:
                line_id = self.env['sale.order.line'].create({
                            'product_id': rec.product_id.id,
                            'name': rec.product_id.name,
                            'product_uom_qty': rec.to_return,
                            'price_unit': rec.sale_line_id.price_unit,
                            'product_uom': rec.product_uom.id,
                            'order_id': sale_id.id,
                            'issue_line_id': rec.id
                        })
                line_id.product_id_change()
                rec.sale_id = sale_id.id
        if sale_id:
            self.write({'order_ref_id': sale_id.id})
        form_view = self.env.ref('sale.view_order_form')
        return {
            'name': 'Quotation',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'views': [(form_view.id, 'form')],
            'res_id': sale_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True
        }

    @api.multi
    def rma_repair(self):
        """
            Create repair order
        """
        repair_obj = self.env['repair.order']
        wh_id = self.env.ref('stock.warehouse0')
        wh_stock_id = wh_id.lot_stock_id.id
        ICPSudo = self.env['ir.config_parameter'].sudo()
        for issue_line in self.issue_line_ids:
            if issue_line.return_type_id.return_purpose == 'repair' and issue_line.product_id.type != 'service' and issue_line.to_return > 0:
                order_data = {
                    'location_id': wh_stock_id,
                    # 'location_dest_id': wh_stock_id,
                    'partner_id': self.partner_id.id,
                    'address_id': self.partner_id.id,
                    'product_id': issue_line.product_id.id,
                    'product_qty': issue_line.to_return,
                    'product_uom': issue_line.product_uom.id,
                    # 'sale_id': self.associated_so.id,
                    'invoice_method': ICPSudo.get_param('sync_rma.invoice_method', 'none'),
                    'partner_invoice_id': self.partner_invoice_id.id if self.partner_invoice_id else self.partner_id.id,
                    'lot_id': issue_line.serial_id.id,
                    'issue_id': self.id,
                    'issue_line_id': issue_line.id,
                    'internal_notes': "Create repair order because of " + issue_line.return_type_id.name
                }
                repair_order = repair_obj.create(order_data)
                issue_line.repair_id = repair_order.id
        form_view = self.env.ref('repair.view_repair_order_form')
        tree_view = self.env.ref('repair.view_repair_order_tree')
        result = {
            'name': 'Repair',
            'view_mode': 'form',
            'res_model': 'repair.order',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('id', 'in', self.repair_ids.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True
        }
        if len(self.repair_ids) > 1:
            result['domain'] = [('id', 'in', self.repair_ids.ids)]
        elif len(self.repair_ids) == 1:
            result['views'] = [(form_view.id, 'form')]
            result['res_id'] = self.repair_ids.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    @api.multi
    def action_view_credit_memo(self):
        """
            Show credit invoice
        """
        if self.invoice_ids:
            action = self.env.ref('account.action_move_out_invoice_type').read()[0]
            if len(self.invoice_ids) > 1:
                action['domain'] = [('id', 'in', self.invoice_ids.ids)]
            elif len(self.invoice_ids) == 1:
                action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
                action['res_id'] = self.invoice_ids.id
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action

    @api.multi
    def action_view_return_delivery(self):
        """
            Show return delivery
        """
        picking_ids = self.env['stock.picking'].search(['|', ('return_rma_issue_id', '=', self.id), ('rma_issue_id', '=', self.id)])
        if picking_ids:
            action = self.env.ref('stock.action_picking_tree_all').read()[0]
            if len(picking_ids) > 1:
                action['domain'] = [('id', 'in', picking_ids.ids)]
            elif len(picking_ids) == 1:
                action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
                action['res_id'] = picking_ids.ids[0]
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action

    @api.multi
    def action_view_repair_order(self):
        """
            Show repair order
        """
        self.ensure_one()
        form_view = self.env.ref('repair.view_repair_order_form')
        tree_view = self.env.ref('repair.view_repair_order_tree')

        result = {
            'name': 'Repair',
            'view_mode': 'form',
            'res_model': 'repair.order',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('id', 'in', self.repair_ids.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True
        }

        if len(self.repair_ids) > 1:
            result['domain'] = [('id', 'in', self.repair_ids.ids)]
        elif len(self.repair_ids) == 1:
            result['views'] = [(form_view.id, 'form')]
            result['res_id'] = self.repair_ids.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    @api.multi
    def action_view_replace_so(self):
        """
            Show replacement sales order
        """
        self.ensure_one()
        form_view = self.env.ref('sale.view_order_form')
        return {
            'name': 'Sale Order',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'views': [(form_view.id, 'form')],
            'res_id': self.order_ref_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True
        }

    @api.multi
    def rma_issue_print(self):
        """
            Print RMA report
        """
        return self.env.ref('sync_rma.action_report_rma_issue_order').report_action(self)

    @api.multi
    def action_rma_quotation_send(self):
        """
            This function opens a window to compose an email, with the RMA issue template message loaded by default
        """
        # ir_model_data = self.env['ir.model.data']
        try:
            template_id = self.env.ref('sync_rma.email_template_rma_issue').id
        except ValueError:
            template_id = False

        try:
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'rma.issue',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_rma_issue_as_sent': True,
        })
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class RmaIssueLine(models.Model):
    _name = 'rma.issue.line'
    _description = 'RMA Issue Lines'

    @api.multi
    def calculate_state(self):
        """
            Calculate line state depnds on repair, replace or credit line
        """
        for rec in self:
            if rec.repair_id and rec.return_type_id.return_purpose == 'repair':
                rec.state = dict(rec.repair_id._fields['state'].selection).get(rec.repair_id.state)
            elif rec.sale_id and rec.return_type_id.return_purpose == 'replace':
                rec.state = dict(rec.sale_id._fields['state'].selection).get(rec.sale_id.state)
            elif rec.invoice_id and rec.return_type_id.return_purpose == 'credit':
                rec.state = dict(rec.invoice_id._fields['state'].selection).get(rec.invoice_id.state)
            else:
                # add temparary to resolve issue
                rec.state = ''

    order_id = fields.Many2one('rma.issue', string='Issue Reference')
    product_id = fields.Many2one('product.product', string='Product', required=True, domain=[('type', 'in', ['consu', 'product'])])
    serial_id = fields.Many2one('stock.production.lot', string="Serial No.", copy=False)
    qty_delivered = fields.Float(string='Delivered Qty', copy=False, digits=dp.get_precision('Product Unit of Measure'), default=0.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    to_return = fields.Float(string='Return Qty')
    reason_id = fields.Many2one('return.reason', string="Reason")
    sale_line_id = fields.Many2one('sale.order.line', string="Sale line")
    return_type_id = fields.Many2one('return.type', string="Return Type")
    state = fields.Char(string="Status", compute='calculate_state')
    repair_id = fields.Many2one('repair.order', string="Repair")
    sale_id = fields.Many2one('sale.order', string="Replace Sale")
    invoice_id = fields.Many2one('account.invoice', string="Credit Memo")
    move_id = fields.Many2one('stock.move', string="Move", copy=False)

    @api.model
    def default_get(self, fields):
        """
            Override method for check constraint
        """
        res = super(RmaIssueLine, self).default_get(fields)
        context = dict(self.env.context)
        if context.get('associated_so'):
            raise UserError(_('Please create lines using generate lines button!'))
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        """
            Set delivered and return quantities
        """
        for rec in self:
            if rec.product_id:
                rec.product_uom = rec.product_id.uom_id.id
                rec.qty_delivered = 1.0
                rec.to_return = 1.0

    @api.constrains('to_return')
    def check_repair_qty(self):
        """
            Check return quantity constraints
        """
        for record in self:
            if record.to_return > record.qty_delivered:
                raise ValidationError(_('Return Quantity Must Be less then Delivered Quantity'))
            if record.to_return <= 0.0:
                raise ValidationError(_('Return Quantity Must Be greter then 0.0!'))
            if record.serial_id and record.to_return > 1:
                raise ValidationError(_('Serial number product Return Quantity should be 1!'))


class ReturnReason(models.Model):
    _name = 'return.reason'
    _description = 'Return Reason'

    name = fields.Char('Name', required=True)


class ReturnType(models.Model):
    _name = 'return.type'
    _description = 'Return Type'

    name = fields.Char('Name', required=True)
    return_purpose = fields.Selection([
                ('credit', 'Credit'),
                ('replace', 'Replace'),
                ('repair', 'Repair')
                ], string='Return Type', copy=False, required=True)
