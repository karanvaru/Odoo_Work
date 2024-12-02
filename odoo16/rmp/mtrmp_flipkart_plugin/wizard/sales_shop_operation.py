# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AttachmentUpdateWizardExtend(models.TransientModel):
    _inherit = "sales.shop.operation"

    def import_sale_orders(self):
        shop_id = self.shop_id
        if shop_id and shop_id.is_api_connection:
            flipkart = shop_id.connect_in_flipkart()
            self.get_flipkart_order(flipkart, shop_id)
            return True
        return super(AttachmentUpdateWizardExtend, self).import_sale_orders()

    def get_flipkart_order(self, flipkart, shop_id):
        sale_order_obj = self.env['sale.order']
        try:
            response = flipkart.search_orders(filters={'states': ['Approved']})
        except Exception as error:
            raise UserError(error)
        if response:
            for item_data in response.items:
                sale_order = sale_order_obj.search_existing_flipkart_order(item_data, shop_id)
                if not sale_order:
                    sale_order_obj.create_flipkart_order_from_api(shop_id, item_data)
                    self._cr.commit()
        return True
