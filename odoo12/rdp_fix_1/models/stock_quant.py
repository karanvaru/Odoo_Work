from odoo import models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import config, float_compare
import logging

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    @api.constrains('product_id', 'quantity')
    def check_negative_qty(self):
        p = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')

        _logger.info("===================The P value is ==================== %s", p)
        check_negative_qty = (
            (config['test_enable'] and
             self.env.context.get('test_rdp_fix_1')) or
            not config['test_enable']
        )
        _logger.info("========================The nagative check================== %s", check_negative_qty)
        if not check_negative_qty:
            _logger.info("======================True====================")
            return
        for quant in self:
            _logger.info("====================The precision digit================== %s", float_compare(quant.quantity, 0, precision_digits=p) == -1)
            _logger.info("====================The product type================== %s", quant.product_id.type == 'product')
            _logger.info("====================The quant product================== %s", quant.product_id.allow_negative_stock)
            _logger.info("====================The quant product================== %s", quant.location_id.usage in ['internal', 'transit'])

            if (
                float_compare(quant.quantity, 0, precision_digits=p) == -1 and
                quant.product_id.type == 'product' and
                not quant.product_id.allow_negative_stock and
                not quant.product_id.categ_id.allow_negative_stock and
                quant.location_id.usage in ['internal', 'transit']
            ):
                msg_add = ''
                if quant.lot_id:
                    msg_add = _(" lot '%s'") % quant.lot_id.name_get()[0][1]
                raise ValidationError(_(
                    "You cannot validate this stock operation because the "
                    "stock level of the product '%s'%s would become negative "
                    "(%s) on the stock location '%s' and negative stock is "
                    "not allowed for this product.") % (
                        quant.product_id.name, msg_add, quant.quantity,
                        quant.location_id.complete_name))
