# -*- coding: utf-8 -*-

import time
from datetime import date
from . import helpdesk_stage
from odoo import models, fields, api, _, SUPERUSER_ID, tools
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, Warning

class HelpdeskSupport(models.Model):
    _name = 'helpdesk.support'
    _description = 'Helpdesk Support'
    _order = 'id desc'
#     _inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin', 'analytic.mixin']
    

#    @api.multi odoo13
    def _write(self, vals):#this is to fix access error on stage write with other records.
        if len(vals.keys()) == 1 and 'stage_type' in vals:
            return super(HelpdeskSupport, self.sudo())._write(vals)
        return super(HelpdeskSupport, self)._write(vals)


    @api.model
    def create(self, vals):
        if vals.get('name', False):
            if vals.get('name', 'New') != 'New':
                vals['subject'] = vals['name']
                vals['name'] = 'New'
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('helpdesk.support') or 'New'
        
        # set up context used to find the lead's sales team which is needed
        # to correctly set the default stage_id
        context = dict(self._context or {})
        if vals.get('type') and not self._context.get('default_type'):
            context['default_type'] = vals.get('type')
        if vals.get('team_id') and not self._context.get('default_team_id'):
            context['default_team_id'] = vals.get('team_id')

        if not vals.get('partner_id', False) and vals.get('email', ''):
            partner = self.env['res.partner'].sudo().search([('email', '=', vals['email'])], limit=1)
            if partner:
                vals.update({'partner_id': partner.id})

        if vals.get('team_id') and not vals.get('team_leader_id'):
            vals['team_leader_id'] = self.env['support.team'].browse(vals.get('team_id')).leader_id.id
            
        if vals.get('custome_client_user_id', False):
            client_user_id = self.env['res.users'].browse(int(vals.get('custome_client_user_id')))
            if client_user_id:
                vals.update({'company_id': client_user_id.company_id.id})
        else:
            vals.update({'custome_client_user_id': self.env.user.id})
        # context: no_log, because subtype already handle this
        return super(HelpdeskSupport, self.with_context(context, mail_create_nolog=True)).create(vals)
        
#        return super(HelpdeskSupport, self).create(vals)
    
#    @api.multi odoo13
    @api.depends('timesheet_line_ids.unit_amount')
    def _compute_total_spend_hours(self):
        for rec in self:
            spend_hours = 0.0
            for line in rec.timesheet_line_ids:
                spend_hours += line.unit_amount
            rec.total_spend_hours = spend_hours
    
    @api.onchange('project_id')
    def onchnage_project(self):
        for rec in self:
            rec.analytic_account_id = rec.project_id.analytic_account_id
    
#    @api.multi odoo13
    def _compute_kanban_state(self):
        today = date.today()
        for help_desk in self:
            kanban_state = 'grey'
            if help_desk.date_action:
                lead_date = fields.Date.from_string(help_desk.date_action)
                if lead_date >= today:
                    kanban_state = 'green'
                else:
                    kanban_state = 'red'
            help_desk.kanban_state = kanban_state
          
#    @api.one odoo13
    def set_to_close(self):
        stage_id = self.env['helpdesk.stage.config'].search([('stage_type','=','closed')])
        if self.is_close != True:
            self.is_close = True
            self.close_date = fields.Datetime.now()#time.strftime('%Y-%m-%d')
            self.stage_id = stage_id.id
#            self.state = 'closed'
            template = self.env.ref('website_helpdesk_support_ticket.custom_email_template_helpdesk_ticket')
            template.send_mail(self.id, force_send=True)

    def get_custom_access_action(self):
        website_id = self.env['website'].search([('company_id','=',self.company_id.id)],limit=1)
        if website_id.domain:
            if website_id.domain.endswith('/'):
                domain_name = website_id.domain
                url = domain_name + 'helpdesk_email/feedback/' + str(self.id)
                return url
            else:
                domain = website_id.domain
                url = domain + '/helpdesk_email/feedback/' + str(self.id)
                return url
        else:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + '/helpdesk_email/feedback/' + str(self.id)
            return url
            
#    @api.one odoo13
    def set_to_reopen(self):
        stage_id = self.env['helpdesk.stage.config'].search([('stage_type','=','work_in_progress')])
        if self.is_close != False:
            self.is_close = False
            self.stage_id = stage_id.id
#            self.state = 'work_in_progress'
            
    def _default_stage_id(self):
        team = self.env['support.team'].sudo()._get_default_team_id(user_id=self.env.uid)
        return self._stage_find(team_id=team.id, domain=[('fold', '=', False)]).id
        
#    @api.multi odoo13
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}
    
    def _stage_find(self, team_id=False, domain=None, order='sequence'):
        """ Determine the stage of the current lead with its teams, the given domain and the given team_id
            :param team_id
            :param domain : base search domain for stage
            :returns crm.stage recordset
        """
        # collect all team_ids by adding given one, and the ones related to the current leads
        team_ids = set()
        if team_id:
            team_ids.add(team_id)
        for help in self:
            if help.team_id:
                team_ids.add(help.team_id.id)
        # generate the domain
        if team_ids:
            search_domain = ['|', ('team_id', '=', False), ('team_id', 'in', list(team_ids))]
        else:
            search_domain = [('team_id', '=', False)]
        # AND with the domain in parameter
        if domain:
            search_domain += list(domain)
        # perform search, return the first found
        return self.env['helpdesk.stage.config'].search(search_domain, order=order, limit=1)
    
    name = fields.Char(
        string='Number', 
        required=False,
        default='New',
        copy=False, 
        readonly=True, 
    )
    custom_customer_name = fields.Char(
        string='Customer Name',
        copy=True
    )
    
#    state = fields.Selection(
#        [('new','New'),
#         ('assigned','Assigned'),
#         ('work_in_progress','Work in Progress'),
#         ('needs_more_info','Needs More Info'),
#         ('needs_reply','Needs Reply'),
#         ('reopened','Reopened'),
#         ('solution_suggested','Solution Suggested'),
#         ('closed','Closed')],
#        tracking=True,
#        default='new',
#        copy=False, 
#    )
#     customer_id = fields.Many2one(
#         'res.partner',
#         string="Customer", 
#         required=True,
#     )
    email = fields.Char(
        string="Email",
        required=False
    )
    phone = fields.Char(
        string="Phone"
    )
    category = fields.Selection(
        [('technical', 'Technical'),
        ('functional', 'Functional'),
        ('support', 'Support')],
        string='Category',
    )
    subject = fields.Char(
        string="Subject"
    )
    type_ticket_id = fields.Many2one(
        'ticket.type',
        string="Type of Ticket",
        copy=False,
    )
    description = fields.Text(
        string="Description"
    )
    priority = fields.Selection(
        [('0', 'Low'),
        ('1', 'Middle'),
        ('2', 'High')],
        string='Priority',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    request_date = fields.Datetime(
        string='Create Date',
        # default=fields.Datetime.now,
        default=lambda self: fields.Datetime.now(),
        copy=False,
    )
    close_date = fields.Datetime(
        string='Close Date',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Assign To',
        tracking=True,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department'
    )
    timesheet_line_ids = fields.One2many(
        'account.analytic.line',
        'support_request_id',
        string='Timesheets',
    )
    is_close = fields.Boolean(
        string='Is Ticket Closed ?',
        tracking=True,
        default=False,
        copy=False,
    )
    total_spend_hours = fields.Float(
        string='Total Hours Spent',
        compute='_compute_total_spend_hours',
        store=True,
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )
    team_id = fields.Many2one(
        'support.team',
        string='Helpdesk Team',
        default=lambda self: self.env['support.team'].sudo()._get_default_team_id(user_id=self.env.uid),
        tracking=True,

    )
    team_leader_id = fields.Many2one(
        'res.users',
        string='Team Leader',
#         related ='team_id.leader_id',
#         store=True,
    )
    invoice_line_ids = fields.One2many(
        'support.invoice.line',
        'support_id',
        string='Invoice Lines',
    )
    journal_id = fields.Many2one(
        'account.journal',
         string='Invoice Journal',
     )
    invoice_id = fields.Many2one(
        # 'account.invoice',odoo13
        'account.move',
         string='Invoice Reference',
         copy='False',
     )
    is_invoice_created = fields.Boolean(
        string='Is Invoice Created',
        default=False,
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        readonly = True,
        
    )
    is_task_created = fields.Boolean(
        string='Is Task Created ?',
        default=False,
    )
    company_id = fields.Many2one(
        'res.company', 
        default=lambda self: self.env.user.company_id, 
        string='Company',
        readonly=False,
#        readonly=True,
     )
    comment = fields.Text(
        string='Customer Comment',
        readonly=True,
    )
    rating = fields.Selection(
        [('poor', 'Poor'),
        ('average', 'Average'),
        ('good', 'Good'),
        ('very good', 'Very Good'),
        ('excellent', 'Excellent')],
        string='Customer Rating',
        readonly=True,
    )
    subject_type_id = fields.Many2one(
        'type.of.subject',
        string="Type of Subject",
        copy=True,
    )
    allow_user_ids = fields.Many2many(
        'res.users',
        string='Allow Users'
    )
    
    custom_project_task_ids = fields.Many2many(
        'project.task', 
        string='Tasks',
        copy=False,
    )
    
    custom_account_invoice_ids = fields.Many2many(
        # 'account.invoice', odoo13
        'account.move',
        string='Invoices',
        copy=False,
    )
    
    custome_client_user_id = fields.Many2one(
        'res.users',
        string="Ticket Created User",
        readonly = True,
        # track_visibility='always'
        tracking=True,
    )
    
#    @api.model
#    def create(self, vals):
#        if vals.get('custome_client_user_id', False):
#            client_user_id = self.env['res.users'].browse(int(vals.get('custome_client_user_id')))
#            if client_user_id:
#                vals.update({'company_id': client_user_id.company_id.id})
#        else:
#            vals.update({'custome_client_user_id': self.env.user.id})
#        return super(HelpdeskSupport, self).create(vals)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # retrieve team_id from the context and write the domain
        # - ('id', 'in', stages.ids): add columns that should be present
        # - OR ('fold', '=', False): add default columns that are not folded
        # - OR ('team_ids', '=', team_id), ('fold', '=', False) if team_id: add team columns that are not folded
        team_id = self._context.get('default_team_id')
        if team_id:
            search_domain = ['|', ('id', 'in', stages.ids), '|', ('team_id', '=', False), ('team_id', '=', team_id)]
        else:
            search_domain = ['|', ('id', 'in', stages.ids), ('team_id', '=', False)]

        # perform search
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)
    
    
    stage_id = fields.Many2one(
                'helpdesk.stage.config',
                string='Stage',
                tracking=True,
                index=True,
                domain="['|', ('team_id', '=', False), ('team_id', '=', team_id)]",
                group_expand='_read_group_stage_ids', 
                default=lambda self: self._default_stage_id(),
                copy=False,
                store=True
    )
    stage_type = fields.Selection(
        'Type',
        store=True,
        related='stage_id.stage_type',
    )
    active = fields.Boolean('Active', default=True)
    color = fields.Integer(
            'Color Index',
            default=0
    )
#     priority = fields.Selection(
#                 helpdesk_stage.AVAILABLE_PRIORITIES,
#                 string='Rating',
#                 index=True,
#                 default=helpdesk_stage.AVAILABLE_PRIORITIES[0][0]
#     )
    planned_revenue = fields.Float(
                        'Expected Revenue',
                        # track_visibility='always'
                        tracking=True
    )
    kanban_state = fields.Selection([('grey', 'No next activity planned'), 
                    ('red', 'Next activity late'), 
                    ('green', 'Next activity is planned')],
#                    string='Activity State', odoo13
                    string='Kanban Activity State',
                    compute='_compute_kanban_state',
    )
    date_action = fields.Date('Next Activity Date', index=True)
    
#    @api.multi odoo13
    @api.depends('analytic_account_id')
    def compute_total_hours(self):
        total_remaining_hours = 0.0
        for rec in self:
            rec.total_purchase_hours = rec.analytic_account_id.total_purchase_hours
            rec.total_consumed_hours = rec.analytic_account_id.total_consumed_hours
            rec.remaining_hours = rec.analytic_account_id.remaining_hours
            rec.balanced_remaining_hours = rec.analytic_account_id.remaining_hours - rec.total_spend_hours
    
    total_purchase_hours = fields.Float(
        string='Total Purchase Hours',
        compute='compute_total_hours',
        store=True,
    )
    total_consumed_hours = fields.Float(
        string='Total Consumed Hours',
        compute='compute_total_hours',
        store=True,
    )
    remaining_hours = fields.Float(
        string='Remaining Hours',
        compute='compute_total_hours',
        store=True,
        help="This refers to remaining hours during creating ticket."
    )
    balanced_remaining_hours = fields.Float(
        string='Balance Remaining Hours',
        compute='compute_total_hours',
        store=True,
        help="This refers to balance remaining hours during working on ticket."
    )
    
#    @api.multi odoo13
    @api.onchange('team_id')
    def team_id_change(self):
        for rec in self:
            rec.team_leader_id = rec.team_id.leader_id.id
    
#    @api.multi odoo13
    @api.onchange('partner_id')
    def partner_id_change(self):
        for rec in self:
            rec.email = rec.partner_id.email
            rec.phone = rec.partner_id.phone
            rec.custom_customer_name = rec.partner_id.name
    
#    @api.one odoo13
    def unlink(self):
        for rec in self:
            if rec.stage_id.stage_type != 'new':
                raise UserError(_('You can not delete record which are not in draft state.'))
        return super(HelpdeskSupport, self).unlink()
        
#    @api.multi odoo13
    def _prepare_invoice_line(self, invoice_id):
        """
        Prepare the dict of values to create the new invoice line.
        :param qty: float quantity to invoice
        """
        for rec in self:
            invoice_line_vals = []
            for line in rec.invoice_line_ids:
                if line.is_invoice:
                    pass
                else:
                    line.is_invoice = "True"
                    product = line.product_id
#                    account = product.property_account_expense_id or product.categ_id.property_account_expense_categ_id odoo13
                    account = product.property_account_income_id or product.categ_id.property_account_income_categ_id
                    if not account:
                        raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') % \
                                (product.name, product.id, product.categ_id.name))
                    fpos = invoice_id.partner_id.property_account_position_id
                    if fpos:
                        account = fpos.map_account(account)
                    vals = {
                        'name': product.name, 
#                        'origin': invoice_id.origin, odoo13
                        'account_id': account.id,
                        'price_unit': line.price_unit,
#                         'price_subtotal' : line.product_id.standard_price * line.quantity,
                        'quantity': line.quantity, 
#                        'uom_id': product.uom_id.id, odoo13
                        'product_uom_id': product.uom_id.id,
                        'product_id': product.id or False, 
                        'analytic_distribution':  {line.sudo().analytic_account_id.id: 100} if line.analytic_account_id else False,
#                        'account_analytic_id' : line.analytic_account_id.id,odoo13
                        # 'analytic_account_id' : line.analytic_account_id.id,
#                        'invoice_id': invoice_id.id odoo13
                        'move_id': invoice_id.id,
                    }
                    invoice_line_vals.append((0,0,vals))
                    # line = self.env['account.invoice.line'].sudo().create(vals)odoo13
#                    line = self.env['account.move.line'].sudo().create(vals) odoo13
            
            invoice_id.write({'invoice_line_ids' : invoice_line_vals})
        return True
    
#    @api.multi odoo13
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice . This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        partner = self.partner_id
        if not partner.property_product_pricelist:
            raise UserError(_('Please set pricelist.'))
        if not self.journal_id:
            raise UserError(_('Please configure an accounting sale journal for this company.'))
        if not self.user_id:
            raise UserError(_('Please set the Assign To.'))
        invoice_vals = {
            'ref': self.name or '', 
#            'origin': self.name, odoo13
            'invoice_origin': self.name, 
#            'type': 'out_invoice',
            'move_type': 'out_invoice',
#            'date_invoice' : fields.Date.today(), odoo13
            'invoice_date' : fields.Date.today(),
#            'account_id': partner.property_account_receivable_id.id, odoo13
            'partner_id': partner.id, 
            'journal_id': self.journal_id.id, 
            'currency_id': partner.property_product_pricelist.currency_id.id,
#            'payment_term_id': partner.property_payment_term_id.id, odoo13
            'invoice_payment_term_id': partner.property_payment_term_id.id,
            'fiscal_position_id': partner.property_account_position_id.id,
            'company_id': self.user_id.company_id.id, 
#            'user_id': self.user_id.id,  odoo13
            'invoice_user_id': self.user_id.id, 
            
        }
        return invoice_vals
    
#    @api.multi odoo13
    def action_create_invoice(self):
        # inv_obj = self.env['account.invoice']odoo13
        # inv_line_obj = self.env['account.invoice.line']odoo13
        inv_obj = self.env['account.move']
        inv_line_obj = self.env['account.move.line']
        vals_invoice=[]
        for rec in self:
            if not rec.invoice_line_ids:
                raise UserError(_('Please add invoice lines.'))
#            else:
#                inv_obj = self.env['account.invoice'].sudo().search([('origin', '=', rec.name)])
#                if inv_obj.origin:
#                    rec._prepare_invoice_line(inv_obj) 
#                    rec.invoice_id = inv_obj.id
            else:
                inv_data = rec._prepare_invoice()
                invoice = inv_obj.create(inv_data)
                rec._prepare_invoice_line(invoice)
                rec.invoice_id = invoice.id
                rec.invoice_id = invoice.id
                vals_invoice.append((4, rec.invoice_id.id))
                vals = {
                    'invoice_id' : invoice.id,
                    'is_invoice_created' : True,
                    'custom_account_invoice_ids':vals_invoice,
                    }
                rec.write(vals)
        
#    @api.multi odoo13
    def show_invoice(self):
        # for rec in self:
        self.ensure_one()
            # salin = self.env['account.invoice']odoo13
        # salin = self.env['account.move']
#            res = self.env.ref('account.action_invoice_tree1') odoo13
        # res = self.env.ref('account.action_move_out_invoice_type')
        # res = res.sudo().read()[0]
        res = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        res['domain'] = str([('id','in',self.custom_account_invoice_ids.ids)])
        return res
        
#    @api.multi odoo13
    def action_create_task(self):
        vals_task=[]
        self.ensure_one()
        for rec in self:
            if rec.subject:
                task_name = rec.subject +'('+rec.name+')'
            else:
                task_name = rec.name
            
            task_vals = {
#            'name' : rec.subject +'('+rec.name+')',
            'name' : task_name,
            # 'user_id' : rec.user_id.id,
            # 'activity_user_id' : rec.user_id.id,
            'user_ids' : [rec.user_id.id] if rec.user_id else False,
            'date_deadline' : rec.close_date,
            'project_id' : rec.project_id.id,
            'partner_id' : rec.partner_id.id,
            'description' : rec.description,
            'ticket_id' : rec.id,
            }
            task_id= self.env['project.task'].sudo().create(task_vals)
            vals_task.append((4, task_id.id))
            vals = {
            'task_id' : task_id.id,
            'is_task_created' : True,
            'custom_project_task_ids':vals_task,
            }
            rec.write(vals)
            if task_id:                               
                action = self.env.ref('project.action_view_task').sudo().read()[0]
                action['domain'] = [('id', '=', task_id.id)]
                ctx = safe_eval(action['context'])
#                ctx.update({'search_default_my_tasks' : 0}) odoo13
                ctx.update({'search_default_my_tasks' : 0, 'default_ticket_id' : rec.id})
                action['context'] = ctx
                return action
            
#    @api.multi odoo13
    def show_task(self):
        # for rec in self:
        self.ensure_one()
        # res = self.env.ref('project.action_view_task')
        # res = res.sudo().read()[0]
        res = self.env['ir.actions.act_window']._for_xml_id('project.action_view_task')
        ticket_task_id = self.env['project.task'].sudo().search([('ticket_id', '=', self.id)])
        task_ticket_list = list(dict.fromkeys(self.custom_project_task_ids.ids + ticket_task_id.ids))
#            res['domain'] = str([('id','in',rec.custom_project_task_ids.ids)]) odoo13
        res['domain'] = str([('id','in',task_ticket_list)])
        ctx = safe_eval(res['context'])
        ctx.update({'search_default_my_tasks' : 0, 'default_ticket_id' : self.id})
        res['context'] = ctx
        return res
    
#    @api.multi odoo13
    def show_analytic_account(self):
        # for rec in self:
        self.ensure_one()
        # res = self.env.ref('analytic.action_account_analytic_account_form')
        # res = res.sudo().read()[0]
        res = self.env['ir.actions.act_window']._for_xml_id('analytic.action_account_analytic_account_form')
        res['domain'] = str([('id','=',self.analytic_account_id.id)])
        return res
    
    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        self = self.with_context(default_user_id=False)

        if custom_values is None:
            custom_values = {}
        defaults = {
            'name':  msg_dict.get('subject') or _("No Subject"),
            'email': msg_dict.get('from'),
            #'email_cc': msg_dict.get('cc'),
            'partner_id': msg_dict.get('author_id', False),
        }
        if 'body' in msg_dict:
            body_msg = tools.html2plaintext(msg_dict['body'])
            defaults.update(description=body_msg)
        defaults.update(custom_values)
        return super(HelpdeskSupport, self).message_new(msg_dict, custom_values=defaults)
        
class HrTimesheetSheet(models.Model):
    _inherit = 'account.analytic.line'

    support_request_id = fields.Many2one(
        'helpdesk.support',
        domain=[('is_close','=',False)],
        string='Helpdesk Support',
    )
    billable = fields.Boolean(
        string='Billable',
        default=True,
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
