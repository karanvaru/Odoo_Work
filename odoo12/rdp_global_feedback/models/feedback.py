from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.modules.module import get_resource_path
import base64

RATING_LIMIT_SATISFIED = 7
RATING_LIMIT_OK = 3
RATING_LIMIT_MIN = 1



class FeedbackApp(models.Model):
    _name = "global.feedback"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Global Feedback App"


    name = fields.Char(string='Reference No', required=True, copy=False,track_visibility='always', readonly=True, index=True, default=lambda self : _('New'))
    feedback = fields.Text(string="Feedback", track_visibility='always')
    # customer_name = fields.Char(string="Name",track_visibility='always')
    company_name = fields.Char(string="Company Name", track_visibility='always')
    email = fields.Char(string="Email",track_visibility='always')
    mobile = fields.Char(string="Mobile", track_visibility='always')
    department = fields.Many2one('hr.department', string="Department", track_visibility='always')
    category = fields.Many2one('feedback.category', string="Category", track_visibility='always')
    sub_category = fields.Many2one('feedback.sub.category', string="Sub Category", track_visibility='always')
    scope = fields.Many2one('feedback.scope', string="Scope", track_visibility='always')
    tag_ids = fields.Many2many('feedback.tags', 'feedback_tags_rel', 'name', string='Tags',
                               track_visibility='onchange')
    notes = fields.Text('Notes', track_visibility='always')
    state = fields.Selection([
        ('new', 'NEW'),
        ('wip', 'WIP'),
        ('improved', 'IMPROVED'),
        ('cancel', 'CANCEL'),
        ('future', 'FUTURE'),
    ], string='Status', default='new', track_visibility='onchange')
    open_days = fields.Char(string='Open Days', compute='calculate_open_days')
    closed_date = fields.Datetime(string="Closed Date")
    # rating_image = fields.Binary('Image',)
    # rating = fields.Float(string="Rating Number", group_operator="avg", default=0, help="Rating value: 0=Unhappy, 10=Happy")
    rating_image = fields.Binary('Image', compute='_compute_rating_image')
    rating_text = fields.Selection([
        ('3', 'Satisfied'),
        ('2', 'Not satisfied'),
        ('1', 'Highly dissatisfied'),
        ('0', 'No Rating yet')], string='Rating',default="0")
    # rating_emoji = fields.Selection([
    #     ('3', 'Satisfied'),
    #     ('2', 'Not satisfied'),
    #     ('1', 'Highly dissatisfied'),
    #     ('0', 'No Rating yet')], 
        
    #     string='Rating',default="0")

    ### Added Fields
    first_name = fields.Char('First Name',track_visibility='always',readonly=True)
    last_name = fields.Char('Last Name',track_visibility='always',readonly=True)
    improve_area = fields.Selection([
        ('product_delivery', 'Product Delivery'),
        ('support_delivery', 'Support Delivery'),
        ('product_quality', 'Product Quality'),
        ('sales_response', 'Sales Response'),
        ('finance', 'Finance'),
        ('others', 'Others'),
    ], string='Improve Area', track_visibility='always')
    subject = fields.Char('Subject',track_visibility='always')
    improvement_suggested= fields.Text('Improvements Suggested',track_visibility='always')
    create_date_temp = fields.Char('Create Date',compute="_compute_create_date")




    
    @api.multi
    @api.depends('rating_text')
    def _compute_rating_image(self):
        for rating in self:
            try:
                image_path = get_resource_path('rdp_global_feedback', 'static/src/img', 'rating_%s.png' % (int(rating.rating_text),))
                rating.rating_image = base64.b64encode(open(image_path, 'rb').read())
            except (IOError, OSError):
                rating.rating_image = False

    # @api.depends('rating')
    # def _compute_rating_text(self):
    #     for rating in self:
    #         if rating.rating >= RATING_LIMIT_SATISFIED:
    #             rating.rating_text = '3'
    #         elif rating.rating > RATING_LIMIT_OK:
    #             rating.rating_text = '2'
    #         elif rating.rating >= RATING_LIMIT_MIN:
    #             rating.rating_text = '1'
    #         else:
    #             rating.rating_text = '0'


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('feedback.sequence')
        res = super(FeedbackApp, self).create(vals)
        return res


    @api.multi
    def action_to_work_in_progress(self):
        self.state = 'wip'

    @api.multi
    def action_to_improved(self):
        self.closed_date = datetime.today()
        self.state = 'improved'

    @api.multi
    def action_to_cancel(self):
        self.closed_date = datetime.today()
        self.state = 'cancel'

    @api.multi
    def action_to_future(self):
        # self.closed_date = datetime.today()
        self.state = 'future'    

    @api.multi
    def action_to_new(self):
        self.write({'state': 'new'})

    @api.multi
    def calculate_open_days(self):
        for rec in self:
            if rec.closed_date:
                rec.open_days = (rec.closed_date - rec.create_date).days
            else:
                rec.open_days = (datetime.today() - rec.create_date).days
    @api.multi
    def _compute_create_date(self):
        for rec in self:
            rec.create_date_temp = rec.create_date
            # # ct = datetime.strftime(rec.create_date, '%Y-%m-%d %H:%M')
            # ct = datetime.strftime(rec.create_date,"%Y-%m-%d, %H:%M")
            # end_last = datetime.strptime(ct, '%Y-%m-%d %H:%M')
            # # end_last[:-3]
            rec.create_date_temp =rec.create_date_temp[:-10]         


class FeedbackTags(models.Model):
    _name = "feedback.tags"

    _description = "Global Feedback Tags"

    name = fields.Char('Name')

class Scope(models.Model):
    _name = "feedback.scope"

    _description = "Global Feedback Scope"

    name = fields.Char('Name')



class FeedbackCategory(models.Model):
    _name = "feedback.category"

    _description = "Global Feedback Category"

    name = fields.Char(string="Name")


class FeedbackSubCategory(models.Model):
    _name = "feedback.sub.category"

    _description = "Global Feedback Sub Category"

    name = fields.Char(string="Name")

class Website(models.Model):
    _inherit = 'website'

    recaptcha_sitekey = fields.Char()
    recaptcha_secretkey = fields.Char()    

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    recaptcha_sitekey = fields.Char(
        string="Recaptcha Site Key",
        related='website_id.recaptcha_sitekey',
        readonly=False,
        )
    recaptcha_secretkey = fields.Char(
        string="Recaptcha Secret Key",
        related='website_id.recaptcha_secretkey',
        readonly=False,
        )    