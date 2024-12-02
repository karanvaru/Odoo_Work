from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from werkzeug import urls


class FreightOrderInherit(models.Model):
    _inherit = "freight.order"
    _description = "Reddot Freight Order"
    _order = 'id desc'

    bill_entry_ids = fields.One2many('freight.bill.entry', 'order_id')
    quantity = fields.Char('Quantity')
    volume = fields.Char('Volume CBM', readonly=1)
    weight = fields.Char('Gross')
    net = fields.Char('Net')
    hs_code = fields.Char('HS Code')
    unit = fields.Char('Unit')
    package_type = fields.Char('Type')
    package_qty = fields.Char('Qty.')
    beneficiary = fields.Char(string='Beneficiary', help="Beneficiary")
    sources = fields.Char(string='Sources', help="Sources")
    code = fields.Char(string='Code')
    release_ref = fields.Char(string='Release Reference', help="Code")
    agency = fields.Char(string='Agency', help="Agency")
    space = fields.Char(string='', readonly=1)
    release_date = fields.Date(string='Release Date')
    eta = fields.Date(string='Estimated Time of Arrival')
    pickings_comment = fields.Char(string='')
    supplier_reference = fields.Char(string='Supplier Reference')
    boe_number = fields.Char('Bill of Entry')
    exit_number = fields.Char('Bill of Exit')
    shipping_reference = fields.Char('Shipping Reference', help="A unique identifier to reference the shipment E.g. "
                                                                "HP shipment.")
    delivery_method = fields.Many2one('account.incoterms', string='Delivery Method', help="The shipment’s delivery "
                                                                                          "method such as DDU, FOB, "
                                                                                          "ExWorks as defined in the "
                                                                                          "delivery methods "
                                                                                          "configuration")
    forwarding_agent = fields.Many2one('res.partner', string='Forwarding Agent',
                                       help='The name of the forwarding agent')
    remarks = fields.Text('Remarks')
    class_pack = fields.Selection([('classification', 'Classification'), ('package', 'Packages')])
    weight_type = fields.Selection([('net', 'Net'), ('gross', 'Gross')])
    class_pack_uom_id = fields.Many2one('uom.uom', string='UOM')
    supplier = fields.Many2one('res.partner', string='Supplier')
    grv_count = fields.Integer(compute='_grv_count')
    po_count = fields.Integer(compute='_po_count')
    picking_ids = fields.Many2many('stock.picking', string='Operations')
    order_date = fields.Date('Pre alert date', default=fields.Date.today(),
                             help="Date of Pre Alert")
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Confirmed'),
                              ('confirm', 'Received'),
                              ('invoice', 'Invoiced'), ('done', 'Done'), ('delivery', 'Delivery'),
                              ('cancel', 'Cancel')], default='draft')

    def create_invoice(self):
        """Create invoice"""
        lines = []
        if self.bill_entry_ids:
            for order in self.bill_entry_ids:
                value = (0, 0, {
                    'name': order.product_id.name,
                    'price_unit': order.cif_local_value,
                    'quantity': order.net + order.weight,
                })
                lines.append(value)

        if self.route_ids:
            for route in self.route_ids:
                value = (0, 0, {
                    'name': route.operation_id.name,
                    'price_unit': route.sale,
                })
                lines.append(value)

        if self.service_ids:
            for service in self.service_ids:
                value = (0, 0, {
                    'name': service.service_id.name,
                    'price_unit': service.sale,
                    'quantity': service.qty
                })
                lines.append(value)

        invoice_line = {
            'move_type': 'in_invoice',
            'partner_id': self.shipper_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.name,
            'ref': self.name,
            'invoice_line_ids': lines,
        }
        inv = self.env['account.move'].create(invoice_line)
        result = {
            'name': 'action.name',
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'current',
            'res_id': inv.id,
            'res_model': 'account.move',
        }
        self.state = 'invoice'
        return result

    @api.model
    def create(self, vals):
        """Create Sequence"""
        sequence_code = 'freight.order.sequence.custom'
        vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code)
        return super(FreightOrderInherit, self).create(vals)

    @api.onchange('bill_entry_ids')
    def coo(self):
        product_country_map = {}
        # Prepare a dictionary of product and country origin IDs for efficient querying
        for entry in self.bill_entry_ids:
            if entry.product_id.product_tmpl_id and entry.country_origin:
                product_country_map[(entry.product_id.product_tmpl_id.id, entry.country_origin.id)] = entry

        # Fetch all relevant HS codes in one database query
        hs_code_records = self.env['product.hs.codes'].search([
            ('product_id', 'in', [product_id for product_id, _ in product_country_map.keys()]),
            ('origin_country_id', 'in', [country_origin for _, country_origin in product_country_map.keys()])
        ])

        # Map retrieved HS codes to their respective entries
        for hs_code in hs_code_records:
            entry = product_country_map.get((hs_code.product_id.id, hs_code.origin_country_id.id))
            if entry:
                entry.hs_code = hs_code.code

    def create_custom_clearance(self):
        if self.bill_entry_ids.product_id:
            return super(FreightOrderInherit, self).create_custom_clearance()
        else:
            raise UserError("You don't have any products scheduled for clearance. Please add them on the Bill "
                            "Entries/Goods Description")

    def action_confirm(self):
        """Confirm order"""
        for rec in self:
            clearance = self.env['custom.clearance'].search([
                ('freight_id', '=', self.id)])
            if clearance:
                if clearance.state == 'confirm':
                    picking = self.env['stock.picking'].search([('carrier_tracking_ref', '=', self.name)])
                    for pick in picking:
                        values_to_write = {}
                        if self.boe_number:
                            values_to_write['boe_number'] = self.boe_number
                        if self.exit_number:
                            values_to_write['exit_number'] = self.exit_number

                        if self.supplier_reference:
                            values_to_write['supplier_reference'] = self.supplier_reference

                        if values_to_write:
                            pick.write(values_to_write)
                    for pick in picking:
                        if pick:
                            if pick.origin and 'P0' in pick.origin:
                                purchase = self.env['purchase.order'].search([('name', '=', pick.origin)])
                                purchase.write({
                                    'supplier_reference': self.supplier_reference
                                })
                    rec.state = 'confirm'
                    for bill_line in rec.bill_entry_ids:
                        prod_id = self.env['product.product'].search(
                            [('id', '=', bill_line.product_id.id)]).product_tmpl_id
                        existing_codes = self.env['product.hs.codes'].search(
                            [('origin_country_id', '=', bill_line.country_origin.id),
                             ('product_id', '=', prod_id.id)])

                        if bill_line.hs_code:
                            if not existing_codes:
                                self.env['product.hs.codes'].create({
                                    'product_id': prod_id.id,
                                    'origin_country_id': bill_line.country_origin.id,
                                    'code': bill_line.hs_code
                                })
                    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    Urls = urls.url_join(base_url, 'web#id=%(id)s&model=freight.order&view_type=form' % {'id': self.id})
                    mail_content = _('Hi %s,<br> '
                                     'The Freight Order %s is Confirmed '
                                     '<div style = "text-align: center; '
                                     'margin-top: 16px;"><a href = "%s"'
                                     'style = "padding: 5px 10px; '
                                     'font-size: 12px; line-height: 18px; '
                                     'color: #FFFFFF; border-color:#875A7B; '
                                     'text-decoration: none; '
                                     'display: inline-block; '
                                     'margin-bottom: 0px; font-weight: 400;'
                                     'text-align: center; '
                                     'vertical-align: middle; '
                                     'cursor: pointer; white-space: nowrap; '
                                     'background-image: none; '
                                     'background-color: #875A7B; '
                                     'border: 1px solid #875A7B; '
                                     'border-radius:3px;">'
                                     'View %s</a></div>'
                                     ) % (rec.agent_id.name, rec.name,
                                          Urls, rec.name)
                    email_to = self.env['res.partner'].search([
                        ('id', 'in', (self.shipper_id.id,
                                      self.consignee_id.id, self.agent_id.id))])
                    for mail in email_to:
                        main_content = {
                            'subject': _('Freight Order %s is Confirmed') % self.name,
                            'author_id': self.env.user.partner_id.id,
                            'body_html': mail_content,
                            'email_to': mail.email
                        }
                        mail_id = self.env['mail.mail'].create(main_content)
                        mail_id.mail_message_id.body = mail_content
                        mail_id.send()
                elif clearance.state == 'draft':
                    raise ValidationError("the custom clearance ' %s ' is "
                                          "not confirmed" % clearance.name)
                elif clearance.state == 'not-released':
                    raise UserError("Customs did not release this freight order")
            else:
                raise ValidationError("Create a custom clearance for %s" % rec.name)
            for line in rec.order_ids:
                line.container_id.state = 'reserve'
        # return super(FreightOrderInherit, self).create()

    def action_done(self):
        """Mark order as done"""
        if self.boe_number or self.exit_number:
            for rec in self:
                picking = self.env['stock.picking'].search([('carrier_tracking_ref', '=', self.name)])
                for pick in picking:
                    values_to_write = {}
                    if self.boe_number:
                        values_to_write['boe_number'] = self.boe_number
                    if self.exit_number:
                        values_to_write['exit_number'] = self.exit_number
                    if self.supplier_reference:
                        values_to_write['supplier_reference'] = self.supplier_reference

                    if values_to_write:
                        pick.write(values_to_write)
                for pick in picking:
                    if pick:
                        if 'P0' in pick.origin:
                            purchase = self.env['purchase.order'].search([('name', '=', pick.origin)])
                            purchase.write({
                                'supplier_reference': self.supplier_reference
                            })
                rec.state = 'confirm'
                for bill_line in rec.bill_entry_ids:
                    prod_id = self.env['product.product'].search(
                        [('id', '=', bill_line.product_id.id)]).product_tmpl_id
                    existing_codes = self.env['product.hs.codes'].search(
                        [('origin_country_id', '=', bill_line.country_origin.id),
                         ('product_id', '=', prod_id.id)])

                    if bill_line.hs_code:
                        if not existing_codes:
                            self.env['product.hs.codes'].create({
                                'product_id': prod_id.id,
                                'origin_country_id': bill_line.country_origin.id,
                                'code': bill_line.hs_code
                            })
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                Urls = urls.url_join(base_url, 'web#id=%(id)s&model=freight.order&view_type=form' % {'id': self.id})

                mail_content = _('Hi %s,<br>'
                                 'The Freight Order %s is Completed'
                                 '<div style = "text-align: center; '
                                 'margin-top: 16px;"><a href = "%s"'
                                 'style = "padding: 5px 10px; font-size: 12px; '
                                 'line-height: 18px; color: #FFFFFF; '
                                 'border-color:#875A7B;text-decoration: none; '
                                 'display: inline-block; '
                                 'margin-bottom: 0px; font-weight: 400;'
                                 'text-align: center; vertical-align: middle; '
                                 'cursor: pointer; white-space: nowrap; '
                                 'background-image: none; '
                                 'background-color: #875A7B; '
                                 'border: 1px solid #875A7B; border-radius:3px;">'
                                 'View %s</a></div>'
                                 ) % (rec.agent_id.name, rec.name, Urls, rec.name)
                email_to = self.env['res.partner'].search([
                    ('id', 'in', (self.shipper_id.id, self.consignee_id.id,
                                  self.agent_id.id))])
                for mail in email_to:
                    main_content = {
                        'subject': _('Freight Order %s is completed') % self.name,
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': mail.email
                    }
                    mail_id = self.env['mail.mail'].create(main_content)
                    mail_id.mail_message_id.body = mail_content
                    mail_id.send()
                self.state = 'done'

                for line in rec.order_ids:
                    line.container_id.state = 'available'
        else:
            msg = _(
                'Please Provide the Bill of Entry or the Bill of Exit Number')
            raise ValidationError(msg)

    def action_related_pickings(self):
        """ This function returns an action that display existing picking orders of given pre-alert ids. When only one found, show the picking immediately.
        """
        self.ensure_one()
        pickings = self.bill_entry_ids.purchase_order.picking_ids
        result = self.env["ir.actions.actions"]._for_xml_id('stock.action_picking_tree_all')
        # choose the view_mode accordingly
        if not pickings or len(pickings) > 1:
            # override the context to get rid of the default filtering on operation type
            result['context'] = {'default_partner_id': self.shipper_id.id, 'default_origin': self.name}

            result['domain'] = [('id', 'in', pickings.ids)]
        elif len(pickings) == 1:
            # override the context to gset rid of the default filtering on operation type
            result['context'] = {'default_partner_id': self.shipper_id.id, 'default_origin': self.name,
                                 'default_picking_type_id': self.bill_entry_ids.purchase_order.picking_ids.picking_type_id.id}

            res = self.env.ref('stock.view_picking_form', False)
            form_view = [(res and res.id or False, 'form')]
            result['views'] = form_view + [(state, view) for state, view in result.get('views', []) if view != 'form']
            result['res_id'] = pickings.id
        return result

    def action_related_purchases(self):
        self.ensure_one()
        pickings = self.bill_entry_ids.purchase_order
        result = self.env["ir.actions.actions"]._for_xml_id('purchase.purchase_form_action')
        # override the context to get rid of the default filtering on operation type
        result['context'] = {'default_partner_id': self.shipper_id.id, 'default_origin': self.name}
        # choose the view_mode accordingly
        if not pickings or len(pickings) > 1:
            result['domain'] = [('id', 'in', pickings.ids)]
        elif len(pickings) == 1:
            res = self.env.ref('purchase.purchase_order_form', False)
            form_view = [(res and res.id or False, 'form')]
            result['views'] = form_view + [(state, view) for state, view in result.get('views', []) if view != 'form']
            result['res_id'] = pickings.id
        return result

    def _grv_count(self):
        self.grv_count = len(self.bill_entry_ids.purchase_order.picking_ids)

    def _po_count(self):
        self.po_count = len(self.bill_entry_ids.purchase_order)
