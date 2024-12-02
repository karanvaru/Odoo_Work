from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import html_translate


class ProductPublicCategory(models.Model):
    _name = "product.public.category"

    def _default_sequence(self):
        cat = self.search([], limit=1, order="sequence DESC")
        if cat:
            return cat.sequence + 5
        return 10000

    name = fields.Char(required=True, translate=True)
    parent_id = fields.Many2one('product.public.category', string='Parent Category', index=True, ondelete="cascade")
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('product.public.category', 'parent_id', string='Children Categories')
    parents_and_self = fields.Many2many('product.public.category', compute='_compute_parents_and_self')
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of product categories.", index=True,
                              default=_default_sequence)
    website_description = fields.Html('Category Description', sanitize_attributes=False, translate=html_translate,
                                      sanitize_form=False)
    product_tmpl_ids = fields.Many2many('product.template', relation='product_public_category_product_template_rel')

    @api.constrains('parent_id')
    def check_parent_id(self):
        if not self._check_recursion():
            raise UserError(_('Error ! You cannot create recursive categories.'))

    def name_get(self):
        res = []
        for category in self:
            res.append((category.id, " / ".join(category.parents_and_self.mapped('name'))))
        return res

    def _compute_parents_and_self(self):
        for category in self:
            if category.parent_path:
                category.parents_and_self = self.env['product.public.category'].browse(
                    [int(p) for p in category.parent_path.split('/')[:-1]])
            else:
                category.parents_and_self = category
