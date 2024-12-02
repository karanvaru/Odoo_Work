from odoo import fields, models, api
from odoo.exceptions import ValidationError


class HelpInquiry(models.Model):
    _name = 'help.inquiry'
    _description = 'Help Inquiry'
    _rec_name = 'customer_name'

    tag_ids = fields.Many2many(
        'product.tag',
        string='Product Tag',
        readonly=1
    )
    product_id = fields.Many2one(
        'product.product',
        'Product',
        readonly=1
    )
    customer_name = fields.Char(
        string="Name",
        readonly=1
    )
    customer_mobile = fields.Char(
        string='Mobile',
        readonly=1
    )

    customer_email = fields.Char(
        string="Email",
        readonly=1
    )

    def create_contact(self):
        contact = self.env['res.partner'].search([('mobile', '=', self.customer_mobile)])
        if contact:
            raise ValidationError("Contact Already exist")
        partner_id = self.env['res.partner'].create({
            'name': self.customer_name,
            'mobile': self.customer_mobile,
            'email': self.customer_email
        })
        action = self.env.ref('contacts.action_contacts').sudo().read([])[0]
        form_view = [(self.env.ref('base.view_partner_form').id, 'form')]

        action['views'] = form_view
        action['res_id'] = partner_id.id
        return action
