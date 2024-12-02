# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date, time, datetime
from openerp.exceptions import UserError,Warning

class RmaMain(models.Model):

    _name = 'rma.main'

    name = fields.Char('Name',default=lambda self: _('New'),store=True)
    is_validate = fields.Boolean("Validated",copy=False)
    sale_order = fields.Many2one('sale.order','Sale Order', required=True, domain="[('state','=','sale')]")
    subject = fields.Char('Subject')
    date = fields.Datetime('Date',default=datetime.now() ,required=True)
    deadline = fields.Datetime('Deadline')
    rma_note = fields.Text('RMA Note')
    priority = fields.Selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority')
    responsible = fields.Many2one('res.users','Responsible', store=True)
    sales_channel = fields.Many2one('crm.team','Sales Channel', store=True)
    delivery_order = fields.Many2one('stock.picking','Delivery Order',store=True)
    email = fields.Char('Email', store=True)
    partner = fields.Many2one('res.partner','Partner', store=True)
    phone = fields.Char('Phone', store=True)
    rma_line_ids = fields.One2many('rma.lines','rma_id','RMA Lines',store=True)
    reject_reason = fields.Char('Reject Reason')

    in_delivery_count = fields.Integer(string='Incoming Orders', compute='_compute_incoming_picking_ids')
    out_delivery_count = fields.Integer(string='Outgoing Orders', compute='_compute_outgoing_picking_ids')
    refund_inv_count = fields.Integer(string='Refund Invoice', compute='_compute_refund_inv_ids')
    sale_order_count = fields.Integer(string='Sale Order',compute='_compute_sale_order_ids')

    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.user.company_id)

    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('approved', 'APPROVED'),
        ('processing', 'PROCESSING'),
        ('close', 'CLOSED'),
        ('reject','REJECTED'),
        ], string='Status', default='draft')

    @api.model
    def create(self,vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('rma.order'),
        })
        return super(RmaMain, self).create(vals)

    @api.multi
    def _compute_incoming_picking_ids(self):
        for order in self:
            stock_picking_ids = self.env['stock.picking'].search([('rma_id','=',order.id)])
            order.in_delivery_count = len(stock_picking_ids)
    
    @api.multi        
    def _compute_sale_order_ids(self): 
        for order in self:
            sale_order_ids = self.env['sale.order'].search([('rma_id','=',order.id)])
            order.sale_order_count = len(sale_order_ids)

    @api.multi
    def _compute_outgoing_picking_ids(self):
        for order in self:
            stock_picking_ids = self.env['stock.picking'].search([('rma_id','=',order.id),('picking_type_code','=','outgoing')])
            order.out_delivery_count = len(stock_picking_ids)

    @api.multi
    def _compute_refund_inv_ids(self):
        for inv in self:
            refund_inv_ids = self.env['account.invoice'].search([('rma_id','=',inv.id)])
            inv.refund_inv_count = len(refund_inv_ids)

    @api.onchange('sale_order')
    def set_sale_details(self):

        sale_order_obj = self.env['sale.order'].search([('id','=',self.sale_order.id)])

        self.sales_channel = sale_order_obj.team_id
        self.partner = sale_order_obj.partner_id.id
        self.responsible = sale_order_obj.user_id.id
        self.phone = sale_order_obj.partner_id.phone
        self.email = sale_order_obj.partner_id.email

        for delivery_ord in sale_order_obj.picking_ids:
            if delivery_ord.state == 'done':
                self.delivery_order = delivery_ord.id

        order_line_dict = {}
        order_line_list = []

        for line in self.rma_line_ids:
            self.rma_line_ids = [(2,line.id,0)]
        
        for i in sale_order_obj.order_line:
            order_line_dict = {
                'product_id': i.product_id.id,
                'price_unit': i.price_unit,
                'delivery_qty': i.qty_delivered
            }
            order_line_list.append((0,0, order_line_dict))

        self.rma_line_ids = order_line_list

    @api.multi
    def rma_line_btn(self):

        self.ensure_one()
        return { 
            'name': 'Product', 
            'type': 'ir.actions.act_window', 
            'view_mode': 'tree,form', 
            'res_model': 'product.product', 
            'domain': [('rma_id','=',self.id)],
        }

    @api.onchange('deadline','date')
    def _onchange_deadline(self):

        if self.deadline and self.date:
            if self.date > self.deadline:
                raise Warning(_("Please select a proper date."))

    @api.multi
    def action_send_rma(self):
        self.ensure_one()

        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('bi_rma', 'email_template_edi_rma')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'rma.main',
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


    @api.multi
    def action_approve(self):
        self.write({'state':'approved'})

        stock_picking_obj = self.env['stock.picking']

        for r in self.rma_line_ids:
            if(r.action == 'replace'):
                r.show_prod_setting = True

        if not self.delivery_order:
            raise Warning(_('Please confirm the sale order first.'))
        else:
            res_company = self.env.user.company_id
            
            vals= {
                'rma_id' : self.id,
                'partner_id' : self.partner.id,
                'location_id' : res_company.b2b_source_picking_type_id.default_location_src_id.id,
                'location_dest_id' : res_company.b2b_source_picking_type_id.default_location_dest_id.id,
                'origin' : self.sale_order.name,
                'scheduled_date' : self.date,
                'picking_type_code' : 'incoming',
                'picking_type_id' : res_company.b2b_source_picking_type_id.id,

            }
            stock_picking = stock_picking_obj.create(vals)

            
            stock_move_obj = self.env['stock.move']
            for product in self.rma_line_ids:
                product_vals = {
                    'name' : product.product_id.name,
                    'product_id' : product.product_id.id,
                    'product_uom_qty' : float(product.return_qty),
                    'product_uom' : product.product_id.uom_id.id,
                    'picking_id' : stock_picking.id,
                    'location_id' : res_company.b2b_source_picking_type_id.default_location_src_id.id,
                    'location_dest_id' : res_company.b2b_source_picking_type_id.default_location_dest_id.id,
                    'picking_type_id' : res_company.b2b_source_picking_type_id.id,
                }
                stock_move_obj.create(product_vals)

            

            return

    @api.multi 
    def action_view_receipt(self): 
        self.ensure_one()
        return { 
            'name': 'Picking', 
            'type': 'ir.actions.act_window', 
            'view_mode': 'tree,form', 
            'res_model': 'stock.picking', 
            'domain': [('rma_id','=',self.id)], 
        }

    @api.multi 
    def action_view_refund_invoice(self): 
        self.ensure_one()
        return { 
            'name': 'Refund Invoice', 
            'type': 'ir.actions.act_window', 
            'view_mode': 'tree,form', 
            'res_model': 'account.invoice', 
            'domain': [('rma_id','=',self.id)], 
            'views' : [(self.env.ref('account.invoice_tree').id, 'tree'),(self.env.ref('account.invoice_form').id, 'form')],
        }

    @api.multi 
    def action_view_sale_order(self): 
        return { 
            'name': 'Sale Order', 
            'type': 'ir.actions.act_window', 
            'view_mode': 'tree,form', 
            'res_model': 'sale.order', 
            'domain': [('rma_id','=',self.id)], 
        }

    @api.multi
    def action_move_to_draft(self):
        self.write({'state':'draft'})
        return

    @api.multi
    def action_close(self):
        self.write({'state':'close'})
        return

    @api.model
    def create_delivery(self,value):
        stock_picking_obj = self.env['stock.picking']
        stock_move_obj = self.env['stock.move']
        res_company = self.env.user.company_id
        
        vals= {
            'rma_id' : self.id,
            'partner_id' : self.partner.id,

            'location_id' : res_company.b2b_source_picking_type_id.default_location_src_id.id,
            'location_dest_id' : res_company.b2b_destination_picking_type_id.default_location_dest_id.id,
                
            'picking_type_code' : 'outgoing',
            'picking_type_id' : res_company.b2b_destination_picking_type_id.id,
            'state': 'done',
        }

        stock_picking = stock_picking_obj.create(vals)

        if stock_picking:
            stock_picking_ids = self.env['stock.picking'].search([('rma_id','=',self.id)])
            self.in_delivery_count = len(stock_picking_ids)

        if value.get('replaced_qty'): 
            r_qty = value['replaced_qty']
        else:
            r_qty = 1

        stock_move_lines = stock_move_obj.create({
            'name': value['product_id'].name,
            'product_uom': value['product_id'].uom_id.id,
            'product_id' : value['product_id'].id,
            'product_uom_qty': r_qty,
            'quantity_done': r_qty,
            'picking_id': stock_picking.id,
            'location_id' : res_company.b2b_source_picking_type_id.default_location_src_id.id,
            'location_dest_id' : res_company.b2b_destination_picking_type_id.default_location_dest_id.id,
            'picking_type_id' : res_company.b2b_destination_picking_type_id.id,
        })

    @api.multi
    def create_replaced_product_sale_order(self,values):
        sale_obj = self.env['sale.order']
        sale_ord_line_obj = self.env['sale.order.line']

        replaced_sale_order = sale_obj.create({
            'rma_id': self.id,
            'name': self.env['ir.sequence'].next_by_code('sale.order'),
            'partner_id': self.partner.id,
            'date_order': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })

        sale_ord_lines = sale_ord_line_obj.create({
            'product_id' : values['product_id'].id,
            'product_uom_qty': values['replaced_qty'],
            'order_id': replaced_sale_order.id,
        })

        sale_ord_count = self.sale_order_count + 1

        self.update({
            'sale_order_count': sale_ord_count,
        })

    @api.multi
    def create_credit_note_for_refundable_product(self,values):

        acc_invoice_obj = self.env['account.invoice']
        acc_inv_line_obj = self.env['account.invoice.line']
        product_obj = self.env['product.product']     
        rma_main = self.env['rma.main'].search([('id','=',values['rma_id'].id)])

        find_curr_prod = product_obj.search([('id','=',values['product_id'].id)])

        replaced_product_id = find_curr_prod.id
        replaced_prod_desc = find_curr_prod.name
        replaced_product_qty = values['replaced_qty']
        replaced_prod_price = find_curr_prod.lst_price

        invoice_for_rma = self.env['account.invoice'].search([('rma_id','=',rma_main.id)])
        if invoice_for_rma:
            acc_invoice = invoice_for_rma
        else:
            acc_invoice = acc_invoice_obj.create({
                'rma_id' : rma_main.id,
                'partner_id' : rma_main.sale_order.partner_id.id,
                'type' : 'out_refund',
            })

        account = find_curr_prod.property_account_income_id or find_curr_prod.categ_id.property_account_income_categ_id
        
        if not account:
            raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (find_curr_prod.name, find_curr_prod.id, find_curr_prod.categ_id.name))
        
        prepare_inv_line = {
            'product_id' : replaced_product_id,
            'name' : replaced_prod_desc,
            'quantity' : replaced_product_qty,
            'price_unit' : replaced_prod_price,
            'invoice_id' : acc_invoice.id,
            'account_id' : account.id,
        }
        acc_inv_line_obj.create(prepare_inv_line)

    @api.multi
    def action_validate(self):
        rma_line_list = []
        move_line_list = []
        related_picking_rma = self
        stock_picking_ids = self.env['stock.picking'].search([('rma_id','=',self.id)])
        for r in related_picking_rma.rma_line_ids:
            if(r.action == 'replace'):
                if r.replaced_with.id:
                    if r.product_id.id == r.replaced_with.id:
                        
                        delivery_vals = {
                            'rma_id': self,
                            'product_id': r.replaced_with,
                            'replaced_qty': r.return_qty,
                        }
                        self.create_delivery(delivery_vals)
                    else:
                        if r.is_invoice:
                            sale_vals = {
                                'rma_id': self,
                                'product_id': r.replaced_with,
                                'replaced_qty': r.replaced_qty,
                                'price_unit':r.price_unit,
                            }
                            self.create_replaced_product_sale_order(sale_vals)
                        else:
                            delivery_vals = {
                                'rma_id': self,
                                'product_id': r.replaced_with,
                                'replaced_qty': r.replaced_qty,
                            }
                            self.create_delivery(delivery_vals)

            if(r.action == 'repair'):
                
                delivery_vals = {
                    'rma_id': self,
                    'product_id': r.product_id,
                    'replaced_qty': r.return_qty,
                }
                self.create_delivery(delivery_vals)

            if(r.action == 'refund'):
                if r.is_invoice:

                    credit_note_vals = {
                        'rma_id': self,
                        'product_id': r.product_id,
                        'price_unit':r.price_unit,
                        'replaced_qty': r.return_qty,
                    }
                    self.create_credit_note_for_refundable_product(credit_note_vals)
            self.write({'is_validate': True})
        return

class RmaChangeProduct(models.TransientModel):

    _name = 'rma.change.product'

    rma_prod = fields.Many2one('product.product','Product', )
    prod_change_qty = fields.Float("Quantity")
    rma_id = fields.Many2one('rma.main','RMA Number')
    create_invoice = fields.Boolean("Create Invoice")
    diff_product = fields.Boolean(help='Different Product Options',default=False)
    
    @api.onchange('rma_prod')
    def _onchange_wizard_product(self):

        if self.rma_prod and self._context["active_id"]:
            curr_line_prod = self.env['rma.lines'].search([('id','=',self._context["active_id"])])
            if self.rma_prod != curr_line_prod.product_id:
                self.diff_product = True
            else:
                self.diff_product = False

    @api.model
    def default_get(self,fields):

        rec = super(RmaChangeProduct, self).default_get(fields)
        ctx = self._context["active_id"]
        t = self.env['rma.lines'].browse(ctx)
        rec.update({
            'rma_id': t.rma_id.id
        })

        return rec

    @api.multi
    def change_prod(self):
        
        product_obj = self.env['product.product']
        find_curr_wiz_prod = product_obj.search([('id','=',self.rma_prod.id)])

        replaced_product_id = self.rma_prod.id
        replaced_prod_desc = find_curr_wiz_prod.name
        replaced_product_qty = self.prod_change_qty
        replaced_prod_price = find_curr_wiz_prod.lst_price

        ctx = self._context["active_id"]
        t = self.env['rma.lines'].browse(ctx)

        t.replaced_with = find_curr_wiz_prod.id

        if t.delivery_qty >= self.prod_change_qty:
            if t.return_qty >= self.prod_change_qty:
                t.replaced_qty = self.prod_change_qty
            else:
                raise Warning(_("Return quantity should be less or equal to return quantity."))    
        else:
            raise Warning(_("Return quantity should be less or equal to delivery quantity."))
            

        if self.create_invoice:
            t.is_invoice = True
        else:
            t.is_invoice = False
            

class RejectWizard(models.Model):

    _name = 'reject.reason'
    _rec_name = 'reject_reason'

    reject_reason = fields.Char("Reject Reason")

class RejectWizard(models.TransientModel):

    _name = 'create.reject'

    rma_reason_id = fields.Many2one('reject.reason','Reject reason')

    @api.multi
    def create_reject(self):
        rma_main_id = self.env['rma.main'].browse(self._context.get('active_id'))
        rma_main_id.write({'reject_reason':self.rma_reason_id.reject_reason,'state':'reject'})
        return

class RmaClaim(models.Model):

    _name = 'rma.claim'
    _rec_name = 'rma_id'

    rma_id = fields.Many2one('rma.main','RMA Number')
    subject = fields.Char('Subject')
    partner = fields.Many2one('res.partner','Partner', store=True)
    responsible = fields.Many2one('res.users','Responsible', store=True)
    date = fields.Datetime('Date')
    nxt_act_dt = fields.Datetime('Next Action Date')
    nxt_act = fields.Char('Next Action')
    stock_picking_id = fields.Many2one('stock.picking')

class RmaLines(models.Model):

    _name = 'rma.lines'

    rma_id = fields.Many2one('rma.main','RMA Id')
    product_id = fields.Many2one('product.product','Product')
    delivery_qty = fields.Float('Delivered Quantity')
    return_qty = fields.Float('Return Quantity')
    reason = fields.Many2one('rma.reason','Reason')
    recieved_qty = fields.Float('Recieved Quantity')
    action = fields.Selection('Action',related='reason.reason_action')
    show_prod_setting = fields.Boolean('Show Poduct setting',default=False)
    price_unit = fields.Float('Price')
    replaced_with = fields.Many2one('product.product','Replaced with')
    replaced_qty = fields.Float('Replaced Quantity')
    is_invoice = fields.Boolean('Is invoice',default=False)

    @api.onchange('return_qty')
    def _onchange_return_qty(self):

        if self.return_qty:
            if self.delivery_qty < self.return_qty:
                raise Warning(_("Quantity should be less than delivered."))

class RmaReason(models.Model):

    _name = 'rma.reason'
    _rec_name = 'rma_reason'

    rma_reason = fields.Char('RMA Reason',required=True)
    reason_action = fields.Selection([('replace', 'Replace'),('refund', 'Refund'),('repair', 'Repair')], string='Action')

class RefundAccInvoice(models.Model):

    _inherit = 'account.invoice'

    rma_id = fields.Many2one('rma.main','RMA Id')

class RmaSaleOrder(models.Model):

    _inherit = 'sale.order'

    rma_id = fields.Many2one('rma.main','RMA Id')
    execution_specs = fields.Selection([('as_per_contract_specs', 'As Per Contract Specs'), ('as_per_revised_specs', 'As Per Revised Specs')], string="Execution Specs")
    otd_version = fields.Selection([('bluedarft', 'Gen 10.0 Bluedart (6w.days)'),
                                    ('zepto', 'Gen 10.0 Zepto (3w.days)'),
                                    ('drone', 'Gen 10.0 Drone (2w.days)'),
                                    ('ferrari', 'Gen 10.0 Ferrari (24 Hours)')])

class RmaStockPicking(models.Model):
    _inherit = "stock.picking"

    rma_id = fields.Many2one('rma.main',string='RMA ID')
    claim_id = fields.Many2one('rma.claim',string='Claim ID')
    claim_count = fields.Float('Claim Count',compute='_compute_rma_claim_ids')

    @api.multi
    def _compute_rma_claim_ids(self):
        for order in self:
            rma_claim_ids = self.env['rma.claim'].search([('stock_picking_id','=',order.id)])
            order.claim_count = len(rma_claim_ids)

    @api.multi 
    def action_rma_claim_view(self): 
        self.ensure_one()
        return { 
            'name': 'Rma Claim', 
            'type': 'ir.actions.act_window', 
            'view_mode': 'tree,form', 
            'res_model': 'rma.claim', 
            'domain': [('stock_picking_id','=',self.id)], 
        }

    @api.multi
    def button_validate(self):

        validate_super = super(RmaStockPicking,self).button_validate()
        
        rma_line_list = []
        move_line_list = []

        related_picking_rma = self.env['rma.main'].search([('id','=',self.rma_id.id)])

        related_picking_rma.write({'state':'processing'})

        for r in related_picking_rma.rma_line_ids:
            rma_line_list.append(r.id)
        for m in self.move_lines:
            move_line_list.append(m.id)
        for m in self.move_lines:
            move_line_list.append(m.id)
        for i,j in zip(rma_line_list,move_line_list):
            get_qty = self.env['stock.move'].browse(j)
            if related_picking_rma.is_validate==False:
                self.env['rma.lines'].browse(i).write({'recieved_qty':get_qty.product_uom_qty})
        if related_picking_rma.is_validate==True:
            self.env['rma.lines'].search([('product_id','=',self.product_id.id)],limit=1).write({'recieved_qty':get_qty.product_uom_qty})
        
        vals = {
                'rma_id' : self.rma_id.id,
                'subject' : self.rma_id.subject,
                'partner' : self.rma_id.partner.id,
                'responsible' : self.rma_id.responsible.id,
                'date' : self.rma_id.date,
                'nxt_act_dt' : datetime.now(),   
                'nxt_act' : datetime.now(), 
                'stock_picking_id' : self.rma_id.delivery_order.id
        }
        claim = self.env['rma.claim'].create(vals)
        return validate_super

    @api.multi
    def action_cancel(self):

        cancel_super = super(RmaStockPicking,self).action_cancel()

        cancel_picking_rma = self.env['rma.main'].search([('id','=',self.rma_id.id)])
        
        cancel_picking_rma.update({
            'state': 'close',
        })

        return True   
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: