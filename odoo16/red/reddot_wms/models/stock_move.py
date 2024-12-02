# -*- coding: utf-8 -*-
from ast import literal_eval

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'
    _description = 'Product Moves Reddot (Stock Move)'

    length = fields.Float('Length')
    width = fields.Float('Width')
    height = fields.Float('Height')
    weight = fields.Float('Weight')
    pre_alert_qty = fields.Float('PreAlert Qty')
    cbm = fields.Char('CBM', compute='_calculate_the_cbm',
                      help="Automatically calculated with formula, "
                           "(HxWxL)/10000000")
    dimension_uom = fields.Many2one('uom.uom', string='UoM Dimensions',
                                    domain="[('category_id.name', '=', 'Length / Distance')]")
    weight_uom = fields.Many2one('uom.uom', string='UoM Weight',
                                 domain="[('category_id.name', '=', 'Weight')]")

    @api.onchange('length', 'width', 'height', 'dimension_uom')
    def _calculate_the_cbm(self):
        for grv_line in self:
            cm = self.env['uom.uom'].search([('name', 'like', 'cm')])
            length_in_cm = ProductTemplateInherit.convert_uom(self, grv_line.length,
                                                              grv_line.dimension_uom, cm)
            width_in_cm = ProductTemplateInherit.convert_uom(self, grv_line.width,
                                                             grv_line.dimension_uom, cm)
            height_in_cm = ProductTemplateInherit.convert_uom(self, grv_line.height,
                                                              grv_line.dimension_uom, cm)

            grv_line.cbm = StockQuantReddot.cbm_compute(grv_line, length_in_cm, width_in_cm, height_in_cm)


class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'
    _description = 'Product Moves Reddot (Stock Move Line)'

    product_uom_qty = fields.Char('Demand')

    lot_id = fields.Many2one('stock.lot', 'Bill of Entry Number',
                             domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]",
                             check_company=True)
    lot_name = fields.Char('Bill of Entry')

    length = fields.Float('Length')
    width = fields.Float('Width')
    height = fields.Float('Height')
    weight = fields.Float('Weight')
    cbm = fields.Char('CBM')
    dimension_uom = fields.Many2one('uom.uom', string='UoM Dimensions')
    weight_uom = fields.Many2one('uom.uom', string='UoM Weight')

    @api.onchange('lot_id')
    def update_dimensions(self):
        self.length = self.lot_id.length
        self.width =self.lot_id.width
        self.height = self.lot_id.height
        self.weight = self.lot_id.weight
        self.cbm = self.lot_id.cbm
        self.dimension_uom = self.lot_id.dimension_uom
        self.weight_uom = self.lot_id.weight

class StockLotReddot(models.Model):
    _inherit = 'stock.lot'

    name = fields.Char(
        'Bill of Entry Number', default=lambda self: self.env['ir.sequence'].next_by_code('stock.lot.serial'),
        required=True, help="Unique Bill of Entry/Exit or /Lot/Serial Number", index='trigram')

    length = fields.Float('Length')
    width = fields.Float('Width')
    height = fields.Float('Height')
    weight = fields.Float('Weight')
    cbm = fields.Char('CBM')
    dimension_uom = fields.Many2one('uom.uom', string='UoM Dimensions')
    weight_uom = fields.Many2one('uom.uom', string='UoM Weight')




class StockQuantReddot(models.Model):
    _inherit = 'stock.quant'

    lot_id = fields.Many2one(
        'stock.lot', 'Bill of Entry/Exit Number', index=True,
        ondelete='restrict', check_company=True,
        domain=lambda self: self._domain_lot_id())
    cbm = fields.Float('Cubic Meter', help="Automatically calculated If dimension is in cm, "
                                           "(HxWxL)/10000000")

    def cbm_compute(self, len, width, height):
        # All dimensions here should be in cm
        b_cbm = 0
        # self.cbm = sum(self.env['stock.move.line'].search([('move_id', '=', self.id)]).mapped('cbm'))
        b_cbm_temp = 0
        if len and width and height:
            b_cbm = (height * width * len) / 1000000
            return round(b_cbm, 1)

        else:
            for self_line in self:
                if hasattr(self_line, "lot_id"):
                    if self_line.lot_id:
                        movement_lines = self.env['stock.move.line'].search(['lot_id', '=', self_line.lot_id])
                        for movement in movement_lines:
                            if movement.height and movement.width and movement.length:
                                b_cbm_temp += movement.height * movement.width * movement.length
                                b_cbm = round(b_cbm_temp / 1000000, 1)


class HSCodes(models.Model):
    _name = 'product.hs.codes'
    _description = 'RDD Product HS Codes'

    origin_country_id = fields.Many2one('res.country', string="Origin Country", ondelete='cascade',
                                        index=True)
    code = fields.Char('HS Code')
    product_id = fields.Many2one('product.template')


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'
    _description = 'Product Template Reddot'

    hs_codes = fields.One2many('product.hs.codes', 'product_id', 'Product HS CODES', copy=True)

    @api.model
    def create(self, vals):
        # Check if 'hs_codes' key exists in vals and it is not an empty list
        if 'service' not in vals.get('detailed_type'):
            hs_codes = vals.get('hs_codes')
            if hs_codes and len(hs_codes) > 0:
                # Check if the first element of 'hs_codes' is a list and it has more than 2 elements
                hs_code = hs_codes[0]
                if isinstance(hs_code, list) and len(hs_code) > 2:
                    # Check if the third element of the first list is a dictionary and it has 'code' and
                    # 'origin_country_id' keys
                    hs_code_details = hs_code[2]
                    if isinstance(hs_code_details,
                                  dict) and 'code' in hs_code_details and 'origin_country_id' in hs_code_details:
                        # Check if 'code' and 'origin_country_id' keys have values
                        if hs_code_details.get('code') and hs_code_details.get('origin_country_id'):
                            return super(ProductTemplateInherit, self).create(vals)
            # Raise validation error if any of the conditions are not met
            raise ValidationError('Please Provide at least one HS CODE line for this product.')
        else:
            return super(ProductTemplateInherit, self).create(vals)

    @api.model
    def convert_uom(self, quantity, from_uom_name, to_uom_name):
        uom_obj = self.env['uom.uom']
        from_uom = uom_obj.search([('id', '=', 6)])
        to_uom = uom_obj.search([('id', '=', 8)])

        if from_uom_name and to_uom_name:
            # Convert quantity to base UoM (assuming 'Unit of Measure' as base)
            quantity_base = from_uom_name._compute_quantity(quantity, to_uom_name)
            # Convert base UoM to target UoM
            converted_quantity = to_uom_name._compute_quantity(quantity_base, to_uom_name)
            return converted_quantity


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'
    _description = 'Reddot Stock Pickings'

    freight_id = fields.Many2one('freight.order', string="Freight")
    customs_date = fields.Char('Customs Date', compute='_compute_customs_date')
    boe_number = fields.Char('Bill of Entry')
    exit_number = fields.Char('Bill of Exit')
    supplier_reference = fields.Char('Supplier Reference')
    picking_code = fields.Char(compute='_compute_picking_code')
    clearance_count = fields.Integer(compute='compute_count')

    rdd_project_id = fields.Many2one('project.project', string="RDD Project")
    business_type = fields.Selection([('RR', 'Run Rate'), ('BTB', 'Back to Back'), ('BSPK', 'Bespoke')],
                                     required=1)
    stc = fields.Text(string="Stc")
    shipping_type = fields.Selection(
        [
            ('import', 'Import'),
            ('export', 'Export'),
            ('fzit', 'Free Zone Internal Transfer'),
            ('ifre', 'Import for Re-Export'),
            ('te', 'Temporary Exit')
        ]
    )

    def _plan_in_shipment(self, shipment_advice):
        """Plan the moves into the given shipment advice."""
        self.freight_id = shipment_advice

    def _compute_picking_code(self):
        self.picking_code = self.picking_type_id.code

    def _sanity_check(self, separate_pickings=True):
        """ Customised/Override Sanity check for `button_validate()`
            to include check for Custom clearance
            :param separate_pickings: Indicates if pickings should be checked independently for Bill of Entry numbers or not.
        """
        settings = self.env['res.config.settings'].sudo().create({})

        if settings.group_stock_bill_of_entry_one_shipment:
            purchase_incoterm = self.env['purchase.order'].search([('name', '=', self.origin)]).incoterm_id
            if purchase_incoterm:
                freight_order = self.env['freight.order'].search([('name', '=', self.carrier_tracking_ref)])
                if self.carrier_tracking_ref:
                    if freight_order and freight_order.state in ('confirm', 'done'):
                        pickings_without_lots = self.browse()
                        products_without_lots = self.env['product.product']
                        pickings_without_moves = self.filtered(lambda p: not p.move_ids and not p.move_line_ids)
                        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')

                        no_quantities_done_ids = set()
                        no_reserved_quantities_ids = set()
                        for picking in self:
                            if all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
                                   picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel'))):
                                no_quantities_done_ids.add(picking.id)
                            if all(float_is_zero(move_line.reserved_qty,
                                                 precision_rounding=move_line.product_uom_id.rounding)
                                   for
                                   move_line in picking.move_line_ids):
                                no_reserved_quantities_ids.add(picking.id)
                        pickings_without_quantities = self.filtered(
                            lambda p: p.id in no_quantities_done_ids and p.id in no_reserved_quantities_ids)

                        pickings_using_lots = self.filtered(
                            lambda p: p.picking_type_id.use_create_lots or p.picking_type_id.use_existing_lots)
                        if pickings_using_lots:
                            lines_to_check = pickings_using_lots._get_lot_move_lines_for_sanity_check(
                                no_quantities_done_ids,
                                separate_pickings)
                            for line in lines_to_check:
                                if not line.lot_name and not line.lot_id:
                                    pickings_without_lots |= line.picking_id
                                    products_without_lots |= line.product_id

                        if not self._should_show_transfers():
                            if pickings_without_moves:
                                raise UserError(_('Please add some items to move.'))
                            if pickings_without_quantities:
                                raise UserError(self._get_without_quantities_error_message())
                            if pickings_without_lots:
                                raise UserError(
                                    _('You need to supply a Bill of Entry number for products %s.') % ', '.join(
                                        products_without_lots.mapped('display_name')))
                        else:
                            message = ""
                            if pickings_without_moves:
                                message += _('Transfers %s: Please add some items to move.') % ', '.join(
                                    pickings_without_moves.mapped('name'))
                            if pickings_without_quantities:
                                message += (_(
                                    '\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved '
                                    'nor'
                                    'done. To force these transfers, switch in edit more and encode the done quantities.') %
                                            ', '.join(
                                                pickings_without_quantities.mapped('name')))
                            if pickings_without_lots:
                                message += _(
                                    '\n\nTransfers %s: You need to supply a Bill of Entry number for products %s.') % (
                                               ', '.join(pickings_without_lots.mapped('name')),
                                               ', '.join(products_without_lots.mapped('display_name')))
                            if message:
                                raise UserError(message.lstrip())
                    else:
                        raise UserError(
                            _('The freight %s has not been confirmed through customs, kindly upload customs '
                              'documents and confirm before validating the picking.') % self.carrier_tracking_ref)
                else:
                    raise UserError(_('Please create a Freight Order for this shipment first. Go to the list view and '
                                      'select it then click action button and choose Shipment Incoming. This can be done '
                                      'for multiple pickings.'))
            else:
                pickings_without_lots = self.browse()
                products_without_lots = self.env['product.product']
                pickings_without_moves = self.filtered(lambda p: not p.move_ids and not p.move_line_ids)
                precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')

                no_quantities_done_ids = set()
                no_reserved_quantities_ids = set()
                for picking in self:
                    if all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
                           picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel'))):
                        no_quantities_done_ids.add(picking.id)
                    if all(float_is_zero(move_line.reserved_qty,
                                         precision_rounding=move_line.product_uom_id.rounding)
                           for
                           move_line in picking.move_line_ids):
                        no_reserved_quantities_ids.add(picking.id)
                pickings_without_quantities = self.filtered(
                    lambda p: p.id in no_quantities_done_ids and p.id in no_reserved_quantities_ids)

                pickings_using_lots = self.filtered(
                    lambda p: p.picking_type_id.use_create_lots or p.picking_type_id.use_existing_lots)
                if pickings_using_lots:
                    lines_to_check = pickings_using_lots._get_lot_move_lines_for_sanity_check(
                        no_quantities_done_ids,
                        separate_pickings)
                    for line in lines_to_check:
                        if not line.lot_name and not line.lot_id:
                            pickings_without_lots |= line.picking_id
                            products_without_lots |= line.product_id

                if not self._should_show_transfers():
                    if pickings_without_moves:
                        raise UserError(_('Please add some items to move.'))
                    if pickings_without_quantities:
                        raise UserError(self._get_without_quantities_error_message())
                    if pickings_without_lots:
                        # if not pickings_without_lots.location_dest_id.is_ict_location:
                        raise UserError(_('You need to supply a Bill of Entry number for products %s.') % ', '.join(
                            products_without_lots.mapped('display_name')))
                else:
                    message = ""
                    if pickings_without_moves:
                        message += _('Transfers %s: Please add some items to move.') % ', '.join(
                            pickings_without_moves.mapped('name'))
                    if pickings_without_quantities:
                        message += (_(
                            '\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved '
                            'nor'
                            'done. To force these transfers, switch in edit more and encode the done quantities.') %
                                    ', '.join(
                                        pickings_without_quantities.mapped('name')))
                    if pickings_without_lots:
                        message += _(
                            '\n\nTransfers %s: You need to supply a Bill of Entry number for products %s.') % (
                                       ', '.join(pickings_without_lots.mapped('name')),
                                       ', '.join(products_without_lots.mapped('display_name')))
                    if message:
                        raise UserError(message.lstrip())
            return super(StockPickingInherit, self)._sanity_check(separate_pickings=True)
        else:
            return super(StockPickingInherit, self)._sanity_check(separate_pickings=True)

    @api.depends('carrier_tracking_ref')
    def _compute_customs_date(self):
        if self.carrier_tracking_ref:
            self.customs_date = self.env['custom.clearance'].search(
                [('freight_id', '=', self.carrier_tracking_ref)]).date

    # TODO WIP
    def button_validate(self):
        settings = self.env['res.config.settings'].sudo().create({})
        if len(self) == 1:
            for pr in self.group_id:
                group_name = pr.name
                purchase_orders = self.env['purchase.order'].sudo().search([('name', '=', group_name)])
                original_order = False

                for purchase_order_x in purchase_orders:
                    purchase_order = purchase_order_x.auto_purchase_order_id
                    if purchase_order:
                        original_order = self.env['purchase.order'].sudo().search(
                            [('id', '=', purchase_order.id), ('company_id', '=', purchase_order.company_id.id)])
                        for orig in original_order:
                            self.send_email_auto(orig, self.location_dest_id.name)
                    msg = _("This order has been received in the sister company in %s please follow up with its "
                            "shipment." % self.location_dest_id.name)
                    if self.supplier_reference:
                        pre_alert = self.env['freight.order'].search(
                            [('bill_entry_ids.purchase_order.picking_ids.id', '=', self.id)])
                        if not pre_alert.supplier_reference:
                            pre_alert.write({
                                'supplier_reference': self.supplier_reference
                            })

                    if original_order:
                        original_order.message_post(body=msg, message_type='notification',
                                                    author_id=self.env.user.id)
                    if settings.group_stock_bill_of_entry_one_shipment:
                        for move in self.move_ids:
                            move.quantity_done = move.quantity_done
                            # Create or update lot number for each product in the move
                            for line in move.move_line_ids:
                                if self.boe_number and self.exit_number:
                                    line.write({
                                        'lot_name': self.boe_number + "#" + self.exit_number,
                                    })
                                elif not self.exit_number:
                                    line.write({
                                            'lot_name': self.boe_number
                                    })

                        # Call the super method to continue with the standard validation process
                        res = super(StockPickingInherit, self).button_validate()
                        self.update_dimensions()
                        return res
                    else:
                        res = super(StockPickingInherit, self).button_validate()
                        self.update_dimensions()
                        return res

            res = super(StockPickingInherit, self).button_validate()
            self.update_dimensions()
            return res
        else:
            raise UserError(_('Please Validate these pickings individually'))

    def update_dimensions(self):
        for line in self.move_ids_without_package:
            for x in line.lot_ids:
                x.sudo().write({
                    'length': line.length,
                    'width': line.width,
                    'height': line.height,
                    'weight': line.weight,
                    'cbm': line.cbm,
                    'dimension_uom': line.dimension_uom,
                    'weight_uom': line.weight_uom
                })

    def send_email_auto(self, original_order, destination_wh):
        # Create a mail template if not already created (assuming it's reused)
        template = self.env['mail.template'].name_search('Intercompany Notifications Template')

        if template:
            subjectt = template[0]
            notif_template = self.env['mail.template'].search([('id', '=', subjectt[0])])

            # Define the email parameters
            email_values = {
                'subject': notif_template.subject + original_order.display_name,
                'author_id': self.env.user.partner_id.id,
                'email_from': self.env.user.email,
                'body_html': notif_template.body_html + self.name + 'Please follow up on its delivery date.</b></br> '
                                                                    'This Email is system generated.</div>',
                'email_to': original_order.create_uid.email
            }

            # Create the mail.mail record
            mail_id = self.env['mail.mail'].sudo().create(email_values)

            mail_id.send()
        else:
            template = self.env['mail.template'].create({
                'name': 'Intercompany Notifications Template',
                'model_id': self.env.ref('reddot_wms.model_stock_picking').id,
                'subject': 'RE: Update on:',
                'body_html': '<p>Here is a reminder that this order has been received in '
                             'the sister company in ' + destination_wh + ' with reference: </p><br><b>',
                'auto_delete': False
            })

            template_ctx = {'object': self}  # Context to render the template, if needed

            # Render the subject and body using the template
            subject = template.subject % template_ctx
            body_html = template.body_html % template_ctx

            # Define the email parameters
            email_values = {
                'subject': subject + original_order.display_name,
                'author_id': self.env.user.partner_id.id,
                'email_from': self.env.user.email,
                'body_html': body_html + " " + self.name + "</br>" + ' Please follow up on its delivery date.</b></br> '
                                                                     ' This Email is system generated',
                'email_to': original_order.create_uid.email
            }
            mail_id = self.env['mail.mail'].sudo().create(email_values)
            mail_id.send()

    # WHEN DEST LOCATION/SOURCE LOCATION IS CHANGED,
    # IT ENSURES CORRECT CHANGE OF LOCATIONS ONCE THE TRANSFERS ARE VALIDATED
    @api.onchange('location_id', 'location_dest_id')
    def _onchange_locations(self):
        (self.move_ids | self.move_ids_without_package).update({
            "location_id": self.location_id,
            "location_dest_id": self.location_dest_id
        })
        if any(line.reserved_qty or line.qty_done for line in self.move_ids.move_line_ids):
            for x in self.move_ids.move_line_ids:
                item = self.env['stock.move.line'].search([('id', '=', x.ids[0])])
                if item:
                    item.write({
                        'location_dest_id': self.location_dest_id
                    })
        return super(StockPickingInherit, self)._onchange_locations()

    @api.model
    def custom_clearance(self, vals):
        return {
            'name': _('Custom Clearance'),
            'type': 'ir.actions.act_window',
            'res_model': 'customs.clearance.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id, 'model': 'stock.picking', 'clearance_count': self.clearance_count}
        }

    def compute_count(self):
        """Compute custom clearance count"""
        for rec in self:
            if rec.env['custom.clearance'].search([('picking_id', '=', rec.id)]):
                rec.clearance_count = rec.env['custom.clearance'].search_count(
                    [('picking_id', '=', rec.id)])
            else:
                rec.clearance_count = 0

    def get_custom_clearance(self):
        """Get custom clearance"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Clearance',
            'view_mode': 'tree,form',
            'res_model': 'custom.clearance',
            'domain': [('picking_id', '=', self.id)],
            'context': "{'create': False}"
        }
