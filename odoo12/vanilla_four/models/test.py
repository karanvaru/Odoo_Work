# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime



class VanillaFour(models.Model):
    _name = "vanilla.four"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = " Vanilla Three"

    # student_update_id = fields.One2many('create.application', 'student_details_ids')
    # name = fields.Char(string='Template Three')
    test_name = fields.Text(string="Multiple Text", track_visibility='always')
    single_text = fields.Char(string="Single Line Text", track_visibility='always')
    test_date = fields.Datetime(string="Date", track_visibility='always')
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self : _('New'))
    open_days = fields.Char(string='Open Days', compute='calculate_open_days')
    closed_date = fields.Datetime(string='closed date')
    tag_ids = fields.Many2many('four.vanilla.one.tags', 'vanilla_four_tags_rel', 'name', string='Tags', track_visibility='onchange')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')
    ], string='Priority', track_visibility='always')
    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('closed', 'Closed'),
        ('cancel', 'CANCELLED'),
    ], string='Status', readonly=True, default='draft', track_visibility='always')
    description = fields.Html("Description")
    one_to_many_ids = fields.One2many('four.vanilla.one.to.many.relation', 'relation_id', string='One to Many')
    many_to_one_id = fields.Many2one('four.vanilla.many.to.one.relation', string='Many to One')
    many_to_many_ids = fields.Many2many('four.vanilla.many.to.many.relation',  string='Many to Many')
    # @api.model
    # def create(self, vals):
    #     if vals.get('reference_seq', _('New')) == _('New'):
    #         vals['reference_seq'] = self.env['ir.sequence'].next_by_code('template.four.sequence') or _('New')
    #     result = super(TemplateFour, self).create(vals)
    #     return result
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('four.vanilla.sequence')
        res = super(VanillaFour, self).create(vals)
        return res

    @api.multi
    def action_to_work_in_progress(self):
        self.state = 'work_in_progress'

    @api.multi
    def action_to_closed(self):
        self.state = 'closed'

    @api.multi
    def action_to_cancel(self):
        self.state = 'cancel'

    @api.multi
    def action_set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def calculate_open_days(self):
        for rec in self:
            if rec.closed_date:
                rec.open_days = (rec.closed_date - rec.create_date).days
            else:
                rec.open_days = (datetime.today() - rec.create_date).days


class FourVanillaOneTags(models.Model):
    _name = "four.vanilla.one.tags"

    _description = "Vanilla Four Tags"

    name = fields.Char('Name')

class FourVanillaOnetoManyRelation(models.Model):
    _name = "four.vanilla.one.to.many.relation"

    _description = "One To Many"

    name = fields.Char('Name')
    relation_id = fields.Many2one('vanilla.four', string='relation')


class FourVanillaManyToManyRelation(models.Model):
    _name = "four.vanilla.many.to.many.relation"

    _description = "Many To Many"

    name = fields.Char('Name')

class FourVanillaManyToOneRelation(models.Model):
    _name = "four.vanilla.many.to.one.relation"

    _description = "Many To One"

    name = fields.Char('Name')



