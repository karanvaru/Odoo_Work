from odoo import api, fields, models, _
from odoo.exceptions import UserError

from odoo import api, fields, models
import logging
from odoo.http import request

_logger = logging.getLogger(__name__)


# Inter company Customizations for Reddot Distribution.
# This works for both SO and PO as per requirements.
# Configurations must be done accordingly.
# Copyright (C) 2024 Douglas Tabut tabutdouglas@gmail.com

class ReddotPurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = 'Reddot Purchase Order'

    auto_generated = fields.Boolean(string='Auto Generated Purchase Order', copy=False)
    auto_purchase_order_id = fields.Many2one('purchase.order', string='Source Purchase Order', readonly=True,
                                             copy=False)
    actual_vendor = fields.Many2one('res.partner', string='Supplier')
    supplier_reference = fields.Char('Supplier Reference')
    order_type = fields.Selection([('RR', 'Run Rate'), ('BTB', 'Back to Back'), ('BSPK', 'Bespoke')],
                                  required=1)
    # rdd_project_id = fields.Many2one('project.project', related="company_id.project_id", store=True)
    state = fields.Selection([
        ('draft', 'Purchase Request'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    total_cost_after_rebate = fields.Float('Total cost after rebate ', compute='_compute_cost_after_rebate',
                                           help='Subtotal price of the items minus the '
                                                'rebate.')
    total_selling_price = fields.Float('Selling', compute='_compute_custom_total_sale',
                                       help='The cumulative selling price for all the quantity')
    proforma_invoices = fields.Many2many('ir.attachment', string="Attach Proforma Invoices", help='Attach PI')
    margin_total = fields.Float('Margin %', compute='_compute_margin_total',
                                help='The resultant margin percentage resulting from the difference between the '
                                     'selling price and the current price/buying price from the supplier.')
    # proforma_invoice = fields.Many2many('ir.attachment', 'res_partner_proforma_invoice_rel', 'partner_id',
    # 'proforma_invoice_rel', string='Proforma Invoice', help='Attach PI')

    proforma_invoice_filename = fields.Char()
    custom_total_cost = fields.Float(
        string='Cost After Rebate',
        compute='_compute_custom_total_cost',
        store=True)
    rdd_project_id = fields.Many2one('project.project', 'RDD Project',
                                     required=True)
    emails_notify = fields.Char('Emails', compute='_compute_email_to')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')

    ship_to = fields.Many2one('res.partner', string='Ship to ')
    bill_to = fields.Many2one('res.partner', string="Bill to")
    sold_to = fields.Many2one('res.partner', string='Sold to')

    def action_view_sale_order(self):
        self.ensure_one()
        if self.sale_order_id:
            return {
                'name': 'Sale Order',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'res_id': self.sale_order_id.id,
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window_close',
            }

    def _compute_email_to(self):
        for record in self:
            admin_mail = set()  # Using a set to prevent duplicates
            group_users = self.env.ref("reddot_wms.group_country_logistics").users
            # Iterate over the users in the group
            for user in group_users:
                # Check if any of the user's companies match the sister companies or the current company
                if any(p_company.id == user.company_id.id for p_company in
                       record.partner_id.ref_company_ids) or self.env.company.id == user.company_id.id:
                    if user.email:
                        admin_mail.add(user.email)
            # Adding the email of the users who created the record and last made changes to the record
            for user in [record.create_uid, record.write_uid]:
                if user.email:
                    admin_mail.add(user.email)
            record.emails_notify = ', '.join(admin_mail)

    def _get_approval_status(self):
        reference = "purchase.order," + str(self.id.origin)

        approvals = self.env['multi.approval'].search([('origin_ref', '=', reference)])

        return approvals.state

    def get_project_domain(self):
        res = [
            ('company_id', '=', self.env.company.id)]
        return res

    @api.depends('order_line.price_total', 'order_line.rebate_id')
    def _compute_cost_after_rebate(self):
        after_rebate = 0
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            for line in order_lines:
                after_rebate += line.rebate_per_unit * line.rebate_id.rebate
                if order.amount_untaxed > after_rebate:
                    order.total_cost_after_rebate = order.amount_untaxed - after_rebate
                else:
                    order.total_cost_after_rebate = 0.0

    def change_vendor_field_attr(self, attribute_dict):
        if 'actual_vendor' in self._fields:
            for key, value in attribute_dict.items():
                setattr(self._fields['actual_vendor'], key, value)

    def button_approve(self, force=False):
        """ Generate intercompany purchase order based on conditions."""
        res = super(ReddotPurchaseOrder, self).button_approve(force=force)
        for order in self:
            # Update `business_type` on pickings with `order_type`
            for picking in order.picking_ids:
                if picking.state not in ('done', 'cancel') and order.order_type:
                    picking.business_type = order.order_type
            # Get the company from the partner then trigger action of intercompany relation
            company_rec = self._find_company_from_partner(order.partner_id.id)
            _logger.error(f"company_rec: {company_rec}")
            if company_rec and company_rec.rule_type in ('purchase', 'sale_purchase') and (
                    not order.auto_generated):
                order.with_user(company_rec.intercompany_user_id).with_context(
                    default_company_id=company_rec.id).with_company(company_rec).inter_company_create_purchase_order(
                    company_rec)
        return res

    @api.model
    def _find_company_from_partner(self, partner):
        company = self.env['res.company'].search([('partner_id', '=', partner)], limit=1)
        return company

    def inter_company_create_purchase_order(self, company):
        """ Create a Purchase Order in the sister company based on the current PO (self).
            :param company: the company of the created PO
            :rtype company: res.company record
        """
        return self.custom_inter_company_create_purchase_order(company)

    def custom_inter_company_create_purchase_order(self, company):
        """ Customized method to create a Purchase Order in the sister company based on the current PO (self).
            :param company: the company of the created PO
            :rtype company: res.company record
        """
        intercompany_uid = company.intercompany_user_id and company.intercompany_user_id.id or False
        if not intercompany_uid:
            raise UserError(_("Provide at least one user for intercompany relation for %s" % company.name))

        if not self.env['purchase.order'].check_access_rights('create', raise_exception=False):
            raise UserError(_("Inter company user of company %s doesn't have enough access rights" % company.name))

        for rec in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            company_partner = rec.company_id.partner_id.with_user(intercompany_uid)
            if rec.currency_id.id != company_partner.property_product_pricelist.currency_id.id:
                raise UserError(_("You cannot create PO in sister company because currency is different."))

            # Create the Purchase Order in the sister company
            if not rec.actual_vendor:
                purchase_order_data = rec.sudo().with_context({"no_actual_vendor": True})._prepare_purchase_order_data(
                    rec.partner_id, company)

                # Notify the employees via email
                order_url = f"{base_url}/web#id={self.id}&view_type=form&model={self._name}"
                ref = self.partner_ref
                self.env.ref('reddot_wms.intercompany_purchase_notification').with_context(
                    url=order_url, resulting_po=ref).send_mail(self.id, force_send=True)
            else:
                purchase_order_data = rec.sudo()._prepare_purchase_order_data(rec.actual_vendor, company)
                inter_user = self.env['res.users'].sudo().browse(intercompany_uid)
                purchase_order = self.env['purchase.order'].with_context(
                    allowed_company_ids=inter_user.company_ids.ids).with_user(intercompany_uid).create(
                    purchase_order_data)

                # Copy lines from original Purchase Order
                for line in rec.order_line.sudo():
                    purchase_order_line_data = rec._prepare_purchase_order_line_data(line, company)
                    purchase_order_line_data['order_id'] = purchase_order.id
                    self.env['purchase.order.line'].with_context(
                        allowed_company_ids=inter_user.company_ids.ids).with_user(
                        intercompany_uid).create(purchase_order_line_data)

                # Add a message to indicate automatic generation
                msg = _("Automatically generated from %s of company %s." % (rec.name, rec.company_id.name))
                purchase_order.message_post(body=msg, message_type='notification',
                                            author_id=self.env.user.id)

                # Notify the employees via email
                order_url = f"{base_url}/web#id={self.id}&view_type=form&model={self._name}"
                ref = self.partner_ref
                sale_order_url = f"{base_url}/web#id={self.id}&view_type=form&model=sale.order"

                self.env.ref('reddot_wms.intercompany_purchase_notification').with_context(
                    url=order_url, resulting_po=purchase_order_data.get("name")).send_mail(self.id, force_send=True)

    def _prepare_purchase_order_data(self, partner, company):
        """ Generate the Purchase Order values from the current PO.
            :param partner: the partner representing the company
            :rtype partner: res.partner record
            :param company: the company of the created PO
            :rtype company: res.company record
        """
        actual_vendor = self._context.get('no_actual_vendor')
        if not actual_vendor:
            self.ensure_one()
            partner_addr = partner.sudo().address_get(['invoice', 'delivery', 'contact'])
            return {
                'partner_id': partner.id,
                'company_id': company.id,
                'currency_id': self.currency_id.id,
                'dest_address_id': partner_addr['delivery'],
                'origin': self.name,
                'date_order': fields.Date.today(),
                'auto_generated': True,
                'auto_purchase_order_id': self.id,
                'state': 'purchase',
                'order_type': self.order_type,
                'rdd_project_id': self.rdd_project_id.id
            }

    def _prepare_purchase_order_line_data(self, line, company):
        """ Generate the Purchase Order Line values from the PO line.
            :param line: the origin Purchase Order Line
            :rtype line: purchase.order.line record
            :param company: the company of the created PO
            :rtype company: res.company record
        """
        return {
            'product_id': line.product_id.id,
            'name': line.name,
            'product_qty': line.product_qty,
            'product_uom': line.product_uom.id,
            'price_unit': line.price_unit,
            'rebate_per_unit': line.rebate_per_unit,
            'date_planned': fields.Date.today(),
            'company_id': company.id,
            'selling_price': line.selling_price,
        }

    #     SO
    def _prepare_sale_order_data(self, name, partner, company, direct_delivery_address):
        """ Generate the Sales Order values from the PO
            :param name : the origin client reference
            :rtype name : string
            :param partner : the partner reprenseting the company
            :rtype partner : res.partner record
            :param company : the company of the created SO
            :rtype company : res.company record
            :param direct_delivery_address : the address of the SO
            :rtype direct_delivery_address : res.partner record
        """
        res = super(ReddotPurchaseOrder, self)._prepare_sale_order_data(name, partner, company, direct_delivery_address)
        self.ensure_one()
        partner_addr = partner.sudo().address_get(['invoice', 'delivery', 'contact'])
        warehouse = company.warehouse_id and company.warehouse_id.company_id.id == company.id and company.warehouse_id or False
        project = self.env['project.project'].search([
            ('name', '=', self.rdd_project_id.name),
            ('company_id', '=', company.id)

        ], limit=1)

        if not warehouse:
            raise UserError(
                _('Configure correct warehouse for company(%s) from Menu: Settings/Users/Companies', company.name))
        return {
            'name': self.env['ir.sequence'].sudo().next_by_code('sale.order') or '/',
            'company_id': company.id,
            'team_id': self.env['crm.team'].with_context(allowed_company_ids=company.ids)._get_default_team_id(
                domain=[('company_id', '=', company.id)]).id,
            'warehouse_id': warehouse.id,
            'client_order_ref': name,
            'partner_id': partner.id,
            'pricelist_id': partner.property_product_pricelist.id,
            'partner_invoice_id': partner_addr['invoice'],
            'date_order': self.date_order,
            'fiscal_position_id': partner.property_account_position_id.id,
            'payment_term_id': partner.property_payment_term_id.id,
            'user_id': False,
            'state': 'sale',
            'auto_generated': True,
            'auto_purchase_order_id': self.id,
            'partner_shipping_id': direct_delivery_address or partner_addr['delivery'],
            'order_line': [],
            'business_type': self.order_type,
            'rdd_project_id': project.id
        }

    # TODO WIP, Rebate,
    # @api.depends_context('lang')
    # @api.depends('order_line.taxes_id', 'order_line.price_subtotal', 'amount_total', 'amount_untaxed')
    # def _compute_tax_totals(self):
    #     for order in self:
    #         order_lines = order.order_line.filtered(lambda x: not x.display_type)
    #
    #         order.tax_totals = self.env['account.tax']._prepare_tax_totals(
    #             [x._convert_to_tax_base_line_dict() for x in order_lines],
    #             order.currency_id or order.company_id.currency_id, )

    @api.depends('order_line.price_total', 'order_line.rebate_per_unit')
    def _compute_custom_total_cost(self):
        for order in self:
            order.custom_total_cost = sum(order.order_line.mapped('price_subtotal'))

    @api.depends('order_line.price_total', 'order_line.total_selling_price')
    def _compute_custom_total_sale(self):
        for order in self:
            order.total_selling_price = sum(order.order_line.mapped('total_selling_price'))

    @api.depends('order_line.price_total', 'order_line.margin')
    def _compute_margin_total(self):
        for order in self:
            total_order_lines = len(order.order_line)
            if total_order_lines > 0:
                order.margin_total = sum(order.order_line.mapped('margin')) / total_order_lines
            else:
                order.margin_total = 0

    def activity_log(self, user_ids, summary, p_self):
        valid_user_ids = self.env['res.users'].browse(user_ids).ids
        activity_vals = []
        for user_id in valid_user_ids:
            existing_activity = self.env['mail.activity'].search_count([
                ('res_id', '=', p_self.id),
                ('user_id', '=', user_id),
                ('res_model', '=', self._name)
            ])
            if existing_activity == 0:
                self.env['mail.activity'].create({
                    'res_id': p_self.id,
                    'res_model_id': self.env['ir.model']._get(self._name).id,
                    'activity_type_id': self.env.ref("mail.mail_activity_data_todo").id,
                    'summary': summary,
                    'user_id': user_id
                })
