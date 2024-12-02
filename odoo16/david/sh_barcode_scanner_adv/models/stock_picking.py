# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ['barcodes.barcode_events_mixin', 'stock.picking']

    def on_barcode_scanned(self, barcode):
        is_last_scanned = False
        sequence = 0
        warm_sound_code = ""

        if not self.picking_type_id:
            raise UserError(
                _(warm_sound_code + "You must first select a Operation Type."))

        if self.env.company.sudo().sh_inventory_barcode_scanner_last_scanned_color:
            is_last_scanned = True

        if self.env.company.sudo().sh_inventory_barcode_scanner_move_to_top:
            sequence = -1

        if self.env.company.sudo().sh_inventory_barcode_scanner_warn_sound:
            warm_sound_code = "SH_BARCODE_SCANNER_"

        if self.env.company.sudo().sh_inventory_barcode_scanner_auto_close_popup:
            warm_sound_code += "AUTO_CLOSE_AFTER_" + \
                str(self.env.company.sudo(
                ).sh_inventory_barcode_scanner_auto_close_popup) + "_MS&"

        if self and self.state not in ['assigned', 'draft', 'confirmed']:
            selections = self.fields_get()['state']['selection']
            value = next((v[1] for v in selections if v[0]
                          == self.state), self.state)
            raise UserError(
                _(warm_sound_code + "You can not scan item in %s state.") % (value))

        elif self:
            # =================================================================
            # If detailed operation enabled
            # =================================================================
            if self.show_operations:
                field_stock_move_line = False
                field_name_stock_move_line = ''

                field_stock_move_line = ''
                # Find field based on operation type and it's settings
                if self.picking_type_id.code in ["internal", "outgoing"]:
                    field_stock_move_line = 'move_line_ids_without_package'

                if self.picking_type_id.code in ['incoming']:
                    field_stock_move_line = 'move_line_nosuggest_ids'
                    if self.show_reserved:
                        field_stock_move_line = 'move_line_ids_without_package'

                if not hasattr(self, field_stock_move_line):
                    raise UserError(
                        _('No any valid stock move line field found for this operation'))

                field_name_stock_move_line = field_stock_move_line
                field_stock_move_line = getattr(
                    self, field_stock_move_line, False)

                records_stock_move_line = False
                domain = []
                field_stock_move_line.update({
                    'sh_inventory_barcode_scanner_is_last_scanned': False,
                    'sequence': 0,
                })

                is_multi_barcode = self.env.user.has_group(
                    'sh_barcode_scanner_adv.group_sh_barcode_scanner_multi_barcode')

                if self.env.company.sudo().sh_inventory_barcode_scanner_type == 'barcode':
                    if is_multi_barcode:
                        records_stock_move_line = field_stock_move_line.filtered(
                            lambda ml: ml.product_id.barcode == barcode)
                        if not records_stock_move_line:
                            for line in field_stock_move_line:
                                if line.product_id and line.product_id.barcode_line_ids:
                                    for barcode_line in line.product_id.barcode_line_ids:
                                        if barcode_line.name == barcode:
                                            records_stock_move_line = line
                                            break

                        domain = ['|',
                                  ("barcode", "=", barcode),
                                  ("barcode_line_ids.name", "=", barcode)
                                  ]

                    else:
                        records_stock_move_line = field_stock_move_line.filtered(
                            lambda ml: ml.product_id.barcode == barcode)
                        domain = [("barcode", "=", barcode)]

                elif self.env.company.sudo().sh_inventory_barcode_scanner_type == 'int_ref':
                    records_stock_move_line = field_stock_move_line.filtered(
                        lambda ml: ml.product_id.default_code == barcode)
                    domain = [("default_code", "=", barcode)]

                elif self.env.company.sudo().sh_inventory_barcode_scanner_type == 'sh_qr_code':
                    records_stock_move_line = field_stock_move_line.filtered(
                        lambda ml: ml.product_id.sh_qr_code == barcode)
                    domain = [("sh_qr_code", "=", barcode)]

                elif self.env.company.sudo().sh_inventory_barcode_scanner_type == 'all':
                    if is_multi_barcode:

                        records_stock_move_line = field_stock_move_line.filtered(lambda ml: ml.product_id.barcode == barcode or
                                                                                 ml.product_id.default_code == barcode or
                                                                                 ml.product_id.sh_qr_code == barcode
                                                                                 )

                        if not records_stock_move_line:
                            for line in field_stock_move_line:
                                if line.product_id and line.product_id.barcode_line_ids:
                                    for barcode_line in line.product_id.barcode_line_ids:
                                        if barcode_line.name == barcode:
                                            records_stock_move_line = line
                                            break

                        domain = ["|", "|", "|",
                                  ("default_code", "=", barcode),
                                  ("barcode", "=", barcode),
                                  ("barcode_line_ids.name", "=", barcode),
                                  ("sh_qr_code", "=", barcode)
                                  ]
                    else:
                        records_stock_move_line = field_stock_move_line.filtered(lambda ml: ml.product_id.barcode == barcode or
                                                                                 ml.product_id.default_code == barcode or
                                                                                 ml.product_id.sh_qr_code == barcode
                                                                                 )

                        domain = ["|", "|",

                                  ("default_code", "=", barcode),
                                  ("barcode", "=", barcode),
                                  ("sh_qr_code", "=", barcode)

                                  ]

                # ---------------------------------------
                # Quantity increase or add line logic
                # --------------------------------------
                if records_stock_move_line:
                    # increase last line qty
                    # 15.0.3
                    if len(records_stock_move_line) > 1:
                        records_stock_move_line = records_stock_move_line[len(records_stock_move_line) - 1]
 
                    qty_done = records_stock_move_line.qty_done + 1
                    vals_line = {
                        'qty_done': qty_done,
                    }
                    self.update({
                        field_name_stock_move_line:
                        [(1, records_stock_move_line.id, vals_line)]
                    })

                    # if records_stock_move_line.qty_done == records_stock_move_line.product_uom_qty + 1:
                    #     warning_mess = {
                    #         'title': _('Alert!'),
                    #         'message': warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                    #     }
                    #     return {'warning': warning_mess}
                    # 15.0.3

                    # for line in records_stock_move_line:
                    #     line.qty_done += 1
                    #     line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                    #     line.sequence = sequence
                    #     break

                elif self.state == 'draft':
                    if self.env.company.sudo().sh_inventory_barcode_scanner_is_add_product:
                        search_product = self.env["product.product"].search(
                            domain, limit=1)
                        if search_product:

                            line_val = {
                                'product_id': search_product.id,
                                'location_dest_id': self.location_dest_id.id,
                                'qty_done': 1,
                                'location_id': self.location_id.id,
                                'sh_inventory_barcode_scanner_is_last_scanned': is_last_scanned,
                                'sequence': sequence,
                                # 'picking_id': self.id,
                            }
                            if search_product.uom_id:
                                line_val.update({
                                    "product_uom_id": search_product.uom_id.id,
                                })
                            self.update({
                                field_name_stock_move_line: [(0, 0, line_val)]
                            })
                        else:
                            raise UserError(
                                _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

                    else:
                        raise UserError(
                            _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

                else:
                    raise UserError(
                        _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

                # ---------------------------------------
                # Quantity increase or add line logic
                # --------------------------------------

            # =================================================================
            # If detailed operation enabled
            # =================================================================
            else:
                # =================================================================
                # If detailed operation not enabled
                # =================================================================
                self.move_ids_without_package.update({
                    'sh_inventory_barcode_scanner_is_last_scanned': False,
                    'sequence': 0,
                })
                search_mls = False
                domain = []
                is_multi_barcode = self.env.user.has_group(
                    'sh_barcode_scanner_adv.group_sh_barcode_scanner_multi_barcode')

                if self.env.company.sudo().sh_inventory_barcode_scanner_type == 'barcode':
                    if is_multi_barcode:
                        search_mls = self.move_ids_without_package.filtered(
                            lambda ml: ml.product_id.barcode == barcode)
                        if not search_mls:
                            for line in self.move_ids_without_package:
                                if line.product_id and line.product_id.barcode_line_ids:
                                    for barcode_line in line.product_id.barcode_line_ids:
                                        if barcode_line.name == barcode:
                                            search_mls = line
                                            break

                        domain = ['|',
                                  ("barcode", "=", barcode),
                                  ("barcode_line_ids.name", "=", barcode)
                                  ]

                    else:
                        search_mls = self.move_ids_without_package.filtered(
                            lambda ml: ml.product_id.barcode == barcode)
                        domain = [("barcode", "=", barcode)]

                elif self.env.company.sudo().sh_inventory_barcode_scanner_type == 'int_ref':
                    search_mls = self.move_ids_without_package.filtered(
                        lambda ml: ml.product_id.default_code == barcode)
                    domain = [("default_code", "=", barcode)]

                elif self.env.company.sudo().sh_inventory_barcode_scanner_type == 'sh_qr_code':
                    search_mls = self.move_ids_without_package.filtered(
                        lambda ml: ml.product_id.sh_qr_code == barcode)
                    domain = [("sh_qr_code", "=", barcode)]

                elif self.env.company.sudo().sh_inventory_barcode_scanner_type == 'all':
                    if is_multi_barcode:
                        search_mls = self.move_ids_without_package.filtered(lambda ml: ml.product_id.barcode == barcode or
                                                                            ml.product_id.default_code == barcode or
                                                                            ml.product_id.sh_qr_code == barcode
                                                                            )
                        if not search_mls:
                            for line in self.move_ids_without_package:
                                if line.product_id and line.product_id.barcode_line_ids:
                                    for barcode_line in line.product_id.barcode_line_ids:
                                        if barcode_line.name == barcode:
                                            search_mls = line
                                            break

                        domain = ["|", "|", "|",
                                  ("default_code", "=", barcode),
                                  ("barcode", "=", barcode),
                                  ("barcode_line_ids.name", "=", barcode),
                                  ("sh_qr_code", "=", barcode)
                                  ]
                    else:
                        search_mls = self.move_ids_without_package.filtered(lambda ml: ml.product_id.barcode == barcode or
                                                                            ml.product_id.default_code == barcode or
                                                                            ml.product_id.sh_qr_code == barcode
                                                                            )

                        domain = ["|", "|",
                                  ("default_code", "=", barcode),
                                  ("barcode", "=", barcode),
                                  ("sh_qr_code", "=", barcode)
                                  ]

                if search_mls:
                    for move_line in search_mls:
                        # 15.0.3
                        if not self.immediate_transfer and self.state == 'draft' and move_line.is_initial_demand_editable:
                            move_line.product_uom_qty = move_line.product_uom_qty + 1
                            move_line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                            move_line.sequence = sequence
                        elif self.immediate_transfer and move_line.is_quantity_done_editable:
                            move_line.quantity_done = move_line.quantity_done + 1
                            move_line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                            move_line.sequence = sequence
                        elif move_line.is_quantity_done_editable:
                            move_line.quantity_done = move_line.quantity_done + 1
                            move_line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                            move_line.sequence = sequence
                            if move_line.quantity_done == move_line.product_uom_qty + 1:
                                warning_mess = {
                                    'title': _('Alert!'),
                                    'message': warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                                }
                                return {'warning': warning_mess}
                        elif move_line.show_details_visible:
                            if move_line.show_details_visible:
                                raise UserError(
                                    _(warm_sound_code + "You can not scan product item for Detailed Operations directly here, Pls click detail button (at end each line) and than rescan your product item."))

                        break
                        # 15.0.3
                    # for move_line in search_mls:
                    #     if move_line.show_details_visible:
                    #         raise UserError(
                    #             _(warm_sound_code + "You can not scan product item for Detailed Operations directly here, Pls click detail button (at end each line) and than rescan your product item."))
                    #
                    #     if self.state == 'draft':
                    #         move_line.product_uom_qty += 1
                    #         move_line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                    #         move_line.sequence = sequence
                    #     else:
                    #         move_line.quantity_done = move_line.quantity_done + 1
                    #         move_line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                    #         move_line.sequence = sequence
                    #         if move_line.quantity_done == move_line.product_uom_qty + 1:
                    #             warning_mess = {
                    #                 'title': _('Alert!'),
                    #                 'message': warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                    #             }
                    #             return {'warning': warning_mess}
                    #     break
                elif self.state == 'draft':
                    if self.env.company.sudo().sh_inventory_barcode_scanner_is_add_product:
                        if not self.picking_type_id:
                            raise UserError(
                                _(warm_sound_code + "You must first select a Operation Type."))
                        search_product = self.env["product.product"].search(
                            domain, limit=1)
                        if search_product:
                            order_line_val = {
                                "name": search_product.name,
                                "product_id": search_product.id,
                                # "product_uom_qty": 1,
                                "price_unit": search_product.lst_price,
                                "location_id": self.location_id.id,
                                "location_dest_id": self.location_dest_id.id,
                                'sh_inventory_barcode_scanner_is_last_scanned': is_last_scanned,
                                'sequence': sequence,
                            }
                            if search_product.uom_id:
                                order_line_val.update({
                                    "product_uom": search_product.uom_id.id,
                                })
                            if self.immediate_transfer:
                                order_line_val.update({
                                    "quantity_done": 1,
                                })
                            else:
                                order_line_val.update({
                                    "product_uom_qty": 1,
                                })

                            old_lines = self.move_ids_without_package
                            new_order_line = self.move_ids_without_package.new(
                                order_line_val)
                            self.move_ids_without_package = old_lines + new_order_line
                            new_order_line._onchange_product_id()
                        else:
                            raise UserError(
                                _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

                    else:
                        raise UserError(
                            _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

                else:
                    raise UserError(
                        _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

                # =================================================================
                # If detailed operation not enabled
                # =================================================================
