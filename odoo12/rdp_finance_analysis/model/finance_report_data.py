from odoo import models, fields, api, _

class report_finance_analysis(models.Model):
    _name = 'finance.analysis.report'
    _description = "RDP Finance Analysis Report"

    @api.model
    def get_finance_analysis_inbound_data(self):
        inbound_list = []       
        # query_kp = (
        #         "SELECT finance_analysis.name, finance_analysis.source_date, finance_analysis.source_reference, finance_analysis.partner_id, rp.partner_id AS customer, finance_analysis.payment_amount,finance_analysis.amount",
        #         "FROM finance_analysis",
        #         "Join res_users rp ON (finance_analysis.user_id=rp.id)")

        #self.env.cr.execute("SELECT * FROM account_payment")
        #self.env.cr.execute("SELECT a.*,b.* FROM account_payment a JOIN finance_analysis b ON a.payment_date=b.source_date")
        self.env.cr.execute("SELECT * FROM account_payment")
        
        for rec in self.env.cr.dictfetchall():
           inbound_list.append(rec)
        return inbound_list

    # @api.model
    # def get_finance_analysis_data(self):
    #     inbound_list = []       
    #     # query_kp = (
    #     #         "SELECT finance_analysis.name, finance_analysis.source_date, finance_analysis.source_reference, finance_analysis.partner_id, rp.partner_id AS customer, finance_analysis.payment_amount,finance_analysis.amount",
    #     #         "FROM finance_analysis",
    #     #         "Join res_users rp ON (finance_analysis.user_id=rp.id)")

    #     self.env.cr.execute("SELECT * FROM finance_analysis")
        
    #     for rec in self.env.cr.dictfetchall():
    #        inbound_list.append(rec)
    #     return inbound_list