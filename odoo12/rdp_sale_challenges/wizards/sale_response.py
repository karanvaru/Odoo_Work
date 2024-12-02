from email.policy import default
from odoo import models, fields
from datetime import datetime


class CreateResponse(models.TransientModel):
    _name = 'sale.response'
    _description = 'Sale Resopnse'

    remarks = fields.Text(string="Remarks")
    emp_name = fields.Char('Employee Name',default=lambda self: self.env.user.name,readonly="1")
    # emp_name=fields.Many2one('res.users',string='Employee Name',default=lambda self: self.env.user.name,readonly="1")
    sale_desc = fields.Text('Disciption')


    def action_submit(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        active_record.update({
            'custom_sale_ids': [(0, 0,{'employee_name': self.emp_name,'sale_remark_id':self.remarks,'sale_date':datetime.today()})]

        })

    def action_to_wizard(self):
        print('=')
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(active_id)
        active_record.update({
            'custom_cl_ids': [(0, 0, {'custom_emp_name': self.emp_name, 'sale_cl_desc': self.sale_desc,
                                        'sale_cl_date':datetime.today()})]
        })