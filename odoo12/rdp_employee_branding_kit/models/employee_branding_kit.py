from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import ValidationError


class EmployeeBrandingKit(models.Model):
    _name = "employee.branding.kit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Employee Branding Kit"
    _order = 'id desc'
    name = fields.Char(string='Reference', required=True, copy=False, track_visibility='always', readonly=True, index=True,
                       default=lambda self: _('New'))
    employee_name_id = fields.Many2one('hr.employee', string="Employee", track_visibility='always', required=True)
    employee_code = fields.Char(string="Employee ID", compute='compute_employee')
    # employee_code = fields.Char(string="Employee ID")
    item_id = fields.Many2one("employee.branding.kit.items", string='Item', required=True)
    quantity = fields.Float(string="Item Quantity")
    item_qty = fields.Float(string="Quantity")
    remarks = fields.Text(string="Remarks")
    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('submitted_to_employee', 'Submitted to Employee'),
        ('confirm_by_employee', 'Confirm by Employee'),
        ('cancel', 'Cancel')
    ], string='Status', readonly=True, default='draft', track_visibility='always')
    open_days = fields.Char(string='Open Days', compute='calculate_open_days')
    closed_date = fields.Datetime(string='Closed date')
    spoc_id = fields.Many2one("hr.employee", string='SPOC')
    employee_page_id = fields.Many2one('hr.employee',string='Employee Page')
    user_id = fields.Many2one('res.users', string='User', \
                              default=lambda self: self.env.user, \
                              states={'draft': [('readonly', False)]}, readonly=True)
    employee_button = fields.Boolean(string="Button Visibility", compute='compute_button_visibility')

    @api.depends('employee_name_id')
    def compute_button_visibility(self):
        for record in self:
            print("employee_name_id:", record.employee_name_id.id)
            print("current_user:", self.env.user.id)
            if record.employee_name_id.user_id.id == self.env.user.id:
                record.employee_button = True
                print("button visible")
            else:
                record.employee_button = False
                print("button hidden")

    @api.constrains('item_qty')
    def _check_item_qty(self):
        for record in self:
            if not record.item_qty:
                raise ValidationError("Quantity cannot be empty")



    @api.depends('employee_name_id')
    def compute_employee(self):
        for rec in self:
            code_of_employee = rec.employee_name_id.x_studio_employee_code
            rec.employee_code = code_of_employee

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('employee.branding.kit.sequence')
        })
        res = super(EmployeeBrandingKit, self).create(vals)
        return res

    @api.multi
    def action_set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_to_submit_to_employee(self):
        self.state = 'submitted_to_employee'

    @api.multi
    def action_set_confirm(self):
        self.state = 'confirm_by_employee'
        self.closed_date = datetime.today()

    @api.multi
    def action_to_cancel(self):
        self.state = "cancel"



    @api.multi
    def calculate_open_days(self):
        for rec in self:
            if rec.closed_date:
                rec.open_days = str((rec.closed_date - rec.create_date).days) + " Days"
            else:
                rec.open_days = str((datetime.today() - rec.create_date).days) + " Days"


class EmployeeBrandingKitItems(models.Model):
    _name = "employee.branding.kit.items"
    _description = 'This class is used  to create branding items'

    name = fields.Char(string='Name')


class EmployeeBrandingKitPage(models.Model):
    _inherit = "hr.employee"

    branding_kit_ids = fields.One2many('employee.branding.kit', 'employee_name_id', string="Branding Kit Page", readonly=True)


