# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from unicodedata import category
from odoo import api, fields, models, _
from datetime import datetime



class ScmKaizen(models.Model):
    _name = "scm.kaizen"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "SCM Kaizen"

    name = fields.Char('Reference', track_visibility='always', default=lambda self: _('New'))
    employee_name = fields.Many2one('res.users', string="Created By", required=True, default=lambda self: self.env.user, readonly=True)
    assigned_to = fields.Many2one('hr.employee', string='Assigned to',track_visibility='onchange')
    raised_date = fields.Datetime(string="Date", required=True,track_visibility='always')
    scm_name = fields.Char('Name',track_visibility='always')
    description = fields.Html(string='Description', required=True,track_visibility='always')
    open_day = fields.Char(string="Open Days", compute="_compute_open_days")
    closed_date = fields.Datetime('Closed Date')
    priority = fields.Selection([
        ('none', 'None'),
        ('poor', 'Poor'),
        ('very_poor', 'Very Poor'),
        ('average', 'Average'),
        ('good', 'Good'),
        ('best', 'Best')
    ], string='Priority', track_visibility='always')

    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('closed', 'Closed'),
        ('cancel', 'CANCELLED'),
    ], string='Status', readonly=True, default='draft', track_visibility='always')
    category_id = fields.Many2one('scm.category',string=" SCM Category",track_visibility='onchange')
    scm_sub_category_id = fields.Many2one('scm.subcategory',string=" Subcategory",track_visibility='onchange')
    bcg = fields.Selection([
        ('bc', 'Business Continuity (BC)'),
        ('bg', 'Growth (G)'),
       
    ], string='BCG',track_visibility='always')
    tag_ids = fields.Many2many('scm.tags','scm_tags_rel','name',string="Tags")
    difficulty_level = fields.Selection([('easy', 'Easy'),
                                         ('normal', 'Normal'),
                                         ('difficult', 'Difficult'),
                                         ('hard', 'Hard'),
                                         ('extreme', 'Extreme'),
                                         ('insane', 'Insane')], string="Difficulty Level")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('scm.kaizen.sequence')
        res = super(ScmKaizen, self).create(vals)
        return res

    @api.multi
    def action_to_closed(self):
        self.state = 'closed'
        self.closed_date = datetime.today()

    @api.multi
    def action_to_cancel(self):
        self.state = 'cancel'
        self.closed_date = datetime.today()

    @api.multi
    def action_set_draft(self):
        self.write({'state': 'draft'})

    @api.depends('raised_date')
    def _compute_open_days(self):
        for rec in self:
            if rec.raised_date:
                if rec.closed_date:
                    opendays = (datetime.today() - rec.closed_date).days + 1
                    rec.open_day = str(opendays) + ' Days'
                else:
                    opendays = (datetime.today() - rec.raised_date).days + 1
                    rec.open_day = str(opendays) + ' Days'


    # @api.depends('raised_date')
    # def _compute_open_days(self):
    #     for rec in self:
    #         if rec.closed_date:
    #                 print("The appraisal date is", rec.raised_date)
    #                 print("The date of today", datetime.today())
    #                 today = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
    #                 date = datetime.strptime(today, "%Y-%m-%d %H:%M:%S")
    #                 rec.open_day = str((date - rec.raised_date).days + 1) + "  days"



class ScmCategory(models.Model):
    _name = "scm.category"   
    _description ="SCM Category"  

    name= fields.Char('Name')   

class ScmTags(models.Model):
    _name = "scm.tags"   
    _description ="SCM Tags"  

    name= fields.Char('Name')     
class ScmSubCategory(models.Model):
    _name = "scm.subcategory"   
    _description ="SCM SubCategory"  

    name= fields.Char('Name')           







