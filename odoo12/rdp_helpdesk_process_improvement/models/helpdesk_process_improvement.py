from odoo import api, fields, models, _
from datetime import date, datetime
import time
from datetime import date, datetime
import time

class HeldeskProcessImprovement(models.Model):
    _name = "helpdesk.process.improvement"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Helpdesk Process Improvement"

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    subject = fields.Char(string="Subject", track_visibility='always')
    description = fields.Text(string="Description", track_visibility='always')
    internal_notes = fields.Text(string="Internal Notes", track_visibility='always')
    state = fields.Selection([
        ('new', 'NEW'),
        ('wip', 'WIP'),
        ('improved', 'IMPROVED'),
        ('cancel', 'CANCELLED'),
        ('future', 'FUTURE'),
    ], string='Status', readonly=True, default='new', track_visibility='always')
    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', "Helpdesk Ticket", track_visibility='always')
    five_why_ticket_id = fields.Many2one('five.why', "Five Why", track_visibility='always')
    quality_audit_ticket_id = fields.Many2one('quality.audit', "Quality Audit", track_visibility='always')
    kam_escalation_ticket_id = fields.Many2one('ked.escalation', "KAM Escalation", track_visibility='always')
    global_feedback_ticket_id = fields.Many2one('global.feedback', "Global Feedback", track_visibility='always')
    sales_challenge_ticket_id = fields.Many2one('sale.challenge', "Sales Challenge", track_visibility='always')
    asp_ticket_id = fields.Many2one('asp.partner', "Asp App", track_visibility='always')
    pspr_ticket_id = fields.Many2one('product.details', "PSPR", track_visibility='always')
    category_id = fields.Many2one('helpdesk.process.improvement.category', string="Category", track_visibility='always')
    engineering = fields.Selection([
        ('reverse', 'Reverse'),
        ('forward', 'Forward'),
        ('other', 'Other')
    ], string='Engineering', track_visibility='always')
    process_imptovement_type = fields.Selection([
        ('butterfly_effect', 'Butterfly Effect'),
        ('medium', 'Medium Effect'),
        ('low', 'Low Effect')
    ], string='Process Improvement Type', track_visibility='always')
    opendays = fields.Char('Opendays', compute="compute_open_days")
    closed_date = fields.Datetime('Close Date', track_visibility='always')
    sub_category_id = fields.Many2one('helpdesk.process.improvement.sub.category', string="Sub Category",
                                  track_visibility='always')
    assigned_to = fields.Many2one('res.users', 'Assigned To', track_visibility='always')
    hpi_cancel_ids = fields.One2many('hpi.cancel', 'hpi_cancel_id', string="Cancel Ids",
                                    track_visibility='always')
    hpi_future_ids = fields.One2many('hpi.future', 'hpi_future_id', string="Future Ids",
                                     track_visibility='always')
    tag_ids = fields.Many2many('hdpi.tags', string='Tags', track_visibility='always')
    priority = fields.Selection([
        ('[0]','All'),
        ('[1]','Low priority'),
        ('[2]','High priority'),
        ('[3]','Urgent'),
        ],string='Priority',track_visibility='always')
    goal_date = fields.Datetime(string="Goal Date")

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('hp.sequence'),
        })
        return super(HeldeskProcessImprovement, self).create(vals)

    @api.multi
    def action_to_wip(self):
        self.state = 'wip'

    @api.multi
    def action_to_improved(self):
        self.state = 'improved'
        self.closed_date = datetime.today()

    @api.multi
    def action_to_cancel(self):
        self.state = 'cancel'

    @api.multi
    def action_to_future(self):
        self.state = 'future'
        self.closed_date = datetime.today()

    @api.multi
    def action_set_new(self):
        self.write({'state': 'new'})


    # @api.multi
    # def compute_open_days(self):
    #     for record in self:
    #         if record['closed_date']:
    #             record['opendays'] = str((record['closed_date'] - record['create_date']))
    #             record['opendays'] = record['opendays'].split('.')[0]
    #         else:
    #                 record['opendays'] = str((datetime.today() - record['create_date']))
    #                 record['opendays'] = record['opendays'].split('.')[0]
    @api.multi
    def compute_open_days(self):
        for record in self:
            if record['closed_date']:
                record['opendays'] = str((record['closed_date'] - record['create_date']).days) + " Days"
                record['opendays'] = record['opendays'].split('.')[0]
            else:
                record['opendays'] = str((datetime.today() - record['create_date']).days) + " Days"
                record['opendays'] = record['opendays'].split('.')[0]

    # source = fields.Char(string='Source', compute='_compute_source_ids')
    #
    # @api.depends('helpdesk_ticket_id', 'quality_audit_ticket_id', 'kam_escalation_ticket_id', 'five_why_ticket_id')
    # def _compute_source_ids(self):
    #     for record in self:
    #         source_ids = []
    #         if record.helpdesk_ticket_id:
    #             source_ids.append(record.helpdesk_ticket_id.display_name)
    #         if record.quality_audit_ticket_id:
    #             source_ids.append(record.quality_audit_ticket_id.name)
    #         if record.kam_escalation_ticket_id:
    #             source_ids.append(record.kam_escalation_ticket_id.name)
    #         if record.five_why_ticket_id:
    #             source_ids.append(record.five_why_ticket_id.name)
    #         record.source_ids = ', '.join(source_ids)

class HeldeskProcessImprovementCategory(models.Model):
    _name = "helpdesk.process.improvement.category"
    _description = "Helpdesk Process Improvement Category"

    name = fields.Char('Name')

class HeldeskProcessImprovementSubCategory(models.Model):
    _name = "helpdesk.process.improvement.sub.category"
    _description = "Helpdesk Process Improvement Sub Category"

    name = fields.Char('Name')

class HpiCategory(models.Model):
    _name = "hdpi.category"
    _description = "Category"

    name = fields.Char('Name')



class HpiFutureReason(models.Model):
    _name = "hpi.future"
    _description = "Future Reason"

    name = fields.Char('Name')
    hpi_future_id = fields.Many2one('helpdesk.process.improvement', string='FUTURE')
    future_description = fields.Text(string='Description', required=True)
    hdpi_future_category_id = fields.Many2one('hdpi.category', string="Category")

class HpiCancelReason(models.Model):
    _name = "hpi.cancel"
    _description = "Cancel Reason"

    name = fields.Char('Name')
    hpi_cancel_id = fields.Many2one('helpdesk.process.improvement', string='Cancel')
    cancel_description = fields.Text(string='Description', required=True)
    hdpi_cancel_category_id = fields.Many2one('hdpi.category', string="Category")

class HDPITags(models.Model):
    _name = "hdpi.tags"

    _description = "HDPI Tags"

    name = fields.Char('Name')

