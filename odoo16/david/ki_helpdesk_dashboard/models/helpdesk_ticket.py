from odoo import models, fields, api, _
import calendar
from odoo.tools import populate, groupby
from odoo.tools import OrderedSet, groupby
import datetime
from dateutil import relativedelta


class HelpDeskTicket(models.Model):
    """ Inherited class to get help desk ticket details...."""
    _inherit = 'helpdesk.support'

    is_failed = fields.Boolean(
        'Is Failed?',
        copy=False,
    )

    def set_to_failed(self):
        for rec in self:
            rec.is_failed = True

    @api.model
    def check_user_group(self):
        """Checking user group"""
        user = self.env.user
        if user.has_group('base.group_user'):
            return True
        return False

    @api.model
    def get_tickets_count(self):
        """ Function To Get The Ticket Count"""

        ticket_details = self.env['helpdesk.support'].search([])
        ticket_data = []
        for ticket in ticket_details:
            ticket_data.append({
                'ticket_name': ticket.name,
                'customer_name': ticket.partner_id.name or ' ',
                'subject': ticket.subject or ' ',
                'stage': ticket.stage_id.name or ' ',
                'assigned_to': ticket.user_id.name or ' ',
                'assigned_category': ticket.category or ' ',
            })
        res_obj = self.env['helpdesk.support']
        tickets_new_count = res_obj.search_count(
            [('stage_id.stage_type', '=', 'new')])

        tickets_in_progress_count = res_obj.search_count(
            [('stage_id.stage_type', '=', 'work_in_progress')])
        tickets_closed_count = res_obj.search_count(
            [('stage_id.stage_type', '=', 'closed')])
        very_low_count = res_obj.search_count([
            ('priority', '=', '0')])
        very_low_count1 = very_low_count * 10

        low_count = res_obj.search_count([
            ('priority', '=', '1')])
        low_count1 = low_count * 10
        normal_count = res_obj.search_count([
            ('priority', '=', '2')])
        normal_count1 = normal_count * 10
        high_count = res_obj.search_count([
            ('priority', '=', '3')])
        high_count1 = high_count * 10
        very_high_count = res_obj.search_count([
            ('priority', '=', '4')])
        very_high_count1 = very_high_count * 10

        teams_count = self.env['support.team'].search_count([])

        tickets = res_obj.search(
            [('stage_id.stage_type', '=', 'new')])
        p_tickets = []
        for ticket in tickets:
            p_tickets.append(ticket.name)
        values = {
            'inbox_count': tickets_new_count,
            'progress_count': tickets_in_progress_count,
            'done_count': tickets_closed_count,
            'team_count': teams_count,
            'p_tickets': p_tickets,
            'very_low_count1': very_low_count1,
            'low_count1': low_count1,
            'normal_count1': normal_count1,
            'high_count1': high_count1,
            'very_high_count1': very_high_count1,
            'ticket_details': ticket_data,

        }

        return values

    @api.model
    def get_tickets_all_count(self):
        """ Function To Get The Ticket Count"""
        data_list = []

        teams_ids = self.env['support.team'].search([])
        res_obj = self.env['helpdesk.support']
        for team in teams_ids:
            domain = [('team_id', '=', team.id)]
            failed_count = res_obj.search_count(domain + [
                ('is_failed', '=', True),
            ])

            close_count = res_obj.search_count(domain + [
                ('stage_id.stage_type', '=', 'closed'),
            ])

            unassigned_count = res_obj.search_count(domain + [
                ('user_id', '=', False),
                 ])

            urgent_count = res_obj.search_count(domain + [
                ('priority', '=', 2)
            ])
            open_count = res_obj.search_count(domain)

            data_list.append({
                'team_id': team.id,
                'name': team.name,
                'failed_count': failed_count,
                'unassigned_count': unassigned_count,
                'open_count': open_count,
                'urgent_count': urgent_count,
                'close_count': close_count,
            },
            )
        return data_list

    @api.model
    def get_tickets_view(self):
        """ Function To Get The Ticket View"""
        res_obj = self.env['helpdesk.support']
        tickets_new_count = res_obj.search_count(
            [('stage_id.stage_type', '=', 'new')])
        tickets_in_progress_count = res_obj.search_count(
            [('stage_id.stage_type', '=', 'work_in_progress')])
        tickets_closed_count = res_obj.search_count(
            [('stage_id.stage_type', '=', 'closed')])
        teams_count = self.env['support.team'].search([])

        tickets_new = res_obj.search(
            [('stage_id.stage_type', '=', 'new')])
        tickets_in_progress = res_obj.search(
            [('stage_id.stage_type', '=', 'work_in_progress')])
        tickets_closed = res_obj.search(
            [('stage_id.stage_type', '=', 'closed')])
        teams = self.env['support.team'].search([])

        new_list = []
        progress_list = []
        done_list = []
        teams_list = []

        for new in tickets_new:
            new_list.append(str(new.name) + ' : ' + str(new.subject))
        for progress in tickets_in_progress:
            progress_list.append(
                str(progress.name) + ' : ' + str(progress.subject))
        for done in tickets_closed:
            done_list.append(str(done.name) + ' : ' + str(done.subject))
        for team in teams:
            teams_list.append(team.name)

        tickets = res_obj.search(
            [('stage_id.stage_type', '=', 'new')])
        p_tickets = []
        for ticket in tickets:
            p_tickets.append(ticket.name)

        values = {
            'inbox_count': tickets_new_count,
            'progress_count': tickets_in_progress_count,
            'done_count': tickets_closed_count,
            'team_count': teams_count,

            'new_tkts': new_list,
            'progress': progress_list,
            'done': done_list,
            'teams': teams_list,
            'p_tickets': p_tickets
        }
        return values

    @api.model
    def get_ticket_month_pie(self):
        """pie chart"""
        month_count = []
        month_value = []
        tickets = self.env['helpdesk.support'].search([])
        for rec in tickets:
            month = rec.create_date.month
            if month not in month_value:
                month_value.append(month)
            month_count.append(month)

        month_val = []
        for index in range(len(month_value)):
            value = month_count.count(month_value[index])
            month_name = calendar.month_name[month_value[index]]
            month_val.append({'label': month_name, 'value': value})

        name = []
        for record in month_val:
            name.append(record.get('label'))

        count = []
        for record in month_val:
            count.append(record.get('value'))

        month = [count, name]
        return month

    @api.model
    def get_team_ticket_count_pie(self):
        """bar chart"""
        ticket_count = []
        team_list = []
        tickets = self.env['helpdesk.support'].search([])

        for rec in tickets:
            if rec.team_id:
                team = rec.team_id.name
                if team not in team_list:
                    team_list.append(team)
                ticket_count.append(team)

        team_val = []
        for index in range(len(team_list)):
            value = ticket_count.count(team_list[index])
            team_name = team_list[index]
            team_val.append({'label': team_name, 'value': value})
        name = []
        for record in team_val:
            name.append(record.get('label'))
        #
        count = []
        for record in team_val:
            count.append(record.get('value'))
        #
        team = [count, name]
        return team
