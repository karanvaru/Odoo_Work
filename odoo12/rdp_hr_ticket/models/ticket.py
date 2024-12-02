from odoo import api, fields, models, _
from datetime import date, datetime
import time


class HrTicket(models.Model):
    _name = "hr.ticket"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    date = fields.Date(string="Date")

    user_id = fields.Many2one('res.users', string='User', \
                              default=lambda self: self.env.user, \
                              states={'draft': [('readonly', False)]}, readonly=True)


    # employee_name = fields.Char("Employee Name", default=lambda self: self.env.user.name, readonly='1')
    employee_name_id = fields.Many2one('hr.employee', "Employee Name", store=True, readonly='1',  compute="compute_employee_name")
    # employee_name_id = fields.Many2one('hr.employee', string='Employee Name', default=lambda self: self.env.user, readonly=True)
    request = fields.Html(string="Reason")
    name = fields.Char(string='HR Reference No', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    open_days = fields.Char(string='Open Days', compute='calculate_open_days')
    closed_date = fields.Datetime(string='closed date')
    # spoc = fields.Many2one('hr.employee', 'SPOC', readonly='1')
    spoc_id = fields.Many2one("hr.employee", 'SPOC',  store=True, compute='compute_employee')
    state = fields.Selection([
        ('new', 'NEW'),
        ('close', 'CLOSE'),
        ('cancel', 'CANCEL'),
    ], string='Status', default='new', track_visibility='always',)

    # @api.model
    # def create(self, vals):
    #     vals.update({
    #         'name': self.env['ir.sequence'].next_by_code('hr.ticket.sequence'),
    #     })
    #
    #
    #     return super(HrTicket, self).create(vals)

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('hr.ticket.sequence'),
        })
        res = super(HrTicket, self).create(vals)
        template_id = \
            self.env['ir.model.data'].get_object_reference('rdp_hr_ticket',
                                                           'hr_Ticket_app_employee_notification')[
                1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(res.id, force_send=True)

        template_id = \
            self.env['ir.model.data'].get_object_reference('rdp_hr_ticket',
                                                           'hr_Ticket_app_spoc_notification')[
                1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(res.id, force_send=True)

        return res

    @api.multi
    def action_to_close(self):
        self.closed_date = datetime.today()
        self.state = 'close'
        template_id = self.env.ref(
            "rdp_hr_ticket.automated_response_to_the_employee_who_raised_ticket")
        print("The template id is ", template_id)
        # template = self.env['mail.template'].browse(template_id)
        template_id.send_mail(self.id, force_send=True)

    # @api.multi
    # def action_to_close(self):
    #     self.closed_date = datetime.today()
    #     self.state = 'close'

    @api.multi
    def action_to_cancel(self):
        self.closed_date = datetime.today()
        self.state = 'cancel'

    @api.multi
    def action_set_new(self):
        self.write({'state': 'new'})

    @api.multi
    def calculate_open_days(self):
        for rec in self:
            if rec.closed_date:
                rec.open_days = (rec.closed_date - rec.create_date).days
            else:
                rec.open_days = (datetime.today() - rec.create_date).days

    @api.depends('user_id')
    def compute_employee_name(self):
        for rec in self:
            print(" id sssssss ", rec.env.uid)
            employee = rec.env['hr.employee'].sudo().search([('user_id', '=', rec.env.uid)])
            print('pppppppllllllggggg145678945llllllll', employee)
            rec.employee_name_id = employee.id
    #
    # def compute_employee(self):
    #     for rec in self:
    #         rec_spoc_id = rec.env['hr.employee'].sudo().search([('user_id', '=', rec.create_uid.id)])
    #         rec.employee_name_id = rec_spoc_id.id
    #         rec.spoc_id = rec_spoc_id.coach_id.id
    #
    @api.depends('employee_name_id')
    def compute_employee(self):
        for rec in self:
            self.spoc_id = self.employee_name_id.coach_id


