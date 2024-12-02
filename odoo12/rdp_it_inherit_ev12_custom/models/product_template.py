from odoo import models, fields, api
from lxml import etree
import logging
import urllib.parse
from docutils import nodes


_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(track_visibility='always')
    categ_id = fields.Many2one('product.category', track_visibility='always')
    tracking = fields.Selection(track_visibility='always')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        _logger.info("fields_view_get called for view_id=%s ================ , view_type=%s", view_id, view_type)
        result = super(ProductTemplate, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                              submenu=submenu)

        user = self.env.user
        _logger.info("Current user: %s (admin: %s)", user.login, user.has_group('base.group_system'))

        if not user.has_group('base.group_system'):
            _logger.info("User is not admin, applying read-only restrictions.=======================")
            doc = etree.XML(result['arch'])
            for node in doc.xpath("//field"):
                node.set('readonly', '1')
            result['arch'] = etree.tostring(doc, encoding='unicode')
            _logger.info("Read-only restrictions applied to the view.==========================")
        else:
            _logger.info("User is admin, no read-only restrictions applied.========================")

        return result
