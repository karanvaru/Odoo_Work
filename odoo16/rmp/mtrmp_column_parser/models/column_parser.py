# -*- coding: utf-8 -*-

from odoo import api, models, fields, _

class DocumentCategory(models.Model):
    _name = 'mtrmp.document.category'
    _description = "Document Category"

    category_id = fields.Integer('Category', required=True)
    name = fields.Char('Name', required=True)
    document_ids = fields.One2many('mtrmp.document', 'category_id')

class Document(models.Model):
    _name = 'mtrmp.document'
    _description = "Document"

    document_id = fields.Integer('Document', required=True)
    name = fields.Char('Name', required=True)
    category_id = fields.Many2one('mtrmp.document.category', ondelete="cascade")
    column_ids = fields.One2many('mtrmp.document.column', 'document_id')
    document_type = fields.Selection([('sale_order', 'Sale Order'), ('delivery_confirmation', 'Delivery Confirmation'),
                                      ('return_confirmation', 'Return Confirmation'), ('payment_settlement', 'Payment Settlement')])

class DocumentColumn(models.Model):
    _name = 'mtrmp.document.column'
    _description = "Document"

    column_id = fields.Integer(required=True)
    name = fields.Char('name', required=True)
    document_id = fields.Many2one('mtrmp.document', ondelete="cascade")
    sale_order_confirmation_fields = fields.Selection([('order reference', 'Order reference'),
                                                       ('customer name', 'customer name'),
                                                       ('customer email', 'Customer Email'),
                                                       ('customer phone', 'Customer Phone'),
                                                       ('shipping name', 'shipping name'),
                                                       ('shipping email', 'shipping email'),
                                                       ('shipping phone', 'shipping phone'),
                                                       ('shipping address', 'shipping address'),
                                                       ('shipping state', 'shipping state'),
                                                       ('shipping country', 'shipping country'),
                                                       ('shipping zip', 'shipping zip'),
                                                       ('shipping city', 'shipping city'),
                                                       ('billing name', 'billing name'),
                                                       ('billing email', 'billing email'),
                                                       ('billing phone', 'billing phone'),
                                                       ('billing address', 'billing address'),
                                                       ('billing state', 'billing state'),
                                                       ('billing country', 'billing country'),
                                                       ('billing zip', 'billing zip'),
                                                       ('billing city', 'billing city'),
                                                       ('product name', 'product name'),
                                                       ('product_sku', 'SKU'),
                                                       ('price', 'Price'),
                                                       ('discount', 'Discount'),
                                                       ('shipping', 'Shipping Price'),
                                                       ('quantity', 'Quantity'),
                                                       ('order_date', 'Order Date'),
                                                       ('tax rate', 'tax rate'),
                                                       ('tax amount', 'tax amount')
                                                       ])

    delivery_order_confirmation_fields = fields.Selection([('order reference', 'Order Reference'),
                                                           ('delivery date', 'Delivery Date'),
                                                           ('AWB number', 'AWB number'),
                                                           ('sku', 'SKU'),
                                                           ('quantity', 'Quantity')])

    return_confirmation_fields = fields.Selection([('order reference', 'Order Reference'),
                                                   ('delivery date', 'Delivery Date'),
                                                   ('AWB number', 'AWB number'),
                                                   ('sku', 'SKU'),
                                                   ('quantity', 'Quantity')])

    payment_settlement_fields = fields.Selection([('sale_order', 'Sale Order'), ('sale_amount', 'Sale Amount'),
                                                  ('sku', 'SKU'), ('quantity', 'Order Quantity'),
                                                  ('unit_price', 'Unit Price'), ('transaction_id', 'Transaction Id'),
                                                  ('payment_date', 'Payment Date'), ('sale_return_amount', 'Sale Return Amount'),
                                                  ('shipping_amount', 'Shipping Amount'), ('igst_rate', 'IGST Rate'),
                                                  ('igst', 'IGST'), ('cgst_rate', 'CGST Rate'),
                                                  ('cgst', 'CGST'), ('sgst_rate', 'SGST Rate'),
                                                  ('sgst', 'SGST'), ('tds_rate', 'TDS Rate'),
                                                  ('other_charges', 'Other Charges'),
                                                  ('return_qty', 'Return Quantity'),
                                                  ('delivered_qty','Delivered Quantity'),
                                                  ('other_charges1', 'Other Charges1'),
                                                  ('other_charges2', 'Other Charges2'),
                                                  ('other_charges3', 'Other Charges3'),
                                                  ('other_charges4', 'Other Charges4'),
                                                  ('other_charges5', 'Other Charges5'),
                                                  ('other_charges6', 'Other Charges6'),
                                                  ('other_charges7', 'Other Charges7'),
                                                  ('other_charges8', 'Other Charges8'),
                                                  ('other_charges9', 'Other Charges9'),
                                                  ('other_charges10', 'Other Charges10'),])
