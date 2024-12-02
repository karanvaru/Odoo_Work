# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_custom_rental_quote = fields.Boolean(
        string='Is Rental Order',
        default=False,
        readonly=True,
    )
    is_custom_rental_so_submitted = fields.Boolean(
        string="Is Rental Reserved",
        readonly=True,
        copy=False,
    )
    custom_request_to_reset_pricelist = fields.Boolean(
        string='Request To Reset Pricelist',
        copy=False,
        help="Request for reset pricelist from Rental request web"
    )
    rental_submit_custom_comment = fields.Text(
        string="Rental Comment",
        copy=False,
        
    )
    custom_rental_drop_options_id = fields.Many2one(
        'rental.drop.option.custom',
        string='Drop Option',
    )
    custom_force_reserv_rental_order = fields.Boolean(
        string="Allow Forcefully Reserve",
        copy=False,
    )

    def action_submit_rental_order_custom(self):
        for order in self:
            for line in order.order_line:
                price_availability_dict = line._check_rental_product_avail_custom()
                if price_availability_dict.get('reserved') or order.custom_force_reserv_rental_order:
                    raise ValidationError("%s has %s" %(line.product_id.display_name, price_availability_dict['availability_msg']))
            order.write({
                'is_custom_rental_so_submitted' : True,
            })

    def action_unreserve_rental_order_custom(self):
        self.write({
            'is_custom_rental_so_submitted' : False,
        })

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        self.write({
            'is_custom_rental_so_submitted': False,
        })
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    custom_start_datetime = fields.Datetime(
        string="Rental Start Date",
    )
    custom_end_datetime = fields.Datetime(
        string='Rental End Date'
    )
    custom_rent_hours = fields.Float(
        string="Hours",
        compute="_compute_custom_rental_days_hours",
        store=True,
    )
    custom_rent_days = fields.Float(
        string="Days",
        compute="_compute_custom_rental_days_hours",
        store=True,
    )
    is_custom_rental_so_submitted = fields.Boolean(
        string="Is Rental Submitted",
        copy=False,
        related="order_id.is_custom_rental_so_submitted",
        store=True,
    )

    @api.depends("custom_start_datetime", "custom_end_datetime")
    def _compute_custom_rental_days_hours(self):
        for line in self:
            line.custom_rent_days = 0.0
            line.custom_rent_hours = 0.0
            if line.custom_start_datetime and line.custom_end_datetime:
                total_hours = (line.custom_end_datetime - line.custom_start_datetime).total_seconds() / 3600.00
                line.custom_rent_days = total_hours / 24.0
                line.custom_rent_hours = total_hours

    def _check_rental_price_custom(self):
        price_availability_dict = {
            'rental_price': 0.0,
            'availability_msg': 'Available',
            'reserved': False
        }
        product_id = self.product_id
        if product_id:
            if self.custom_start_datetime and self.custom_end_datetime:
                start_datetime = self.custom_start_datetime
                end_datetime = self.custom_end_datetime
                days = ((end_datetime - start_datetime).total_seconds()/3600.00)/24.0
                rent_day_price_id = product_id.product_tmpl_id.custom_rent_day_ids.filtered(lambda rent_day:
                    (rent_day.pricelist_id.id == self.order_id.pricelist_id.id or rent_day.pricelist_id.id == False) and\
                    (product_id.id in rent_day.product_variant_ids.ids or not rent_day.product_variant_ids) and\
                    rent_day.days_from <= float(days) and rent_day.days_to >= float(days))

                rent_day_price_id = rent_day_price_id[0] if rent_day_price_id else rent_day_price_id

                rental_price = rent_day_price_id.price
                if rent_day_price_id.currency_id.id != self.order_id.currency_id.id:
                    rental_price = rent_day_price_id.currency_id._convert(
                        from_amount=rental_price,
                        to_currency=self.order_id.currency_id,
                        company=self.order_id.company_id,
                        date=fields.Date.today(),
                    )
                price_availability_dict['rental_price'] = rental_price * self.custom_rent_days
        return price_availability_dict

    def _preapre_avail_domain_custom(self, domain=[]):
        kw_start_datetime = self.custom_start_datetime
        kw_end_datetime = self.custom_end_datetime
        domain += [
            ('is_custom_rental_so_submitted', '=', True),
            ('product_id', '=', self.product_id.id),
            '|', '|', '&', 
            ('custom_start_datetime', '>=', kw_start_datetime),
            ('custom_start_datetime', '<=', kw_end_datetime),
            '&',
            ('custom_end_datetime', '>=', kw_start_datetime),
            ('custom_end_datetime', '<=', kw_end_datetime),
            '&',
            ('custom_start_datetime', '<=', kw_start_datetime),
            ('custom_end_datetime', '>=', kw_end_datetime)
        ]
        return domain
    
    def _check_rental_product_avail_custom(self):
        self.ensure_one()
        price_availability_dict = {
            'availability_msg': 'Available',
            'reserved': False
        }
        product_id = self.product_id
        domain = self._preapre_avail_domain_custom(domain=[])
        sale_line_ids = sale_order_line_obj = self.env['sale.order.line'].sudo().search(domain)
        print ("@@@@@@@@@@@@@@@@@@@@@@@sale_line_ids",sale_line_ids.mapped('order_id'))

        reserved_qty = sum(sale_line_ids.mapped("product_uom_qty")) or 0.0
        message = ''
        avail_rental_qty = product_id.custom_rental_qty - reserved_qty

        if avail_rental_qty < float(self.product_uom_qty):
            message += "%s Quantity is available" %(avail_rental_qty)
            price_availability_dict['availability_msg'] = message
            price_availability_dict['reserved'] = True
        return price_availability_dict

    @api.onchange('product_id', 'custom_start_datetime', 'custom_end_datetime', 'product_uom_qty')
    def _onchange_product_rental_duration_custom(self):
        if self.order_id.is_custom_rental_quote and self.product_id and self.custom_start_datetime and self.custom_end_datetime:
            price_availability_dict = self._check_rental_price_custom()
            price_availability_dict.update(
                self._check_rental_product_avail_custom()
            )
            if price_availability_dict.get('reserved'):
                return {
                    'warning': {
                        'title': _("Not Enough Quantity"),
                        'message': price_availability_dict['availability_msg']
                    }
                }
            self.price_unit = price_availability_dict['rental_price']

    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        if self.order_id.is_custom_rental_quote and not self._context.get('website_id'):
            price_availability_dict = self._check_rental_price_custom()
            self.price_unit = price_availability_dict['rental_price']
        return result

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        result = super(SaleOrderLine, self).product_uom_change()
        if self.order_id.is_custom_rental_quote and not self._context.get('website_id'):
            price_availability_dict = self._check_rental_price_custom()
            self.price_unit = price_availability_dict['rental_price']
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
