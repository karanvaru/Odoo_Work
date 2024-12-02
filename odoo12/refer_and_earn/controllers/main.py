# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class website_refer_and_earn(http.Controller):
    #home page of refer and earn
    @http.route('/refer_earn/', auth='public',type='http', website=True)
    def homepage(self, **kw):
        values = request.env['res.config.settings'].sudo().referrals_homepage_default()
        bonus = request.env['res.config.settings'].sudo().get_values()
        currency_id = request.env.user.partner_id.currency_id
        values.update(bonus)
        values.update({'currency_id':currency_id})
        return http.request.render('refer_and_earn.homepage', values)


    @http.route('/my/refer_earn/', auth='user',type='http', website=True)
    def myReferEarn(self, **kw):
        user = request.env.user
        if not user.partner_id.referral_code:
            user.partner_id.referral_code = user.partner_id.generate_referralCode()

        signup_link = request.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/web/signup?referral="+user.partner_id.referral_code
        usertransaction = request.env['transaction.history'].sudo().search([('user_id','=',user.id),('point_type','=','c')])
        referrals_values = request.env['res.config.settings'].sudo().get_values()
        d,e,r,c,a = 0,0,0,0,0
        for txn in usertransaction:
            if txn.state == 'draft':
                d+=1
            if txn.state == 'reject':
                r+=1
            if txn.state == 'cancel':
                c+=1
            if txn.state == 'error':
                e+=1
            if txn.state == 'approve':
                a+=1
        matrix = str(d)+"-"+str(e)+"-"+str(r)+"-"+str(c)+"-"+str(a)
        if matrix == '0-0-0-0-0':
            matrix= '0-0-0-0-0-1'
        else:
            matrix= matrix+"-0"
        values = {
                    'signup_link'        : signup_link,
                    'referral_code'      : user.partner_id.referral_code,
                    'refral_earning'     : user.partner_id.getReferralAmount(),
                    'referralCount'      : user.partner_id.getSignedUpReferralCount(),
                    'directReferralCount': user.partner_id.getDirectSignedUpReferralCount(),
                    'currency_id'        : user.partner_id.currency_id,
                    "matrix"             : matrix,
                    }
        values.update(referrals_values)

            # 'Draft', 'Error',  'Rejected', 'Cancel',    'Approved', 'NoTransaction'
        return http.request.render('refer_and_earn.myReferEarn', values)

    @http.route('/my/stats/', auth='user',type='http', website=True)
    def myReferEarnStats(self, **kw):
        user = request.env.user
        usertransaction = request.env['transaction.history'].sudo().search([('user_id','=',user.id)])
        values ={
        'txn':usertransaction,
        'total_earning': user.partner_id.referral_earning,
        'referralCount'      : user.partner_id.getSignedUpReferralCount(),
        }

        return http.request.render('refer_and_earn.stats', values)

    @http.route("/payment/referralEarning", type='json', auth="public", methods=['POST'], website=True)
    def setreferalErnings(self, used_earnings,**kw):
        sale_order = request.env.user.partner_id.last_website_so_id
        sale_order.use_re_epoints = used_earnings
        return True


    @http.route("/usedAmt/referralEarning", type='json', auth="public", methods=['POST'], website=True)
    def getreferalAmt(self,**kw):
        sale_order = request.env.user.partner_id.last_website_so_id
        used_referal_amt = sale_order.redeemable_points
        return used_referal_amt
