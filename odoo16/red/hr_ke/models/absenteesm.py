from odoo import _, api, fields, models
from datetime import timedelta
from odoo.exceptions import ValidationError




class KeAbsenteesm(models.Model):
    _name = 'ke.absenteesm'
    _description = 'Absenteesm Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = "id desc"

    def default_date(self):
        """ returns today's date and time """
        return fields.Datetime.now(self)

    def default_date_end(self):
        return fields.Datetime.now(self) + timedelta(days=30)
    
    name = fields.Char(
        'Brief Title', required=True, readonly=True, states={
            'draft': [
                ('readonly', False)]}, tracking=True)

    state = fields.Selection([('draft',
                               'Draft'),
                              ('confirm',
                               'Confirm')],
                             'Status',
                             default='draft', tracking=True)
    date_from = fields.Datetime(
        'Date',
        required=True,
        readonly=True,
        states={
            'draft': [
                ('readonly',
                 False)]},
        default=default_date,
        tracking=True)

    date_end = fields.Datetime(
        'Date End',
        required=True,
        readonly=True,
        states={
            'draft': [
                ('readonly',
                 False)]},
        default=default_date_end,
        tracking=True)
    
    employee_list_ids = fields.One2many(
        'emp.absent.list',
        'employee_list_id',
        string='Employees List',
        required=True,
        readonly=True,
        states={
            'draft': [
                ('readonly',
                 False)]}, tracking=True)
    

    def action_confirm(self):
        for rec in self:
            if not rec.employee_list_ids:
                raise ValidationError('Missing Employee record')
            deduction_type = self.env.ref('hr_ke.ke_before_gross_deduction1')
            if not deduction_type:
                raise ValidationError('No salary rule found for processing overtime\
                                allowances in your payroll system!')
            all_vals = []
            for record in rec.employee_list_ids:
                daily_rate = 0
                if record.contract_id.rem_type in ['monthly']:
                    daily_rate = (record.contract_id.wage/30)
                elif record.contract_id.rem_type in ['daily']:
                    daily_rate = record.contract_id.wage
                
                values = {
                    'deduction_id': deduction_type.id,
                    'computation': 'fixed',
                    'employee_id': record.Emp_name.id,
                    'rule_id': deduction_type.rule_id.id,
                    'fixed': (record.absent_days * daily_rate),
                    'date_start': record.employee_list_id.date_from,
                    'date_end': record.employee_list_id.date_end
                }
                if values:
                    all_vals.append(values)

            if all_vals:
                self.env['ke.before.gross.deduction'].create(all_vals)
            else:
                raise ValidationError(
                    'Missing Absenteesm details. Please consult HR')
            rec.state = 'confirm'    


class EmployeesAbsentList(models.Model):
    _name = "emp.absent.list"
    _description = "Employees Absent List"

    employee_list_id = fields.Many2one('ke.absenteesm')
    Emp_name = fields.Many2one('hr.employee', string="Employee Name")
    absent_days = fields.Float('Absent Days', default=0)
    
    contract_id = fields.Many2one(
        'hr.contract',
        'Contract',
        required=True,
        domain="[('employee_id','=', Emp_name)]")


    @api.constrains('absent_days')
    def overtime_worked_hours(self):
        for rec in self:
            if rec.absent_days == 0:
                raise ValidationError('Please Enter Valid Absent Hours')
