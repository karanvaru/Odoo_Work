import json
from odoo import http
from odoo.http import request
from odoo import models, fields, api, _


class SearchStockMove(http.Controller):
    @http.route('/searchpicking/', auth="public", type="json")
    def search_stock_picking(self, **kwargs):
        picking = kwargs['picking']
        picking_search_by = kwargs['search_by']
        picking_type = int(kwargs['picking_type'])

        PickingObj = request.env['stock.picking'].sudo()
        PickintypegObj = request.env['stock.picking.type'].search([('id', '=', picking_type)])

        stock_picking = PickingObj

        if picking_search_by == 'Name':
            stock_picking = PickingObj.search(
                [('name', '=', picking), ('picking_type_id', '=', PickintypegObj.id)], limit=1
            )
        elif picking_search_by == 'Tracking Reference':
            stock_picking = PickingObj.search(
                [('carrier_tracking_ref', '=', picking), ('picking_type_id', '=', PickintypegObj.id)], limit=1
            )
        elif picking_search_by == 'AWB Number':
            stock_picking = PickingObj.search(
                [('mp_awb_number', '=', picking), ('picking_type_id', '=', PickintypegObj.id)], limit=1
            )
        if stock_picking.state == 'done':
            return {
                'error': 'Picking already Validated'
            }
        if not stock_picking:
            return {
                'error': 'Not valid Picking Found!'
            }

        return {
            'message': request.env['ir.ui.view']._render_template("ki_picking_barcode_scan.template_move_lines", {
                'stock_picking': stock_picking,
                'move_lines': stock_picking.move_ids_without_package,
            })
        }

    @http.route('/searchproduct/', auth="public", type="json")
    def search_stock_move(self, **kwargs):
        picking = kwargs['picking']
        is_lot = kwargs['is_lot']
        stock_picking = False
        if picking:
            stock_picking = request.env['stock.picking'].sudo().browse(int(picking))
            stock_picking.action_assign()
        else:
            return {
                'error': 'Please Scan for picking first!'
            }
        search_by = kwargs['search_by']
        product = kwargs['product_name']
        product_lot_number = kwargs['product_lot_number']
        ProductObj = request.env['product.product'].sudo()
        StockMoveLineObj = request.env['stock.move.line'].sudo()

        product_id = False
        domain = []
        if search_by == 'Barcode':
            product_id = ProductObj.search([('barcode', '=', product)], limit=1)
        elif search_by == 'Internal Reference':
            product_id = ProductObj.search([('default_code', '=', product)], limit=1)
        StockMoveLine_id = False
        # if is_lot == True:
        if is_lot == True:
            if product_lot_number:
                StockMoveLine_id = StockMoveLineObj.search(
                    [('picking_id', '=', stock_picking.id), ('lot_id.name', '=', product_lot_number),
                     ('product_id', '=', product_id.id)], limit=1)
                if not StockMoveLine_id:
                    find_lot = False
                    StockMoveLine_id = StockMoveLineObj.search(
                        [('picking_id', '=', stock_picking.id), ('product_id', '=', product_id.id)], limit=1)

                    available_lots = request.env['stock.production.lot'].search(
                        [('product_qty', '>', 0), ('product_id', '=', product_id.id)])

                    available_lots_number = []
                    for rec in available_lots:
                        available_lots_number.append(rec)

                    for res in available_lots_number:
                        if product_lot_number == res.name:
                            StockMoveLine_id_new = StockMoveLineObj.search(
                                [('product_id', '=', product_id.id), ('qty_done', '=', 0), ('lot_id', '=', res.id)])
                            StockMoveLine_id_new.lot_id = StockMoveLine_id.lot_id
                            StockMoveLine_id.lot_id = res
                            find_lot = True
                            break
                    if find_lot == False:
                        return {
                            'error': 'Not valid product found!'
                        }

        else:
            StockMoveLine_id = StockMoveLineObj.search(
                [('picking_id', '=', stock_picking.id),
                 ('product_id', '=', product_id.id)], limit=1)
            if not StockMoveLine_id:
                find_lot = False
                StockMoveLine_id = StockMoveLineObj.search(
                    [('picking_id', '=', stock_picking.id), ('product_id', '=', product_id.id)], limit=1)

                available_lots = request.env['stock.production.lot'].search(
                    [('product_qty', '>', 0), ('product_id', '=', product_id.id)])

                available_lots_number = []
                for rec in available_lots:
                    available_lots_number.append(rec)

                for res in available_lots_number:
                    if product_lot_number == res.name:
                        StockMoveLine_id_new = StockMoveLineObj.search(
                            [('product_id', '=', product_id.id), ('qty_done', '=', 0), ('lot_id', '=', res.id)])
                        StockMoveLine_id_new.lot_id = StockMoveLine_id.lot_id
                        StockMoveLine_id.lot_id = res
                        find_lot = True
                        break
                if find_lot == False:
                    return {
                        'error': 'Not valid product found!'
                    }


        move_id = stock_picking.move_ids_without_package.filtered(lambda i: i.product_id == product_id)
        if move_id:
            if StockMoveLine_id:
                StockMoveLineValue = {
                    'move_id': move_id.id,
                    'move_line': StockMoveLine_id.id,
                    'StockMoveLineQty': StockMoveLine_id.product_uom_qty,
                }
                return StockMoveLineValue
            else:
                return {
                    'move_id': move_id.id,
                    # 'StockMoveLineQty': move_id.product_uom_qty,
                }
        else:
            return {
                'error': 'Not valid product found!'
            }

    @http.route('/validatestockpicking/', auth="public", type="json")
    def validate_stock_picking(self, **kwargs):
        if 'picking_id' in kwargs:
            picking_id = kwargs['picking_id']
            # scanned_lots_name = kwargs['scanned_lots_name']
            # move_id_lst = kwargs['move_id_lst']
            move_line_lst = kwargs['move_line_lst']

            PickingObj = request.env['stock.picking'].sudo()
            stock_picking = PickingObj.search(
                [('id', '=', picking_id)], limit=1
            )
            if stock_picking:
                if stock_picking.state == 'done':
                    return {
                        'error': 'Picking already Validated'
                    }
                else:
                    picking_validate = False
                    for res in json.loads(kwargs['move_lines']):
                        # if res['Scanned Qty'] == "1":
                        if res['Scanned Qty'] > "0":
                            move_id = int(res['Move'])
                            # stock_move = request.env['stock.move'].sudo().search(
                            #     [('id', 'in', move_id_lst)])
                            # for move in stock_move:
                            #     for move_line in move.move_line_ids:
                            #         move_line.qty_done = move_line.product_uom_qty

                                # move.quantity_done = move.product_uom_qty
                            stock_move_line = request.env['stock.move.line'].sudo().search(
                                [('move_id', '=', move_id), ('id', 'in', move_line_lst)]
                            )

                            for move_line in stock_move_line:
                                move_line.qty_done = move_line.product_uom_qty

                            picking_validate = True
                    result = stock_picking.with_context(skip_immediate=True, skip_sms=True).button_validate()
                    if type(result) is dict:
                        if 'context' in result:
                            request.env['stock.backorder.confirmation'].with_context(result['context']).process()
                    if picking_validate:
                        return {
                            'error': 'picking successfully validated'
                        }
