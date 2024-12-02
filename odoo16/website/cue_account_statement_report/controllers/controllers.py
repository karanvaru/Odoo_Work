
import json
from odoo import http
from odoo.http import content_disposition, request
# from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape


class TBXLSXReportController(http.Controller):
    @http.route('/fund_statement_dynamic_xlsx_reports', type='http', auth='user',
                methods=['POST'], csrf=False)
    def fund_statement_get_report_xlsx(self, model, report_month, output_format, report_data,
                        report_name, dfr_data, **kw):
        dfr_data = json.loads(dfr_data)
        uid = request.session.uid
        report_obj = request.env[model].with_user(uid)
        if 'filtered_data_domain' in dfr_data:
            dfr_data = dfr_data['filtered_data_domain']
        report_month = report_month
        token = 'dummy-because-api-expects-one'
        try:
            if output_format == 'xlsx':
                response = request.make_response(
                    None,
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition',
                         content_disposition(report_name + '.xlsx'))
                    ]
                )
                report_obj.get_dynamic_xlsx_report(report_month, response,
                                                   report_data, dfr_data)
            response.set_cookie('fileToken', token)
            return response
        except Exception as e:
            se = http.serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))