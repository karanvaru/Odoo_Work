# -*- coding: utf-8 -*-

import time
from datetime import date
from odoo.exceptions import UserError
from . import helpdesk_stage

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, Warning

class HelpdeskSupport(models.Model):
    _name = 'helpdesk.support'
    _description = 'Helpdesk Support'
    _order = 'id desc'
#     _inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
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

        # context: no_log, because subtype already handle this
        return super(HelpdeskSupport, self.with_context(context, mail_create_nolog=True)).create(vals)
        
#        return super(HelpdeskSupport, self).create(vals)
    
    @api.multi
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
    
    @api.multi
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
          
    @api.one
    def set_to_close(self):
        stage_id = self.env['helpdesk.stage.config'].search([('stage_type','=','closed')])
        if self.is_close != True:
            self.is_close = True
            self.close_date = fields.Datetime.now()#time.strftime('%Y-%m-%d')
            self.stage_id = stage_id.id
#            self.state = 'closed'
            template = self.env.ref('website_helpdesk_support_ticket.email_template_helpdesk_ticket')
            template.send_mail(self.id, force_send=True)
            
    @api.one
    def set_to_reopen(self):
        stage_id = self.env['helpdesk.stage.config'].search([('stage_type','=','work_in_progress')])
        if self.is_close != False:
            self.is_close = False
            self.stage_id = stage_id.id
#            self.state = 'work_in_progress'
            
    def _default_stage_id(self):
        team = self.env['support.team'].sudo()._get_default_team_id(user_id=self.env.uid)
        return self._stage_find(team_id=team.id, domain=[('fold', '=', False)]).id
        
    @api.multi
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
        default=fields.Datetime.now,
        copy=False,
    )
    close_date = fields.Datetime(
        string='Close Date',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Assign To',
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
        'account.invoice',
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
        readonly=True,
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
    priority = fields.Selection(
                helpdesk_stage.AVAILABLE_PRIORITIES,
                string='Rating',
                index=True,
                default=helpdesk_stage.AVAILABLE_PRIORITIES[0][0]
    )
    planned_revenue = fields.Float(
                        'Expected Revenue',
                        # track_visibility='always'
                        tracking=True
    )
    kanban_state = fields.Selection([('grey', 'No next activity planned'), 
                    ('red', 'Next activity late'), 
                    ('green', 'Next activity is planned')],
                    string='Activity State',
                    compute='_compute_kanban_state',
    )
    date_action = fields.Date('Next Activity Date', index=True)
    
    @api.multi
    @api.depends('analytic_account_id')
    def compute_total_hours(self):
        total_remaining_hours = 0.0
        for rec in self:
            rec.total_purchase_hours = rec.analytic_account_id.total_purchase_hours
            rec.total_consumed_hours = rec.analytic_account_id.total_consumed_hours
            rec.remaining_hours = rec.analytic_account_id.remaining_hours
    
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
    )
    
    @api.multi
    @api.onchange('team_id')
    def team_id_change(self):
        for rec in self:
            rec.team_leader_id = rec.team_id.leader_id.id
    
    @api.multi
    @api.onchange('partner_id')
    def team_id_change(self):
        for rec in self:
            rec.email = rec.partner_id.email
            rec.phone = rec.partner_id.phone
    
    @api.one
    def unlink(self):
        for rec in self:
            if rec.stage_id.stage_type != 'new':
                raise UserError(_('You can not delete record which are not in draft state.'))
        return super(HelpdeskSupport, self).unlink()
        
    @api.multi
    def _prepare_invoice_line(self, invoice_id):
        """
        Prepare the dict of values to create the new invoice line.
        :param qty: float quantity to invoice
        """
        for rec in self:
            for line in rec.invoice_line_ids:
                if line.is_invoice:
                    pass
                else:
                    line.is_invoice = "True"
                    product = line.product_id
                    account = product.property_account_expense_id or product.categ_id.property_account_expense_categ_id
                    if not account:
                        raise UserError(_('Please define expense account for this product: "%s" (id:%d) - or for its category: "%s".') % \
                                (product.name, product.id, product.categ_id.name))
                    fpos = invoice_id.partner_id.property_account_position_id
                    if fpos:
                        account = fpos.map_account(account)
                    vals = {
                        'name': product.name, 
                        'origin': invoice_id.origin,
                        'account_id': account.id,
                        'price_unit': line.price_unit,
#                         'price_subtotal' : line.product_id.standard_price * line.quantity,
                        'quantity': line.quantity, 
                        'uom_id': product.uom_id.id,
                        'product_id': product.id or False, 
                        'account_analytic_id' : line.analytic_account_id.id,
                        'invoice_id': invoice_id.id 
                    }
                    line = self.env['account.invoice.line'].sudo().create(vals)
        return True
    
    @api.multi
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
        invoice_vals = {
            'name': self.name or '', 
            'origin': self.name, 
            'type': 'out_invoice',
            'date_invoice' : fields.Date.today(),
            'account_id': partner.property_account_receivable_id.id,
            'partner_id': partner.id, 
            'journal_id': self.journal_id.id, 
            'currency_id': partner.property_product_pricelist.currency_id.id,
            'payment_term_id': partner.property_payment_term_id.id,
            'fiscal_position_id': partner.property_account_position_id.id,
            'company_id': self.user_id.company_id.id, 
            'user_id': self.user_id.id, 
            
        }
        return invoice_vals
    
    @api.multi
    def action_create_invoice(self):
        inv_obj = self.env['account.invoice']
        inv_line_obj = self.env['account.invoice.line']
        for rec in self:
            if not rec.invoice_line_ids:
                raise UserError(_('Please add invoice lines.'))
            else:
                inv_obj = self.env['account.invoice'].sudo().search([('origin', '=', rec.name)])
                if inv_obj.origin:
                    rec._prepare_invoice_line(inv_obj) 
                    rec.invoice_id = inv_obj.id
                else:
                    inv_data = rec._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    rec._prepare_invoice_line(invoice)
                    rec.invoice_id = invoice.id
                    rec.invoice_id = invoice.id
                    vals = {
                        'invoice_id' : invoice.id,
                        'is_invoice_created' : True,
                        }
                    rec.write(vals)
        
    @api.multi
    def show_invoice(self):
        for rec in self:
            salin = self.env['account.invoice']
            res = self.env.ref('account.action_invoice_tree1')
            res = res.sudo().read()[0]
            res['domain'] = str([('id','=',rec.invoice_id.id)])
        return res
        
    @api.multi
    def action_create_task(self):
        for rec in self:
            task_vals = {
            'name' : rec.subject +'('+rec.name+')',
            'user_id' : rec.user_id.id,
            'date_deadline' : rec.close_date,
            'project_id' : rec.project_id.id,
            'partner_id' : rec.partner_id.id,
            'description' : rec.description,
            'ticket_id' : rec.id,
            }
            task_id= self.env['project.task'].sudo().create(task_vals)
            vals = {
            'task_id' : task_id.id,
            'is_task_created' : True,
            }
            rec.write(vals)
            
    @api.multi
    def show_task(self):
        for rec in self:
            res = self.env.ref('project.action_view_task')
            res = res.sudo().read()[0]
            res['domain'] = str([('id','=',rec.task_id.id)])
        return res
    
    @api.multi
    def show_analytic_account(self):
        for rec in self:
            res = self.env.ref('analytic.action_account_analytic_account_form')
            res = res.sudo().read()[0]
            res['domain'] = str([('id','=',rec.analytic_account_id.id)])
        return res
        
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
