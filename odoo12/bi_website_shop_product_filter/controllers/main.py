# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
from werkzeug.exceptions import Forbidden, NotFound
from operator import itemgetter

from odoo import fields, http, tools, _
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.tools import groupby as groupbyelem
from odoo.exceptions import ValidationError
from odoo.addons.website.controllers.main import Website
from odoo.addons.sale.controllers.product_configurator import ProductConfiguratorController
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.osv import expression

_logger = logging.getLogger(__name__)


PPG = 9  # Products Per Page
PPR = 4  # Products Per Row


class TableCompute(object):

	def __init__(self):
		self.table = {}

	def _check_place(self, posx, posy, sizex, sizey):
		res = True
		for y in range(sizey):
			for x in range(sizex):
				if posx + x >= PPR:
					res = False
					break
				row = self.table.setdefault(posy + y, {})
				if row.setdefault(posx + x) is not None:
					res = False
					break
			for x in range(PPR):
				self.table[posy + y].setdefault(x, None)
		return res

	def process(self, products, ppg=PPG):
		# Compute products positions on the grid
		minpos = 0
		index = 0
		maxy = 0
		x = 0
		for p in products:
			x = min(max(p.website_size_x, 1), PPR)
			y = min(max(p.website_size_y, 1), PPR)
			if index >= ppg:
				x = y = 1

			pos = minpos
			while not self._check_place(pos % PPR, pos // PPR, x, y):
				pos += 1

			if index >= ppg and ((pos + 1.0) // PPR) > maxy:
				break

			if x == 1 and y == 1:   # simple heuristic for CPU optimization
				minpos = pos // PPR

			for y2 in range(y):
				for x2 in range(x):
					self.table[(pos // PPR) + y2][(pos % PPR) + x2] = False
			self.table[pos // PPR][pos % PPR] = {
				'product': p, 'x': x, 'y': y,
				'class': " ".join(x.html_class for x in p.website_style_ids if x.html_class)
			}
			if index <= ppg:
				maxy = max(maxy, y + (pos // PPR))
			index += 1

		# Format table according to HTML needs
		rows = sorted(self.table.items())
		rows = [r[1] for r in rows]
		for col in range(len(rows)):
			cols = sorted(rows[col].items())
			x += len(cols)
			rows[col] = [r[1] for r in cols if r[1]]

		return rows


class WebsiteSale(ProductConfiguratorController):


	def _get_search_domain(self, search, category, attrib_values, filter_values):
		domain = request.website.sale_product_domain()
		if search:
			for srch in search.split(" "):
				domain += [
					'|', '|', '|', ('name', 'ilike', srch), ('description', 'ilike', srch),
					('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]

		if category:
			domain += [('public_categ_ids', 'child_of', int(category))]

		if attrib_values:
			attrib = None
			ids = []
			for value in attrib_values:
				if not attrib:
					attrib = value[0]
					ids.append(value[1])
				elif value[0] == attrib:
					ids.append(value[1])
				else:
					domain += [('attribute_line_ids.value_ids', 'in', ids)]
					attrib = value[0]
					ids = [value[1]]
			if attrib:
				domain += [('attribute_line_ids.value_ids', 'in', ids)]


		if filter_values:
			filter = None
			ids = []
			for value in filter_values:
				if not filter:
					filter = value[0]
					ids.append(value[1])
				elif value[0] == filter:
					ids.append(value[1])
				else:
					domain += [('filter_ids.filter_value_ids', 'in', ids)]
					filter = value[0]
					ids = [value[1]]
			if filter:
				domain += [('filter_ids.filter_value_ids', 'in', ids)]

		return domain




	@http.route([
		'''/shop''',
		'''/shop/page/<int:page>''',
		'''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>''',
		'''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>/page/<int:page>'''
	], type='http', auth="public", website=True)
	def shop(self, page=0, category=None, search='', ppg=False, **post):
		add_qty = int(post.get('add_qty', 1))
		if category:
			category = request.env['product.public.category'].search([('id', '=', int(category))], limit=1)
			if not category or not category.can_access_from_current_website():
				raise NotFound()

		if ppg:
			try:
				ppg = int(ppg)
			except ValueError:
				ppg = PPG
			post["ppg"] = ppg
		else:
			ppg = PPG

		attrib_list = request.httprequest.args.getlist('attrib')
		attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
		attributes_ids = {v[0] for v in attrib_values}
		attrib_set = {v[1] for v in attrib_values}

		filter_list = request.httprequest.args.getlist('filter')
		
		filter_values = [[int(x) for x in v.split("-")] for v in filter_list if v]
		filter_ids = {v[0] for v in filter_values}
		filter_set = {v[1] for v in filter_values}
		
		domain = self._get_search_domain(search, category, attrib_values, filter_values)
		
		keep = QueryURL('/shop', category=category and int(category), search=search, filter=filter_list, attrib=attrib_list, order=post.get('order'))

		pricelist_context, pricelist = self._get_pricelist_context()

		request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

		url = "/shop"
		if search:
			post["search"] = search
		if attrib_list:
			post['attrib'] = attrib_list
		if filter_list:
			post['filter'] = filter_list



		Product = request.env['product.template'].with_context(bin_size=True)

		Category = request.env['product.public.category']
		search_categories = False
		if search:
			categories = Product.search(domain).mapped('public_categ_ids')
			search_categories = Category.search([('id', 'parent_of', categories.ids)] + request.website.website_domain())
			categs = search_categories.filtered(lambda c: not c.parent_id)
		else:
			categs = Category.search([('parent_id', '=', False)] + request.website.website_domain())

		parent_category_ids = []
		if category:
			url = "/shop/category/%s" % slug(category)
			parent_category_ids = [category.id]
			current_category = category
			while current_category.parent_id:
				parent_category_ids.append(current_category.parent_id.id)
				current_category = current_category.parent_id

		product_count = Product.search_count(domain)
		pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
		products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))
		
		ProductAttribute = request.env['product.attribute']
		ProductFilter = request.env['product.filter']
		if products:
			# get all products without limit
			selected_products = Product.search(domain, limit=False)
			attributes = ProductAttribute.search([('attribute_line_ids.value_ids', '!=', False), ('attribute_line_ids.product_tmpl_id', 'in', selected_products.ids)])
		else:
			attributes = ProductAttribute.browse(attributes_ids)

		filters = grouped_tasks = None
		
		
		if products:
			# get all products without limit
			selected_products = Product.search(domain, limit=False)
			
			filters = ProductFilter.search([('filter_value_ids', '!=', False), ('filter_ids.product_tmpl_id', 'in', selected_products.ids)])
			
		else:
			filters = ProductFilter.browse(filter_ids)
		
		
		compute_currency = self._get_compute_currency(pricelist, products[:1])

		filter_group = request.env['group.filter'].search([])
		
		applied_filter = False
		if filter_values:
			applied_filter = True

		if filter_group:
			grouped_tasks = [request.env['product.filter'].concat(*g) for k, g in groupbyelem(filters, itemgetter('group_id'))]
		else:
			grouped_tasks = [filters]

		prods  = Product.sudo().search(domain)
		request.website.sudo().get_dynamic_count(prods)

		values = {
			'search': search,
			'category': category,
			'attrib_values': attrib_values,
			'filter_set': filter_set,
			'filter_values': filter_values,
			'attrib_set': attrib_set,
			'pager': pager,
			'pricelist': pricelist,
			'grouped_tasks':grouped_tasks,
			'add_qty': add_qty,
			'products': products,
			'search_count': product_count,  # common for all searchbox
			'bins': TableCompute().process(products, ppg),
			'rows': PPR,
			'categories': categs,
			'attributes': attributes,
			'filters': filters,
			'compute_currency': compute_currency,
			'keep': keep,
			'filter_group' : filter_group,
			'parent_category_ids': parent_category_ids,
			'search_categories_ids': search_categories and search_categories.ids,
		}
		if category:
			values['main_object'] = category
		return request.render("website_sale.products", values)