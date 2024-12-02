from odoo import models, fields, api

class CreatePartnerDeliveryAddress(models.TransientModel):
    _name = 'create.partner.delivery.address.ept'
    _description = 'Wizard to add new delivery partner'

    street = fields.Char()
    street2 = fields.Char()
    state_id = fields.Many2one('res.country.state', string='State', ondelete='restrict')
    city = fields.Char()
    zip = fields.Integer(change_default=True)
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    name = fields.Char(string="Contact Name")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    comment = fields.Char(string="Note")
    mobile = fields.Char(string="Mobile")

    
    @api.multi
    def create_new_contact_partner(self):
        """
        author:bhavesh jadav 6/4/2019
        func: this method use for create new contact partner and write new partner in RMA record delivery field
        :return:
        """
        rma_id = self._context.get('record')
        rma_id = self.env['crm.claim.ept'].browse(rma_id)
        partner_id = self._context.get("current_partner_id")
        is_contact_person = self._context.get("is_create_contact_person")
        value = {'street': self.street, 'street2': self.street2,
                 'state_id': self.state_id.id, 'city': self.city,
                 'zip': self.zip, 'country_id': self.country_id.id,
                 'name': self.name, 'phone': self.phone, 'email': self.email, 
                 'parent_id': partner_id}
        if is_contact_person:
            value.update({ 'type': 'contact'})
        else:
            value.update({'type': 'delivery'})
        new_partner_id = self.env['res.partner'].create(value)
        if is_contact_person:
            rma_id.write({'rma_support_person_id':new_partner_id.id})
        else:
            rma_id.write({'partner_delivery_id':new_partner_id.id})
        return True