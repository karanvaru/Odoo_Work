# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

import base64
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class WarrantyRegistration(models.Model):
    _name = 'warranty.registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Warranty Registration"
    _order = 'create_date desc, id desc'


    name = fields.Char(string='Warranty Reference', required=True, copy=False,
        readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('expired', 'Expired'),
        ('renewed', 'Renewed'),
        ('cancel', 'Cancelled'),
        ], string='Status', copy=False, index=True, track_visibility='onchange', default='draft')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, index=True, default=lambda self: self.env.user.company_id.id)
    user_id = fields.Many2one(
        'res.users', string='Warranty Manager', index=True, track_visibility='onchange', default=lambda self: self.env.user)
    lot_id = fields.Many2one(
        'stock.production.lot',
        string="Serial Number", store=True, copy=False, track_visibility='onchange')
    order_id = fields.Many2one(
        'sale.order', string="Sale Order", required=True)
    order_line = fields.Many2one(
        'sale.order.line', string="Order Line", required=True, copy=False)
    product_id = fields.Many2one(
        'product.product', string="Product", required=True, copy=False, track_visibility='onchange')
    picking_id = fields.Many2one(
        'stock.picking', string="Sale Order")
    partner_id = fields.Many2one('res.partner', string='Customer')
    prod_qty = fields.Float(string="Quantity", default=1)
    warranty_start_date = fields.Date(
        required=True, copy=False, string="Start Date")
    parnter_invoice = fields.Many2one(
        related="order_id.partner_invoice_id",
        copy=False,
        string="Invoice Id")
    warranty_end_date = fields.Date(
        string="End Date", required=True, copy=False, track_visibility='onchange')
    warranty_history_ids = fields.One2many(
        'warranty.history', 'warranty_id', string="Warranty History")


    @api.multi
    def action_done(self):
        for wrntyObj in self:
            wrntyObj.state = 'done'

    @api.multi
    def action_cancel(self):
        for wrntyObj in self:
            wrntyObj.state = 'cancel'

    @api.model
    def create(self, vals):
        ctx = dict(self._context or {})
        orderLine = False
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('warranty.registration') or 'New'
        if vals.get('product_id') and vals.get('order_id') and not ctx.get('not_onchange'):
            saleOrder = self.env['sale.order'].browse(vals.get('order_id'))
            orderLines = saleOrder.order_line
            orderLine = orderLines.filtered(lambda obj : obj.product_id.id == vals.get('product_id'))
            lineId = orderLine and orderLine[0].id
            vals.update({
                'order_line' : lineId,
                'partner_id' : saleOrder.partner_id.id
            })
        res =  super().create(vals)
        if res:
            histryObj = self.env['warranty.history'].create({
                'name' : res.name,
                'invoice_id' : res.order_id.invoice_ids and res.order_id.invoice_ids[0].id or False,
                'warranty_id' : res.id,
                'is_fresh' : True,
                'state' : res.state,
                'old_start_date' : res.warranty_start_date,
                'old_end_date' : res.warranty_end_date,
            })
            pdf = self.env.ref('warranty_management.action_report_warranty_rec').sudo(
            ).render_qweb_pdf([histryObj.id])[0]
            base64Data = base64.b64encode(pdf)
            histryObj.write({'datas' : base64Data})
        return res


    @api.multi
    def confirm_send_mail(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'warranty_management', 'email_template_edi_wk_warranty_regi_1')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'warranty.registration',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
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

    @api.onchange('order_id')
    def update_customer_product_so(self):
        self.ensure_one()
        self.order_line = False
        self.product_id = False
        if self.order_id:
            self.partner_id = self.order_id.partner_id.id
            orderLines = self.order_id.order_line
            lineIds = orderLines.ids
            domain = [('id', 'in', lineIds)]
            return {'domain': {'order_line': domain}}

    @api.onchange('order_line')
    def update_line_product(self):
        self.ensure_one()
        self.product_id = False
        if self.order_line:
            productIds = self.order_line.mapped('product_id').ids or []
            domain = [('id', 'in', productIds)]
            return {'domain': {'product_id': domain}}

    @api.model
    def send_product_reg_mail(self, wrntObj):
        mailTemplateModel = self.env['mail.template']
        irModelData = self.env['ir.model.data']
        templXmlId = irModelData.get_object_reference(
            'warranty_management', 'email_template_product_register')[1]
        if templXmlId:
            today = datetime.now()
            month = today.strftime("%B")
            day = today.day
            year = today.year
            tdDate = "{} {}, {}".format(month, day, year)
            mailTmplObj = mailTemplateModel.browse(templXmlId)
            ctx = {
                'wkdate' : tdDate,
                'warrantyref': wrntObj.name,
            }
            mailTmplObj.with_context(
                **ctx).send_mail(wrntObj.id, force_send=True)
        return True


    @api.model
    def get_warranty_end_date(self, productObj, startDate):
        wPeriod = productObj.warranty_period
        wUnit = productObj.warranty_unit
        wDict = {wUnit: wPeriod}
        endDate = startDate + relativedelta(**wDict)
        return endDate

    @api.onchange('product_id')
    def update_line_so(self):
        if self.product_id and self.order_id:
            if self.product_id.is_warranty and self.warranty_start_date:
                endDate = self.get_warranty_end_date(
                    self.product_id, self.warranty_start_date)
                self.warranty_end_date = endDate
            else:
                self.warranty_end_date = ''
            self.prod_qty = 1


    @api.multi
    def write(self, vals):
        for obj in self:
            if vals.get('serial_number'):
                productLotSerial = self.env['stock.production.lot']
                domain = [('name', '=', vals.get('serial_number')),
                        ('product_id', '=', vals.get('product_id'))]
                lotSerial = productLotSerial.search(domain)
                if not lotSerial:
                    raise ValidationError("Invalid Serial Number!")
            if vals.get('order_id'):
                saleOrder = self.env['sale.order'].browse(vals.get('order_id'))
                vals['partner_id'] = saleOrder.partner_id.id
            elif obj.order_id:
                saleOrder = obj.order_id
                vals['partner_id'] = saleOrder.partner_id.id
            else: continue
            if vals.get('state', '') in ['draft', 'confirm', 'expired', 'cancel']:
                history = obj.warranty_history_ids
                if history and len(history) == 1:
                    history.write({'state' : vals.get('state')})
        return super().write(vals)


    @api.model
    def _wk_warranty_renewal_settings(self):
        configModel = self.env['res.config.settings']
        vals = {
            'renewal_prod' : self.env.ref('warranty_management.warranty_prod').id,
            'warranty_expire_notification' : True,
            'days_before': 15,
            }
        defaultSetObj = configModel.create(vals)
        defaultSetObj.execute()
        return True