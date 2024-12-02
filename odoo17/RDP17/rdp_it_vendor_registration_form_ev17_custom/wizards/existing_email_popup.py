# models.py
from odoo import models, fields

class ContactExistsWizard(models.TransientModel):
    _name = 'contact.exists.wizard'
    _description = 'Contact Exists Wizard'

    message = fields.Text(string='Message', readonly=True)
