from odoo import models,api
from datetime import datetime

class product_product(models.Model):
    _inherit = "product.product"
    
    @api.multi
    def get_stock_ept(self,product_id,warehouse_id,fix_stock_type=False,fix_stock_value=0,stock_type='virtual_available'):
        product = self.with_context(warehouse=warehouse_id).browse(product_id.id)
        try:
            actual_stock = getattr(product, stock_type)
            if actual_stock >= 1.00:
                if fix_stock_type == 'fix':
                    if fix_stock_value >= actual_stock:
                        return actual_stock
                    else:
                        return fix_stock_value
    
                elif fix_stock_type == 'percentage':
                    quantity = int((actual_stock * fix_stock_value) / 100.0)
                    if quantity >= actual_stock:
                        return actual_stock
                    else:
                        return quantity
            return actual_stock
        except Exception as e:
            raise Warning(e)

    def get_qty_on_hand(self, warehouse, product_list):
        """
        This method is return On hand quantity based on warehouse and product list
        @author:Krushnasinh Jadeja
        :param warehouse: warehouse object
        :param product_list: list of product object
        :return:On hand quantity
        """
        locations = self.env['stock.location'].search(
            [('location_id', 'child_of', warehouse.mapped('lot_stock_id').mapped('id'))])
        location_ids = ','.join(str(e) for e in locations.ids)
        product_list_ids = ','.join(str(e) for e in product_list.ids)
        # Query Updated by Udit
        qry = """select pp.id as product_id,
                COALESCE(sum(sq.quantity)-sum(sq.reserved_quantity),0) as stock
                from product_product pp
                left join stock_quant sq on pp.id = sq.product_id and
                sq.location_id in (%s)
                where pp.id in (%s) group by pp.id;""" % (location_ids, product_list_ids)
        self._cr.execute(qry)
        on_hand = self._cr.dictfetchall()
        return on_hand

    def get_forecated_qty(self, warehouse, product_list):
        """
        This method is return forecasted quantity based on warehouse and product list
        @author:Krushnasinh Jadeja
        :param warehouse:warehouse object
        :param product_list:list of product object
        :return: Forecasted Quantity
        """
        # locations = self.env['stock.location'].search(
        #     [('location_id', 'child_of', warehouse.lot_stock_id.id)])
        locations = self.env['stock.location'].search(
            [('location_id', 'child_of', warehouse.mapped('lot_stock_id').mapped('id'))])
        location_ids = ','.join(str(e) for e in locations.ids)
        product_list_ids = ','.join(str(e) for e in product_list.ids)
        # Query Updated by Udit
        qry = """select *
                from (select pp.id as product_id,
                COALESCE(sum(sq.quantity)-sum(sq.reserved_quantity),0) as stock
                from product_product pp
                left join stock_quant sq on pp.id = sq.product_id and
                sq.location_id in (%s)
                where pp.id in (%s) group by pp.id
                union all
                select product_id as product_id,sum(product_qty) as stock from stock_move
                where state in ('assigned') and product_id in (%s) and location_dest_id in (%s)
                group by product_id) as test""" \
              % (location_ids, product_list_ids, product_list_ids, location_ids)
        self._cr.execute(qry)
        forecasted = self._cr.dictfetchall()
        return forecasted

    def get_products_based_on_movement_date(self, from_datetime, company=False):
        """
        This method is give the product list from selected date.
        @author: Haresh Mori @ Emipro on date 24/06/2020
        :param from_datetime:from this date it gets the product move list
        :param company:company id
        :return:Product List
        """
        date = str(datetime.strftime(from_datetime, '%Y-%m-%d %H:%M:%S'))
        if company:
            qry = """select product_id from stock_move where date >= '%s' and company_id = %d and
                             state in ('partially_available','assigned','done')""" % (date, company.id)
        else:
            qry = """select product_id from stock_move where date >= '%s' and
                                     state in ('partially_available','assigned','done')""" % date
        self._cr.execute(qry)
        return self._cr.dictfetchall()
