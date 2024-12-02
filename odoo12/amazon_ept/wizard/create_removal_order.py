from odoo import models, fields, api
import base64
from io import StringIO
import csv
from odoo.exceptions import Warning

class create_removal_order(models.TransientModel): 
    _name = 'create.removal.order'
   
    sellable_365plus_days = fields.Boolean("Sellable-365+-days")
    sellable_271_365_days = fields.Boolean("Sellable-271-365-days")
    sellable_181_270_days = fields.Boolean("Sellable-181-270-days")
    sellable_121_180_days = fields.Boolean("Sellable-121-180-days")
    unsellable_61_90_days = fields.Boolean("Unsellable-61-90-days")
    unsellable_8_60_days = fields.Boolean("Unsellable-8-60-days")
    unsellable_0_7_days = fields.Boolean("Unsellable-0-7-days")
    instance_id  = fields.Many2one('amazon.instance.ept', string="Instance")
    warehouse_id = fields.Many2one('stock.warehouse', string="Destination Warehouse")
    company_id = fields.Many2one(related='instance_id.company_id', string="Company",store=True)
   
    
    @api.multi
    def create_removal_order(self):
        report_obj = self.env['report.fba.recommended.removal.data'].browse(self.env.context.get('active_id'))
        if not report_obj.attachment_id:
            raise Warning("There is no any report are attached with this record.")
        imp_file = StringIO(base64.decodestring(report_obj.attachment_id.datas))
        reader = csv.DictReader(imp_file,delimiter='\t')
        removal_order_obj = self.env['amazon.removal.order.ept']
        order_vals = {
            'instance_id': self.instance_id.id,
            'warehouse_id': self.warehouse_id.id,
            'ship_address_id': self.warehouse_id.partner_id.id,
            'company_id': self.instance_id.company_id.id,
            'report_removal_order_id':report_obj.id
        }
        new_removal_order_obj = removal_order_obj.create(order_vals)
        
        sellable_quantity = 0
        unsellable_quantity = 0    
        for row in reader:
            for line in report_obj.report_fba_recommended_removal_line:
                if row.get('sku') == line.amazon_product_id.seller_sku:                    
                    if self.sellable_365plus_days and not self.sellable_271_365_days and not self.sellable_181_270_days and not self.sellable_121_180_days:
                        sellable_quantity = int(row.get('sellable-365+-days'))
                    if self.sellable_365plus_days and self.sellable_271_365_days and not self.sellable_181_270_days and not self.sellable_121_180_days:
                        sellable_quantity = int(row.get('sellable-271-365-days')) + int(row.get('sellable-365+-days'))
                    if self.sellable_365plus_days and self.sellable_271_365_days and self.sellable_181_270_days and not self.sellable_121_180_days:
                        sellable_quantity = int(row.get('sellable-271-365-days')) + int(row.get('sellable-365+-days')) + int(row.get('sellable-181-270-days'))
                    if self.sellable_365plus_days and self.sellable_271_365_days and self.sellable_181_270_days and self.sellable_121_180_days:
                        sellable_quantity = int(row.get('sellable-271-365-days')) + int(row.get('sellable-365+-days')) + int(row.get('sellable-181-270-days')) + int(row.get('sellable-121-180-days'))
                    
                    if self.unsellable_61_90_days and not self.unsellable_8_60_days and not self.unsellable_0_7_days:
                        unsellable_quantity = int(row.get('unsellable-61-90-days'))
                    if self.unsellable_61_90_days and self.unsellable_8_60_days and not self.unsellable_0_7_days:
                        unsellable_quantity = int(row.get('unsellable-61-90-days')) + int(row.get('unsellable-8-60-days'))
                    if self.unsellable_61_90_days and self.unsellable_8_60_days and self.unsellable_0_7_days:
                        unsellable_quantity = int(row.get('unsellable-61-90-days')) + int(row.get('unsellable-8-60-days')) + int(row.get('unsellable-0-7-days')) 
                    
                    if sellable_quantity > 0 or unsellable_quantity > 0:
                        new_removal_order_obj.write({
                                'removal_order_lines_ids': [(0, 0, {
                                'amazon_product_id': line.amazon_product_id.id,
                                'sellable_quantity': sellable_quantity,
                                'unsellable_quantity': unsellable_quantity,
                                })]
                            })
                    else:
                        new_removal_order_obj.write({
                                'removal_order_lines_ids': [(0, 0, {
                                'amazon_product_id': line.amazon_product_id.id,
                                'sellable_quantity':  0.0,
                                'unsellable_quantity': 0.0,
                                })]
                            })
        removal_order_form_id = self.env['ir.model.data'].get_object_reference('amazon_removal_order_ept', 'removal_order_form_view')[1]
        report_obj.write({'is_removal_order_created':True})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'amazon.removal.order.ept',
            'views': [(removal_order_form_id, 'form')],
            'view_id': removal_order_form_id,
            'res_id': new_removal_order_obj.id,
         
        }
                        
                
        
        
        
