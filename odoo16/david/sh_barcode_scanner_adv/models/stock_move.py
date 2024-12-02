# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    sequence = fields.Integer(string='Sequence', default=0)
    sh_inventory_barcode_scanner_is_last_scanned = fields.Boolean(
        string="Last Scanned?")


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["barcodes.barcode_events_mixin", "stock.move"]

    sequence = fields.Integer(string="Sequence", default=0)
    sh_inventory_barcode_scanner_is_last_scanned = fields.Boolean(
        string="Last Scanned?")

    def sh_stock_move_barcode_scanner_has_tracking(self, barcode, sequence, is_last_scanned, warm_sound_code):
        if self.picking_code == 'incoming':
            # FOR PURCHASE
            # LOT PRODUCT
            if self.product_id.tracking == 'lot':
                # First Time Scan
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: r.lot_name == False)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode,
                        }
                        self.update({
                            'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        break
                else:
                    # Second Time Scan
                    lines = self.move_line_nosuggest_ids.filtered(
                        lambda r: r.lot_name == barcode)
                    if lines:
                        for line in lines:
                            # odoo v14 update below way
                            qty_done = line.qty_done + 1
                            vals_line = {
                                'qty_done': qty_done,
                            }
                            self.update({
                                'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                            })
                            # odoo v14 update below way
                            break

                    else:
                        move_lines_commands = self._generate_serial_move_line_commands(
                            [barcode])
                        # New Barcode Scan then create new line
                        # vals_line = {
                        #     'product_id': self.product_id.id,
                        #     'location_dest_id': self.location_dest_id.id,
                        #     'lot_name': barcode,
                        #     'qty_done': 1,
                        #     'product_uom_id': self.product_uom.id,
                        #     'location_id': self.location_id.id,
                        # }
                        self.update({
                            'move_line_nosuggest_ids': move_lines_commands
                        })

            # SERIAL PRODUCT
            if self.product_id.tracking == 'serial':
                # lot_names = self.env['stock.lot'].generate_lot_names(
                #     barcode, False)

                # VALIDATION SERIAL NO. ALREADY EXIST.
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: r.lot_name == barcode)
                if lines:
                    raise UserError(
                        _(warm_sound_code + "Serial Number already exist!"))
                # First Time Scan
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: r.lot_name == False)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode
                        }
                        self.update({
                            'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        break
                else:
                    move_lines_commands = self._generate_serial_move_line_commands(
                        [barcode])

                    # Create new line if not found any unallocated serial number line
                    # vals_line = {
                    #     'product_id': self.product_id.id,
                    #     'location_dest_id': self.location_dest_id.id,
                    #     'lot_name': barcode,
                    #     'qty_done': 1,
                    #     'product_uom_id': self.product_uom.id,
                    #     'location_id': self.location_id.id,
                    # }
                    self.update({
                        'move_line_nosuggest_ids': move_lines_commands
                    })
            quantity_done = 0
            for move_line in self.move_line_nosuggest_ids:
                quantity_done += move_line.product_uom_id._compute_quantity(
                    move_line.qty_done, self.product_uom, round=False)

            if quantity_done == self.product_uom_qty + 1:
                warning_mess = {
                    'title': _('Alert!'),
                    'message': warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                }
                return {'warning': warning_mess}

        elif self and self.picking_code in ['outgoing', 'internal']:
            # FOR SALE
            # LOT PRODUCT
            quant_obj = self.env['stock.quant']

            # FOR LOT PRODUCT
            if self.product_id.tracking == 'lot':
                # First Time Scan
                quant = quant_obj.search([
                    ('product_id', '=', self.product_id.id),
                    ('quantity', '>', 0),
                    ('location_id.usage', '=', 'internal'),
                    ('lot_id.name', '=', barcode),
                    ('location_id', 'child_of', self.location_id.id)
                ], limit=1)

                if not quant:
                    raise UserError(
                        _(warm_sound_code + "There are no available qty for this lot/serial.%s") % (barcode))

                lines = self.move_line_ids.filtered(
                    lambda r: r.lot_id == False)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_id': quant.lot_id.id
                        }
                        self.update({
                            'move_line_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        break
                else:
                    # Second Time Scan
                    lines = self.move_line_ids.filtered(
                        lambda r: r.lot_id.name == barcode)
                    if lines:
                        for line in lines:
                            # odoo v14 update below way
                            qty_done = line.qty_done + 1
                            vals_line = {
                                'qty_done': qty_done,
                            }
                            self.update({
                                'move_line_ids': [(1, line.id, vals_line)]
                            })
                            # odoo v14 update below way
                            break
                    else:
                        # move_lines_commands = self._generate_serial_move_line_commands(
                        #     [barcode])
                        move_lines_commands = []
                        lot = quant.lot_id
                        move_line_vals = self._prepare_move_line_vals(
                            quantity=0)
                        move_line_vals['lot_id'] = lot.id
                        move_line_vals['lot_name'] = lot.name
                        move_line_vals['product_uom_id'] = self.product_id.uom_id.id
                        move_line_vals['qty_done'] = 1
                        move_lines_commands.append((0, 0, move_line_vals))

                        # move_lines_commands.append((0, 0, move_line_vals))
                        # New Barcode Scan then create new line
                        vals_line = {
                            'product_id': self.product_id.id,
                            'location_dest_id': self.location_dest_id.id,
                            'lot_id': quant.lot_id.id,
                            'qty_done': 1,
                            'product_uom_id': self.product_uom.id,
                            'location_id': quant.location_id.id,
                        }

                        self.update({
                            'move_line_ids': move_lines_commands
                        })
                        self._onchange_move_line_ids()

            # FOR SERIAL PRODUCT
            if self.product_id.tracking == 'serial':
                # First Time Scan
                lines = self.move_line_ids.filtered(
                    lambda r: r.lot_id.name == barcode)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        vals_line = {
                            'qty_done': qty_done,
                        }
                        self.update({
                            'move_line_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        res = {}
                        if float_compare(line.qty_done, 1.0, precision_rounding=line.product_id.uom_id.rounding) != 0:
                            message = _(
                                warm_sound_code + 'You can only process 1.0 %s of products with unique serial number.') % line.product_id.uom_id.name
                            res['warning'] = {'title': _(
                                'Warning'), 'message': message}
                            return res
                        break
                else:
                    list_allocated_serial_ids = []
                    if self.move_line_ids:
                        for line in self.move_line_ids:
                            if line.lot_id:
                                list_allocated_serial_ids.append(
                                    line.lot_id.id)

                    # if need new line.
                    quant = quant_obj.search([
                        ('product_id', '=', self.product_id.id),
                        ('quantity', '>', 0),
                        ('location_id.usage', '=', 'internal'),
                        ('lot_id.name', '=', barcode),
                        ('location_id', 'child_of', self.location_id.id),
                        ('lot_id.id', 'not in', list_allocated_serial_ids),
                    ], limit=1)

                    if not quant:
                        raise UserError(
                            _(warm_sound_code + "There are no available qty for this lot/serial: %s") % (barcode))

                    move_lines_commands = []
                    lot = quant.lot_id
                    move_line_vals = self._prepare_move_line_vals(
                        quantity=0)
                    move_line_vals['lot_id'] = lot.id
                    move_line_vals['lot_name'] = lot.name
                    move_line_vals['product_uom_id'] = self.product_id.uom_id.id
                    move_line_vals['qty_done'] = 1
                    move_lines_commands.append((0, 0, move_line_vals))
                    # New Barcode Scan then create new line
                    vals_line = {
                        'product_id': self.product_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'lot_id': quant.lot_id.id,
                        'qty_done': 1,
                        'product_uom_id': self.product_uom.id,
                        'location_id': quant.location_id.id,
                    }
                    self.update({
                        'move_line_ids':  move_lines_commands
                    })
                    self._onchange_move_line_ids()

            quantity_done = 0
            for move_line in self._get_move_lines():
                quantity_done += move_line.product_uom_id._compute_quantity(
                    move_line.qty_done, self.product_uom, round=False)

            if self.picking_code == 'outgoing' and quantity_done == self.product_uom_qty + 1:
                warning_mess = {
                    'title': _('Alert!'),
                    'message': warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                }
                return {'warning': warning_mess}
        else:
            raise UserError(
                _(warm_sound_code + "Picking type is not outgoing or incoming or internal transfer."))

    def sh_stock_move_barcode_scanner_no_tracking(self, barcode, sequence, is_last_scanned, warm_sound_code):
        move_lines = self._get_move_lines()
        # 15.0.3

        if move_lines:
            for line in move_lines:
                is_multi_barcode = self.env.user.has_group(
                    "sh_barcode_scanner_adv.group_sh_barcode_scanner_multi_barcode")
                if self.env.company.sudo().sh_inventory_barcode_scanner_type == "barcode":

                    is_match_product = False
                    if self.product_id.barcode == barcode:
                        is_match_product = True

                    if not is_match_product and self.product_id.barcode_line_ids and is_multi_barcode:
                        for barcode_line in self.product_id.barcode_line_ids:
                            if barcode_line.name == barcode:
                                is_match_product = True
                                break

                    if is_match_product:
                        similar_lines = move_lines.filtered(
                            lambda ml: ml.product_id == self.product_id)
                        len_similar_lines = len(similar_lines)
                        if len_similar_lines:
                            last_line = similar_lines[len_similar_lines - 1]
                            last_line.qty_done += 1
                            last_line._onchange_qty_done()

#                         line.qty_done += 1

                        self.sequence = sequence
                        self.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned

                        if self.quantity_done == self.product_uom_qty + 1:
                            warning_mess = {
                                "title": _("Alert!"),
                                "message": warm_sound_code + "Becareful! Quantity exceed than initial demand!"
                            }
                            return {"warning": warning_mess}
                        break
                    else:
                        raise UserError(
                            _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

                elif self.env.company.sudo().sh_inventory_barcode_scanner_type == "int_ref":
                    if self.product_id.default_code == barcode:
                        similar_lines = move_lines.filtered(
                            lambda ml: ml.product_id.default_code == barcode)
                        len_similar_lines = len(similar_lines)
                        if len_similar_lines:
                            last_line = similar_lines[len_similar_lines - 1]
                            last_line.qty_done += 1
                            last_line._onchange_qty_done()
                        self.sequence = sequence
                        self.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                        if self.quantity_done == self.product_uom_qty + 1:
                            warning_mess = {
                                "title": _("Alert!"),
                                "message": warm_sound_code + "Becareful! Quantity exceed than initial demand!"
                            }
                            return {"warning": warning_mess}
                        break
                    else:
                        raise UserError(
                            _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))
                elif self.env.company.sudo().sh_inventory_barcode_scanner_type == "sh_qr_code":
                    if self.product_id.sh_qr_code == barcode:
                        similar_lines = move_lines.filtered(
                            lambda ml: ml.product_id.sh_qr_code == barcode)
                        len_similar_lines = len(similar_lines)
                        if len_similar_lines:
                            last_line = similar_lines[len_similar_lines - 1]
                            last_line.qty_done += 1
                            last_line._onchange_qty_done()
                        self.sequence = sequence
                        self.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                        if self.quantity_done == self.product_uom_qty + 1:
                            warning_mess = {
                                "title": _("Alert!"),
                                "message": warm_sound_code + "Becareful! Quantity exceed than initial demand!"
                            }
                            return {"warning": warning_mess}
                        break
                    else:
                        raise UserError(
                            _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

                elif self.env.company.sudo().sh_inventory_barcode_scanner_type == "all":
                    is_match_product = False
                    if self.product_id.barcode == barcode or self.product_id.default_code == barcode or self.product_id.sh_qr_code == barcode:
                        is_match_product = True

                    if not is_match_product and self.product_id.barcode_line_ids and is_multi_barcode:
                        for barcode_line in self.product_id.barcode_line_ids:
                            if barcode_line.name == barcode:
                                is_match_product = True
                                break

                    if is_match_product:
                        similar_lines = move_lines.filtered(
                            lambda ml: ml.product_id == self.product_id)
                        len_similar_lines = len(similar_lines)
                        if len_similar_lines:
                            last_line = similar_lines[len_similar_lines - 1]
                            last_line.qty_done += 1
                            last_line._onchange_qty_done()

                        self.sequence = sequence
                        self.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned

                        if self.quantity_done == self.product_uom_qty + 1:
                            warning_mess = {
                                "title": _("Alert!"),
                                "message": warm_sound_code + "Becareful! Quantity exceed than initial demand!"
                            }
                            return {"warning": warning_mess}
                        break
                    else:
                        raise UserError(
                            _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

        else:
            raise UserError(
                _(warm_sound_code + "Pls add all product items in line than rescan."))

    def on_barcode_scanned(self, barcode):
        is_last_scanned = False
        sequence = 0
        warm_sound_code = ""

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

        # UPDATED CODE
        # =============================
        if self.picking_id.state not in ["confirmed", "assigned"]:
            selections = self.picking_id.fields_get()["state"]["selection"]
            value = next((v[1] for v in selections if v[0] ==
                          self.picking_id.state), self.picking_id.state)
            raise UserError(
                _(warm_sound_code + "You can not scan item in %s state.") % (value))

        # if self.has_tracking != 'none':
        #     # LOT / SERIAL FLOW
        #     self.sh_stock_move_barcode_scanner_has_tracking(
        #         barcode, sequence, is_last_scanned, warm_sound_code)
        # else:
        #     # NORMAL PRODUCT FLOW
        #     self.sh_stock_move_barcode_scanner_no_tracking(
        #         barcode, sequence, is_last_scanned, warm_sound_code)

        # -----------------------------
        # sh_auto_serial_scanner
        # -----------------------------
        show_lots_m2o = self.has_tracking != 'none' and (
            self.picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id)
        show_lots_text = self.has_tracking != 'none' and self.picking_type_id.use_create_lots and not self.picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id

        res = {}
        if show_lots_m2o:
            res = self.sh_auto_serial_scanner_has_tracking_show_lots_m2o(
                barcode, sequence, is_last_scanned, warm_sound_code)
        elif show_lots_text:
            res = self.sh_auto_serial_scanner_has_tracking_show_lots_text(
                barcode, sequence, is_last_scanned, warm_sound_code)
        else:
            res = self.sh_stock_move_barcode_scanner_no_tracking(
                barcode, sequence, is_last_scanned, warm_sound_code)
        return res

    def sh_auto_serial_scanner_search_or_create_lot_serial_number(self, lot_name, product_id, warm_sound_code):
        """
            Search or Create lot number
            @param: lot_name - search record based given lot name.
            @param: product_id - Integer -  search record based given product_id.
            @return: lot object
        """
        # able to create lots, whatever the value of ` use_create_lots`.

        # Search or create lot/serial number
        lot = self.env['stock.lot'].search([
            ('name', '=', lot_name),
            ('product_id', '=',
                product_id),
            ('company_id', '=',
                self.env.company.id)
        ], limit=1)
        if not lot:
            lot = self.env['stock.lot'].create({
                'name': lot_name,
                'product_id': product_id,
                # 'product_qty': move_line_vals['qty_done'],
                'company_id': self.env.company.id,
            })

        if not lot:
            raise UserError(
                _(warm_sound_code + "Can't create Lots/Serial Number record for this lot/serial. % s") % (lot_name))

        return lot

    def sh_auto_serial_scanner_has_tracking_show_lots_m2o(self, barcode, sequence, is_last_scanned, warm_sound_code):
        # self.picking_id.show_lots_text
        if self.picking_code == 'incoming':
            # FOR PURCHASE
            # LOT PRODUCT
            # --------------------------------------------
            # incoming - show_lots_m2o - lot
            # --------------------------------------------
            if self.product_id.tracking == 'lot':
                # First Time Scan
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: not r.lot_id)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(
                            barcode, self.product_id.id, warm_sound_code)
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode,
                            'lot_id': lot.id,
                        }
                        self.update({
                            'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        break
                else:
                    # Second Time Scan
                    lines = self.move_line_nosuggest_ids.filtered(
                        lambda r: r.lot_id.name == barcode)
                    if lines:
                        for line in lines:
                            # odoo v14 update below way
                            qty_done = line.qty_done + 1
                            vals_line = {
                                'qty_done': qty_done,
                            }
                            self.update({
                                'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                            })
                            # odoo v14 update below way
                            break

                    else:
                        move_lines_commands = self._generate_serial_move_line_commands(
                            [barcode])
                        for move_line_command in move_lines_commands:
                            move_line_vals = move_line_command[2]
                            lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(
                                barcode, self.product_id.id, warm_sound_code)
                            move_line_vals['lot_id'] = lot.id
                        self.update({
                            'move_line_nosuggest_ids': move_lines_commands
                        })
                        self._onchange_move_line_ids()

            # SERIAL PRODUCT
            # --------------------------------------------
            # incoming - show_lots_m2o - serial
            # --------------------------------------------
            if self.product_id.tracking == 'serial':
                # lot_names = self.env['stock.lot'].generate_lot_names(
                #     barcode, False)

                # VALIDATION SERIAL NO. ALREADY EXIST.
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: r.lot_id.name == barcode)
                if lines:
                    raise UserError(
                        _(warm_sound_code + "Serial Number already exist!"))
                # First Time Scan
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: not r.lot_id)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        #qty_done = line.qty_done + 1
                        qty_done = 1
                        lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(
                            barcode, self.product_id.id, warm_sound_code)
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode,
                            'lot_id': lot.id
                        }
                        self.update({
                            'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        break
                else:
                    move_lines_commands = self._generate_serial_move_line_commands(
                        [barcode])

                    for move_line_command in move_lines_commands:
                        move_line_vals = move_line_command[2]
                        lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(
                            barcode, self.product_id.id, warm_sound_code)
                        move_line_vals['lot_id'] = lot.id
                    self.update({
                        'move_line_nosuggest_ids': move_lines_commands
                    })
                    self._onchange_move_line_ids()

            quantity_done = 0
            for move_line in self.move_line_nosuggest_ids:
                quantity_done += move_line.product_uom_id._compute_quantity(
                    move_line.qty_done, self.product_uom, round=False)

            if quantity_done == self.product_uom_qty + 1:
                warning_mess = {
                    'title': _('Alert!'),
                    'message': 'Becareful! Quantity exceed than initial demand!'
                }
                return {'warning': warning_mess}

        elif self and self.picking_code in ['outgoing', 'internal']:
            # FOR SALE
            # LOT PRODUCT
            quant_obj = self.env['stock.quant']

            # FOR LOT PRODUCT
            # --------------------------------------------
            # outgoing / internal - show_lots_m2o - lot
            # --------------------------------------------
            if self.product_id.tracking == 'lot':
                # First Time Scan
                quant = quant_obj.search([
                    ('product_id', '=', self.product_id.id),
                    ('quantity', '>', 0),
                    ('location_id.usage', '=', 'internal'),
                    ('lot_id.name', '=', barcode),
                    ('location_id', 'child_of', self.location_id.id)
                ], limit=1)

                if not quant and not self.picking_id.picking_type_id.use_create_lots:
                    raise UserError(
                        _(warm_sound_code + "There are no available qty for this lot/serial.%s") % (barcode))

                lot = False
                if quant and quant.lot_id:
                    lot = quant.lot_id
                else:
                    # Create New Lot if it's allow.
                    lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(
                        barcode, self.product_id.id, warm_sound_code)
                # Assign lot_id in move_lines_command
                if not lot:
                    raise UserError(
                        _(warm_sound_code + "Can't create Lots/Serial Number record for this lot/serial. % s") % (barcode))

                lines = self.move_line_ids.filtered(
                    lambda r: not r.lot_id)

                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_id': lot.id
                        }
                        self.update({
                            'move_line_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        break
                else:
                    # Second Time Scan
                    lines = self.move_line_ids.filtered(
                        lambda r: r.lot_id.name == barcode)
                    if lines:
                        for line in lines:
                            # odoo v14 update below way
                            qty_done = line.qty_done + 1
                            vals_line = {
                                'qty_done': qty_done,
                            }
                            self.update({
                                'move_line_ids': [(1, line.id, vals_line)]
                            })
                            # odoo v14 update below way
                            break
                    else:
                        # move_lines_commands = self._generate_serial_move_line_commands(
                        #     [barcode])
                        move_lines_commands = []
                        move_line_vals = self._prepare_move_line_vals(
                            quantity=0)
                        move_line_vals['lot_id'] = lot.id
                        move_line_vals['lot_name'] = lot.name
                        move_line_vals['product_uom_id'] = self.product_id.uom_id.id
                        move_line_vals['qty_done'] = 1
                        move_lines_commands.append((0, 0, move_line_vals))

                        # move_lines_commands.append((0, 0, move_line_vals))
                        # New Barcode Scan then create new line
                        vals_line = {
                            'product_id': self.product_id.id,
                            'location_dest_id': self.location_dest_id.id,
                            'lot_id': lot.id,
                            'qty_done': 1,
                            'product_uom_id': self.product_uom.id,
                            'location_id': self.location_id.id,
                        }

                        self.update({
                            'move_line_ids': move_lines_commands
                        })
                        self._onchange_move_line_ids()

            # FOR SERIAL PRODUCT
            # --------------------------------------------
            # outgoing / internal - show_lots_m2o - serial
            # --------------------------------------------
            if self.product_id.tracking == 'serial':
                # VALIDATION SERIAL NO. ALREADY EXIST.
                lines = self.move_line_ids.filtered(
                    lambda r: r.lot_id.name == barcode)
                if lines:
                    raise UserError(
                        _(warm_sound_code + "Serial Number already exist!"))
                # First Time Scan
                lines = self.move_line_ids.filtered(
                    lambda r: not r.lot_id)
                # First Time Scan
                # lines = self.move_line_ids.filtered(
                #     lambda r: r.lot_id.name == barcode)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = 1
                        lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(
                            barcode, self.product_id.id, warm_sound_code)
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode,
                            'lot_id': lot.id
                        }
                        self.update({
                            'move_line_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        res = {}
                        if float_compare(line.qty_done, 1.0, precision_rounding=line.product_id.uom_id.rounding) != 0:
                            message = _(
                                'You can only process 1.0 %s of products with unique serial number.') % line.product_id.uom_id.name
                            res['warning'] = {'title': _(
                                'Warning'), 'message': message}
                            return res
                        break
                else:
                    list_allocated_serial_ids = []
                    if self.move_line_ids:
                        for line in self.move_line_ids:
                            if line.lot_id:
                                list_allocated_serial_ids.append(
                                    line.lot_id.id)

                    # if need new line.
                    quant = quant_obj.search([
                        ('product_id', '=', self.product_id.id),
                        ('quantity', '>', 0),
                        ('location_id.usage', '=', 'internal'),
                        ('lot_id.name', '=', barcode),
                        ('location_id', 'child_of', self.location_id.id),
                        ('lot_id.id', 'not in', list_allocated_serial_ids),
                    ], limit=1)

                    # if not quant:
                    #     raise UserError(
                    #         _("There are no available qty for this lot/serial: %s") % (barcode))

                    if not quant and not self.picking_id.picking_type_id.use_create_lots:
                        raise UserError(
                            _(warm_sound_code + "There are no available qty for this lot/serial.%s") % (barcode))

                    lot = False
                    if quant and quant.lot_id:
                        lot = quant.lot_id
                    else:
                        # Create New Lot if it's allow.
                        lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(
                            barcode, self.product_id.id, warm_sound_code)
                    # Assign lot_id in move_lines_command
                    if not lot:
                        raise UserError(
                            _(warm_sound_code + "Can't create Lots/Serial Number record for this lot/serial. % s") % (barcode))

                    move_lines_commands = []
                    move_line_vals = self._prepare_move_line_vals(
                        quantity=0)
                    move_line_vals['lot_id'] = lot.id
                    move_line_vals['lot_name'] = lot.name
                    move_line_vals['product_uom_id'] = self.product_id.uom_id.id
                    move_line_vals['qty_done'] = 1
                    move_lines_commands.append((0, 0, move_line_vals))
                    # New Barcode Scan then create new line
                    vals_line = {
                        'product_id': self.product_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'lot_id': lot.id,
                        'qty_done': 1,
                        'product_uom_id': self.product_uom.id,
                        'location_id': self.location_id.id,
                    }
                    self.update({
                        'move_line_ids':  move_lines_commands
                    })
                    self._onchange_move_line_ids()

            quantity_done = 0
            for move_line in self._get_move_lines():
                quantity_done += move_line.product_uom_id._compute_quantity(
                    move_line.qty_done, self.product_uom, round=False)

            if self.picking_code == 'outgoing' and quantity_done == self.product_uom_qty + 1:
                warning_mess = {
                    'title': _('Alert!'),
                    'message': 'Becareful! Quantity exceed than initial demand!'
                }
                return {'warning': warning_mess}
        else:
            raise UserError(
                _(warm_sound_code + "Picking type is not outgoing or incoming or internal transfer."))

    def sh_auto_serial_scanner_has_tracking_show_lots_text(self, barcode, sequence, is_last_scanned, warm_sound_code):
        # self.picking_id.show_lots_text
        if self.picking_code == 'incoming':

            # FOR PURCHASE
            # LOT PRODUCT
            # --------------------------------------------
            # incoming - show_lots_text - lot
            # --------------------------------------------
            if self.product_id.tracking == 'lot':
                # First Time Scan
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: r.lot_name == False)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode,
                        }
                        self.update({
                            'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        break
                else:
                    # Second Time Scan
                    lines = self.move_line_nosuggest_ids.filtered(
                        lambda r: r.lot_name == barcode)
                    if lines:
                        for line in lines:
                            # odoo v14 update below way
                            qty_done = line.qty_done + 1
                            vals_line = {
                                'qty_done': qty_done,
                            }
                            self.update({
                                'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                            })
                            # odoo v14 update below way
                            break

                    else:
                        move_lines_commands = self._generate_serial_move_line_commands(
                            [barcode])
                        # New Barcode Scan then create new line
                        # vals_line = {
                        #     'product_id': self.product_id.id,
                        #     'location_dest_id': self.location_dest_id.id,
                        #     'lot_name': barcode,
                        #     'qty_done': 1,
                        #     'product_uom_id': self.product_uom.id,
                        #     'location_id': self.location_id.id,
                        # }
                        self.update({
                            'move_line_nosuggest_ids': move_lines_commands
                        })

            # SERIAL PRODUCT
            # --------------------------------------------
            # incoming - show_lots_text - serial
            # --------------------------------------------
            if self.product_id.tracking == 'serial':
                # lot_names = self.env['stock.lot'].generate_lot_names(
                #     barcode, False)

                # VALIDATION SERIAL NO. ALREADY EXIST.
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: r.lot_name == barcode)
                if lines:
                    raise UserError(
                        _(warm_sound_code + "Serial Number already exist!"))
                # First Time Scan
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: r.lot_name == False)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode
                        }
                        self.update({
                            'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        break
                else:
                    move_lines_commands = self._generate_serial_move_line_commands(
                        [barcode])

                    # Create new line if not found any unallocated serial number line
                    # vals_line = {
                    #     'product_id': self.product_id.id,
                    #     'location_dest_id': self.location_dest_id.id,
                    #     'lot_name': barcode,
                    #     'qty_done': 1,
                    #     'product_uom_id': self.product_uom.id,
                    #     'location_id': self.location_id.id,
                    # }
                    self.update({
                        'move_line_nosuggest_ids': move_lines_commands
                    })
            quantity_done = 0
            for move_line in self.move_line_nosuggest_ids:
                quantity_done += move_line.product_uom_id._compute_quantity(
                    move_line.qty_done, self.product_uom, round=False)

            if quantity_done == self.product_uom_qty + 1:
                warning_mess = {
                    'title': _('Alert!'),
                    'message': 'Becareful! Quantity exceed than initial demand!'
                }
                return {'warning': warning_mess}

        elif self and self.picking_code in ['outgoing', 'internal']:
            # FOR SALE
            # LOT PRODUCT
            quant_obj = self.env['stock.quant']

            # FOR LOT PRODUCT
            # --------------------------------------------
            # outgoing / internal  - show_lots_text - lot
            # --------------------------------------------
            if self.product_id.tracking == 'lot':
                # First Time Scan
                quant = quant_obj.search([
                    ('product_id', '=', self.product_id.id),
                    ('quantity', '>', 0),
                    ('location_id.usage', '=', 'internal'),
                    ('lot_id.name', '=', barcode),
                    ('location_id', 'child_of', self.location_id.id)
                ], limit=1)

                # if not quant:
                #     raise UserError(
                #         _("There are no available qty for this lot/serial.%s") % (barcode))

                if not quant and not self.picking_id.picking_type_id.use_create_lots:
                    raise UserError(
                        _(warm_sound_code + "There are no available qty for this lot/serial.%s") % (barcode))

                lot = False
                if quant and quant.lot_id:
                    lot = quant.lot_id
                else:
                    # Create New Lot if it's allow.
                    lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(
                        barcode, self.product_id.id, warm_sound_code)
                # Assign lot_id in move_lines_command
                if not lot:
                    raise UserError(
                        _(warm_sound_code + "Can't create Lots/Serial Number record for this lot/serial. % s") % (barcode))

                lines = self.move_line_ids.filtered(
                    lambda r: r.lot_id == False)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_id': quant.lot_id.id
                        }
                        self.update({
                            'move_line_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        break
                else:
                    # Second Time Scan
                    lines = self.move_line_ids.filtered(
                        lambda r: r.lot_id.name == barcode)
                    if lines:
                        for line in lines:
                            # odoo v14 update below way
                            qty_done = line.qty_done + 1
                            vals_line = {
                                'qty_done': qty_done,
                            }
                            self.update({
                                'move_line_ids': [(1, line.id, vals_line)]
                            })
                            # odoo v14 update below way
                            break
                    else:
                        # move_lines_commands = self._generate_serial_move_line_commands(
                        #     [barcode])
                        move_lines_commands = []
                        lot = quant.lot_id
                        move_line_vals = self._prepare_move_line_vals(
                            quantity=0)
                        move_line_vals['lot_id'] = lot.id
                        move_line_vals['lot_name'] = lot.name
                        move_line_vals['product_uom_id'] = self.product_id.uom_id.id
                        move_line_vals['qty_done'] = 1
                        move_lines_commands.append((0, 0, move_line_vals))

                        # move_lines_commands.append((0, 0, move_line_vals))
                        # New Barcode Scan then create new line
                        vals_line = {
                            'product_id': self.product_id.id,
                            'location_dest_id': self.location_dest_id.id,
                            'lot_id': quant.lot_id.id,
                            'qty_done': 1,
                            'product_uom_id': self.product_uom.id,
                            'location_id': quant.location_id.id,
                        }

                        self.update({
                            'move_line_ids': move_lines_commands
                        })
                        self._onchange_move_line_ids()

            # FOR SERIAL PRODUCT
            # ----------------------------------------------
            # outgoing / internal  - show_lots_text - serial
            # ----------------------------------------------
            if self.product_id.tracking == 'serial':
                list_allocated_serial_ids = []
                if self.move_line_ids:
                    for line in self.move_line_ids:
                        if line.lot_id:
                            list_allocated_serial_ids.append(
                                line.lot_id.id)

                # if need new line.
                quant = quant_obj.search([
                    ('product_id', '=', self.product_id.id),
                    ('quantity', '>', 0),
                    ('location_id.usage', '=', 'internal'),
                    ('lot_id.name', '=', barcode),
                    ('location_id', 'child_of', self.location_id.id),
                    ('lot_id.id', 'not in', list_allocated_serial_ids),
                ], limit=1)

                # if not quant:
                #     raise UserError(
                #         _("There are no available qty for this lot/serial.%s") % (barcode))

                if not quant and not self.picking_id.picking_type_id.use_create_lots:
                    raise UserError(
                        _(warm_sound_code + "There are no available qty for this lot/serial.%s") % (barcode))

                lot = False
                if quant and quant.lot_id:
                    lot = quant.lot_id
                else:
                    # Create New Lot if it's allow.
                    lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(
                        barcode, self.product_id.id, warm_sound_code)
                # Assign lot_id in move_lines_command
                if not lot:
                    raise UserError(
                        _(warm_sound_code + "Can't create Lots/Serial Number record for this lot/serial. % s") % (barcode))

                # First Time Scan
                lines = self.move_line_ids.filtered(
                    lambda r: r.lot_id.name == barcode)
                if lines:
                    raise UserError(
                        _(warm_sound_code + "Serial Number already exist!"))
                # First Time Scan
                lines = self.move_line_ids.filtered(
                    lambda r: not r.lot_id)

                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode,
                            'lot_id': lot.id
                        }
                        self.update({
                            'move_line_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        res = {}
                        if float_compare(line.qty_done, 1.0, precision_rounding=line.product_id.uom_id.rounding) != 0:
                            message = _(
                                'You can only process 1.0 %s of products with unique serial number.') % line.product_id.uom_id.name
                            res['warning'] = {'title': _(
                                'Warning'), 'message': message}
                            return res
                        break
                else:
                    # list_allocated_serial_ids = []
                    # if self.move_line_ids:
                    #     for line in self.move_line_ids:
                    #         if line.lot_id:
                    #             list_allocated_serial_ids.append(
                    #                 line.lot_id.id)

                    # # if need new line.
                    # quant = quant_obj.search([
                    #     ('product_id', '=', self.product_id.id),
                    #     ('quantity', '>', 0),
                    #     ('location_id.usage', '=', 'internal'),
                    #     ('lot_id.name', '=', barcode),
                    #     ('location_id', 'child_of', self.location_id.id),
                    #     ('lot_id.id', 'not in', list_allocated_serial_ids),
                    # ], limit=1)

                    # if not quant:
                    #     raise UserError(
                    #         _("There are no available qty for this lot/serial: %s") % (barcode))

                    move_lines_commands = []
                    move_line_vals = self._prepare_move_line_vals(
                        quantity=0)
                    move_line_vals['lot_id'] = lot.id
                    move_line_vals['lot_name'] = lot.name
                    move_line_vals['product_uom_id'] = self.product_id.uom_id.id
                    move_line_vals['qty_done'] = 1
                    move_lines_commands.append((0, 0, move_line_vals))
                    # New Barcode Scan then create new line
                    # vals_line = {
                    #     'product_id': self.product_id.id,
                    #     'location_dest_id': self.location_dest_id.id,
                    #     'lot_id': quant.lot_id.id,
                    #     'qty_done': 1,
                    #     'product_uom_id': self.product_uom.id,
                    #     'location_id': quant.location_id.id,
                    # }
                    self.update({
                        'move_line_ids':  move_lines_commands
                    })
                    self._onchange_move_line_ids()

            quantity_done = 0
            for move_line in self._get_move_lines():
                quantity_done += move_line.product_uom_id._compute_quantity(
                    move_line.qty_done, self.product_uom, round=False)

            if self.picking_code == 'outgoing' and quantity_done == self.product_uom_qty + 1:
                warning_mess = {
                    'title': _('Alert!'),
                    'message': 'Becareful! Quantity exceed than initial demand!'
                }
                return {'warning': warning_mess}
        else:
            raise UserError(
                _(warm_sound_code + "Picking type is not outgoing or incoming or internal transfer."))

    # def sh_auto_serial_scanner_no_tracking(self, barcode, sequence, is_last_scanned, warm_sound_code):
    #     move_lines = False

    #     # INCOMING
    #     # ===================================
    #     if self.picking_code in ['incoming']:
    #         move_lines = self.move_line_nosuggest_ids

    #     # OUTGOING AND TRANSFER
    #     # ===================================
    #     elif self.picking_code in ['outgoing', 'internal']:
    #         move_lines = self.move_line_ids

    #     if move_lines:
    #         for line in move_lines:
    #             if self.product_id.barcode == barcode:
    #                 # odoo v14 update below way
    #                 qty_done = line.qty_done + 1
    #                 if self.picking_code in ['incoming']:
    #                     self.update({
    #                         'move_line_nosuggest_ids': [(1, line.id, {'qty_done': qty_done})]
    #                     })
    #                 if self.picking_code in ['outgoing', 'internal']:
    #                     self.update({
    #                         'move_line_ids': [(1, line.id, {'qty_done': qty_done})]
    #                     })
    #                 # odoo v14 update below way
    #                 if self.quantity_done == self.product_uom_qty + 1:
    #                     warning_mess = {
    #                         'title': _('Alert!'),
    #                         'message': 'Becareful! Quantity exceed than initial demand!'
    #                     }
    #                     return {'warning': warning_mess}
    #                 break
    #             else:
    #                 raise UserError(
    #                     _(warm_sound_code + "Scanned Internal Reference/Barcode not exist in any product"))
    #     else:
    #         raise UserError(
    #             _(warm_sound_code + "Pls add all product items in line than rescan."))

        # -----------------------------
        # sh_auto_serial_scanner
        # -----------------------------

        # =============================
        # UPDATED CODE
        # 15.0.23
        # move_lines = False

        # # INCOMING
        # # ===================================
        # if self.picking_code in ["incoming"]:
        #     move_lines = self.move_line_nosuggest_ids
        #
        # # OUTGOING AND TRANSFER
        # # ===================================
        # elif self.picking_code in ["outgoing", "internal"]:
        #     move_lines = self.move_line_ids
