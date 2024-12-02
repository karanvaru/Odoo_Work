from odoo import api, fields, models, tools, _


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
    #     res = super().search_read(domain, fields, offset, limit, order, **read_kwargs)
    #     if self._context.get('web_domain_widget') and hasattr(self, 'company_id'):
    #         for rec in res:
    #             rec.update({'company_name': self.browse(rec.get('id')).company_id.name})

    #     return res
    
    @api.model
    def domain_search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        res = self.sudo().search_read(domain, ["id", "display_name"], offset, limit, order, **read_kwargs)
        return res
    
    @api.model
    def get_widget_count(self, args):
        return self.sudo().search_count(args)
