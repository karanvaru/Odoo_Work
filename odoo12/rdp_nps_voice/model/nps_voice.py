import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class NPSVoice(models.Model):
    _name = 'nps.voice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "NPS Voice"
    _order = 'id desc'

    name = fields.Char('Reference',track_visibility= True)
    sale_order_id = fields.Many2one('sale.order',string='Source Document',track_visibility= True,readonly=True)
    partner_id = fields.Many2one('res.partner', string="Customer", compute="compute_nps_sale_order",track_visibility= True)
    # so_gem_rp_id = fields.Many2one('res.partner', string="SO GeM RP", compute="compute_nps_sale_order",track_visibility= True)
    mobile = fields.Char('Mobile',track_visibility= True,compute="compute_nps_sale_order")
    phone = fields.Char('Phone',track_visibility= True,compute="compute_nps_sale_order")
    so_state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], compute ='compute_nps_sale_order', string='SO Status',readonly=True,track_visibility= True)
    inv_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
        ], string='Invoice Status',compute = 'compute_nps_sale_order', readonly=True,track_visibility= True)
    nps_rating = fields.Selection([
        ('0', '0 - Annoyed'),
        ('1', '1 - Bad Experience'),
        ('2', '2 - Not Satisfactory'),
        ('3', '3 - Could Improve'),
        ('4', '4 - Tolerable'),
        ('5', '5 - Average'),
        ('6', '6 - Its Okay'),
        ('7', '7 - Nice'),
        ('8', '8 - Greate'),
        ('9', '9 - Awesome'),
        ('10', '10 - Brillient')
    ], string='NPS Rating', track_visibility='True')
    nps_category_id = fields.Many2one('nps.category', string="NPS Category",track_visibility='onchange')
    problem_category_id = fields.Many2one('nps.problem.category','Problem Category',track_visibility='always')
    nps_feed_back = fields.Text(string="Feedback",track_visibility='always')

    note = fields.Text('Notes',track_visibility='always')

    sdm_asdm_call_done = fields.Boolean(string='Internal Stake Holders Call Done',track_visibility='always')
    dd_comments = fields.Text('DD Comments',track_visibility='always')
    improvement_task_id = fields.Many2one('nps.improvement.task', string="Improvement Task", track_visibility='onchange')
    is_implemented = fields.Boolean(string="Is Implemented", track_visibility='always')

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('nps.voice.sequence')
        })
        res = super(NPSVoice, self).create(vals)
        return res
    
    # @api.depends('sale_order_id')
    # def compute_nps_sale_order(self):
    #     for rec in self:
    #         rec.so_state = rec.sale_order_id.state
    #         rec.inv_status = rec.sale_order_id.invoice_status
    #         rec.partner_id = rec.sale_order_id.partner_id
    #         rec.so_gem_rp_id = rec.sale_order_id.so_gem_rp_id
    #         rec.mobile = rec.so_gem_rp_id.mobile
    #         rec.phone = rec.so_gem_rp_id.phone


class NPSCategory(models.Model):
    _name = "nps.category"
    _description = "NPS Category"

    name = fields.Char(string="Name")


class NPSProblemCategory(models.Model):
    _name = "nps.problem.category"
    _description = "NPS Problem Category"

    name = fields.Char(string="Name")


class NPSImprovementTasks(models.Model):
    _name = 'nps.improvement.task'
    _description = 'Improvement Task'

    name = fields.Char(string="Improvement Task")
