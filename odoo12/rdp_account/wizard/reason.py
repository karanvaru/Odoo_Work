from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime

class IssueReasonWizard(models.TransientModel):
    _name = "issue.reason.wizard"
    _description = "This wizard is to collect the description about the Issue."

    # created_by = fields.Many2one("res.users",'Created By', default = lambda self: self.env.user.id,readonly= True)
    created_by_user = fields.Many2one("res.users",'Created By', default = lambda self: self.env.user.id,readonly= True)
    created_on = fields.Datetime('Created On',readonly= True, default=datetime.now())
    action = fields.Selection([('issue', 'Issue'),
                               ('rectified', 'Rectified')], string='Action', default='issue',readonly= True)
    description = fields.Text('Description',required= True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('issue', 'Issue'),
        ('rectified', 'Rectified'),
        ('audited', 'Audited'),
        ('refuse', 'Refuse')], string='Status',readonly=1, default='issue')
    

    def create_issue_history(self):
        active_id = self._context.get('active_id')
        active_record = self.env['journal.audit'].browse(active_id)
        self.state = 'issue'
        active_record.update({
                    'state': self.state,
                    'reason_line_ids':[(0,6,{
                    'created_by':self.created_by_user,
                    'created_on':self.created_on,
                    'action': self.action,
                    'description':self.description
                                    })]
                    })
        print('========================active_id==================',active_id)
        print('========================active_record==================',active_record)
        print('========================active_record==================',active_record)
        # line = active_id
        # print('=====================Dayan==========================',line)
        # line = self.reason_line_ids.search([], order="id desc", limit=1)
        # for rec in active_id:
        # if line and line.action =='issue':
        var = self.env['journal.audit'].browse(self.env.context.get('active_id'))
        # print('========================Dayan=======================',var)
        # issue_content = "  Hello  <b>" +var.journal_entry_id.create_uid.name + ",</b><br>Referring to the recorded transaction, the auditor error is noted below. <br><b>" + str(var.journal_entry_id.name) + ",</b><br><br> Description: " + self.description
        issue_content = "  <p> Hi  <b>" +var.journal_entry_id.create_uid.name + "</b>,</p><p>Referring to the recorded transaction, the auditor error is noted below.</p><p> <b>" + str(var.journal_entry_id.name) + "</b>(" + self.description + ")</p>"
        main_content = {
            'subject': _('Ticket No: %s || Transaction No: %s Identified Issue !!!!!') % (var.name, var.journal_entry_id.name),
            'author_id': var.env.user.partner_id.id,
            'body_html': issue_content,
            # 'auto_delete': False,
            # 'notification': True,
            # 'type': 'email',
            # 'res_id': active_id,
            # 'model': var._context.get('active_model'),
            'email_to': var.journal_entry_id.create_uid.email,
        } 
        print('========================body_html==================',issue_content)

        self.env['mail.mail'].sudo().create(main_content).send()
        var.message_post(body=issue_content)



         


# ==================================Dayan====================================
# Refrence to pass data from wizard to One2Many(Update)
    # def action_submit(self):
    #     active_id = self._context.get('active_id')
    #     active_model = self._context.get('active_model')
    #     active_record = self.env[active_model].browse(active_id)
    #     self.status = 'cancel'
    #     active_record.update({
    #         'description': self.reason,
    #         'state':self.status
    #     })


class RectifiedReasonWizard(models.TransientModel):
    _name = "rectified.reason.wizard"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "This wizard is to collect the description of how its Rectified."
    issued_by = fields.Many2one('res.users', 'Issued By')
    created_by = fields.Many2one("res.users",'Created By', default = lambda self: self.env.user.id,readonly= True)
    created_by_user = fields.Many2one("res.users",'Created By', default = lambda self: self.env.user.id,readonly= True)
    created_on = fields.Datetime('Created On',readonly= True, default=datetime.now())
    action = fields.Selection([('issue', 'Issue'),
                               ('rectified', 'Rectified')], string='Action', default='rectified',readonly= True)
    description = fields.Text('Description',required= True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('issue', 'Issue'),
        ('rectified', 'Rectified'),
        ('audited', 'Audited'),
        ('refuse', 'Refuse')], string='Status',readonly=1, default='rectified')


    def create_rectified_history(self):
        active_id = self._context.get('active_id')
        active_record = self.env['journal.audit'].browse(active_id)
        print('========================active_record=======================',active_record)

        issue_line = self.env['audit.reason.line'].search([('journal_audit_id.id','=',active_record.id)],order = "id desc", limit = 1)
        print('========================issue_line=======================',issue_line)
        
        var = self.env['journal.audit'].browse(self.env.context.get('active_id'))
        print('========================var=======================',var)
        for val in issue_line:
            self.issued_by = val.create_uid
        
        self.state = 'rectified'
        active_record.update({
                    'state': self.state,
                    'reason_line_ids':[(0,6,{
                    'created_by':self.created_by_user,
                    'created_on':self.created_on,
                    'action': self.action,
                    'description':self.description,
                    # 'issued_by':self.issued_by
                                    })]
                    })
        # line = active_id
        print('========================7568767856=======================',self.issued_by.name)
        # line = self.reason_line_ids.search([], order="id desc", limit=1)
        # for rec in active_id:
        # if line and line.action =='issue':
        
        
        # issue_content = "  Hello  <b>" +var.journal_entry_id.create_uid.name + ",</b><br>Issue Rectified for <b>" + str(var.journal_entry_id.name) + ",</b><br><br> Description: " + self.description
        issue_content = " <p> Hi  <b>" + issue_line.create_uid.name + "</b>,</p> <p>Thank you for notifying us about the mistake in the transaction. Please consider the comment<br/> below.</p> <p> <b>" + str(var.journal_entry_id.name) + "</b>(" + self.description + ")</p>"
        main_content = {
            'subject': _('Ticket No: %s || Transaction No: %s Issue Rectified !!!!!') % (var.name, var.journal_entry_id.name),
            'author_id': issue_line.env.user.partner_id.id,
            'body_html': issue_content,
            'email_to': val.create_uid.email,
            # 'email_to': var.journal_entry_id.create_uid.email,
        } 
        self.env['mail.mail'].sudo().create(main_content).send()
        var.message_post(body=issue_content)


    # def mail_reminder(self):
    #     """Sending document expiry notification to employees."""

    #     now = datetime.now() + timedelta(days=1)
    #     date_now = now.date()
    #     match = self.search([])
    #     for i in match:
    #         if i.expiry_date:
    #             exp_date = fields.Date.from_string(i.expiry_date) - timedelta(days=7)
    #             if date_now >= exp_date:
    #                 mail_content = "  Hello  " + i.employee_ref.name + ",<br>Your Document " + i.name + "is going to expire on " + \
    #                                str(i.expiry_date) + ". Please renew it before expiry date"
    #                 main_content = {
    #                     'subject': _('Document-%s Expired On %s') % (i.name, i.expiry_date),
    #                     'author_id': self.env.user.partner_id.id,
    #                     'body_html': mail_content,
    #                     'email_to': i.employee_ref.work_email,
    #                 }
    #                 self.env['mail.mail'].create(main_content).send()
