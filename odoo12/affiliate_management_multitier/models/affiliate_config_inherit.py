import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models


class AffiliateConfigurationInherit(models.TransientModel):

    _inherit = 'res.config.settings'


    benefit_text = fields.Html(String="Benefit Text")



    @api.multi
    def set_values(self):
        super(AffiliateConfigurationInherit, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings', 'benefit_text', self.benefit_text)

    @api.model
    def get_values(self):
        res = super(AffiliateConfigurationInherit, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update(
            benefit_text = IrDefault.get('res.config.settings', 'benefit_text') or "<p>As being an Affiliate of us, you'll receive:</p><ul><li><p>Commission of $10* on every qualifying sale that takes place via your Affiliate link.</p></li><li><p>Commission of 10%* on sale value when anyone else joins our Affiliate Program via your referral link/code and further his/her user makes any purchase by clicking the Affiliate link.</p></li></ul>",
        )
        return res

    def get_default_benefits_values(self, fields=None):
        res={}
        IrDefault = self.env['ir.default'].sudo()
        res.update(
            benefit_text = IrDefault.get('res.config.settings',
                                       'benefit_text') or "<p>As being an Affiliate of us, you'll receive:</p><ul><li><p>Commission of $10* on every qualifying sale that takes place via your Affiliate link.</p></li><li><p>Commission of 10%* on sale value when anyone else joins our Affiliate Program via your referral link/code and further his/her user makes any purchase by clicking the Affiliate link.</p></li></ul>",
        )
        return res
