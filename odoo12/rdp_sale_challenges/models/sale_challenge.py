from unicodedata import name
from odoo import api, fields, models, _
from datetime import date, datetime
import time

class SaleChallenges(models.Model):
    _name = "sale.challenge"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Sale Challenges"

    kam = fields.Many2one('res.users', 'KAM',track_visibility='onchnage')
    related_to = fields.Many2one('sale.groups',string='Related To',track_visibility='always')
    brief_concern = fields.Char(string="Subject",track_visibility='always')
    state = fields.Selection([
        ('draft', 'New'),
        ('submitted', 'WIP'),
        # ('approved', 'Approved'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', track_visibility='always')
    custom_sale_ids = fields.One2many('sale.challengeline','sale_challenge_ref', string="Sale Ids")
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    custom_cl_ids = fields.One2many('sale.challengepages','sale_cl_id', string="Sale Desc")
    open_days = fields.Char(string="Open Days",compute="compute_open_days")
    closed_date = fields.Datetime('Closed Date')
    cancelled_date = fields.Datetime('Cancelled Date')
    submit_to = fields.Many2one('res.users',"Submit To")
    action = fields.Text('Description',track_visibility='always')
    note = fields.Text('Note', track_visibility='always')
    partner_id = fields.Many2one('res.users',string="Assigned To",track_visibility='always')
    partner_name_id = fields.Many2one('res.partner',string="Partner",track_visibility='always')
    category_id = fields.Many2one('sale.challenge.category',string="Category")
    scope_id = fields.Many2one('sale.challenge.scope',string="Scope",track_visibility='always')
    tag_ids = fields.Many2one('sale.challenge.tags',string='Sub Category',track_visibility='onchange')
    sale_order_id = fields.Many2one('sale.order',string="SO Number",track_visibility='always')
    customer_id = fields.Many2one('res.partner',string="Customer",track_visibility='always') 
    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket',string="Ticket Number",track_visibility='always') 
    is_physical_fixed = fields.Selection([
        ('yes', 'Yes'),
        ('not_relevant', 'Not Relevant'),
        ('future_consideration', 'Future Consideration'),
        ('other', 'Other')
    ], string='Physical Fixed')
    is_digitally_fixed = fields.Selection([
        ('yes', 'Yes'),
        ('not_relevant', 'Not Relevant'),
        ('future_consideration', 'Future Consideration'),
        ('other', 'Other')
    ], string='Digitally Fixed')
    fixed_status = fields.Selection([('temporarily', 'Temporarily'),('permanently', 'Permanently'),('other', 'Other')], string='Fixed Status',track_visibility='always')
    sales_channel = fields.Selection([('gem', 'GeM'),('corporate', 'Corporate'),('retail', 'Retail'),('ecommerce', 'eCommerce')], string='Sales Channel',track_visibility='always')
    five_why_button_action = fields.Char(string="Five Why", compute="compute_five_why_button_action")
    sale_channel_scm_kaizen_id = fields.Many2one('scm.kaizen', string="SCM Kaizen")
    scm_kaizen_button_action = fields.Char(string="SCM Kaizen", compute="compute_scm_kaizen_button_action")
    current_partner_status = fields.Selection([
        ('active', 'Active'),
        ('come_back_kid', 'Comeback Kid'),
        ('killed', 'Killed'),
        ('not_active', 'Not Active'),
        ('other', 'Other')
    ], string='Current Partner Status')
    hod_quick_comments = fields.Char(string="HOD Quick Comments")

    # def create_send_mail(self):
        
    #     for rec in self:
    #         rec.state = 'submitted'
    #         # template_id = self.env.ref('rdp_sale_challenges.sale_challenge_create_email_template').id
    #         template_id = self.env['ir.model.data'].get_object_reference('rdp_sale_challenges','sale_challenge_create_email_template')[1]
    #         template = self.env['mail.template'].browse(template_id)
    #         template_values = {'auto_delete': False}
    #         template.write(template_values)
    #         template.send_mail(rec.id, force_send=True)

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('sale.challenge.sequence'),
        })
        res = super(SaleChallenges, self).create(vals)
        template_id = \
            self.env['ir.model.data'].get_object_reference('rdp_sale_challenges',
                                                           'sale_challenge_ticket_creation_confirmation')[
                1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(res.id, force_send=True)
        return res

    # @api.model
    # def create(self, vals):
    #
    #     vals.update({
    #         'name': self.env['ir.sequence'].next_by_code('sale.challenge.sequence'),
    #     })
    #     return super(SaleChallenges, self).create(vals)
    #     template_id = \
    #         self.env['ir.model.data'].get_object_reference('rdp_sale_challenges',
    #                                                        'sca_ticket_creation_confirmation')[1]
    #     template = self.env['mail.template'].browse(template_id)
    #     template.send_mail(self.id, force_send=True)


        

        # for rec in self:
           
        #     # template_id = self.env.ref('rdp_sale_challenges.sale_challenge_create_email_template').id
        #     template_id = self.env['ir.model.data'].get_object_reference('rdp_sale_challenges','sale_challenge_create_email_template')[1]
        #     template = self.env['mail.template'].browse(template_id)
        #     template_values = {'auto_delete': False}
        #     template.write(template_values)
        #     template.send_mail(rec.id, force_send=True)
        



    # .template_id.send_mail(rec.id, force_send=True)
        # return super(SaleChallenges, self).create(vals),vals.create_send_mail()
    
      

    @api.multi
    def action_to_submit(self):
        self.ensure_one()

        self.state = 'submitted'
        template_id = self.env['ir.model.data'].get_object_reference('rdp_sale_challenges','sale_challenge_ticket_update_work_in_progress')[1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
      

    # @api.multi
    # def action_to_approve(self):
    #     self.state = 'approved'
       

    @api.multi
    def action_to_closed(self):
        self.closed_date = datetime.today()
       
        self.state = 'closed'
        template_id = \
        self.env['ir.model.data'].get_object_reference('rdp_sale_challenges', 'sale_challenge_ticket_update_once_ticket_is_closed')[1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)

    @api.multi
    def action_to_cancelled(self):
        self.cancelled_date = datetime.today()
        self.state = 'cancelled'
        template_id = \
        self.env['ir.model.data'].get_object_reference('rdp_sale_challenges', 'sale_challenge_ticket_update_once_ticket_is_cancelled')[1]
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)

    @api.multi
    def action_set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def compute_open_days(self):
        for record in self:
            if record['closed_date']:
                record['open_days'] = str((record['closed_date'] - record['create_date']).days) + " Days"
            if record['cancelled_date']:
                record['open_days'] = str((record['cancelled_date'] - record['create_date']).days) + " Days"
            else:
                record['open_days'] = str((datetime.today() - record['create_date']).days) + " Days"

            record['open_days'] = record['open_days'].split(',')[0]
            if record['open_days'] == '0:00:00':
                record['open_days'] = '0 Days'

    sales_challenge_five_why_count = fields.Integer("Five Why Count", compute="sales_challenge_five_why_ticket_count")

    @api.multi
    def sales_challenge_five_why_ticket_count(self):
        for rec in self:
            count_values = rec.env['five.why'].search_count([('sales_challenge_five_why_id', '=', rec.id)])
            rec.sales_challenge_five_why_count = count_values

    @api.multi
    def action_five_why_ticket(self):
        return {
            'name': 'Five Why',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'five.why',
            'context': {
                'default_sales_challenge_five_why_id': self.id
            },
            'domain': [('sales_challenge_five_why_id', '=', self.id)],

        }

    @api.depends('sales_challenge_five_why_count')
    def compute_five_why_button_action(self):
        for rec in self:
            if rec.sales_challenge_five_why_count != 0:
                rec.five_why_button_action = "Yes"

    scm_kaizen_count_id = fields.Integer('SCM Kaizen')

    scm_kaizen_count_sale_challenges = fields.Integer('SCM Kaizen', compute="scm_kaizen_count")

    @api.multi
    def scm_kaizen_count(self):
        for rec in self:
            count_values = rec.env['scm.kaizen'].search_count([('sales_challenge_scm_kaizen_id', '=', rec.id)])
            rec.scm_kaizen_count_sale_challenges = count_values

    @api.multi
    def action_scm_kaizen_button(self):
        self.ensure_one()
        return {
            'name': 'SCM Kaizen',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'scm.kaizen',
            'context': {
                           'default_sales_challenge_scm_kaizen_id': self.id
            },
            'domain': [('sales_challenge_scm_kaizen_id', '=', self.id)],
        }

    @api.depends('scm_kaizen_count_sale_challenges')
    def compute_scm_kaizen_button_action(self):
        for rec in self:
            if rec.scm_kaizen_count_sale_challenges != 0:
                rec.scm_kaizen_button_action = "Yes"


class SaleChallengeLine(models.Model):
    _name = "sale.challengeline"
    _description = "Sale Challenge Line"
    
    sale_challenge_ref = fields.Many2one('sale.challenge',string="Ref")
    # employee_name_id = fields.Many2one('sale.challenge', 'Sale Challenge Id')
    employee_name = fields.Char('Employee Name')
    # employee_name = fields.Integer('Employee Name')
    sale_remark_id = fields.Text('Remarks')
    sale_date = fields.Datetime('Date')


class CustomSaleChallenge(models.Model):
    _name = "sale.challengepages"
    _description = "Sale Challenge Pages"

    sale_cl_id = fields.Many2one('sale.challenge',string='SaleCL')
    custom_emp_name = fields.Many2one('res.users',string ="Employee Name")
    sale_cl_date = fields.Datetime('Date')
    sale_cl_desc = fields.Text('Action Description')


class CustomSaleGroups(models.Model):
    _name ="sale.groups"
    _order = 'sequence,id'
    _description="Sale Groups"

    sequence = fields.Integer("Sequence", default=1)
    name =fields.Char('Name')


class SaleChallegeCategory(models.Model):
    _name ="sale.challenge.category"
    _description="Sale Challenge Category"

    name =fields.Char('Name')


class SaleChallegeScope(models.Model):
    _name ="sale.challenge.scope"
    _description="Sale Challenge Scope"
    _order = 'sequence,id'

    sequence = fields.Integer("Sequence", default=1)

    name =fields.Char('Name')


class SaleChallegeTags(models.Model):
    _name ="sale.challenge.tags"
    _description="Sale Challenge Tags"

    name =fields.Char('Name')


class RdpSalesChallengeFiveWhy(models.Model):
    _inherit = 'five.why'

    sales_challenge_five_why_id = fields.Many2one('sale.challenge', 'Sales Challenge')


class SalesChallengeSCMKaizen(models.Model):
    _inherit = 'scm.kaizen'

    sales_challenge_scm_kaizen_id = fields.Many2one('sale.challenge', 'Sales Challenge SCM Kaizen')









