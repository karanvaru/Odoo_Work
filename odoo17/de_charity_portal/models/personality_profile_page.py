from odoo import api, fields, models, _


class TheCaptain(models.Model):
    _name = 'the.captain'
    _description = "The Captain"

    name = fields.Char(
        string="Name",
    )
    value = fields.Integer(
        string="Value",
    )
    captain_partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
    )


class TheSocialDirector(models.Model):
    _name = 'the.social.director'
    _description = "The Social Director"

    name = fields.Char(
        string="Name",
    )
    value = fields.Integer(
        string="Value",
    )
    social_director_partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
    )


class TheSteward(models.Model):
    _name = 'the.steward'
    _description = "The Steward"

    name = fields.Char(
        string="Name",
    )
    value = fields.Integer(
        string="Value",
    )
    steward_partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
    )


class TheNavigator(models.Model):
    _name = 'the.navigator'
    _description = "The Navigator"

    name = fields.Char(
        string="Name",
    )
    value = fields.Integer(
        string="Value",
    )
    navigator_partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
    )
