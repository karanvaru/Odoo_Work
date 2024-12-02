from odoo import models, fields, api


class StudentDetails(models.Model):
    _inherit = 'res.partner'

    gem_revenue_percent_of_total_revenue = fields.Selection([
        ('less_than_10_percent', 'Less than 10%'),
        ('10_percent_plus', '10% +'),
        ('20_percent_plus', '20% +'),
        ('30_percent_plus', '30% +'),
        ('40_percent_plus', '40% +'),
        ('50_percent_plus', '50% +'),
        ('60_percent_plus', '60% +'),
        ('70_percent_plus', '70% +'),
        ('80_percent_plus', '80% +'),
        ('90_percent_plus', '90% +'),
        ('100_percent', '100%')
    ], string="GeM Revenue % Of His Total Revenue", track_visibility='onchange')
    govt_revenue_percent_of_total_revenue = fields.Selection([
        ('less_than_10_percent', 'Less than 10%'),
        ('10_percent_plus', '10% +'),
        ('20_percent_plus', '20% +'),
        ('30_percent_plus', '30% +'),
        ('40_percent_plus', '40% +'),
        ('50_percent_plus', '50% +'),
        ('60_percent_plus', '60% +'),
        ('70_percent_plus', '70% +'),
        ('80_percent_plus', '80% +'),
        ('90_percent_plus', '90% +'),
        ('100_percent', '100%')
    ], string="Govt Revenue % Of His Total Revenue", track_visibility='onchange')
    brands_working_for_grm_and_govt_id = fields.Many2one('brands.working',
                                                         string="Brands He Is working With For GeM/Govt",
                                                         track_visibility='always')
    last_two_years_avg_revenue_in_gem = fields.Float(string="Last 2 years Avg Revenue In GeM",
                                                     track_visibility='always')
    last_two_years_avg_revenue_in_govt = fields.Float(string="Last 2 years Avg Revenue In Govt",
                                                      track_visibility='always')
    top_three_pet_accounts = fields.Char(string="Top 3 Pet Accounts (GBO's)", track_visibility='always')
    five_point_validation_by_rm = fields.Boolean(string="5P Validation By RM", track_visibility='always')
    five_point_validation_by_zm = fields.Boolean(string="5P Validation By ZM", track_visibility='always')
    five_point_validation_by_drt = fields.Boolean(string="5P Validation By DRT", track_visibility='always')
    five_point_validation_by_crh = fields.Boolean(string="5P Validation By CRH", track_visibility='always')
    five_point_validation_by_vp = fields.Boolean(string="5P Validation By VP", track_visibility='always')
    associated_supply_chain_id = fields.Many2one('associated.supply.chain',
                                                 string="Associated With Supply Chain Finance Companies",
                                                 track_visibility='always')
    approx = fields.Char(string="Approx Bank OD Limits", track_visibility='always')
    connects_with_fff = fields.Char(string="Connects With FFF (Family,Friends,Fool's)", track_visibility='always')
    cash_rich = fields.Char(string="Cash Rich", track_visibility='always')

    # new code
    partner_annual_turn_over = fields.Selection(
        [('alpa_five_to_twentyfive_cr', 'Alpha (5-25Cr)'),
         ('beta_zero_to_five_cr', 'Beta (0-5Cr)'),
         ('gamma_twentyfive_cr', 'Gamma (25Cr - 100Cr)'),
         ('club_hundred', 'Club 100 (100Cr - 500Cr)'),
         ('club_five_hundred', 'Club 500 (500Cr - 1000Cr)'),
         ('club_thousand', 'Club 1000 (1000Cr - 5000Cr)'),
         ('club_five_thousand', 'Club 5000 (5000Cr+)'),
         ('club_billion', 'Club Billion$ (8500Cr+)'),
         ('i_dont_know', "I don't Know")], string="Partner Annual Turnover",
        track_visibility='onchange')
    relationship_last_fy = fields.Selection(
        # [('titanium_five_cr_plus', 'Titanium (5Cr+)'),
        [('iridum_ten_cr_plus', 'Iridum (10Cr)'),
         ('titanium_five_minus_ten_cr_plus', 'Titanium (5Cr to 10Cr)'),
         ('platinum_two_cr', 'Platinum (2Cr to 5Cr)'),
         ('gold_fifty_l_two_cr', 'Gold (50L to 2Cr)'),
         ('silver_less_than_fifty_l', 'Silver (10L to 50L)'),
         ('nano_less_than_ten_l', 'Bronze (<10L)'),
         ('new_registration', 'New Registration')], string="Relationship Last FY", track_visibility='onchange')
    relationship_ptc = fields.Selection([
        # [('titanium_five_cr_plus', 'Titanium (5Cr+)'),
        ('iridum_ten_cr_plus', 'Iridum (10Cr)'),
        ('titanium_five_minus_ten_cr_plus', 'Titanium (5Cr to 10Cr)'),
        ('platinum_two_cr', 'Platinum (2Cr to 5Cr)'),
        ('gold_fifty_l_two_cr', 'Gold (50L to 2Cr)'),
        ('silver_less_than_fifty_l', 'Silver (10L to 50L)'),
        ('nano_less_than_ten_l', 'Bronze (<10L)')], string="Relationship PTC", track_visibility='onchange')
    code_status = fields.Selection(
        [('code_active', 'Code-Active'),
         ('code_deactivate', 'Code-Deactivate'),
         ('code_hold', 'Code-Queue'),
         ('Code_rejected', 'Code-Rejected'),
         ('other', 'Other')], string="Code Status", track_visibility='onchange')
    code_active_categories = fields.Many2many('active.category', string="Code-Active Categories", )
    golden_path = fields.Selection([('physical', 'Physical'),
                                    ('virtual', 'Virtual'),
                                    ('not_yet_any', 'Not Yet Any')
                                    ], string="Golden Path", track_visibility='onchange')
    partner_type = fields.Selection([('proactive', 'Proactive'),
                                     ('reactive', 'Reactive'),
                                     ('ad_hoc', 'Ad-hoc')], string="Partner Type", track_visibility='onchange')
    gen_partner_onboarding = fields.Selection([('received_lead_and_hunt', '(Step 0) Received Lead/Hunt'),
                                               ('documentation_done', '(Step 1) Documentation Done'),
                                               ('introductory_vc_done', '(Step 2) Introductory VC Done'),
                                               ('virtual_golden_path_done', '(Step 3) Virtual Golden Path Done'),
                                               ('code_active_done', '(Step 4) Code-active Done'),
                                               ('crm_training_by_kam', '(Step 5) CRM Training by KAM'),
                                               ('ready_to_role', '(Step 6) Ready to Role')],
                                              string="GeM 3.0 Partner Onboarding",
                                              track_visibility='onchange')
    additional_notes = fields.Text(string="Additional Notes", track_visibility='always')
    brands_working_with_id = fields.Many2one('brands.working', string="Brands Working With", track_visibility='always')
    pet_account_one_id = fields.Many2one('res.partner', string="Pet Account 1", track_visibility='always')
    pet_account_two_id = fields.Many2one('res.partner', string="Pet Account 2", track_visibility='always')
    pet_account_three_id = fields.Many2one('res.partner', string="Pet Account 3", track_visibility='always')
    partner_geography = fields.Selection([
        ('prefers_same_city', 'Prefers Same City'),
        ('prefers_same_state', 'Prefers Same State'),
        ('prefers_same_zone', 'Prefers Same Zone'),
        ('national_player', 'National Player'),
        ('international_player', 'International Player')], string="Partner Geography", track_visibility='onchange')
    gem_kyc_tags_ids = fields.Many2many('gem.kyc', string='GeM KYC Tags')
    working_brand_ids = fields.Many2many('brands.working', string='Brands Working With')
    otd_ots_priority = fields.Selection([
        ('vip_platinum', 'VIP Platinum'),
        ('gold', 'Gold'),
        ('general', 'General'),
    ], string="OTD & OTS Priority", track_visibility='onchange')
    supply_chain_finance_id = fields.Many2one('rdp.supply.chain.finance', string="Supply Chain Finance [SCF] With",
                                              track_visibility='always')
    total_scf_value = fields.Float('Total SCF Value', track_visibility='always')
    supply_chain_finance_ids = fields.Many2many('rdp.supply.chain.finance', string='Supply Chain Finance [SCF] With')
    low_hanging_fruit = fields.Selection([
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')], string="Low Hanging Fruit", track_visibility='onchange')
    r_ptc_performance = fields.Selection([
        ('on_track', 'On-Track'),
        ('on_track_*', 'On-Track*'),
        ('off_track', 'Off-Track'),
        ('other', 'Other')], string="R.PTC Performance", track_visibility='onchange')
    is_contacts_otd_ots_manager = fields.Boolean(compute='_compute_is_contact_manager')

    def _compute_is_contact_manager(self):
        group_contacts_manager = self.env.ref('rdp_contacts_inherited.group_contacts_otd_ots_manager')
        for record in self:
            record.is_contacts_otd_ots_manager = group_contacts_manager in self.env.user.groups_id



class GemKycTags(models.Model):
    _name = "gem.kyc"
    _description = 'gem.kyc.tags'

    name = fields.Char(string="Name")
    color = fields.Integer('Color')


class ActiveCategory(models.Model):
    _name = "active.category"
    _description = 'code.active.category'
    name = fields.Char(string="Name")


class AssociatedSupplyChain(models.Model):
    _name = "associated.supply.chain"
    _description = 'associate.supply.chain'

    name = fields.Char(string="Name")


class BrandsWorking(models.Model):
    _name = "brands.working"
    _description = 'brands.working'

    name = fields.Char(string="Name")
    color = fields.Integer('Color')


class SupplyChainFinance(models.Model):
    _name = "rdp.supply.chain.finance"
    _description = 'Supply Chain Finance'

    name = fields.Char(string="Name")
    # color = fields.Integer('Color')
