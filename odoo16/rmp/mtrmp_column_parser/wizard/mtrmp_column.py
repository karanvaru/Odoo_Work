import requests
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class DocumentColumn(models.TransientModel):
    _name = "document.column.wizard"
    _description = 'Document Wizard'

    def get_domain(self):
        return 'http://194.163.165.59'

    def get_category_route(self):
        return 'column-parser/api/get-all-categories'

    def get_document_route(self):
        return 'column-parser/api/get-all-documents'

    def get_colomn_route(self):
        return 'column-parser/api/get-columns-by-document'

    def get_token(self):
        return 'bc71bb16e9330ec6b09a1b645d64ec27c7279da0'

    def get_column_parser_route(self):
        return 'column-parser/api/column-parser'

    def create_all_records(self):
        new_cr = self.pool.cursor()
        self = self.with_env(self.env(cr=new_cr))
        domain = self.get_domain()
        token = self.get_token()
        self.get_categories(domain, token)
        self.get_documents(domain, token)
        self.get_columns(domain, token)

    def get_categories(self, domain, token):
        route = self.get_category_route()
        endpoint = f'{domain}/{route}'
        self._get_categories(endpoint=endpoint, token=token)
        return

    def get_documents(self, domain, token):
        route = self.get_document_route()
        endpoint = f'{domain}/{route}'
        self._get_documents(endpoint=endpoint, token=token)
        return

    def get_columns(self, domain, token):
        route = self.get_colomn_route()
        endpoint = f'{domain}/{route}'
        self._get_columns(endpoint=endpoint, token=token)
        return

    def _get_categories(self, endpoint, token):
        new_cr = self.pool.cursor()
        self = self.with_env(self.env(cr=new_cr))
        query = f'{endpoint}?token={token}'
        try:
            response = requests.get(query)
            data = response.json()
            if data.get('success', False):
                vals = []
                recs = data.get('data') # list
                for rec in recs:
                    check = self.env['mtrmp.document.category'].search([('category_id', '=', rec.get('id')), ('name', '=', rec.get('name'))])
                    if not check:
                        vals.append({
                            'category_id': rec.get('id'),
                            'name': rec.get('name'),
                        })
                if vals:
                    new_categories = self.env['mtrmp.document.category'].create(vals)
                    self._cr.commit()
            return
        except Exception as e:
            _logger.info(f"Error Occured : {e}")
            return

    def _get_documents(self, endpoint, token):
        new_cr = self.pool.cursor()
        self = self.with_env(self.env(cr=new_cr))
        categories = self.env['mtrmp.document.category'].sudo().search([])

        try:
            for category in categories:
                query = f'{endpoint}?category_id={category.category_id}&token={token}'
                response = requests.get(query)
                data = response.json()
                if data.get('success', False):
                    vals = []
                    recs = data.get('data')  # list
                    for rec in recs:
                        check = self.env['mtrmp.document'].search(
                            [('document_id', '=', rec.get('id')), ('name', '=', rec.get('name')), ('category_id','=', category.id)])
                        if not check:
                            vals.append({
                                'document_id': rec.get('id'),
                                'category_id': category.id,
                                'name': rec.get('name'),
                            })
                    if vals:
                        new_documents = self.env['mtrmp.document'].create(vals)
                self._cr.commit()
            return
        except Exception as e:
            _logger.info("Error Occured")
            return

    def _get_columns(self, endpoint, token):
        documents = self.env['mtrmp.document'].sudo().search([])
        try:
            for document in documents:
                query = f'{endpoint}?document_id={document.document_id}&token={token}'
                response = requests.get(query)
                data = response.json()
                if data.get('success', False):
                    vals = []
                    recs = data.get('data')  # list
                    for rec in recs:
                        check = self.env['mtrmp.document.column'].search(
                            [('column_id', '=', rec.get('id')), ('name', '=', rec.get('column_name')),
                             ('document_id', '=', document.id)])
                        if not check:
                            vals.append({
                                'column_id': rec.get('id'),
                                'document_id': document.id,
                                'name': rec.get('column_name'),
                            })
                    if vals:
                        new_columns = self.env['mtrmp.document.column'].create(vals)
                        self._cr.commit()
        except Exception as e:
            _logger.info(f"Error Occured as {e}")
            return

