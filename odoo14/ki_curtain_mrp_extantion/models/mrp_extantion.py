from odoo import api, fields, models, _


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    computation_type = fields.Selection([
        ('Standard', 'Standard'),
        ('Width', 'Width'),
        ('Height', 'Height'),
        ('Both', 'Both') 
    ], default='Standard', string='Computation Type')


class stockMove(models.Model):
    _inherit = "stock.move"

    computation_type = fields.Selection([
        ('Standard', 'Standard'),
        ('Width', 'Width'),
        ('Height', 'Height'),
        ('Both', 'Both') 
    ], default='Standard', string='Computation Type')


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    width = fields.Float(
        'Width',
        default=1.0,
        readonly=True, required=True, tracking=True,
        states={'draft': [('readonly', False)]})

    height = fields.Float(
        'Height',
        default=1.0,
        readonly=True, required=True, tracking=True,
        states={'draft': [('readonly', False)]})

    def _get_move_raw_values(self, product_id, product_uom_qty, product_uom, operation_id=False, bom_line=False):
        res = super(MrpProduction, self)._get_move_raw_values(product_id, product_uom_qty, product_uom, operation_id,
                                                              bom_line)
        # print('res',res);
        if not res.get('computation_type',False):
            res.update({'computation_type': bom_line.computation_type})
        if res['computation_type'] == 'Width':
            res['product_uom_qty'] = res['product_uom_qty'] * self.width
        elif res['computation_type'] == 'Height':
            res['product_uom_qty'] = res['product_uom_qty'] * self.height
        elif res['computation_type'] == 'Both':
            res['product_uom_qty'] = res['product_uom_qty'] * self.height * self.width

        # print('product_id',product_id.name);
        # print('product_uom_qty',res['product_uom_qty']);
        return res

    @api.onchange('width','height')
    def _onchange_width_height_move_raw(self):
        print ('check call')
        return self._onchange_move_raw()

    # @api.onchange('bom_id', 'product_id', 'product_qty', 'product_uom_id','width','height')
    # def _onchange_move_raw(self):
    #     print ('check call')
    #     return super(MrpProduction, self)._onchange_move_raw()

