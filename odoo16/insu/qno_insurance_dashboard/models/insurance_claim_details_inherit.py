from odoo import models, fields, api


class InsuranceClaimDetailsInherit(models.Model):
    _inherit = "insurance.claim.details"

    def formatINR(self, number):
        s, *d = str(number).partition(".")
        r = ",".join([s[x - 2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
        amt = "".join([r])
        return amt

    @api.model
    def get_claim_count(self):
        claim_status = self.search([])
        #### claimed amount ####
        new_claim_amount = 0
        in_process_claim_amount = 0
        query_claim_amount = 0
        approved_claim_amount = 0
        rejected_claim_amount = 0
        cancelled_claim_amount = 0

        #### pass amount ####
        new_pass_amount = 0
        in_process_pass_amount = 0
        query_pass_amount = 0
        approved_pass_amount = 0
        rejected_pass_amount = 0
        cancelled_pass_amount = 0

        #### lenth ####
        new_claim_len_count = 0
        in_process_claim_len_count = 0
        query_claim_len_count = 0
        approved_claim_len_count = 0
        rejected_claim_len_count = 0
        cancelled_claim_len_count = 0

        new_claim = claim_status.search([
            ('state', '=', 'new'),
        ])
        in_process_claim = claim_status.search([
            ('state', '=', 'in_process'),
        ])
        query_claim = claim_status.search([
            ('state', '=', 'query'),
        ])
        approved_claim = claim_status.search([
            ('state', '=', 'approved'),
        ])
        rejected_claim = claim_status.search([
            ('state', '=', 'rejected'),
        ])
        cancelled_claim = claim_status.search([
            ('state', '=', 'cancelled'),
        ])

        for rec in new_claim:
            new_claim_amount += rec.claimed_amount
            new_pass_amount += rec.passed_amount
            new_claim_len_count += 1

        for rec in in_process_claim:
            in_process_claim_amount += rec.claimed_amount
            in_process_pass_amount += rec.passed_amount
            in_process_claim_len_count += 1

        for rec in query_claim:
            query_claim_amount += rec.claimed_amount
            query_pass_amount += rec.passed_amount
            query_claim_len_count += 1

        for rec in approved_claim:
            approved_claim_amount += rec.claimed_amount
            approved_pass_amount += rec.passed_amount
            approved_claim_len_count += 1

        for rec in rejected_claim:
            rejected_claim_amount += rec.claimed_amount
            rejected_pass_amount += rec.passed_amount
            rejected_claim_len_count += 1

        for rec in cancelled_claim:
            cancelled_claim_amount += rec.claimed_amount
            cancelled_pass_amount += rec.passed_amount
            cancelled_claim_len_count += 1

        data_dct = {
            'new_claim_amount': self.formatINR(new_claim_amount),
            'new_pass_amount': self.formatINR(new_pass_amount),
            'new_claim_len_count': new_claim_len_count,


            'in_process_claim_amount': self.formatINR(in_process_claim_amount),
            'in_process_pass_amount': self.formatINR(in_process_pass_amount),
            'in_process_claim_len_count': in_process_claim_len_count,


            'query_claim_amount': self.formatINR(query_claim_amount),
            'query_pass_amount':self.formatINR(query_pass_amount),
            'query_claim_len_count': query_claim_len_count,


            'approved_claim_amount': self.formatINR(approved_claim_amount),
            'approved_pass_amount': self.formatINR(approved_pass_amount),
            'approved_claim_len_count': approved_claim_len_count,


            'rejected_claim_amount': self.formatINR(rejected_claim_amount),
            'rejected_pass_amount':self.formatINR(rejected_pass_amount),
            'rejected_claim_len_count': rejected_claim_len_count,


            'cancelled_claim_amount': self.formatINR(cancelled_claim_amount),
            'cancelled_pass_amount': self.formatINR(cancelled_pass_amount),
            'cancelled_claim_len_count': cancelled_claim_len_count,

            'currency': self.env.user.company_id.currency_id.symbol,

        }
        return data_dct

