# -*- coding: utf-8 -*-
import datetime
from odoo import models, api


class ReportAvgPrices(models.AbstractModel):
    _name = 'report.product_ageing_report.report_ageing_analysis'

    def get_productss(self, docs):
        """input : starting date, location and category
          output: a dictionary with all the products and their stock for that currespnding intervals"""

        cr = self._cr
        if docs.location_id and docs.product_categ:
            cr.execute("select sq.id as quant,pp.id as product from stock_quant sq "
                       "join product_product pp on (pp.id = sq.product_id) "
                       "join product_template pt on (pt.id=pp.product_tmpl_id and pt.categ_id in %s) "
                       " join stock_location st on st.id = sq.location_id"
                       " where sq.location_id in %s and sq.quantity > 0 and sq.in_date <=%s and st.usage ='internal'"
                       ,
                       (tuple(docs.product_categ.ids),
                        tuple(docs.location_id.ids), docs.from_date))
        elif docs.location_id:
            cr.execute(
                "select sq.id as quant ,sq.product_id as product from stock_quant sq "
                " join stock_location st on st.id = sq.location_id"
                " where sq.location_id in %s and sq.quantity > 0 "
                "and sq.in_date <=%s and st.usage ='internal'",
                (tuple(docs.location_id.ids), docs.from_date))
        elif docs.product_categ:
            cr.execute("select sq.id as quant,pp.id as product from stock_quant sq "
                       "join product_product pp on(pp.id=sq.product_id) "
                       "  join stock_location st on st.id = sq.location_id"
                       " join product_template pt on(pt.id=pp.product_tmpl_id and pt.categ_id in %s)"
                       "where sq.quantity > 0  and sq.in_date <=%s and st.usage ='internal'"
                       "", (tuple(docs.product_categ.ids), docs.from_date))
        else:
            cr.execute("select sq.id as quant,sq.product_id as product from stock_quant sq "
                       " join stock_location st on st.id = sq.location_id"
                       " where quantity > 0  and in_date <=%s  and st.usage ='internal'"
                       , (docs.from_date,))
        product_ids = cr.dictfetchall()
        products = {}
        product = []
        for i in product_ids:
            if i['product'] not in product:
                product.append(i['product'])
        for pr in product:
            quant = []
            for val in product_ids:
                if val['product'] == pr:
                    quant.append(val['quant'])
            cr.execute(" select pt.name as product,sq.quantity as quantity ,st.name as location,lot.name as lot ,sq.in_date as in_date"
                       " from stock_quant sq "
                        "join product_product pp on (pp.id = sq.product_id)"
                       " join product_template pt on (pt.id=pp.product_tmpl_id)"
                       " join stock_production_lot lot on lot.id=sq.lot_id"  
                        " join stock_location st on st.id = sq.location_id"
                        " where sq.lot_id IS NOT NULL  and sq.id in %s",
                       (tuple(quant),))
            rec_with_lot = cr.dictfetchall()
            cr.execute(" select pt.name as product,sq.quantity as quantity ,st.name as location,sq.in_date as in_date "
                       " from stock_quant sq "
                       "join product_product pp on (pp.id = sq.product_id)"
                       "join product_template pt on (pt.id=pp.product_tmpl_id)"
                       " join stock_location st on st.id = sq.location_id"
                       " where sq.lot_id IS NULL  and sq.id in %s",
                       (tuple(quant),))
            rec_without_lot = cr.dictfetchall()
            vals = []
            date1 = datetime.datetime.strptime(str(docs.from_date), '%Y-%m-%d %H:%M:%S').date()
            if rec_with_lot:
                for re in rec_with_lot:
                    flag = 0
                    if vals:
                        for val in vals:
                            if val['location'] == re['location'] and val['lot'] == re['lot']:
                                date2 = datetime.datetime.strptime(str(re['in_date']), '%Y-%m-%d %H:%M:%S').date()
                                no_days = (date1 - date2).days
                                t1 = 0
                                t2 = docs.interval
                                for j in range(0, 5):
                                    if no_days >= 4 * docs.interval:
                                        val['quantity'][4] += re['quantity']
                                        val['total_qty'] += re['quantity']
                                        break
                                    elif no_days in range(t1, t2):
                                        val['quantity'][j] += re['quantity']
                                        val['total_qty'] += re['quantity']
                                        break
                                    t1 = t2
                                    t2 += docs.interval
                                age_range = len([x for x in val['quantity'] if x != 0])
                                if age_range > 1:
                                    val['age'] = ''
                                else:
                                    val['age'] = no_days
                                flag = 1
                        if not flag:
                            temp = {
                                'product': re['product'],
                                'location': re['location'],
                                'lot': re['lot'],
                                'total_qty': re['quantity']
                            }
                            quantity = [0, 0, 0, 0, 0]

                            date2 = datetime.datetime.strptime(str(re['in_date']), '%Y-%m-%d %H:%M:%S').date()
                            no_days = (date1 - date2).days
                            t1 = 0
                            t2 = docs.interval
                            for j in range(0, 5):
                                if no_days >= 4 * docs.interval:
                                    quantity[4] += re['quantity']
                                    break
                                elif no_days in range(t1, t2):
                                    quantity[j] += re['quantity']
                                    break

                                t1 = t2
                                t2 += docs.interval
                            temp['quantity'] = quantity
                            age_range = len([x for x in temp['quantity'] if x != 0])
                            if age_range > 1:
                                temp['age'] = ''
                            else:
                                temp['age'] = no_days
                            vals.append(temp)

                    else:
                        temp = {
                            'product': re['product'],
                            'location': re['location'],
                            'lot': re['lot'],
                            'total_qty': re['quantity']
                        }
                        quantity = [0, 0, 0, 0, 0]

                        date2 = datetime.datetime.strptime(str(re['in_date']), '%Y-%m-%d %H:%M:%S').date()
                        no_days = (date1 - date2).days
                        t1 = 0
                        t2 = docs.interval
                        for j in range(0, 5):
                            if no_days >= 4 * docs.interval:
                                quantity[4] += re['quantity']
                                break
                            elif no_days in range(t1, t2):
                                quantity[j] += re['quantity']
                                break

                            t1 = t2
                            t2 += docs.interval
                        temp['quantity'] = quantity
                        age_range = len([x for x in temp['quantity'] if x != 0])
                        if age_range > 1:
                            temp['age'] = 'MULTIPLE'
                        else:
                            temp['age'] = no_days
                        vals.append(temp)
            vals_without_lot = []
            if rec_without_lot:
                for re in rec_without_lot:
                    flag = 0
                    if vals_without_lot:
                        for val in vals_without_lot:
                            if val['location'] == re['location']:
                                date2 = datetime.datetime.strptime(str(re['in_date']), '%Y-%m-%d %H:%M:%S').date()
                                no_days = (date1 - date2).days
                                t1 = 0
                                t2 = docs.interval
                                for j in range(0, 5):
                                    if no_days >= 4 * docs.interval:
                                        val['quantity'][4] += re['quantity']
                                        val['total_qty'] += re['quantity']
                                        break
                                    elif no_days in range(t1, t2):
                                        val['quantity'][j] += re['quantity']
                                        val['total_qty'] += re['quantity']
                                        break
                                    t1 = t2
                                    t2 += docs.interval
                                flag = 1
                        if not flag:
                            temp = {
                                'product': re['product'],
                                'location': re['location'],
                                'lot': '',
                                'age': '',
                                'total_qty': re['quantity']
                            }
                            quantity = [0, 0, 0, 0, 0]

                            date2 = datetime.datetime.strptime(str(re['in_date']), '%Y-%m-%d %H:%M:%S').date()
                            no_days = (date1 - date2).days
                            t1 = 0
                            t2 = docs.interval
                            for j in range(0, 5):
                                if no_days >= 4 * docs.interval:
                                    quantity[4] += re['quantity']
                                    break
                                elif no_days in range(t1, t2):
                                    quantity[j] += re['quantity']
                                    break

                                t1 = t2
                                t2 += docs.interval
                            temp['quantity'] = quantity
                            vals_without_lot.append(temp)

                    else:
                        temp = {
                            'product': re['product'],
                            'location': re['location'],
                            'lot': '',
                            'total_qty': re['quantity'],
                            'age': ''
                        }
                        quantity = [0, 0, 0, 0, 0]

                        date2 = datetime.datetime.strptime(str(re['in_date']), '%Y-%m-%d %H:%M:%S').date()
                        no_days = (date1 - date2).days
                        t1 = 0
                        t2 = docs.interval
                        for j in range(0, 5):
                            if no_days >= 4 * docs.interval:
                                quantity[4] += re['quantity']
                                break
                            elif no_days in range(t1, t2):
                                quantity[j] += re['quantity']
                                break

                            t1 = t2
                            t2 += docs.interval
                        temp['quantity'] = quantity
                        vals_without_lot.append(temp)
            products[pr] = vals + vals_without_lot
        return products

    @api.model
    def _get_report_values(self, docids, data=None):
        """we are overwriting this function because we need to show values from other models in the report
                we pass the objects in the docargs dictionary"""

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        products = self.get_productss(docs)
        interval = ['0-' + str(docs.interval),
                    str(docs.interval) + '-' + str(2 * docs.interval),
                    str(2 * docs.interval) + '-' + str(3 * docs.interval),
                    str(3 * docs.interval) + '-' + str(4 * docs.interval),
                    str(4 * docs.interval) + '+']
        loc = ""
        categ = ""
        for i in docs.location_id:
            if i.location_id.name and i.name:
                loc += i.location_id.name + " / " + i.name + ", "
        for i in docs.product_categ:
            if i.name:
                categ += i.name + ", "
        loc = loc[:-2]
        categ = categ[:-2]
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'loc': loc,
            'categ': categ,
            'interval': interval,
            'products': products,
        }
        return docargs
