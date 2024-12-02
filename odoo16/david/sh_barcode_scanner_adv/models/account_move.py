# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo.exceptions import UserError
from odoo import fields, models, Command, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sh_invoice_barcode_scanner_is_last_scanned = fields.Boolean(
        string="Last Scanned?")


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["barcodes.barcode_events_mixin", "account.move"]

    def _add_product(self, barcode):
        # step 1 make sure order in proper state.
        is_last_scanned = False
        sequence = 0
        warm_sound_code = ""

        if self.env.company.sudo().sh_invoice_barcode_scanner_last_scanned_color:
            is_last_scanned = True

        if self.env.company.sudo().sh_invoice_barcode_scanner_move_to_top:
            sequence = -1

        if self.env.company.sudo().sh_invoice_barcode_scanner_warn_sound:
            warm_sound_code = "SH_BARCODE_SCANNER_"

        if self.env.company.sudo().sh_invoice_barcode_scanner_auto_close_popup:
            warm_sound_code += "AUTO_CLOSE_AFTER_" + \
                str(self.env.company.sudo(
                ).sh_invoice_barcode_scanner_auto_close_popup) + "_MS&"

        if self and self.state != "draft":
            selections = self.fields_get()["state"]["selection"]
            value = next((v[1] for v in selections if v[0]
                          == self.state), self.state)
            raise UserError(
                _(warm_sound_code + "You can not scan item in %s state.") % (value))

        # step 2 increaset product qty by 1 if product not in order line than create new order line.
        elif self:
            self.invoice_line_ids.with_context(check_move_validity=False).update({
                'sh_invoice_barcode_scanner_is_last_scanned': False,
                'sequence': 0,
            })

            search_lines = False
            domain = []
            is_multi_barcode = self.env.user.has_group(
                'sh_barcode_scanner_adv.group_sh_barcode_scanner_multi_barcode')
            if self.env.company.sudo().sh_invoice_barcode_scanner_type == "barcode":
                if is_multi_barcode:
                    search_lines = self.invoice_line_ids.filtered(
                        lambda ol: ol.product_id.barcode == barcode)
                    if not search_lines:
                        for line in self.invoice_line_ids:
                            if line.product_id and line.product_id.barcode_line_ids:
                                for barcode_line in line.product_id.barcode_line_ids:
                                    if barcode_line.name == barcode:
                                        search_lines = line
                                        break

                    domain = ['|',
                              ("barcode", "=", barcode),
                              ("barcode_line_ids.name", "=", barcode)
                              ]
                else:
                    search_lines = self.invoice_line_ids.filtered(
                        lambda ol: ol.product_id.barcode == barcode)
                    domain = [("barcode", "=", barcode)]

            elif self.env.company.sudo().sh_invoice_barcode_scanner_type == "int_ref":
                search_lines = self.invoice_line_ids.filtered(
                    lambda ol: ol.product_id.default_code == barcode)
                domain = [("default_code", "=", barcode)]

            elif self.env.company.sudo().sh_invoice_barcode_scanner_type == "sh_qr_code":
                search_lines = self.invoice_line_ids.filtered(
                    lambda ol: ol.product_id.sh_qr_code == barcode)
                domain = [("sh_qr_code", "=", barcode)]

            elif self.env.company.sudo().sh_invoice_barcode_scanner_type == "all":

                if is_multi_barcode:
                    search_lines = self.invoice_line_ids.filtered(lambda ol: ol.product_id.barcode == barcode or
                                                                  ol.product_id.default_code == barcode or
                                                                  ol.product_id.sh_qr_code == barcode
                                                                  )

                    if not search_lines:
                        for line in self.invoice_line_ids:
                            if line.product_id and line.product_id.barcode_line_ids:
                                for barcode_line in line.product_id.barcode_line_ids:
                                    if barcode_line.name == barcode:
                                        search_lines = line
                                        break

                    domain = ["|", "|", "|",
                              ("default_code", "=", barcode),
                              ("barcode", "=", barcode),
                              ("barcode_line_ids.name", "=", barcode),
                              ("sh_qr_code", "=", barcode)
                              ]

                else:
                    search_lines = self.invoice_line_ids.filtered(lambda ol: ol.product_id.barcode == barcode or
                                                                  ol.product_id.default_code == barcode or
                                                                  ol.product_id.sh_qr_code == barcode
                                                                  )

                    domain = ["|", "|",

                              ("default_code", "=", barcode),
                              ("barcode", "=", barcode),
                              ("sh_qr_code", "=", barcode)

                              ]

            if search_lines:
                # PICK LAST LINE IF MULTIPLE LINE FOUND
                search_lines = search_lines[len(search_lines) - 1]
                search_lines.quantity += 1
                search_lines.sh_invoice_barcode_scanner_is_last_scanned = is_last_scanned
                search_lines.sequence = sequence
            else:
                search_product = self.env["product.product"].search(
                    domain, limit=1)
                if search_product:
                    self.invoice_line_ids = [Command.create({
                        'product_id': search_product.id,
                        'sh_invoice_barcode_scanner_is_last_scanned': is_last_scanned,
                        'sequence': sequence,
                    })]
                else:
                    raise UserError(
                        _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

    def on_barcode_scanned(self, barcode):
        self._add_product(barcode)
