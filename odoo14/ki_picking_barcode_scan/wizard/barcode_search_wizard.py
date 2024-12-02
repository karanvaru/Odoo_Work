from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SearchBarcodeProductPickingWizard(models.TransientModel):
    _name = 'search.barcode.product.picking.wizard'
    _description = "Search Product and Picking From Barcode"
    _rec_name = "picking"

    barcode = fields.Char(
        string="Product Barcode / Internal Reference",
    )
    picking = fields.Char(
        string="picking Name / Tracking Reference",
    )

    move_ids = fields.Many2many(
        'stock.move',
        string="Stock Move",
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string="Picking",
    )

    check_picking = fields.Boolean(
        string="Picking Not Found",
    )
    check_barcode = fields.Boolean(
        string="Product Not Found",
    )
    validate_done = fields.Boolean(
        string="validate Done",
        default=False
    )

    search_by_product = fields.Selection([
        ('barcode', 'Barcode'),
        ('internal_reference', 'Internal Reference')
    ], string='Product Search By', default='barcode')
    search_by_picking = fields.Selection([
        ('name', 'Name'),
        ('tracking_ref', 'Tracking Reference'),
        ('awb_number', 'AWB Number')
    ], string='Picking Search By', default='name')


    @api.onchange('picking', 'barcode')
    def onchange_picking_barcode(self):
        if self.picking:
            stock_picking = ''
            if self.search_by_picking == 'name':
                stock_picking_id = self.env['stock.picking'].sudo().search(
                    [('name', '=', self.picking)], limit=1
                )
                stock_picking = stock_picking_id
            elif self.search_by_picking == 'tracking_ref':
                stock_picking_id = self.env['stock.picking'].sudo().search(
                    [('carrier_tracking_ref', '=', self.picking)], limit=1
                )
                stock_picking = stock_picking_id
            elif self.search_by_picking == 'awb_number':
                stock_picking_id = self.env['stock.picking'].sudo().search(
                    [('mp_awb_number', '=', self.picking)], limit=1
                )
                stock_picking = stock_picking_id
            if stock_picking:
                self.check_picking = False
                self.picking_id = stock_picking
                product = []
                for rec in self.picking_id.move_ids_without_package.product_id:
                    product.append(rec.id)
                if self.barcode:
                    self.check_barcode = False
                    search_product = ''
                    if self.search_by_product == 'barcode':
                        search_product_id = self.env['product.product'].sudo().search(
                            [('barcode', '=', self.barcode), ('id', 'in', product)], limit=1
                        )
                        search_product = search_product_id
                    elif self.search_by_product == 'internal_reference':
                        search_product_id = self.env['product.product'].sudo().search(
                            [('default_code', '=', self.barcode), ('id', 'in', product)], limit=1
                        )
                        search_product = search_product_id
                    search_move = self.env['stock.move'].sudo().search(
                        [('picking_id', '=', self.picking_id.id), ('product_id', '=', search_product.id)], limit=1
                    )
                    if search_product and search_move:
                        self.write({
                            'move_ids': [(4, search_move.id)]
                        })
                    else:
                        self.check_barcode = True
                        self.barcode = ""
            else:
                self.check_picking = True
                self.picking_id = False
                self.move_ids = False
                self.picking = ""
                self.barcode = ""
        else:
            self.picking_id = False
            self.move_ids = False
            self.barcode = ""

    def validate_button(self):
        if self.picking:
            if self.picking_id.state == 'done':
                raise ValidationError(_('Picking already Validated'))
            else:
                picking_validated = False
                search_move = []
                for move in self.move_ids:
                    search_move.append(move)
                for rec in self.picking_id.move_ids_without_package:
                    if rec in search_move:
                        picking_validated = True
                    else:
                        added_pro_list = []
                        for added_pro in self.move_ids.product_id:
                            added_pro_list.append(added_pro.id)

                        pro_missing_list = []
                        for move_line in self.picking_id.move_ids_without_package:
                            search_product_missing = self.env['product.product'].sudo().search(
                                [('id', '=', move_line.product_id.id), ('id', 'not in', added_pro_list)]
                            )
                            if search_product_missing:
                                pro_missing_list.append(search_product_missing.name)
                        missing_product = "\n"
                        missing_product += "\n".join(pro_missing_list)
                        raise ValidationError(
                            _('Product Missing: %s ', (missing_product))
                            )

                if picking_validated:
                    immediate_transfer_line_ids = []
                    for picking in self.picking_id:
                        immediate_transfer_line_ids.append([0, False, {
                            'picking_id': picking.id,
                            'to_immediate': True
                        }])

                    res = self.env['stock.immediate.transfer'].create({
                        'pick_ids': [(4, p.id) for p in self.picking_id],
                        'show_transfers': False,
                        'immediate_transfer_line_ids': immediate_transfer_line_ids
                    })
                    self.validate_done = True

                    return res.with_context(button_validate_picking_ids=res.pick_ids.ids).process()

    def next_button(self):
        action = self.env.ref('ki_picking_barcode_scan.action_search_barcode_picking_product_wizard').sudo().read([])[0]
        return action

    @api.model
    def get_data(self):
        stock_picking_id = self.env['stock.picking'].sudo().search([])
        product_ids = self.env['product.product'].sudo().search([])
        stock_picking_dict = {}
        for rec in stock_picking_id:
            stock_picking_dict[rec.id] = rec.name
        product_ids_dict = {}
        for rec in product_ids:
            product_ids_dict[rec.id] = rec.name
        picking_type = self.env['stock.picking.type'].search([])
        picking_type_dict = {}
        for rec in picking_type:
            picking_type_dict[rec.id] = rec.name

        return {
            'stock_picking_dict': stock_picking_dict,
            'product_ids_dict': product_ids_dict,
            'picking_type_dict': picking_type_dict,
        }


