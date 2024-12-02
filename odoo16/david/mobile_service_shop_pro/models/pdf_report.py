# -*- coding: utf-8 -*-
######################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Milind Mohan(odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################

from odoo import models, api


class MobileServiceReport(models.AbstractModel):

    _name = 'report.mobile_service_shop_pro.service_template'

    @api.model
    def _get_report_values(self, docids, data=None):

        if data['form']['date_start']:
            if data['form']['service_status']:
                if data['form']['technician']:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '>=', data['form']['date_start']),
                        ('date_request', '<=', data['form']['date_end']),
                        ('technician_name', '=', data['form']['technician']),
                        ('service_state', '=', data['form']['service_status']),
                    ])
                else:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '>=', data['form']['date_start']),
                        ('date_request', '<=', data['form']['date_end']),
                        ('service_state', '=', data['form']['service_status']),
                    ])
            else:
                if data['form']['technician']:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '>=', data['form']['date_start']),
                        ('date_request', '<=', data['form']['date_end']),
                        ('technician_name', '=', data['form']['technician']),
                    ])
                else:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '>=', data['form']['date_start']),
                        ('date_request', '<=', data['form']['date_end']),
                    ])

        else:
            if data['form']['service_status']:
                if data['form']['technician']:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '<=', data['form']['date_end']),
                        ('service_state', '=', data['form']['service_status']),
                        ('technician_name', '=', data['form']['technician']),
                    ])
                else:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '<=', data['form']['date_end']),
                        ('service_state', '=', data['form']['service_status']),
                    ])
            else:
                if data['form']['technician']:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '<=', data['form']['date_end']),
                        ('technician_name', '=', data['form']['technician']),
                    ])
                else:
                    service_ids = self.env['mobile.service'].search([
                        ('date_request', '<=', data['form']['date_end']),
                    ])

        lst = []
        for line in service_ids:
            if line.brand_name.brand_name and line.model_name.mobile_brand_models:
                product_name = line.brand_name.brand_name + "( " + line.model_name.mobile_brand_models + " )"
            else:
                product_name = " "
            lst.append({
                'code': line.name,
                'customer_name': line.person_name.name,
                'product_name': product_name,
                'date_assign': line.date_request,
                'date_return': line.return_date,
                'technician': line.technician_name.name,
                'status': line.service_state,
            })
        return {
            'values': lst,
            'start_date': data['form']['date_start'],
            'end_date': data['form']['date_end'],

        }


class PartsUsageReport(models.AbstractModel):

    _name = 'report.mobile_service_shop_pro.parts_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        prod_id_lst = []
        if data['form']['date_start']:
            order_line_ids = self.env['product.order.line'].search([
                ('write_date', '>=', data['form']['date_start']),
                ('write_date', '<=', data['form']['date_end'])
            ])
        else:
            order_line_ids = self.env['product.order.line'].search([])

        for obj in order_line_ids:
            if obj.product_id.product_tmpl_id and obj.product_id.product_tmpl_id.id not in prod_id_lst:
                prod_id_lst.append(obj.product_id.product_tmpl_id.id)
        if data['form']['parts_id']:
            product_id = self.env['product.template'].search([('is_a_parts', '=', True), ('id', '=', data['form']['parts_id'])])
        else:
            product_id = self.env['product.template'].search([('is_a_parts', '=', True)])
        lst = []
        lst1 = []
        for line in product_id:
            if line.id in prod_id_lst:
                lst.append({
                    'id': line.id,
                    'part_brand': line.brand_name.brand_name,
                    'part_model': line.model_name.mobile_brand_models,
                    'part_colour': line.model_colour,
                    'product_name': line.name,

                })
        for line in order_line_ids:
            lst1.append({
                'product_id': line.product_id.product_tmpl_id.id,
                'serv_id': line.product_order_id.name,
                'qty': line.qty_invoiced,
                'qty_used': line.product_uom_qty,
                'qty_stock_move': line.qty_stock_move,
                'price': line.part_price,
                'create_date': line.write_date,
                'technician': line.product_order_id.technician_name.name,
                'symbol': self.env.user.company_id.currency_id.symbol,

            })
        return {
            'values': lst,
            'used': lst1,
            'start_date': data['form']['date_start'],
            'end_date': data['form']['date_end'],

        }


class ComplaintTypeReport(models.AbstractModel):

    _name = 'report.mobile_service_shop_pro.complaint_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        if data['form']['date_start']:
            if data['form']['complaint_type']:
                complaints_filterd = self.env['mobile.complaint.tree'].search([
                    ('write_date', '>=', data['form']['date_start']),
                    ('write_date', '<=', data['form']['date_end']),
                    ('complaint_type_tree', '=', data['form']['complaint_type'])
                ])
            else:
                complaints_filterd = self.env['mobile.complaint.tree'].search([
                    ('write_date', '>=', data['form']['date_start']),
                    ('write_date', '<=', data['form']['date_end']),
                ])
        else:
            if data['form']['complaint_type']:
                complaints_filterd = self.env['mobile.complaint.tree'].search([
                    ('complaint_type_tree', '=', data['form']['complaint_type'])
                ])
            else:
                complaints_filterd = self.env['mobile.complaint.tree'].search([])

        complaints_obj = self.env['mobile.complaint.description'].search([])
        lst = []
        lst1 = []
        for line1 in complaints_filterd:
            lst1.append({
                'complaint_type': line1.complaint_type_tree.complaint_type,
                'description': line1.description_tree.description,
                'serv_no': line1.complaint_id.name,
                'brand': line1.complaint_id.brand_name.brand_name,
                'model': line1.complaint_id.model_name.mobile_brand_models,
                'date': line1.complaint_id.date_request,
                'technician': line1.complaint_id.technician_name.name,
            })
        for line in complaints_obj:
            lst.append({
                'complaint_type': line.complaint_type_template.complaint_type,
                'description': line.description,
                'print': 0,
            })
        for lst_obj in lst:
            for lst1_obj in lst1:
                if lst_obj['complaint_type'] == lst1_obj['complaint_type'] and lst_obj['description'] == lst1_obj['description']:
                    lst_obj['print'] = 1

        return {
            'values': lst,
            'complaints': lst1,
            'start_date': data['form']['date_start'],
            'end_date': data['form']['date_end'],

        }