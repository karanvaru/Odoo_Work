# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    optional_product_ids = fields.Many2many(
        'product.template', 'sh_product_optional_rel', 'sh_product_tmpl_id', 'sh_optional_product_tmpl_id', string='Optional Products')
    vehicle_oem_lines = fields.One2many(
        'sh.vehicle.oem', 'product_id', string='Vehicle OEM Lines', copy=True)
    specification_lines = fields.One2many(
        'sh.product.specification', 'product_id', string='Specification Lines', copy=True)


    @api.model
    def _get_type_list(self):
        """
            METHOD BY SOFTHEALER
            to get product type list
        """
        type_list = self.env['motorcycle.type'].sudo().search_read(
            domain=[],
            fields=['id', 'name'],
            order="id asc",
        )
        return type_list or []

    @api.model
    def _get_make_list(self, type_id=None):
        """
            METHOD BY SOFTHEALER
            to get product make list
        """
        make_list = []
        if type_id not in ('', "", None, False):
            if type_id != int:
                type_id = int(type_id)
            search_make_list = self.env['motorcycle.mmodel'].sudo().search_read(
                domain=[('type_id', '=', type_id)],
                fields=['make_id'],
                order="name asc",
            )
            make_dic = {}
            if search_make_list:
                for item_dic in search_make_list:
                    make_tuple = item_dic.get('make_id', False)
                    if make_tuple:
                        make_dic.update(
                            {make_tuple[0]: {'id': make_tuple[0], 'name': make_tuple[1]}})

            if make_dic:
                for key, value in sorted(make_dic.items(), key=lambda kv: kv[1]['name']):
                    make_list.append(value)
        return make_list or []

    @api.model
    def _get_model_list(self, type_id=None, make_id=None):
        """
            METHOD BY SOFTHEALER
            to get product model list
        """
        model_list = []
        if (
            type_id not in ('', "", None, False) and
            make_id not in ('', "", None, False)
        ):
            if type_id != int:
                type_id = int(type_id)
            if make_id != int:
                make_id = int(make_id)
            model_list = self.env['motorcycle.mmodel'].sudo().search_read(
                domain=[
                    ('make_id', '=', make_id),
                    ('type_id', '=', type_id),
                ],
                fields=['id', 'name'],
                order="name asc",
            )
        return model_list or []

    @api.model
    def _get_year_list(self, type_id=None, make_id=None, model_id=None):
        """
            METHOD BY SOFTHEALER
            to get product year list
        """
        year_list = []
        if (
            type_id not in ('', "", None, False) and
            make_id not in ('', "", None, False) and
            model_id not in ('', "", None, False)
        ):
            if type_id != int:
                type_id = int(type_id)
            if make_id != int:
                make_id = int(make_id)
            if model_id != int:
                model_id = int(model_id)
            vehicles = self.env['motorcycle.motorcycle'].sudo().search([
                ('type_id', '=', type_id),
                ('make_id', '=', make_id),
                ('mmodel_id', '=', model_id),
            ]
            )
            if vehicles:
                year_list_ruff = []
                for vehicle in vehicles:
                    if vehicle.year_id:
                        year_list_ruff.append(vehicle.year_id.name)
                    if vehicle.end_year_id:
                        year_list_ruff.append(vehicle.end_year_id.name)
                if year_list_ruff:
                    min_year = min(year_list_ruff)
                    max_year = max(year_list_ruff)
                    for year in range(min_year, max_year+1):
                        year_list.append(year)
        return year_list or []

    @api.model
    def _search_get_detail(self, website, order, options):
        """
            INHERITED BY SOFTHEALER
            ==> In order to add vehicle domain in base_domain and return
                - motorcycle_heading,
                - motorcycle_type,
                - motorcycle_make
                - motorcycle_model
                - motorcycle_year
                - type_list
                - make_list
                - model_list
                - year_list

        """

        result = super(ProductTemplate, self)._search_get_detail(
            website, order, options)
        base_domain = result.get('base_domain', [])
        keep_vehicle = True
        category = options.get('category')
        min_price = options.get('min_price')
        max_price = options.get('max_price')
        attrib_values = options.get('attrib_values')
        if website:
            if category and website.sh_do_not_consider_vehicle_over_category:
                keep_vehicle = False

            if attrib_values and website.sh_do_not_consider_vehicle_over_attribute:
                keep_vehicle = False

            if min_price or max_price:
                if website.sh_do_not_consider_vehicle_over_price:
                    keep_vehicle = False

        # --------------------------------------------------------------------
        # softhealer custom code start here
        # --------------------------------------------------------------------
        base_domain = base_domain or []
        motorcycle_heading = False
        type_id = False
        make_id = False
        mmodel_id = False
        year_id = False

        type_list = []
        make_list = []
        model_list = []
        year_list = []

        search_motorcycles = False
        if (
            keep_vehicle and
            options and
            options.get('type', False) and
            options.get('make', False) and
            options.get('model', False) and
            options.get('year', False)
        ):

            type_id = options.get('type')
            make_id = options.get('make')
            mmodel_id = options.get('model')
            year_id = options.get('year')

            try:
                if type(type_id) != int:
                    type_id = int(type_id)
                if type(make_id) != int:
                    make_id = int(make_id)
                if type(mmodel_id) != int:
                    mmodel_id = int(mmodel_id)
                if type(year_id) != int:
                    year_id = int(year_id)

                vehicle_domain = [
                    ('type_id', '=', type_id),
                    ('make_id', '=', make_id),
                    ('mmodel_id', '=', mmodel_id),
                    ('year_id.name', '<=', year_id),
                    ('end_year_id.name', '>=', year_id),
                ]
                search_motorcycles = self.env[
                    'motorcycle.motorcycle'
                ].sudo().search(vehicle_domain)

                # =========================================================
                # Type, Make, Model, Year selected when page refresh.

                type_list = self._get_type_list()
                make_list = self._get_make_list(type_id)
                model_list = self._get_model_list(type_id, make_id)
                year_list = self._get_year_list(type_id, make_id, mmodel_id)

                # =========================================================

            except ValueError:
                pass

            product_tmpl_id_list = []
            is_compute_vehicle_name = True
            if search_motorcycles:
                for motorcycle in search_motorcycles:
                    if is_compute_vehicle_name:
                        # VEHICLE NAME
                        vehicle_name = ''
                        if motorcycle.make_id:
                            vehicle_name += motorcycle.make_id.name + ' '
                        if motorcycle.mmodel_id:
                            vehicle_name += motorcycle.mmodel_id.name + ' '
                        if motorcycle.year_id:
                            vehicle_name += str(year_id)
                        if vehicle_name == '':
                            vehicle_name = False
                        motorcycle_heading = vehicle_name
                        # VEHICLE NAME
                        is_compute_vehicle_name = False

                    if motorcycle.product_ids:
                        for product in motorcycle.product_ids:
                            if product.product_tmpl_id:
                                product_tmpl_id_list.append(
                                    product.product_tmpl_id.id)

                # ------------------
                # Universal Products
                universal_products = self.env['product.product'].search([
                    ('sh_is_common_product', '=', True)
                ])

                product_tmpl_id_list += universal_products.mapped(
                    'product_tmpl_id').ids
                # ------------------
                # Universal Products
            base_domain.append([('id', 'in', product_tmpl_id_list)])

        result.update({'base_domain': base_domain})
        result.update({
            'motorcycle_heading': motorcycle_heading,
            'motorcycle_type': type_id,
            'motorcycle_make': make_id,
            'motorcycle_model': mmodel_id,
            'motorcycle_year': year_id,
            'type_list': type_list,
            'make_list': make_list,
            'model_list': model_list,
            'year_list': year_list,
        })
        # --------------------------------------------------------------------
        # softhealer custom code ends here
        # --------------------------------------------------------------------

        # BRAND
        list_sh_shop_product_brands = options.get(
            'list_sh_shop_product_brands', [])
        if list_sh_shop_product_brands:
            base_domain.append(
                [('product_variant_ids.brand', 'in', list_sh_shop_product_brands)])
            result.update({'base_domain': base_domain})

        # COUNTRY
        list_sh_shop_product_made_in = options.get(
            'list_sh_shop_product_made_in', [])
        if list_sh_shop_product_made_in:
            base_domain.append(
                [('product_variant_ids.made_in', 'in', list_sh_shop_product_made_in)])
            result.update({'base_domain': base_domain})

        # GARDE
        list_sh_shop_product_garde = options.get(
            'list_sh_shop_product_garde', [])
        if list_sh_shop_product_garde:
            base_domain.append(
                [('product_variant_ids.garde', 'in', list_sh_shop_product_garde)])
            result.update({'base_domain': base_domain})

        # TRANSMISSION
        list_sh_shop_product_transmission = options.get(
            'list_sh_shop_product_transmission', [])
        if list_sh_shop_product_transmission:
            base_domain.append(
                [('product_variant_ids.transmission_ids', 'in', list_sh_shop_product_transmission)])
            result.update({'base_domain': base_domain})

        # ENGINE
        list_sh_shop_product_engine = options.get(
            'list_sh_shop_product_engine', [])
        if list_sh_shop_product_engine:
            base_domain.append(
                [('product_variant_ids.engine', 'in', list_sh_shop_product_engine)])
            result.update({'base_domain': base_domain})

        # PRODUCT TYPE
        list_sh_shop_product_p_type = options.get(
            'list_sh_shop_product_p_type', [])
        if list_sh_shop_product_p_type:
            base_domain.append(
                [('product_variant_ids.product_type', 'in', list_sh_shop_product_p_type)])
            result.update({'base_domain': base_domain})

        return result


class ProductProduct(models.Model):
    _inherit = "product.product"

    motorcycle_ids = fields.Many2many(
        'motorcycle.motorcycle',
        'product_product_motorcycle_motorcycle_rel',
        'product_id', 'motorcycle_id',
        string='Vehicle', copy=True
    )

    sh_is_common_product = fields.Boolean(string="Common Products?")
    garde = fields.Many2many(comodel_name='motorcycle.garde', string='Grade')
    engine = fields.Many2many(
        comodel_name='motorcycle.engine', string='Engine')
    product_type = fields.Many2many(
        comodel_name='motorcycle.product.type', string='Vehicle Product Type')
    brand = fields.Many2one(comodel_name='motorcycle.brand', string='Brand')
    made_in = fields.Many2one(comodel_name='res.country', string='Made In')
    transmission_ids = fields.Many2many(
        comodel_name='motorcycle.transmission', string='Transmission')

    @api.onchange('sh_is_common_product')
    def onchange_sh_is_common_product(self):
        if self:
            for record in self:
                if record.sh_is_common_product:
                    record.motorcycle_ids = False
