from odoo import models, api, fields


class Helpdesk_tickets(models.Model):
    _inherit = 'helpdesk.ticket'

    helpdesk_portal_id = fields.Many2one(
        'helpdesk.ticket',
        string="Helpdesk Portal",
        website_form_blacklisted=False
    )
    created_by_user_id = fields.Many2one(
        'res.users',
        string="Created By",
        default=lambda self: self.env.user.id
    )
    portal_datetime = fields.Datetime('Date and Time')
    x_studio_field_engineer_mobile = fields.Char('Field Engineer Name')
    asp_engineer_id = fields.Many2one('res.users',string="Assign to ASP",track_visibility="onchange")
    # x_studio_model_name = fields.Selection(
    # x_studio_model_name = fields.Selection(
    #     [
    #         ('1', 'Model1'),
    #         ('2', 'Model2')
    #     ],
    #     "Model Name"
    # )
    # x_studio_field_w3gK7 = fields.Char(
    #     "Customer Mobile"
    # )
    # x_studio_serial_no = fields.Char(
    #     "Serial No."
    # )
    # x_studio_opendays = fields.Integer(
    #     'Open Days',
    #     default=5
    # )

    @api.model
    def create(self, values):
        call_super = super(Helpdesk_tickets, self).create(values)
        if 'x_studio_field_w3gK7' in values:
            call_super.partner_id.mobile = values.get('x_studio_field_w3gK7')
        for rec in call_super:
            rec.helpdesk_portal_id = rec.id
        return call_super
