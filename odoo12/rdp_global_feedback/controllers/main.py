from odoo import http
from odoo.http import request
from odoo import fields, http, _, tools
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import \
    CustomerPortal, pager as portal_pager, get_records_pager
from collections import OrderedDict
import json, base64
from dateutil.parser import parse
from operator import itemgetter
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR
import datetime
import pytz
from datetime import timedelta
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.addons.website_form.controllers.main import WebsiteForm


class GlobalFeedbackController(http.Controller):

    @http.route('/feedback', type="http", auth="public", website=True)
    def fe_webform(self, **kw):
        fe_rec = request.env['global.feedback'].sudo().search([])
        return http.request.render('rdp_global_feedback.global_feedback', {
                                                                  'fe_rec': fe_rec})

    @http.route('/service/feedback', type="http", auth="public", website=True)
    def create_webfeticket(self, **kw):
        print("Data Received.....", kw)
        f_ls=request.env['global.feedback'].sudo().search([])
        gf_val = {
            'first_name':kw.get('first_name'),
            'last_name':kw.get('last_name'),
            'company_name':kw.get('company_name'),
            # 'customer_name': kw.get('customer_name'),
            'email':kw.get('email'),
            'mobile': kw.get('mobile'),
            'improvement_suggested':kw.get('improvement_suggested'),
            'subject':kw.get('subject'),
            'improve_area':kw.get('improve_area'),
            # 'notes': kw.get('notes'),
            # 'rating_text':kw.get('rating_text')
           
            
        }
        
        res = f_ls.create(gf_val)
       
        # request.env['field.engineer'].create([({'field_engineer_ids':[(0,0,fe_val)]})])
        return request.render("rdp_global_feedback.gf_thanks", {'gf_val':res})
     