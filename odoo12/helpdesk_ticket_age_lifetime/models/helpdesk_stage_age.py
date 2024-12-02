# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class helpdesk_ticket_age(models.Model):
    _inherit = 'helpdesk.ticket'

    age_audit = fields.One2many('helpdesk.age.audit', 'ticket_id', index=True, store=True)

    @api.model
    def set_create_date_for_old_ticket(self):
        self._cr.execute("""INSERT INTO helpdesk_age_audit (ticket_id, date_in, stage_id)
                    SELECT p.id, p.create_date,r.id FROM helpdesk_ticket p
                    left join helpdesk_stage r on (r.id=p.stage_id)
                    WHERE r.is_close != True""")


    # Override Create Function
    @api.model
    def create(self, values):
        line = super(helpdesk_ticket_age, self).create(values)
        line.age_audit.create({'ticket_id': line.id,
                               'stage_id': line.stage_id.id,
                               'date_in': fields.date.today()})
        return line

    # Override Write Function
    @api.multi
    def write(self, vals):
        res = super(helpdesk_ticket_age, self).write(vals)
        for rec_age in self:
            if 'stage_id' in vals and vals['stage_id']:
                closing_value = self.env['helpdesk.stage'].sudo().browse(vals['stage_id'])
                for rec in rec_age.age_audit:
                    if not rec.date_out:
                        rec.date_out = fields.date.today()

                if closing_value.is_close != True :
                        rec_age.age_audit.create({'ticket_id': rec_age.id,
                                               'stage_id': rec_age.stage_id.id,
                                               'date_in': fields.date.today()})

        return res





class helpdesk_stage_age_audit(models.Model):
    _name = 'helpdesk.age.audit'

    ticket_id = fields.Many2one('helpdesk.ticket')
    stage_id = fields.Many2one('helpdesk.stage')
    date_in = fields.Date()
    date_out = fields.Date()
    days = fields.Integer(compute='_compute_days', store=True)

    @api.depends('date_in', 'date_out')
    def _compute_days(self):
        for res in self:
            if res.date_in and res.date_out:
                res.days = (res.date_out - res.date_in).days


