from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError


class ResConfigSettingsReddont(models.TransientModel):
    _inherit = 'res.config.settings'

    group_stock_bill_of_entry_one_shipment = fields.Boolean("Bill of Entry Number",  config_parameter='reddot_wms.boe_shipment',
                                                            implied_group='reddot_wms'
                                                                          '.group_stock_bill_of_entry_one_shipment',
                                                            group="base.group_user,base.group_portal")