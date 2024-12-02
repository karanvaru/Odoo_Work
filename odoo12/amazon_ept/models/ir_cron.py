from odoo import models, fields, _


class IrCron(models.Model):
    _inherit = 'ir.cron'

    amazon_seller_cron_id = fields.Many2one('amazon.seller.ept', string="Cron Scheduler")
