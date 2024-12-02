# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BusinessUnitGroup(models.Model):
    _name = 'business.unit.group'
    _description = 'Business Unit Group'


    name = fields.Char('Name', required=True)
    bu_manager_ids = fields.One2many('business.unit.group.managers', 'bu_group_id', string='BU Group Managers')



class BusinessUnit(models.Model):
    _name = 'business.unit'
    _description = 'Business Unit'
    

    name = fields.Char('Name', required=True)
    bu_group_id = fields.Many2one('business.unit.group', string='BU Group')
    bu_manager_ids = fields.One2many('business.unit.managers', 'bu_id', string='BU Managers')


class BusinessUnitManagers(models.Model):
    _name = 'business.unit.managers'
    _description = 'Business Unit Managers'


    name = fields.Char(compute='_compute_name', string='Name', store=True)
    bu_id = fields.Many2one('business.unit', string='BU')
    user_id = fields.Many2one('res.users', string='User Id', required=True)
    company_ids = fields.Many2many('res.company', string='Companies', required=True)


    @api.depends('bu_id', 'user_id')
    def _compute_name(self):
        for rec in self:
            name = f'{rec.user_id.name} in {rec.bu_id.name}'

class BusinessUniGrouptManagers(models.Model):
    _name = 'business.unit.group.managers'
    _description = 'Business Unit Group Managers'


    name = fields.Char(compute='_compute_name', string='Name', store=True)
    bu_group_id = fields.Many2one('business.unit.group', string='BU')
    user_id = fields.Many2one('res.users', string='User Id', required=True)
    company_ids = fields.Many2many('res.company', string='Companies', required=True)


    @api.depends('bu_group_id', 'user_id')
    def _compute_name(self):
        for rec in self:
            name = f'{rec.user_id.name} in {rec.bu_group_id.name}'