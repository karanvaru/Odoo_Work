# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

import pytz
from pytz import timezone
from datetime import datetime
import time

from odoo import http, _, tools, fields
from odoo.http import request


class CustomRentalSale(http.Controller):

    def _convert_to_utc(self, localdatetime=None):
        if not localdatetime:
            return False
    
        check_in_date = localdatetime
        if type(localdatetime) == str:
            check_in_date = datetime.strptime(localdatetime, '%m/%d/%Y %I:%M %p')
        timezone_tz = 'utc'

        user_id = request.env.user
        if user_id.tz:
            timezone_tz = user_id.tz
        local = pytz.timezone(timezone_tz)
        local_dt = local.localize(check_in_date, is_dst=None)
        return local_dt.astimezone(pytz.utc).replace(tzinfo=None)

    def _prepare_product_rental_request(self, kw):
        product_templ_ids = request.env['product.template'].sudo().search([
            ('custom_rental_product', '=', True),
            ('is_custom_rental_published', '=', True),
        ])
        product_varian_ids = request.env['product.product'].sudo().search([
            ('product_tmpl_id', 'in', product_templ_ids.ids),
        ])
        pricelist_ids = request.env['product.pricelist'].sudo().search([])
        rental_drop_options_ids = request.env['rental.drop.option.custom'].sudo().search([])
        values = {
            'product_templ_ids': product_templ_ids,
            'product_varian_ids': product_varian_ids,
            'pricelist_ids': pricelist_ids,
            'rental_drop_options_ids': rental_drop_options_ids,
        }
        user_id = request.env.user
        if not user_id._is_public() and user_id.partner_id.property_payment_term_id:
            values.update({
                'payment_term_id': user_id.partner_id.property_payment_term_id
            })
        else:
            payment_term_id = request.env['account.payment.term'].sudo().search([
                    ('is_custom_rental_term', '=', True)], limit=1)
            values.update({
                'payment_term_id': payment_term_id,
            })
        return values

    @http.route(['/product/sale/rental_request','/product/sale/rental_request/<int:order_id>'], type='http', auth="public", website=True)
    def product_sale_custom_rental_request(self, **kw):
        order_id = request.env['sale.order'].sudo().browse(int(kw.get('order_id'))) if kw.get('order_id') else False

        user_id = request.env.user
        if kw.get("order_id") and not user_id._is_public():
            if order_id.partner_id.id != user_id.partner_id.id:
                return request.redirect("/product/sale/rental_request")
        elif order_id and user_id._is_public() and order_id.is_custom_rental_so_submitted:
                return request.redirect("/product/sale/rental_request")

        values = self._prepare_product_rental_request(kw)
        values.update({
            'sale_order_id': order_id
        })
        return http.request.render('odoo_rental_request_management.rental_request_template_view', values)

    def _prepare_rental_so_line(self, kw):
        order_line_lst = []
        line_dict = {}
        rent_hours = float(kw.get("rental_product_fade_hours").split(":")[0]) + (float(kw.get("rental_product_fade_hours").split(":")[1]) / 60) if kw.get("rental_product_fade_hours") else 0.0
        line_dict['product_id'] = int(kw.get("rental_product_variant_select")) if kw.get("rental_product_variant_select") else False
        line_dict['custom_start_datetime'] = self._convert_to_utc(kw.get("input_rental_start_datetime"))
        line_dict['custom_end_datetime'] = self._convert_to_utc(kw.get("input_rental_end_datetime"))
        line_dict['product_uom_qty'] = float(kw.get("rental_product_fade_qty")) if kw.get("rental_product_fade_qty") else 0.0
        line_dict['custom_rent_days'] = float(kw.get("rental_product_fade_days")) if kw.get("rental_product_fade_days") else 0.0
        line_dict['custom_rent_hours'] =  rent_hours
        line_dict['price_unit'] = float(kw.get("rental_product_fade_price")) if kw.get("rental_product_fade_price") else 0.0
        return [(0, 0, line_dict)]

    def _prepare_partner_vals(self, kw):
        return{
            'name': kw.get('customer_id'),
            'email': kw.get('email'),
            'phone': kw.get('phone'),
        }

    def _find_customer_rental(self, kw):
        name = kw.get('customer_id')
        email = kw.get('email')
        phone = kw.get('phone')
        partner_obj = request.env['res.partner']
        partner_id = partner_obj.sudo().search([('email', '=', str(email))], limit=1)
        if not partner_id:
            vals = self._prepare_partner_vals(kw)
            partner_id = partner_obj.sudo().create(vals)
        return partner_id.id

    def _prepare_rental_so_vals(self, kw):
        return {
            'partner_id': request.env.user.partner_id.id if not request.env.user._is_public() else self._find_customer_rental(kw),
            'pricelist_id': int(kw.get("rental_web_pricelist_fade")) if kw.get("rental_web_pricelist_fade") else False,
            'is_custom_rental_quote': True,
            'user_id': False,
            'order_line': self._prepare_rental_so_line(kw)
        }

    def _prepare_rental_so_write(self, kw, values):
        return {
            'pricelist_id': int(kw.get("rental_web_pricelist_fade")) if kw.get("rental_web_pricelist_fade") else False,
            'custom_request_to_reset_pricelist': False,
            'order_line': values.get('order_line'),
        }

    @http.route(['/create/rental_so'], type="http", auth="public", website=True)
    def create_custom_rental_so(self, **kw):
        values = self._prepare_rental_so_vals(kw)
        sale_order_obj = request.env['sale.order']
        if kw.get("rental_sale_order"):
            sale_order_id = sale_order_obj.sudo().browse(int(kw.get("rental_sale_order"))) if kw.get("rental_sale_order") else sale_order_obj
            vals = self._prepare_rental_so_write(kw, values)
            sale_order_id.sudo().write(vals)
        else:
            sale_order_id = sale_order_obj.with_context(force_company=request.website.company_id.id).sudo().create(values)
        return request.redirect("/product/sale/rental_request/%s" % str(sale_order_id.id))

    def _check_rental_price(self, kw):
        lst_price = 0.0
        sale_order_line_obj = request.env['sale.order.line'].sudo()
        product_id = kw.get("product_id")
        price_availability_dict = {
            'rental_price': 0.0,
        }
        if product_id:
            start_datetime = self._convert_to_utc(kw.get("start_datetime"))
            end_datetime = self._convert_to_utc(kw.get("end_datetime"))
            days = ((end_datetime - start_datetime).total_seconds()/3600.00)/24.0
            product_id = request.env['product.product'].sudo().browse(int(product_id))
            rent_day_price_id = product_id.product_tmpl_id.custom_rent_day_ids.filtered(lambda rent_day:
                (rent_day.pricelist_id.id == int(kw.get("pricelist_id")) or rent_day.pricelist_id.id == False) and\
                (int(kw.get("product_id")) in rent_day.product_variant_ids.ids or not rent_day.product_variant_ids) and\
                rent_day.days_from <= float(days) and rent_day.days_to >= float(days)
            )

            rent_day_price_id = rent_day_price_id[0] if rent_day_price_id else rent_day_price_id

            pricelist_id = request.env['product.pricelist'].sudo().browse(int(kw.get("pricelist_id")))
            rental_price = rent_day_price_id.price
            if rent_day_price_id.currency_id != pricelist_id.currency_id:
                rental_price = rent_day_price_id.currency_id._convert(
                    from_amount=rental_price,
                    to_currency=pricelist_id.currency_id,
                    company=request.env.user.company_id,
                    date=fields.Date.today(),
                )
            price_availability_dict['rental_price'] = rental_price * days

        return price_availability_dict

    @http.route(['/json/rental/product/price'], type='json', auth="public",website=True)
    def rental_product_price_json(self, **kw):
        price_availability_dict = {
            'rental_price': 0.0,
        }
        if kw.get("product_id") and kw.get('start_datetime') and kw.get("end_datetime"):
            price_availability_dict = self._check_rental_price(kw)
        return price_availability_dict

    def _prepare_check_avail_domain(self, kw, domain=[]):
        product_id = request.env['product.product'].sudo().browse(int(kw.get("product_id")))
        kw_start_datetime = datetime.strptime(kw.get("start_datetime"), '%m/%d/%Y %I:%M %p')
        kw_end_datetime = datetime.strptime(kw.get("end_datetime"), '%m/%d/%Y %I:%M %p')
        if kw.get('sale_id'):
            domain += ['|', ('order_id', '=', int(kw.get('sale_id')))]
        
        domain += [
            ('is_custom_rental_so_submitted', '=', True),
            ('product_id', '=', int(product_id.id)),
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

    def _check_rental_product_avail(self, kw, product_availability_dict):
        sale_order_line_obj = request.env['sale.order.line'].sudo()
        product_id = request.env['product.product'].sudo().browse(int(kw.get("product_id")))
        domain = self._prepare_check_avail_domain(kw, domain=[])
        sale_line_ids = sale_order_line_obj.sudo().search(domain)

        reserved_qty = sum(sale_line_ids.mapped("product_uom_qty")) or 0.0
        message = ''
        avail_rental_qty = product_id.custom_rental_qty - reserved_qty

        if avail_rental_qty < 0.0 or avail_rental_qty < float(kw.get("qty")):
            message += "%s Quantity is available" %(avail_rental_qty)
            product_availability_dict['availability_msg'] = message
            product_availability_dict['reserved'] = True

        return product_availability_dict

    @http.route(['/json/rental/product/avail/status'], type='json', auth="public",website=True)
    def rental_product_avail_status_json(self, **kw):
        product_availability_dict = {
            'availability_msg': 'Available',
            'reserved': False,
            'first_load_fade': True,
        }
        if kw.get("product_id") and kw.get('start_datetime') and kw.get("end_datetime"):
            product_availability_dict = self._check_rental_product_avail(kw, product_availability_dict)
            product_availability_dict['first_load_fade'] = False
        if not kw.get("product_id") or not kw.get('start_datetime') or not kw.get("end_datetime"):
            product_availability_dict.update({
                'availability_msg': 'Mendatory Fields Must Be Set',
                'reserved': True,
            })
        return product_availability_dict

    def _reset_rental_product(self, kw, order_lines=None):
        if order_lines:
            for line in order_lines:
                line.unlink()
        return True

    @http.route(['/json/reset/rental/soline'], type="json", auth="public", website=True)
    def json_reset_rental_so(self, **kw):
        order_id = False
        if kw.get("sale_order_id"):
            order_id = request.env['sale.order'].sudo().browse(int(kw.get("sale_order_id")))
            self._reset_rental_product(kw, order_id.order_line)
            order_id.write({
                'custom_request_to_reset_pricelist': True,
            })
        if kw.get('order_line_id'):
            order_line_id = request.env['sale.order.line'].sudo().browse(int(kw.get("order_line_id")))
            order_id = order_line_id.order_id
            self._reset_rental_product(kw, order_line_id)
        return {
            'order_id': order_id.id if order_id else kw.get("sale_order_id"),
        }

    def _check_rental_back_product_avail(self, kw):
        reserved_message = ''
        rental_product_reserved = False
        sale_order_id = False
        if kw.get('sale_order_id'):
            sale_order_id = request.env['sale.order'].sudo().browse(int(kw.get('sale_order_id')))
            reserved_product_lst = []
            for line in sale_order_id.order_line:
                
                price_availability_dict = line._check_rental_product_avail_custom()
                if price_availability_dict.get('reserved'):
                    rental_product_reserved = True
                    reserved_product_lst.append(line.product_id.display_name)
            reserved_message = ', '.join(reserved_product_lst)
            reserved_message += ' is Reserved on your selected dates'

        return {
            'rental_product_reserved': rental_product_reserved,
            'message': reserved_message,
            'sale_order_id': sale_order_id.id
        }

    def _prepare_to_submit_so(self, kw):
        return {
            'is_custom_rental_so_submitted': True,
            'rental_submit_custom_comment': kw.get("customer_additional_comment"),
            'custom_rental_drop_options_id': int(kw.get("rental_drop_options")) if kw.get("rental_drop_options") else False,
        }

    def _submit_rental_quotation(self, kw):
        if kw.get('sale_order_id'):
            rental_product_avail_dict = self._check_rental_back_product_avail(kw)
            if rental_product_avail_dict.get('rental_product_reserved'):
                rental_product_avail_dict.update({
                    'is_rental_quot_submitted': False
                })
                return rental_product_avail_dict
            else:
                vals = self._prepare_to_submit_so(kw)
                sale_order_id = request.env['sale.order'].sudo().browse(int(kw.get('sale_order_id')))
                sale_order_id.sudo().write(vals)
                rental_product_avail_dict.update({
                    'sale_order_id': sale_order_id,
                    'is_rental_quot_submitted': True
                })
                return rental_product_avail_dict
        return {
            'is_rental_quot_submitted': False,
            'reserved_message': 'Something Went Wrong',
        }

    @http.route(['/submit/custom/rental/order'], type="http", auth="public", website=True)
    def submit_custom_rental_order(self, **kw):
        sale_order_id = request.env['sale.order'].sudo().browse(int(kw.get('sale_order_id')))
        if sale_order_id.is_custom_rental_so_submitted:
            kw.update({
                'sale_order_id': sale_order_id,
                'so_allready_submitted': True,
            })
            return request.render('odoo_rental_request_management.rental_request_submitted',kw)
        quotation_submitted = self._submit_rental_quotation(kw)
        kw.update(quotation_submitted)
        return request.render('odoo_rental_request_management.rental_request_submitted',kw)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
