import base64
from csv import DictWriter
from io import StringIO
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, Warning


class amazon_prepare_product_wizard(models.TransientModel):
    _name = 'amazon.product.wizard'
    _description = 'amazon.product.wizard'

    instance_id = fields.Many2one("amazon.instance.ept", "Instance")
    amazon_product_ids = fields.Many2many('amazon.product.ept', 'amazon_product_copy_rel',
                                          'wizard_id', 'amazon_product_id', "Amazon Product")
    from_instance_id = fields.Many2one("amazon.instance.ept", "From Instance")
    to_instance_id = fields.Many2one("amazon.instance.ept", "To Instance")
    copy_all_products = fields.Boolean("Copy All Products", default=True)

    """Added field by Dhruvi [14-11-2018] for export product as csv"""
    datas = fields.Binary('File')
    
    fulfillment_by = fields.Selection(
        [('MFN', 'Manufacturer Fulfillment Network'), ('AFN', 'Amazon Fulfillment Network')],
        string="Fulfillment By", default='MFN')    

    @api.onchange("from_instance_id")
    def on_change_instance(self):
        for record in self:
            record.to_instance_id = False

    """Added method [export_products_to_csv,get_product_data]by Dhruvi [14-11-2018]
        To export product as csv"""

    @api.model
    def export_products_to_csv(self, product_ids=[]):
        buffer = StringIO()
        field_names = [
            'SKU',
            'Barcode',
            'Title',
            'Brand Name',
            'Manufacturer',
            'Product Description',
            'Main Image URL',
            'Search Keywords',
            'Bullet Point 1',
            'Bullet Point 2',
            'Bullet Point 3',
            'Bullet Point 4',
            'Bullet Point 5',
            'Size',
            'Color',
            'Price',
            'Quantity',
        ]
        # csvwriter = UnicodeDictWriter(buffer, field_names, delimiter='\t')
        csvwriter = DictWriter(buffer, field_names, delimiter='\t')
        csvwriter.writer.writerow(field_names)
        active_ids = self._context.get('active_ids', [])
        product_ids = self.env['amazon.product.ept'].browse(active_ids)
        for product in product_ids:
            data = self.get_product_data(product)
            csvwriter.writerow(data)
        filename = "%s_%s.csv" % ('Export_Amazon_Product', datetime.now())
        buffer.seek(0)
        file_data = buffer.read().encode("utf-8")
        rec = self.create({"datas": base64.encodestring(file_data)})
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=amazon.product.wizard&field=datas&id=%s&filename=%s' % (
            rec.id, filename),
            'target': 'self',
        }

    @api.multi
    def get_product_data(self, product):
        #         search_keywords=",".join(product.search_term_ids.mapped('name'))
        url = ''
        if product.product_id.ept_image_ids.ids:
            main_images = self.env['product.image.ept'].search(
                [('image_type', '=', 'Main'), ('id', 'in', product.product_id.ept_image_ids.ids)])

            if len(main_images) == 1:
                url = main_images.url

        bullent_point_dict = {}
        if product.bullet_point_ids.ids:
            count = 0
            for x in range(0, len(product.bullet_point_ids.ids)):
                bullent_point_dict.update({'bullet_point' + str(count): list(
                    reversed(product.bullet_point_ids.mapped('name')))[x]})
                count += 1
                if count > 5:
                    break
        return {'SKU': product.seller_sku,
                'Barcode': product.barcode or '',
                'Title': product.title or product.name or '',
                'Brand Name': product.brand or '',
                'Manufacturer': product.manufacturer or '',
                'Main Image URL': url or '',  # product.product_id.image.ept_image_ids  or
                'Product Description': product.description or product.name or '',
                'Search Keywords': product.search_term_ids and
                                   product.search_term_ids.mapped('name')[0] or '',
                'Bullet Point 1': bullent_point_dict.get('bullet_point0', ''),
                'Bullet Point 2': bullent_point_dict.get('bullet_point1', ''),
                'Bullet Point 3': bullent_point_dict.get('bullet_point2', ''),
                'Bullet Point 4': bullent_point_dict.get('bullet_point3', ''),
                'Bullet Point 5': bullent_point_dict.get('bullet_point4', ''),
                'Size': '',  # product or
                'Color': '',  # product.color or '',
                'Price': product.lst_price or '',  # round(product.lst_price,2)
                'Quantity': product.qty_available or '',

                }

    @api.multi
    def export_product_in_amazon(self):
        amazon_instance_obj = self.env['amazon.instance.ept']
        amazon_product_obj = self.env['amazon.product.ept']

        if self._context.get('key') == 'export_selective_products_in_amazon':
            amazon_instances = amazon_instance_obj.search([])
            active_ids = self._context.get('active_ids', [])
            for instance in amazon_instances:
                amazon_products = amazon_product_obj.search(
                    [('id', 'in', active_ids), ('instance_id', '=', instance.id)])
                if not amazon_products:
                    continue
                self.env['amazon.product.ept'].export_product_amazon(instance, amazon_products)
        return True

    @api.multi
    def prepare_product(self):
        template_obj = self.env['product.template']
        if self._context.get('key') == 'prepare_selective_product_for_export':
            template_ids = self._context.get('active_ids', [])
            templates = template_obj.browse(template_ids)
            for template in templates:
                if template.type == 'service':
                    continue
                odoo_products = template.product_variant_ids
                if len(template.product_variant_ids.ids) == 1:
                    odoo_product = template.product_variant_ids
                    self.create_or_update_amazon_product(odoo_product, template,
                                                         odoo_product.default_code,
                                                         template.description, False)
                else:
                    for odoo_product in odoo_products:
                        if odoo_product.is_amazon_virtual_variant:
                            continue
                        self.create_or_update_amazon_product(odoo_product, template,
                                                             odoo_product.default_code,
                                                             template.description, 'child')
        return True

    """This method prepare amazon product by product category for the export in amazon"""

    @api.multi
    def create_or_update_amazon_product(self, odoo_product, template, default_code, description,
                                        parentage):
        amazon_product_ept_obj = self.env['amazon.product.ept']
        amazon_attribute_line_obj = self.env['amazon.attribute.line.ept']
        amazon_attribute_value_obj = self.env['amazon.attribute.value.ept']
        domain = [('country_id', '=', self.instance_id.country_id.id)]
        odoo_product and domain.append(('odoo_category_id', '=', odoo_product.categ_id.id))
        """changes by Dhruvi condition is fetched according to seller wise."""
        vals = {
            'instance_id': self.instance_id.id,
            'product_id': odoo_product and odoo_product.id or False,
            'seller_sku': default_code or False,
            'condition': self.instance_id.seller_id.condition or 'New',
            'tax_code_id': self.instance_id.default_amazon_tax_code_id and
                           self.instance_id.default_amazon_tax_code_id.id or False,
            'long_description': description or False,
            'fulfillment_by': self.fulfillment_by or 'MFN',
            'variation_data': parentage
        }
        if not odoo_product:
            vals.update({'name': template.name, 'product_tmpl_id': template.id,
                         'default_code': default_code, 'is_amazon_virtual_variant': True})
        else:
            vals.update({'product_id': odoo_product.id})
            
#         amazon_product = odoo_product and amazon_product_ept_obj.search(
#             [('instance_id', '=', self.instance_id.id),
#              ('product_id', '=', odoo_product.id)]) or False
#         if amazon_product:
#             amazon_product.write(
#                 {'long_description': description or False, 'variation_data': parentage})
#         else:
#             amazon_product = amazon_product_ept_obj.create(vals)
            
        if parentage == 'parent':
            amazon_product = amazon_product_ept_obj.search(
                [('seller_sku', '=', default_code), ('instance_id', '=', self.instance_id.id),
                 ('fulfillment_by', '=', self.fulfillment_by)])
        else:
            amazon_product = odoo_product and amazon_product_ept_obj.search(
                [('instance_id', '=', self.instance_id.id), ('product_id', '=', odoo_product.id),
                 ('fulfillment_by', '=', self.fulfillment_by)]) or False
        if amazon_product:
            amazon_product.write(vals)
        else:
            amazon_product = amazon_product_ept_obj.create(vals)
            
        if odoo_product:
            for attribute_value in odoo_product.attribute_value_ids:
                if attribute_value.attribute_id.amazon_attribute_id:
                    amazon_attribute_line = amazon_attribute_line_obj.search(
                        [('product_id', '=', amazon_product.id), (
                        'attribute_id', '=', attribute_value.attribute_id.amazon_attribute_id.id)])
                    value = amazon_attribute_value_obj.search(
                        [('attribute_id', '=', attribute_value.attribute_id.amazon_attribute_id.id),
                         ('name', '=', attribute_value.name)], limit=1)
                    if not value:
                        value = amazon_attribute_value_obj.create(
                            {'attribute_id': attribute_value.attribute_id.amazon_attribute_id.id,
                             'name': attribute_value.name})
                    if amazon_attribute_line:
                        amazon_attribute_line.write({'value_ids': [(6, 0, value.ids)]})
                    else:
                        amazon_attribute_line_obj.create({'product_id': amazon_product.id,
                                                          'attribute_id': attribute_value.attribute_id.amazon_attribute_id.id,
                                                          'value_ids': [(6, 0, value.ids)]})
        return True

    @api.multi
    def copy_product(self):
        amazon_product_ept_obj = self.env['amazon.product.ept']
        from_instance = self.from_instance_id
        to_instance = self.to_instance_id
        odoo_product_ids = []
        amazon_products = []
        if self.copy_all_products:
            amazon_products = amazon_product_ept_obj.search(
                [('instance_id', '=', from_instance.id)])
            for amazon_product in amazon_products:
                amazon_product.product_id and odoo_product_ids.append(amazon_product.product_id.id)

        else:
            amazon_products = self.amazon_product_ids
            for amazon_product in amazon_products:
                amazon_product.product_id and odoo_product_ids.append(amazon_product.product_id.id)
        exist_products = amazon_product_ept_obj.search(
            [('instance_id', '=', to_instance.id), ('product_id', 'in', odoo_product_ids)])
        odoo_product_ids = []
        for amazon_product in exist_products:
            amazon_product.product_id and odoo_product_ids.append(amazon_product.product_id.id)
        for amazon_product in amazon_products:
            if amazon_product.product_id.id in odoo_product_ids:
                continue
            amazon_product.copy({'instance_id': to_instance.id})
        return True
    
    
    @api.multi
    def get_product_prep_instructions(self):
        amazon_instance_obj = self.env['amazon.instance.ept']
        amazon_product_obj = self.env['amazon.product.ept']

        if self._context.get('key') == 'get_product_prep_instructions':
            amazon_instances = amazon_instance_obj.search([])
            active_ids = self._context.get('active_ids', [])

            for instance in amazon_instances:
                amazon_products = amazon_product_obj.search(
                    [('id', 'in', active_ids), ('instance_id', '=', instance.id),
                     ('fulfillment_by', '=', 'AFN'), ('exported_to_amazon', '=', True)])
                amazon_products and amazon_product_obj.get_product_prep_instructions(instance,
                                                                                     amazon_products)
        return True    

    "This method is called based on condition when it is called from\
    product wizard it calls,'update_selective_image'(IF part)   \
    else it will call,update_categ_wise_image(ELIF part) if it is called from \
    product category wizard "

    @api.multi
    def update_image(self):
        amazon_product_obj = self.env['amazon.product.ept']
        amazon_instance_obj = self.env['amazon.instance.ept']

        if self._context.get('key', False) == 'update_selective_image':
            amazon_product_ids = self._context.get('active_ids', [])
            instances = amazon_instance_obj.search([('ept_product_ids', 'in', amazon_product_ids)])
            for instance in instances:
                amazon_products = amazon_product_obj.search(
                    [('instance_id', '=', instance.id), ('id', 'in', amazon_product_ids),
                     ('exported_to_amazon', '=', True)])
                amazon_products.update_images(instance)
                instance.write({'image_last_sync_on': datetime.now()})
        """Commented by Dhruvi [13-11-2018] as Browse node menu is made invisible"""
        # elif self._context.get('key', False) == 'update_categ_wise_image':
        # amazon_categ_ids = self._context.get('active_ids', [])
        # instances = amazon_instance_obj.search([])
        # for instance in instances:
        #     amazon_browse_categs = amazon_browse_node_obj.search(
        #         [('id', 'in', amazon_categ_ids), ('instance_id', '=', instance.id)])
        #     amazon_product_ids = []
        #     for amazon_browse_categ in amazon_browse_categs:
        #         amazon_products = amazon_product_obj.search(
        #             [('amazon_browse_node_id', '=', amazon_browse_categ.id),
        #              ('exported_to_amazon', '=', True)])
        #         amazon_product_ids += amazon_products.ids
        #     amazon_products = amazon_product_obj.browse(amazon_product_ids)
        #     amazon_products.update_images(instance)
        #     instance.write({'image_last_sync_on':datetime.now()})

        return True

    @api.multi
    def update_price(self):
        amazon_instance_obj = self.env['amazon.instance.ept']
        amazon_product_obj = self.env['amazon.product.ept']
#         amazon_browse_node_obj = self.env['amazon.browse.node.ept']

        if self._context.get('key', False) == 'update_selective_price':
            amazon_product_ids = self._context.get('active_ids', [])
            instances = amazon_instance_obj.search([('ept_product_ids', 'in', amazon_product_ids)])
            for instance in instances:
                amazon_products = amazon_product_obj.search(
                    [('instance_id', '=', instance.id), ('id', 'in', amazon_product_ids),
                     ('exported_to_amazon', '=', True)])
                amazon_products.update_price(instance)
        """Commented by Dhruvi [13-11-2018] as Browse node menu is made invisible"""
        # elif self._context.get('key', False) == 'update_categ_wise_price':
        # amazon_categ_ids = self._context.get('active_ids', [])
        # instances = amazon_instance_obj.search([])
        # for instance in instances:
        #     amazon_browse_categs = amazon_browse_node_obj.search(
        #         [('id', 'in', amazon_categ_ids), ('instance_id', '=', instance.id)])
        #     amazon_product_ids = []
        #     for amazon_browse_categ in amazon_browse_categs:
        #         amazon_products = amazon_product_obj.search(
        #             [('amazon_browse_node_id', '=', amazon_browse_categ.id),
        #              ('exported_to_amazon', '=', True)])
        #         amazon_product_ids += amazon_products.ids
        #     amazon_products = amazon_product_obj.browse(amazon_product_ids)
        #     amazon_products.update_price(instance)
        return True

    @api.multi
    def update_stock_ept(self):
        product_obj = self.env['amazon.product.ept']
        product_ids = self._context.get('active_ids')
        for instance in self.env['amazon.instance.ept'].search([]):
            products = product_obj.search(
                [('id', 'in', product_ids), ('instance_id', '=', instance.id),
                 ('fulfillment_by', '=', 'MFN')])
            products and product_obj.export_stock_levels(instance, products.ids)
        return True

    """This method is used to import category from amazon based on root category,\
    it checks if the category is root OR not child then it will import all the \
    child categories"""

