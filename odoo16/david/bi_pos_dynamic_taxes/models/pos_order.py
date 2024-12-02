# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _, tools
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError


class PosOrder(models.Model):
	_inherit = 'pos.order'

	@api.model
	def _process_order(self, order, draft, existing_order):

		"""Create or update an pos.order from a given dictionary.

		:param dict order: dictionary representing the order.
		:param bool draft: Indicate that the pos_order is not validated yet.
		:param existing_order: order to be updated or False.
		:type existing_order: pos.order.
		:returns: id of created/updated pos.order
		:rtype: int
		"""
		order = order['data']
		pos_session = self.env['pos.session'].browse(order['pos_session_id'])
		if pos_session.state == 'closing_control' or pos_session.state == 'closed':
			order['pos_session_id'] = self._get_valid_session(order).id

		pos_order = False
		if not existing_order:
			pos_order = self.create(self._order_fields(order))
		else:
			pos_order = existing_order
			pos_order.lines.unlink()
			order['user_id'] = pos_order.user_id.id
			pos_order.write(self._order_fields(order))

		pos_order = pos_order.with_company(pos_order.company_id)
		self = self.with_company(pos_order.company_id)
		self._process_payment_lines(order, pos_order, pos_session, draft)

		if not draft:
			try:
				pos_order.action_pos_order_paid()
			except psycopg2.DatabaseError:
				# do not hide transactional errors, the order(s) won't be saved!
				raise
			except Exception as e:
				_logger.error('Could not fully process the POS Order: %s', tools.ustr(e))
			pos_order._create_order_picking()
			pos_order._compute_total_cost_in_real_time()

		line1 = order.get('lines')
		for line in pos_order.lines:
			for a in line1:
				if a[2].get('product_id'):
					if line.product_id.id == a[2].get('product_id'):
						if a[2].get('tax_id_include_base'):
							bi_taxes_id = a[2].get('tax_id_include_base')
							line.tax_ids = [(6, 0, bi_taxes_id)]
							line.tax_ids_after_fiscal_position = [(6, 0, bi_taxes_id)]

							
		if pos_order.to_invoice and pos_order.state == 'paid':
			pos_order._generate_pos_order_invoice()

		if pos_session._is_capture_system_activated():
			pos_session._remove_capture_content(order)
		return pos_order.id

	def _get_fields_for_order_line(self):
		fields = super(PosOrder, self)._get_fields_for_order_line()
		fields.extend(['tax_ids_after_fiscal_position','price_subtotal', 'price_subtotal_incl'])
		return fields

	def _prepare_order_line(self, order_line):
		"""Method that will allow the cleaning of values to send the correct information.
		:param order_line: order_line that will be cleaned.
		:type order_line: pos.order.line.
		:returns: dict -- dict representing the order line's values.
		"""
		order_line = super()._prepare_order_line(order_line)
		if(order_line.get('tax_ids_after_fiscal_position', False)):
			taxes = self.env["account.tax"].search_read([('id','in',order_line.get('tax_ids_after_fiscal_position'))], ['name'])
			taxes_name = ", ".join([x['name'] for x in taxes])
			order_line['all_tax'] = order_line.get('price_subtotal_incl', 0.0) - order_line.get('price_subtotal', 0.0)
			order_line['tax_id_include_base'] = [x['id'] for x in taxes]
			order_line['tax_ids_after_fiscal_position'] = taxes_name
		return order_line


class PosOrderLine(models.Model):
	_inherit = 'pos.order.line'


	def _export_for_ui(self, orderline):
		result = super()._export_for_ui(orderline)
		result['tax_ids_after_fiscal_position'] = orderline.tax_ids_after_fiscal_position
		return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: