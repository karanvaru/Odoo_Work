from odoo import fields, models, api, _
from odoo.tools.translate import _
from odoo.tools import html2plaintext
from odoo.exceptions import Warning, AccessError


class ResUsers(models.Model):
    _inherit = "res.users"

    default_section_id = fields.Many2one('crm.team', string="Default Sales Team")


class CRMLead(models.Model):
    _inherit = "crm.lead"

    @api.multi
    def _resolve_section_id_from_context(self):
        if self._context is None:
            self._context = {}
        if type(self._context.get('default_section_id')) in (int, int):
            return self._context.get('default_section_id')
        if isinstance(self._context.get('default_section_id'), str):
            section_ids = self.env['crm.team'].name_search(name=self._context['default_section_id'])
            if len(section_ids) == 1:
                return int(section_ids[0][0])
        return None


class CRMClaim(models.Model):
    _name = "crm.claim.ept"
    _description = 'RMA CRM Claim'
    _order = "priority,date desc"
    _inherit = ['mail.thread']

    @api.constrains('picking_id')
    def check_picking_id(self):
        for record in self:
            if not record.sale_id:
                if not record.picking_id.rma_sale_id:
                    raise Warning("Sale Order not found in delivery, Please select valid delivery with sale order")

    @api.model
    def default_get(self, default_fields):
        res = super(CRMClaim, self).default_get(default_fields)
        picking = self.env['stock.picking'].search([('id', '=', self._context.get('active_id'))])
        if picking:
            res['picking_id'] = picking.id
        return res

    @api.multi
    def _get_default_section_id(self):
        return self.env['crm.lead']._resolve_section_id_from_context() or False

    @api.depends('picking_id')
    @api.multi
    def get_product_ids(self):
        product_ids = []
        for record in self:
            if not record.picking_id:
                continue
            for move in record.picking_id.move_lines:
                product_ids.append(move.product_id.id)
            record.move_product_ids = [(6, 0, product_ids)]

    @api.depends('claim_line_ids.product_id')
    @api.multi
    def get_line_product_ids(self):
        for record in self:
            lines = [p for p in self.claim_line_ids]
            record.move_product_ids = [(6, 0, [p.product_id.id for p in lines])]

    @api.onchange('picking_id')
    def onchange_picking_id(self):
        claim_lines = []
        crm_calim_line_obj = self.env['claim.line.ept']
        if self.picking_id:
            self.partner_id = self.picking_id.partner_id.id
            self.partner_phone = self.picking_id.partner_id.phone
            self.email_from = self.picking_id.partner_id.email
            self.sale_id = self.picking_id.sale_id.id
            self.partner_delivery_id = self.picking_id.sale_id and self.picking_id.sale_id.partner_shipping_id and self.picking_id.sale_id.partner_shipping_id.id or self.picking_id.rma_sale_id and self.picking_id.rma_sale_id.partner_shipping_id and self.picking_id.rma_sale_id.partner_shipping_id.id or False
            for move_id in self.picking_id.move_lines:
                previous_claimline_ids = crm_calim_line_obj.search([('move_id', '=', move_id.id), ('product_id', '=', move_id.product_id.id)])
                if previous_claimline_ids:
                    returned_qty = 0
                    for line_id in previous_claimline_ids:
                        returned_qty += line_id.quantity
                
                    if returned_qty < move_id.quantity_done:
                        qty = move_id.quantity_done - returned_qty
                        claim_lines.append({'product_id':move_id.product_id.id,
                                            'quantity':qty,
                                            'move_id':move_id.id})
                        
                else:
                     claim_lines.append({'product_id':move_id.product_id.id,
                                        'quantity':move_id.quantity_done,
                                        'move_id':move_id.id})
            self.claim_line_ids = claim_lines

    @api.onchange('sale_id')
    def onchange_sale_id(self):
        if self.sale_id:
            self.section_id = self.sale_id.team_id

    @api.depends('picking_id')
    @api.model
    def get_products(self):
        for record in self:
            move_products = []
            for move in record.picking_id.move_lines:
                move_products.append(move.product_id.id)
            record.move_product_ids = [(6, 0, move_products)]

    @api.multi
    def get_so(self):
        for record in self:
            if record.picking_id:
                record.sale_id = record.picking_id.sale_id.id

    @api.multi
    def get_is_visible(self):
        for record in self:
            record.is_visible = False
            if record.return_picking_id and record.return_picking_id.state == 'done':
                record.is_visible = True
                if record.state == 'approve':
                    record.write({'state': 'process'})
            if self.is_rma_without_incoming:
                record.is_visible = True
                if record.state == 'approve':
                    record.write({'state': 'process'})
                    
                    
    active = fields.Boolean(string='Active', default=1)
    is_visible = fields.Boolean(string='Is Visible', compute=get_is_visible, default=False)
    rma_send = fields.Boolean(string="RMA Send")
    is_rma_without_incoming = fields.Boolean(string="Is RMA Without Incoming", default=False)
    is_return_internal_transfer = fields.Boolean(string="Is Return Internal Trnafer", default=False)
     
    code = fields.Char(string='RMA Number', default="New", readonly=True, copy=False)
    name = fields.Char(string='Subject', required=True)
    action_next = fields.Char(string='Next Action', copy=False)
    user_fault = fields.Char(string='Trouble Responsible')
    email_from = fields.Char(string='Email', size=128, help="Destination email for email gateway.")
    partner_phone = fields.Char(string='Phone')
    
    email_cc = fields.Text(string='Watchers Emails', size=252, help="These email addresses will be added to the CC field of all inbound and outbound emails for this record before being sent. Separate multiple email addresses with a comma")
    description = fields.Text(string='Description')
    resolution = fields.Text(string='Resolution', copy=False)
    cause = fields.Text(string='Root Cause')
    
    date_deadline = fields.Date(string='Deadline', copy=False)
    date_action_next = fields.Datetime(string='Next Action Date', copy=False)
    create_date = fields.Datetime(string='Creation Date', readonly=True, copy=False)
    write_date = fields.Datetime(string='Update Date', readonly=True, copy=False)
    date_closed = fields.Datetime(string='Closed', readonly=True, copy=False)
    date = fields.Datetime(string='Date', Index=True, default=fields.Datetime.now, copy=False)
    priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High')], string='Priority', default="1")
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('process', 'Processing'), ('close', 'Closed'), ('reject', 'Rejected')], default='draft', copy=False, track_visibility="onchange")
    
    type_action = fields.Selection([('correction', 'Corrective Action'), ('prevention', 'Preventive Action')], string='Action Type')
    user_id = fields.Many2one('res.users', string='Responsible', track_visibility='always', default=lambda self: self._uid)
    section_id = fields.Many2one('crm.team', string='Sales Channel', index=True, default=lambda self: self._get_default_section_id(), help="Responsible sales channel." " Define Responsible user and Email account for" "mail gateway.")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('crm.case'))
    partner_id = fields.Many2one('res.partner', string='Partner')
    invoice_id = fields.Many2one("account.invoice", string="Invoice", copy=False)
   
    sale_id = fields.Many2one('sale.order', string="Sale Order", compute=get_so)
    reject_message_id = fields.Many2one("claim.reject.message", string="Reject Reason", copy=False)
    new_sale_id = fields.Many2one('sale.order', string='New Sale Order', copy=False)
    location_id = fields.Many2one('stock.location', string='Return Location', domain=[('usage', '=', 'internal')])
    internal_picking_id = fields.Many2one('stock.picking', string='Internal Delivery Order', default=False, copy=False)
    picking_id = fields.Many2one('stock.picking', string='Delivery Order')
    return_picking_id = fields.Many2one('stock.picking', string='Return Delivery Order', default=False, copy=False)
    rma_support_person_id = fields.Many2one("res.partner", string="Contact Person")
    partner_delivery_id = fields.Many2one('res.partner', string='Partner Delivery Address') 
    
    claim_line_ids = fields.One2many("claim.line.ept", "claim_id", string="Return Line")
 
    move_product_ids = fields.Many2many('product.product', string="Products", compute=get_products)
    to_return_picking_ids = fields.Many2many('stock.picking', string='Return Delivery Orders', default=False, copy=False)
    refund_invoice_ids = fields.Many2many('account.invoice', string='Refund Invoices', copy=False)

    @api.model
    def create(self, vals):
        context = dict(self._context or {})
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('crm.claim.ept')
        if vals.get('section_id') and not context.get('default_section_id'):
            context['default_section_id'] = vals.get('section_id')
        res = super(CRMClaim, self).create(vals)
        reg = {
            'res_id': res.id,
            'res_model': 'crm.claim.ept',
            'partner_id': res.partner_id.id,
        }
        if not self.env['mail.followers'].search([('res_id', '=', res.id), ('res_model', '=', 'crm.claim.ept'), ('partner_id', '=', res.partner_id.id)]):
            follower_id = self.env['mail.followers'].create(reg)
        
        if res.rma_support_person_id:
            if not self.env['mail.followers'].search([('res_id', '=', res.id), ('res_model', '=', 'crm.claim.ept'), ('partner_id', '=', res.rma_support_person_id.id)]):
                reg.update({"partner_id":res.rma_support_person_id.id})
                self.env['mail.followers'].create(reg)
        return res
    
    
    @api.multi
    def write(self, vals):
        res = super(CRMClaim, self).write(vals)
        if vals.get('rma_support_person_id'):
            if not self.env['mail.followers'].search([('res_id', '=', self.id), ('res_model', '=', 'crm.claim.ept'), ('partner_id', '=', vals.get('rma_support_person_id'))]):
                follo_vals = {'res_id': self.id,
                            'res_model': 'crm.claim.ept',
                            "partner_id":vals.get('rma_support_person_id')}
                self.env['mail.followers'].create(follo_vals)
        
        return res
    
    @api.multi
    def create_contact_partner(self):
        context = dict(self._context) or {}
        context.update({'current_partner_id': self.partner_id.id, 'record': self.id or False, "is_create_contact_person":True})
        return {'name': 'Add New Contact Person',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'create.partner.delivery.address.ept',
                'type': 'ir.actions.act_window',
                'context': context,
                'target': 'new'}

    @api.multi
    def add_delivery_address(self):
        context = dict(self._context) or {}
        context.update({'current_partner_id': self.partner_id and self.partner_id.id or False, 'record':self.id or False})
        return {'name': 'Add New Delivery Address',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'create.partner.delivery.address.ept',
                'type': 'ir.actions.act_window',
                'context': context,
                'target': 'new' }

    @api.multi
    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise Warning(_("Claim cannot be delete once it Processed."))
        return super(CRMClaim, self).unlink()

    @api.multi
    def create_return_picking(self, claim_lines=False):
        stock_picking_obj = self.env['stock.picking']
        location_id = self.location_id.id
        vals = {'picking_id': self.return_picking_id.id if claim_lines else self.picking_id.id}
        if location_id and not claim_lines:
            vals.update({'location_id': location_id})
        return_picking_wizard = self.env['stock.return.picking'].with_context(
            active_id=self.return_picking_id.id if claim_lines else self.picking_id.id).create(vals)
        return_lines = []
        lines = claim_lines or self.claim_line_ids
        for line in lines:
            move_id = self.env['stock.move'].search([('product_id', '=', line.product_id.id), (
            'picking_id', '=', self.return_picking_id.id if claim_lines else self.picking_id.id),
                                                     ('sale_line_id', '=', line.move_id.sale_line_id.id)])
            return_line = self.env['stock.return.picking.line'].create(
                {'product_id': line.product_id.id, 'quantity': line.quantity, 'wizard_id': return_picking_wizard.id,
                 'move_id': move_id.id})
            return_lines.append(return_line.id)
        return_picking_wizard.write({'product_return_moves': [(6, 0, return_lines)]})
        new_picking_id, pick_type_id = return_picking_wizard._create_returns()
        if claim_lines:
            self.write({'to_return_picking_ids': [(4, new_picking_id)]})
        else:
            self.return_picking_id = new_picking_id
        if self.location_id:
            stock_picking_id = stock_picking_obj.browse(new_picking_id)
            internal_picking_id = stock_picking_obj.search([('group_id', '=', stock_picking_id.group_id.id), ('location_id', '=', self.location_id.id), ('picking_type_id.code', '=', 'internal'), ('state', 'not in', ['cancel', 'draft'])])
            if claim_lines:
                 self.write({'internal_picking_ids':[(4, internal_picking_id.id)]})
            else:
                self.internal_picking_id = internal_picking_id
            self.is_return_internal_transfer = True
            internal_picking_id.write({'claim_id': self.id})
        return True
    
    
    

    @api.multi
    def approve_claim(self):
        crm_calim_line_obj = self.env['claim.line.ept']
        processed_product_list = []
        if len(self.claim_line_ids) <= 0:
            raise Warning(_("Please set return products."))
        total_qty = 0
        for line in self.claim_line_ids:
            moves = line.search([('move_id', '=', line.move_id.id)])
            for m in moves:
                if m.claim_id.state in ['process', 'approve', 'close']:
                    total_qty += m.quantity
            if total_qty >= line.move_id.quantity_done:
                processed_product_list.append(line.product_id.name)
                
                
            for move_id in self.picking_id.move_lines:
                previous_claimline_ids = crm_calim_line_obj.search([('move_id', '=', move_id.id), ('product_id', '=', move_id.product_id.id), ('claim_id.state', '=', 'close')])
                if previous_claimline_ids:
                    returned_qty = 0
                    for line_id in previous_claimline_ids:
                        returned_qty += line_id.quantity
                
                    if returned_qty < move_id.quantity_done:
                        qty = move_id.quantity_done - returned_qty
                        if line.quantity > qty:
                           raise Warning(_("You have already one time process RMA. So You need to check Product Qty"))
       
        if processed_product_list:
            raise Warning(_('%s Product\'s delivered quantites were already processed for RMA' % (
                ", ".join(processed_product_list))))
        for line in self.claim_line_ids:
            if line.quantity <= 0 or not line.rma_reason_id:
                raise Warning(_("Please set Return Quantity and Reason for all products."))
        self.write({'state': 'approve'})
        if self.is_rma_without_incoming:
            self.write({'state': 'process'})
        else:
            self.create_return_picking()
        self.action_rma_send_email()
        return True

    def action_rma_send_email(self):
        email_template = self.env.ref('rma_ept.mail_rma_details_notification_ept', False)
        mail_mail = email_template and email_template.send_mail(self.id) or False
        mail_mail and self.env['mail.mail'].browse(mail_mail).send()

    @api.multi
    def reject_claim(self):
        return {
            'name': "Reject Claim",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'claim.process.wizard',
            'view_id': self.env.ref('rma_ept.view_claim_reject_ept').id,
            'type': 'ir.actions.act_window',
            'context': {'claim_lines': self.claim_line_ids.ids},
            'target': 'new'
        }

    @api.multi
    def set_to_draft(self):
        if self.return_picking_id and self.return_picking_id.state != 'draft':
            if self.return_picking_id.state in ['cancel', 'done']:
                raise Warning("Claim cannot be move draft state once it Receipt is done or cancel.")
            else:
                self.return_picking_id.action_cancel()
        if self.internal_picking_id and self.internal_picking_id.state != 'draft':
            self.internal_picking_id.action_cancel()
            self.is_return_internal_transfer = False
        self.write({'state': 'draft'})

    @api.multi
    def show_return_picking(self):
        if len(self.return_picking_id) == 1:
            return {
                'name': "Receipt",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'type': 'ir.actions.act_window',
                'res_id': self.return_picking_id.id
            }
        else:
            return {'name': "Receipt",
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'stock.picking',
                'type': 'ir.actions.act_window',
                'domain': [('id', '=', self.return_picking_id.id)]}
            

    @api.multi
    def show_delivery_picking(self):
        if len(self.to_return_picking_ids.ids) == 1:
            return {
                'name': "Delivery",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'type': 'ir.actions.act_window',
                'res_id': self.to_return_picking_ids.id
            }
        else:
            return {
                'name': "Deliveries",
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'stock.picking',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', self.to_return_picking_ids.ids)]
            }


    @api.multi
    def show_internal_transfer(self):
        """
        author:bhavesh jadav 11/4/2019
        func:this method use for button click event and open from view for internal transfer.
        :return:dict for open form
        """
        form = self.env.ref('stock.view_picking_form', False)
        if len(self.internal_picking_id) == 1:
            return {'name': "Internal Transfer",
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id':form.id,
                    'res_model': 'stock.picking',
                    'type': 'ir.actions.act_window',
                    'res_id':self.internal_picking_id.id,
                    'target': 'current'}
        else:
            return {'name': "Internal Transfer's",
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'stock.picking',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', self.internal_picking_id.ids)] }
           
            
    @api.multi
    def action_claim_reject_process_ept(self):
        return {
            'name': "Reject Claim",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'claim.process.wizard',
            'view_id': self.env.ref('rma_ept.view_claim_reject_ept').id,
            'type': 'ir.actions.act_window',
            'context': {'claim_lines': self.claim_line_ids.ids},
            'target': 'new'
        }

    @api.multi
    def act_supplier_invoice_refund_ept(self):
        if len(self.refund_invoice_ids) == 1:
            view_id = self.env.ref('account.invoice_form').id
            return {
                'name': "Customer Invoices",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'view_id': view_id,
                'res_id': self.refund_invoice_ids.id
            }
        else:
            return {
                'name': "Customer Invoices",
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'views': [(self.env.ref('account.invoice_tree').id, 'tree'),
                          (self.env.ref('account.invoice_form').id, 'form')],
                'domain': [('id', 'in', self.refund_invoice_ids.ids), ('type', '=', 'out_refund')]
            }

    @api.multi
    def act_new_so_ept(self):
        return {
            'name': "Sale Order",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'res_id': self.new_sale_id.id
        }

    @api.multi
    def process_claim(self):
        if self.state != 'process':
            raise Warning("Claim can't process.")
        if self.return_picking_id.state != 'done'and not self.is_rma_without_incoming:
            raise Warning("Please first validate Return Picking Order.")
        if self.internal_picking_id and self.internal_picking_id.state != 'done':
            raise Warning("Please first validate Internal Transfer Picking Order.")
        return_lines = []
        refund_lines = []
        do_lines = []
        so_lines = []
        for line in self.claim_line_ids:
            if self.return_picking_id and self.return_picking_id.state == 'done' and not line.claim_type:
                raise Warning(_("Please set apporpriate Action for all rma lines."))
            if self.is_rma_without_incoming and not line.claim_type:
                raise Warning(_("Please set appropriate Action for all rma lines."))
            if line.claim_type == 'replace':
                if not line.to_be_replace_product_id or line.to_be_replace_quantity <= 0:
                    raise Warning("Claim line with product %s has Replace product or Replace quantity or both not set." % (line.product_id.name))
            if line.claim_type == 'repair':
                if self.is_rma_without_incoming:
                    do_lines.append(line)
                else:
                    return_lines.append(line)
            if line.claim_type == 'refund':
                line.update({'is_create_refund':True})
                refund_lines.append(line)
            if line.claim_type == 'replace':
                if not line.is_create_invoice:
                    do_lines.append(line)
                else:
                    if line.is_create_refund and line.is_create_invoice:
                        so_lines.append(line)
                        self.create_refund(line)
                    else:
                        so_lines.append(line)
        return_lines and self.create_return_picking(return_lines)
        refund_lines and self.create_refund(refund_lines)
        do_lines and self.create_do(do_lines)
        so_lines and self.create_so(so_lines)
        self.state = 'close'
        self.action_rma_send_email()
        return self

    @api.multi
    def create_so(self, lines):
        sale_order = self.env['sale.order']
        order_vals = {
            'company_id': self.company_id.id,
            'partner_id': self.partner_id.id,
            'warehouse_id': self.sale_id.warehouse_id.id,
        }
        new_record = sale_order.new(order_vals)
        new_record.onchange_partner_id()
        order_vals = sale_order._convert_to_write({name: new_record[name] for name in new_record._cache})
        new_record = sale_order.new(order_vals)
        new_record.onchange_partner_shipping_id()
        order_vals = sale_order._convert_to_write({name: new_record[name] for name in new_record._cache})
        order_vals.update({
            'state': 'draft',
            'team_id': self.section_id.id,
            'client_order_ref': self.name,
        })
        so = sale_order.create(order_vals)
        self.new_sale_id = so.id
        for line in lines:
            sale_order_line = self.env['sale.order.line']
            order_line = {
                'order_id': so.id,
                'product_id': line.to_be_replace_product_id.id,
                'company_id': self.company_id.id,
                'name': line.to_be_replace_product_id.name
            }
            new_order_line = sale_order_line.new(order_line)
            new_order_line.product_id_change()
            order_line = sale_order_line._convert_to_write(
                {name: new_order_line[name] for name in new_order_line._cache})
            order_line.update({
                'product_uom_qty': line.to_be_replace_quantity,
                'state': 'draft',
            })
            sale_order_line.create(order_line)
        self.write({'new_sale_id': so.id})
        return True

    @api.multi
    def create_do(self, lines):
        do = self.env['stock.picking'].create(
            {'partner_id': self.partner_id.id, 'location_id': self.picking_id.location_id.id,
             'location_dest_id': self.picking_id.location_dest_id.id,
             'picking_type_id': self.picking_id.picking_type_id.id, 'origin': self.name,
             "rma_sale_id":self.sale_id.id})
        for line in lines:
            self.env['stock.move'].create({'location_id': self.picking_id.location_id.id, 'location_dest_id': self.picking_id.location_dest_id.id,
                'product_uom_qty': line.to_be_replace_quantity or line.quantity, 'name': line.to_be_replace_product_id.name or line.product_id.name,
                'product_id': line.to_be_replace_product_id.id or line.product_id.id, 'state': 'draft',
                'picking_id': do.id, 'product_uom': line.to_be_replace_product_id.uom_id.id or line.product_id.uom_id.id,
                'company_id': self.company_id.id})
        self.write({'to_return_picking_ids': [(4, do.id)]})
        self.sale_id.write({'picking_ids': [(4, do.id)]})
        do.action_assign()
        return True

    @api.multi
    def create_refund(self, lines):
        if not self.sale_id.invoice_ids:
            return False
        refund_invoice_ids = {}
        refund_invoice_ids_rec = []
        product_process_dict = {}
        is_create_refund = False
        for line in lines:
            if line.is_create_refund:
                if self.is_rma_without_incoming:
                    if line.id not in product_process_dict:
                        product_process_dict.update({line.id: {'total_qty': line.to_be_replace_quantity, 'invoice_line_ids': {}}})
                if line.id not in product_process_dict:
                    product_process_dict.update({line.id: {'total_qty': line.return_qty, 'invoice_line_ids': {}}})
                for invoice_line in line.move_id.sale_line_id.invoice_lines:
                    if invoice_line.invoice_id.state not in ['open', 'paid'] or invoice_line.invoice_id.type != 'out_invoice':
                        continue
                    is_create_refund = True
                    if product_process_dict.get(line.id).get('process_qty', 0) < product_process_dict.get(line.id).get(
                            'total_qty', 0):
                        if product_process_dict.get(line.id).get('process_qty',
                                                                 0) + invoice_line.quantity < product_process_dict.get(
                                line.id).get('total_qty', 0):
                            process_qty = invoice_line.quantity
                            product_process_dict.get(line.id).update({'process_qty': product_process_dict.get(line.id).get(
                                'process_qty', 0) + invoice_line.quantity})
                        else:
                            process_qty = product_process_dict.get(line.id).get('total_qty', 0) - product_process_dict.get(
                                line.id).get('process_qty', 0)
                            product_process_dict.get(line.id).update(
                                {'process_qty': product_process_dict.get(line.id).get('total_qty', 0)})
                        product_process_dict.get(line.id).get('invoice_line_ids').update(
                            {invoice_line.id: process_qty, 'invoice_id': invoice_line.invoice_id.id})
                        if refund_invoice_ids.get(invoice_line.invoice_id.id):
                            refund_invoice_ids.get(invoice_line.invoice_id.id).append(
                                {invoice_line.product_id.id: process_qty, 'price': line.move_id.sale_line_id.price_unit,
                                 'tax_id': line.move_id.sale_line_id.tax_id.ids
                                })
                        else:
                            refund_invoice_ids.update({invoice_line.invoice_id.id: [
                                {invoice_line.product_id.id: process_qty, 'price': line.move_id.sale_line_id.price_unit,
                                 'tax_id': line.move_id.sale_line_id.tax_id.ids
                                 }]})
        if not is_create_refund:
            return False
        for invoice_id, lines in refund_invoice_ids.items():
            invoice = self.env['account.invoice'].browse(invoice_id)
            refund_invoice = invoice.refund(invoice.date_invoice, invoice.date, self.name, invoice.journal_id.id)
            if not refund_invoice:
                continue
            refund_invoice and refund_invoice.invoice_line_ids and refund_invoice.invoice_line_ids.unlink()
            for line in lines:
                if not list(line.keys()) or not list(line.values()):
                    continue
                price = line.get('price')
                tax = line.get('tax_id')
                del line['price']
                del line['tax_id']
                product_id = self.env['product.product'].browse(list(line.keys())[0])
                if not product_id:
                    continue
                line_vals = self.env['account.invoice.line'].new({'product_id': product_id.id, 'name': product_id.name, 'invoice_id': refund_invoice.id, 'account_id': invoice.account_id.id})
                line_vals._onchange_product_id()
                line_vals = line_vals._convert_to_write({name: line_vals[name] for name in line_vals._cache})
                #Calculate Tax : sale order line wise @uthor:Priya Pal @date:12th March 2020.
                if tax:
                    line_vals.update({'invoice_line_tax_ids':[(6, 0, tax)]})
                else:
                    line_vals.update({'invoice_line_tax_ids':[(6, 0, [])]})
                line_vals.update({'quantity': list(line.values())[0], 'price_unit': price})
                self.env['account.invoice.line'].create(line_vals)
            refund_invoice.compute_taxes()
            refund_invoice_ids_rec.append(refund_invoice.id)
        refund_invoice_ids_rec and self.write({'refund_invoice_ids': [(6, 0, refund_invoice_ids_rec)]})

    @api.multi
    def copy(self, default=None):
        claim = self.browse(self.id)
        default = dict(default or {},
                       name=_('%s (copy)') % claim.name)
        res = super(CRMClaim, self).copy(default)
        res.onchange_picking_id()
        return res

    @api.multi
    def message_new(self, msg, custom_values=None):
        if custom_values is None:
            custom_values = {}
        desc = html2plaintext(msg.get('body')) if msg.get('body') else ' '
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'description': desc,
            'email_from': msg.get('from'),
            'email_cc': msg.get('cc'),
            'partner_id': msg.get('author_id', False),
        }
        if msg.get('priority'):
            defaults['priority'] = msg.get('priority')
        defaults.update(custom_values)
        return super(CRMClaim, self).message_new(msg, custom_values=defaults)

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super(CRMClaim, self).message_get_suggested_recipients()
        try:
            for record in self:
                if record.partner_id:
                    record._message_add_suggested_recipient(recipients, partner=record.partner_id, reason=_('Customer'))
                elif record.email_from:
                    record._message_add_suggested_recipient(recipients, email=record.email_from,
                                                            reason=_('Customer Email'))
        except AccessError:  # no read access rights -> just ignore suggested recipients because this imply modifying followers
            pass
        return recipients

    @api.multi
    def action_rma_send(self):
        self.ensure_one()
        self.rma_send = True
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('rma_ept', 'mail_rma_details_notification_ept')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'crm.claim.ept',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class CRMClaimLine(models.Model):
    _name = 'claim.line.ept'
    _description = 'CRM Claim Line'

    @api.multi
    def get_return_quantity(self):
        for record in self:
            if record.claim_id.return_picking_id:
            # Issue: While BOM type product record occurred at that time 2 move was found, because both move have the same picking_id 
            # as well sale_line_id for that reason singletone error occurred.
            # Solution: Added record product_id in domain by that filter only one move found which have same product.
		    # Last change : Priya Pal 26 July 2019 
                move_line = self.env['stock.move'].search([('picking_id', '=', record.claim_id.return_picking_id.id),
                                                           ('sale_line_id', '=', record.move_id.sale_line_id.id),
                                                           ('product_id', '=', record.product_id.id),
                                                           ('origin_returned_move_id', '=', record.move_id.id)])
                record.return_qty = move_line.quantity_done

    @api.multi
    def get_done_quantity(self):
        for record in self:
            if record.claim_id.picking_id:
                record.done_qty = record.move_id.quantity_done

    @api.constrains('quantity')
    def check_qty(self):
        for line in self:
            if line.quantity < 0:
                raise Warning(_('Quantity must be positive number'))
            elif line.quantity > line.move_id.quantity_done:
                raise Warning(_('Quantity must be less than or equal to the delivered quantity'))

    product_id = fields.Many2one('product.product', string='Product')
    done_qty = fields.Float('Delivered Quantity', compute=get_done_quantity)
    quantity = fields.Float('Return Quantity', copy=False)
    return_qty = fields.Float('Received Quantity', compute=get_return_quantity)
    claim_id = fields.Many2one('crm.claim.ept', string='Related claim', copy=False)
    claim_type = fields.Selection([('refund', 'Refund'), ('replace', 'Replace'), ('repair', 'Repair')], "Claim Type",
                                  copy=False)
    to_be_replace_product_id = fields.Many2one('product.product', "Product to be Replace", copy=False)
    to_be_replace_quantity = fields.Float("Replace Quantity", copy=False)
    is_create_invoice = fields.Boolean('Create Invoice', copy=False)
    is_create_refund = fields.Boolean(string="Create Refund", Copy=False)
    move_id = fields.Many2one('stock.move')
    rma_reason_id = fields.Many2one('rma.reason.ept', 'Reason')

    @api.multi
    def write(self, vals):
        for record in self:
            if record and record.claim_id.state == 'draft' or 'rma_reason_id' in vals:
                rma_reason = self.env['rma.reason.ept'].browse(vals.get('rma_reason_id'))
                if rma_reason and rma_reason.action:
                    record.claim_type = rma_reason.action
        return super(CRMClaimLine, self).write(vals)

    @api.multi
    def unlink(self):
        for record in self:
            if record.claim_id and record.claim_id.state != 'draft':
                raise Warning(_("Claim Line cannot be delete once it Approved."))
        return super(CRMClaimLine, self).unlink()

    @api.multi
    def action_claim_refund_process_ept(self):
        return {
            'name': 'Return Products',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'claim.process.wizard',
            'src_model': 'claim.line.ept',
            'target': 'new',
            'context': {'product_id': self.product_id.id, 'hide': True, 'claim_line_id': self.id}
        }


class CRMClaimRejectMessage(models.Model):
    _name = 'claim.reject.message'
    _description = 'CRM Claim Reject Message'

    name = fields.Char("Reject Reason", required=1)


class CRMReason(models.Model):
    _name = 'rma.reason.ept'
    _description = 'CRM Reason'

    name = fields.Char("RMA Reason", required=1)
    action = fields.Selection([('refund', 'Refund'), ('replace', 'Replace'), ('repair', 'Repair')], "Related Action")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _claim_count(self):
        for partner_id in self:
            partner_id.claim_count = self.env['crm.claim.ept'].search_count([('partner_id', '=', partner_id.id)])

    claim_count = fields.Integer(compute='_claim_count', string='# Claims')
