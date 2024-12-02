from odoo import api, models

class GenerateReport(models.AbstractModel):
    _name = 'report.inventory_report_ept.inventoryage_doc'
    
    @api.model
    def get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        products = self.env['product.product'].browse(data.get('active_id', data.get('active_id')))
        return {
            'doc_ids': data.get('active_id', data.get('active_id')),
            'doc_model': 'inventory.age.report.ept',
            'doc': products,
            'inventory_data': dict(
                data
            ),
        }