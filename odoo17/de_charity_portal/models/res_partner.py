from odoo import models, api, fields
import base64
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_charity_customer = fields.Boolean(
        string="FHIN Client?",
        copy=False
    )

    dob = fields.Date(
        string="DOB",
    )
    occupation = fields.Char(
        "Occupation",
    )
    fax_number = fields.Char(
        "Fax Number",
    )
    sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], tracking=True)

    age = fields.Float(
        "Age"
    )
    height = fields.Float(
        "Height"
    )

    marital_status = fields.Selection([
        ('SINGLE', 'Single'),
        ('STEADY', 'Steady'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
    ], string='Marital Status', tracking=True)

    primary_edu = fields.Selection([
        ('p_first', '1'),
        ('p_second', '2'),
        ('p_third', '3'),
        ('p_fourth', '4'),
    ], string='Primary education', tracking=True)

    high_school_edu = fields.Selection([
        ('h_first', '1'),
        ('h_second', '2'),
        ('h_third', '3'),
        ('h_fourth', '4'),
        ('h_fifth', '5'),
        ('h_six', '6'),
    ], string='High School Education', tracking=True)

    college_edu = fields.Selection([
        ('c_first', '1'),
        ('c_second', '2'),
        ('c_third', '3'),
        ('c_fourth', '4'),
        ('c_fifth', '5'),
        ('c_six', '6'),
    ], string='College Education', tracking=True)

    university_edu = fields.Selection([
        ('u_first', '1'),
        ('u_second', '2'),
        ('u_third', '3'),
        ('u_fourth', '4'),
    ], string='University Education', tracking=True)
    other_training = fields.Char(
        "Other Training",
    )
    referred_by = fields.Char(
        "Referred By",
    )
    referred_by_of = fields.Char(
        "Of",
    )
    physical_health_rate = fields.Selection([
        ('VERY_GOOD', 'Very Good'),
        ('GOOD', 'Good'),
        ('AVERAGE', 'Average'),
        ('DECLINING', 'Declining'),
        ('OTHER', 'Other'),
    ], string='Physical Health Rate', tracking=True)

    part_illnesses = fields.Text(
        string="Part Illnesses",
    )
    prepare_medicine = fields.Boolean(
        string="Prepare Medicine?",
    )
    what = fields.Char(
        "What",
    )
    emotional_upset = fields.Boolean(
        string="Emotional Upset?",
    )
    is_counselling = fields.Boolean(
        string="Counselling?",
    )
    major_change_life = fields.Text(
        string="Major Change",
    )
    demonational_preference = fields.Char(
        "Demonational Preference",
    )
    is_baptized = fields.Boolean(
        string="Is Baptized?",
    )

    is_confirmed = fields.Boolean(
        string="Is Confirmed?",
    )

    is_received = fields.Boolean(
        string="Is Received?",
    )
    religious_background = fields.Char(
        "Religious Background",
    )

    first_q_details = fields.Char(
        "What is your main problem as you see it? (why are you here?)",
    )

    second_q_details = fields.Char(
        "What have you done about it?",
    )
    third_q_details = fields.Char(
        "What can we do",
    )
    fourth_q_details = fields.Char(
        "Describe your spouse’s or fiancé in a few words",
    )
    fifth_q_details = fields.Char(
        "Describe yourself in a few words",
    )
    spouse_name = fields.Char(
        "Spouse Of Name",
    )
    spouse_address = fields.Char(
        "Address",
    )

    spouse_phone = fields.Char(
        "Phone",
    )
    spouse_occupation = fields.Char(
        "Occupation",
    )
    spouse_mobile = fields.Char(
        "Mobile",
    )
    spouse_dom = fields.Char(
        "Date of Marriage",
    )
    broken_by_divorce = fields.Char(
        "Broken by divorce",
    )
    death = fields.Char(
        "Death",
    )
    partner_signature = fields.Binary(
        "Signature",
        attachment=False,
        store=True,
        readonly=True,
    )

    the_captain_ids = fields.One2many(
        'the.captain',
        "captain_partner_id",
        string="The Captain",
    )

    the_social_director_ids = fields.One2many(
        'the.social.director',
        "social_director_partner_id",
        string="The Social Director",
    )
    the_steward_ids = fields.One2many(
        'the.steward',
        "steward_partner_id",
        string="The Steward",
    )
    the_navigator_ids = fields.One2many(
        'the.navigator',
        "navigator_partner_id",
        string="The Navigator",
    )

    children_details_ids = fields.One2many(
        'partner.children.details',
        "partner_children_partner_id",
        string="Children",
    )
    is_content = fields.Boolean(
        string="Is Content?",
        default=False,
        store=True
    )



    def action_send_mail(self):
        for rec in self:
            if not rec.email:
                raise UserError("Add Email Befor Send Mail!")

            partner_id = str(rec.id)
            id_bytes = partner_id.encode("ascii")
            base64_bytes = base64.b64encode(id_bytes)
            id_encoded = base64_bytes.decode("ascii")
            url = self.get_base_url() + "/customer-verification/%s" % id_encoded
            ctx = {
                'url': url
            }
            template_id = self.env.ref('de_charity_portal.customer_verification_send_mail_template')
            template_id.with_context(ctx).send_mail(rec.id, force_send=True)
