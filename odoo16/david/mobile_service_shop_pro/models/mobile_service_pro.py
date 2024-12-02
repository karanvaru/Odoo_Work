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

import json
import certifi
import urllib3
import requests
import pytz
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_key = fields.Char(string="Api Token")

    get_api_details = fields.Boolean(string="Get device details from external api ", default=False,
                                     help="If the active field is set to True, it will allow you to get mobile details from imei number.")

    show_complain_types = fields.Boolean(
        string="Show complaints on "
               "service tickets",
        help="Tick this option if you need "
             "to show complaints on service"
             " tickets")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        api_key = params.get_param('api_key', default=False)
        show_complain_types = params.get_param('show_complain_types',
                                               )
        get_api_details = params.get_param('get_api_details', default=False)
        res.update(
            get_api_details=get_api_details,
            api_key=api_key,
            show_complain_types=show_complain_types,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("api_key",
                                                         self.api_key)
        self.env['ir.config_parameter'].sudo().set_param(
            "show_complain_types", self.show_complain_types
        )
        self.env['ir.config_parameter'].sudo().set_param("get_api_details",
                                                         self.get_api_details)


class MobileServiceShopPro(models.Model):
    _name = 'mobile.service'
    _inherit = ['mobile.service']

    real_phone_image = fields.Binary(
        "Real Phone Image", attachment=True, store=True)
    complaint_visibility_status = fields.Boolean(
        compute='_compute_complaint_visibility_status', invisible=True)

    active_api = fields.Boolean(string="Active api details.", compute="_check_active")
    manufacturer = fields.Char(string="Manufacturer")
    device_Name = fields.Char(string="Device name")

    @api.depends('person_name')
    def _check_active(self):
        for rec in self:
            rec.active_api = self.env['ir.config_parameter'].sudo().get_param('get_api_details')

    @api.depends('service_state')
    def _compute_complaint_visibility_status(self):
        configparameter = self.env['ir.config_parameter'].sudo()
        self.complaint_visibility_status = \
            configparameter.get_param('show_complain_types')

    def get_ticket(self):
        self.ensure_one()
        user = self.env['res.users'].browse(self.env.uid)
        if user.tz:
            tz = pytz.timezone(user.tz)
            time = pytz.utc.localize(datetime.now()).astimezone(tz)
            date_today = time.strftime("%Y-%m-%d %H:%M %p")
        else:
            date_today = datetime.datetime.strftime(datetime.now(),
                                           "%Y-%m-%d %I:%M:%S %p")
        complaint_text = ""
        description_text = ""
        complaint_id = self.env['mobile.complaint.tree'].search(
            [('complaint_id', '=', self.id)])
        if complaint_id:
            for obj in complaint_id:
                complaint = obj.complaint_type_tree
                description = obj.description_tree
                complaint_text = complaint.complaint_type + ", " + complaint_text
                if description.description:
                    description_text = description.description + ", " + description_text
        else:
            for obj in complaint_id:
                complaint = obj.complaint_type_tree
                complaint_text = complaint.complaint_type + ", " + complaint_text
        data = {
            'ids': self.ids,
            'model': self._name,
            'date_today': date_today,
            'date_request': self.date_request,
            'date_return': self.return_date,
            'sev_id': self.name,
            'real_phone_image': self.real_phone_image,
            'warranty': self.is_in_warranty,
            'customer_name': self.person_name.name,
            'imei_no': self.imei_no,
            'technician': self.technician_name.name,
            'complaint_types': complaint_text,
            'complaint_description': description_text,
            'mobile_brand': self.brand_name.brand_name,
            'model_name': self.model_name.mobile_brand_models,

        }
        return self.env.ref(
            'mobile_service_shop.mobile_service_ticket').report_action(self,
                                                                       data=data)

    def get_device_details(self):
        if self.env['ir.config_parameter'].sudo().get_param('get_api_details'):
            api_token = self.env['ir.config_parameter'].sudo().get_param('api_key')
            if self.imei_no and len(self.imei_no) == 15:
                # working 2
                http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                           ca_certs=certifi.where())
                response1 = http.request('GET',
                                         "https://imeidb.xyz/api/imei/" + self.imei_no + "?token=" + api_token + "&format=json")
                res = json.loads(response1.data.decode("utf-8"))

                if res['success']:
                    response_brand = res['data']['brand']
                    self.device_Name = res['data']['name']
                    response_model = res['data']['model']
                    self.manufacturer = res['data']['manufacturer']

                    models_obj = self.env['brand.model'].search(
                        [('mobile_brand_models', '=', response_model), ('mobile_brand_name', '=', response_brand)])
                    if not models_obj:

                        models_create_obj = self.env['brand.model']
                        brand_create_obj = self.env['mobile.brand']

                        if not brand_create_obj.search([('brand_name', '=', response_brand)]):
                            new_obj = self._create_mobile_brand(response_brand)
                        else:
                            new_obj = brand_create_obj.search([('brand_name', '=', response_brand)])

                        vals = {
                            'mobile_brand_name': new_obj.id,
                            'mobile_brand_models': response_model,
                        }
                        created_obj = models_create_obj.create(vals)

                        self.model_name = created_obj
                        self.brand_name = created_obj.mobile_brand_name
                    else:
                        self.model_name = models_obj
                        self.brand_name = models_obj.mobile_brand_name
                else:
                    if res['code'] == 401:
                        raise UserError(_("Your request was made with invalid credentials. Please Check your token."))
                    elif res['code'] == 429:
                        raise UserError(_(
                            "Your reached the rate limit. Goto 'https://imeidb.xyz/user/settings' to change the maximum number of requests per minute."))
                    elif res['code'] == 460:
                        raise UserError(_("Invalid IMEI."))
                    elif res['code'] == 402:
                        raise UserError(
                            _("Out of money, please top up your balance from www.imeidb.xyz/balance/index "))
            else:
                raise UserError(
                    _("Enter a valid imei. "))
        else:
            raise UserError(
                _("Api token error."))

    def _create_mobile_brand(self, response_brand):
        brand_create_obj = self.env['mobile.brand']
        vals = {
            'brand_name': response_brand,
        }
        new_obj = brand_create_obj.create(vals)
        return new_obj


class MobileServiceShopPivotReport(models.Model):
    _name = "mobile.pivot.report"
    _description = "Mobile Service Statistics"
    _auto = False

    service = fields.Char(string='Service Number', readonly=True)
    person_name = fields.Many2one('res.partner', string="Customer", readonly=True)
    brand_name = fields.Many2one('mobile.brand', string="Mobile Brand", readonly=True)
    imei_no = fields.Char(string="IMEI Number", readonly=True)
    model_name = fields.Many2one('brand.model', string="Model", readonly=True)
    date_request = fields.Date(string="Requested date", readonly=True)
    return_date = fields.Date(string="Return date", readonly=True)
    technician_name = fields.Many2one('res.users', string="Technician Name", readonly=True)
    service_state = fields.Selection([('draft', 'Draft'), ('assigned', 'Assigned'),
                                      ('completed', 'Completed'), ('returned', 'Returned'),
                                      ('not_solved', 'Not solved')],
                                     string='Service Status', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Parts', readonly=True)
    complaint_type = fields.Char('Complaint Type', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        query = """
                      CREATE OR REPLACE VIEW %s AS (
                        SELECT
                            ROW_NUMBER() OVER ()  as id,
                            m.name AS service,
                            m.person_name AS person_name,
                            m.brand_name AS brand_name,
                            m.imei_no AS imei_no,
                            m.model_name AS model_name,
                            m.date_request AS date_request,
                            m.return_date AS return_date,
                            m.technician_name AS technician_name,
                            m.service_state AS service_state,
                            pt.id AS product_tmpl_id,
                            string_agg(COALESCE (mobile_complaint.complaint_type,''), ',')  as complaint_type
                            FROM mobile_service m
                            left join product_order_line po ON m.id = po.product_order_id
                            left JOIN product_product pp ON pp.id = po.product_id
                            left JOIN product_template pt ON pp.product_tmpl_id = pt.id
                            
                            left JOIN mobile_complaint_tree ON m.id = mobile_complaint_tree.complaint_id
                            left JOIN mobile_complaint ON mobile_complaint.id = mobile_complaint_tree.complaint_type_tree
                            group by pt.id, po.id, m.id, m.person_name, m.imei_no, m.model_name, m.date_request, m.technician_name, m.service_state
                      )
                        """ % self._table
        self._cr.execute(query)


class ProductOrderLineInherited(models.Model):
    _inherit = 'product.order.line'

    @api.onchange('product_id')
    def change_prod(self):
        self.ensure_one()
        filter_list = [('is_a_parts', '=', True)]
        if self.product_order_id.brand_name:
            filter_list.append(('brand_name', '=', self.product_order_id.brand_name.id))
        if self.product_order_id.model_name:
            filter_list.append(('model_name', '=', self.product_order_id.model_name.id))
        domain = {'domain': {'product_id': filter_list}}
        if self.product_id:
            product_template_obj = self.product_id.product_tmpl_id
            self.price_unit = product_template_obj.list_price
            self.product_uom = product_template_obj.uom_id.name
        return domain


class StockMoveReportInherited(models.AbstractModel):
    _inherit = 'report.mobile_service_shop.mobile_service_ticket_template'

    @api.model
    def _get_report_values(self, docids, data):
        terms = self.env['terms.conditions'].search([])
        return {
            'date_today': data['date_today'],
            'date_request': data['date_request'],
            'date_return': data['date_return'],
            'sev_id': data['sev_id'],
            'imei_no': data['imei_no'],
            'technician': data['technician'],
            'complaint_types': data['complaint_types'],
            'complaint_description': data['complaint_description'],
            'mobile_brand': data['mobile_brand'],
            'model_name': data['model_name'],
            'customer_name': data['customer_name'],
            'warranty': data['warranty'],
            'real_phone_image': data['real_phone_image'],
            'terms': terms,
        }
