# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# from time import strptime
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError
import logging
import time

class Lead(models.Model):
    _inherit = 'crm.lead'
    
    leg_one = fields.Datetime(string="Start OP (Open)")
    potca = fields.Datetime(string="POTCA (Send)")
    op_potca_sent = fields.Char(string='Open Days (POTCA)',compute = 'compute_potca_sent_timer')
    potca_status = fields.Selection([('waiting', 'Waiting'),('pass', 'Pass'), ('fail', 'Fail')],compute='compute_potca_sent_timer',string ='POTCA Status', default ='waiting')

    @api.multi
    @api.onchange('stage_id')
    def op_potca_send_stage_date(self):
        for rec in self:
            today = datetime.today()
            today_d = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')
            today_dt = datetime.strptime(today_d, '%Y-%m-%d %H:%M:%S')
            if rec.stage_id.id == 12 or rec.stage_id.id == 108:
            # if rec.stage_id.id == 2:
                rec.leg_one = datetime.today()
                rec.op_potca_sent = (datetime.today() - rec.leg_one)
                # rec.op_potca_sent = rec.op_potca_sent.split('.')[0]
            elif rec.stage_id.id == 106 or rec.stage_id.id == 109:
            # elif rec.stage_id.id == 3:
                rec.potca = datetime.today()
                # rec.op_potca_sent = (datetime.today() - rec.potca)
                # rec.op_potca_sent = rec.op_potca_sent.split('.')[0]
            # if rec.leg_one and rec.potca:   
            #     leg_one_d = datetime.strftime(rec.leg_one, '%Y-%m-%d %H:%M:%S')
            #     leg_one_dt = datetime.strptime(leg_one_d, '%Y-%m-%d %H:%M:%S')
            #     potca_d = datetime.strftime(rec.potca, '%Y-%m-%d %H:%M:%S')
            #     potca_dt = datetime.strptime(potca_d, '%Y-%m-%d %H:%M:%S')
            #     rec.op_potca_sent = (potca_dt-leg_one_dt)

    # @api.multi
    # @api.depends('potca', 'leg_one')
    # def compute_potca_sent_timer(self):
    #     for record in self:
    #         if record.potca and record.leg_one:
    #             record.op_potca_sent = (record.potca-record.leg_one)

    @api.multi
    @api.depends('potca', 'leg_one')
    def compute_potca_sent_timer(self):
        for record in self:
            if record.potca and record.leg_one:
                record.op_potca_sent = (record.potca-record.leg_one)
                leg_one_d = datetime.strftime(record.leg_one, '%Y-%m-%d %H:%M:%S')
                leg_one_dt = datetime.strptime(leg_one_d, '%Y-%m-%d %H:%M:%S')
                potca_d = datetime.strftime(record.potca, '%Y-%m-%d %H:%M:%S')
                potca_dt = datetime.strptime(potca_d, '%Y-%m-%d %H:%M:%S')
                # differ = (potca_dt - leg_one_dt).total_seconds()//60
                differ = (potca_dt - leg_one_dt).total_seconds()
                if record.op_potca_sent:
                    if differ <= 14400:
                        record.potca_status="pass"
                    else:
                        record.potca_status="fail"
                # else:
                #     record.potca_status="waiting"


    