from odoo import api, fields, models


class StockPackageType(models.Model):
    _inherit = "stock.package.type"

    def name_get(self):
        result = []
        for record in self:
            name = str(record.packaging_length) + 'L' + 'X' + str(record.width) + 'W' + 'x'+ str(record.height) + 'H'
            result.append((record.id, name))
        return result
