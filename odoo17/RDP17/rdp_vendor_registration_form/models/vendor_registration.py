from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class VendorRegistrationForm(models.Model):
    _inherit = 'res.partner'

    # Company Info fields -----------

    vat = fields.Char(string='GSTIN')
    website = fields.Char(string='website')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')

    company_profile = fields.Binary(
        string="Company Profile"
    )
    company_profile_name = fields.Char(
        string="Company Profile Name"
    )
    company_registration_certificate = fields.Binary(
        string="Company Registration Certificate"
    )
    company_registration_certificate_name = fields.Char(
        string="Company Registration Certificate Name"
    )
    product_road_map = fields.Binary(
        string="Product Road Map"
    )
    product_road_map_name = fields.Char(
        string="Product Road Map Name"
    )
    quality_control_document = fields.Binary(
        string="Quality Control Document"
    )
    quality_control_document_name = fields.Char(
        string="Quality Control Document Name"
    )
    established_in = fields.Date(
        string="Established In"
    )
    revenue_category = fields.Selection([
        ('rev_less_1_cr', 'Less than 1 Crore'),
        ('rev_1_to_5', '1 to 5 Crores'),
        ('rev_5_to_25', '5 to 25 Crores'),
        ('rev_25_to_100', '25 to 100 Crores'),
        ('rev_100_to_250', '100 to 250 Crores'),
        ('rev_250_to_1000', '250 to 1000 Crores'),
        ('rev_1000_plus', '1000+ Crores'),
    ],
        string="Revenue Category",
    )
    last_2_year_avg_revenue = fields.Char(
        string="Last 2 year Avg Revenue(in Crores)"
    )
    social_contact = fields.Char(
        string="Social Contact"
    )
    company_logo = fields.Binary(
        string="Company Logo"
    )
    company_logo_name = fields.Char(
        string="Company Logo Name"
    )
    vendor_type = fields.Selection([
        ('manufacturer', 'Manufacturer'),
        ('trader', 'Trader'),
        ('manufacturer_trader', 'Manufacturer/Trader'),
        ('other', 'Other'),
    ],
        string="Vendor Type",
    )
    major_suppliers_of_product_components = fields.Char(
        string="Major Suppliers of Product/Components"
    )
    top_5_customers_for_reference = fields.Char(
        string="Top 5 Customers For Reference"
    )
    services = fields.Char(
        string="services"
    )

    @api.constrains('phone','mobile')
    def _check_valid_mobile_phone_number(self):
        if self.phone:
            if len(self.phone) != 10:
                raise ValidationError("Phone Number Must Be 10 Digits")
        if self.mobile:
            if len(self.mobile) != 10:
                raise ValidationError("Mobile Number Must Be 10 Digits")

    @api.constrains()
    def _check_valid_fields(self):
        for record in self:
            # Get all fields of the model
            fields_to_check = self._fields.keys()
            for field_name in fields_to_check:
                field_value = getattr(record, field_name)
                # if field_name == 'vat' and field_value:
                #     if len(field_value) != 15:
                #         raise ValidationError("GSTIN must be 15 characters long")
                #     # GSTIN format validation (XXAAAB1234C5Z6)
                #     if not re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9A-Z]{1}[Z]{1}$', field_value):
                #         raise ValidationError("Invalid GSTIN format")

                # Validation for Website    
                if field_name == 'website' and field_value:
                    if not field_value.startswith('http://') and not field_value.startswith('https://'):
                        raise ValidationError("Website must start with http:// or https://")
                    # Website format validation (using regular expression)
                    if not re.match(r'^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,})$', field_value):
                        raise ValidationError("Invalid website URL format")
                    

                # Validation for Email Format
                elif field_name == 'email' and field_value:
                    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', field_value):
                        raise ValidationError("Invalid email format")
                    # Email Domain Validation
                    domain = field_value.split('@')[1]
                    if not re.match(r'^[a-zA-Z0-9.-]+$', domain):
                        raise ValidationError("Invalid characters in email domain")

                    # Email TLD (Top-Level Domain) Validation
                    tld = domain.split('.')[-1]
                    if not re.match(r'^[a-zA-Z]{2,}$', tld):
                        raise ValidationError("Invalid top-level domain in email address")

                elif (field_name == 'mobile' or field_name == 'phone') and field_value and record.phone:
                    # Validation for Phone Number Length
                    if len(field_value) != 10:
                        raise ValidationError("Mobile number must be 10 digits long")
                    # Validation for Phone Number Format
                    if not re.match(r'^\d{10}$', field_value):
                        raise ValidationError("Invalid mobile number format")
                    # Validation for Repeating Digits in Phone Number
                    if all(char == field_value[0] for char in field_value):
                        raise ValidationError("Mobile number cannot contain all the same digits")
                    
