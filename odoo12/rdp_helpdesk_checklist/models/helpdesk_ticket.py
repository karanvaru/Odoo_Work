#coding: utf-8

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

STAGEVALIDATIONERRORMESSAGE = _(u"""Please enter check list for the Helpdesk Ticket '{0}'!
You can't move this case forward until you confirm all jobs have been done.""")


class helpdesk_ticket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.multi
    @api.depends("stage_id.default_helpdesk_check_list_ids", "check_list_line_ids")
    def _compute_check_list_len(self):
        """
        Compute method for 'check_list_len'
        """
        for ticket_id in self:
            check_list_len = ticket_id.stage_id and len(ticket_id.stage_id.default_helpdesk_check_list_ids) or 0
            ticket_id.check_list_len = check_list_len
            ticket_id.checklist_progress = check_list_len and (len(ticket_id.check_list_line_ids)/check_list_len)*100 or 0.0


    check_list_line_ids = fields.Many2many(
        "helpdesk.check.list",
        "helpdek_ticket_helpdesk_check_list_rel_table",
        "helpdesk_team_id",
        "helpdesk_check_list_id",
        string="Check list",
        help="Confirm that you finished all the points. Otherwise, you would not be able to move the record forward"
    )
    check_list_history_ids = fields.One2many(
        "helpdesk.check.history",
        "ticket_id",
        string="History",
    )
    check_list_len = fields.Integer(
        string= "Total points",
        compute= _compute_check_list_len,
        store= True,
    )
    checklist_progress = fields.Float(
        string="Progress",
        compute=_compute_check_list_len,
        store=True,
    )

    @api.model
    def create(self, vals):
        """
        Overwrite to check whether the checklist is pre-filled and check whether this user might do that

        Methods:
         * _check_cheklist_rights of check.list
         * _register_history
        """
        task_id = super(helpdesk_ticket, self).create(vals)
        if vals.get("check_list_line_ids"):
            changed_items = self.env["helpdesk.check.list"].browse(vals.get("check_list_line_ids")[0][2])
            changed_items._check_cheklist_rights()
            task_id._register_history(changed_items)
        return task_id

    @api.multi
    def write(self, vals):
        """
        Overwrite to check:
         1. if check item is entered: whether a user has rights for that
         2. if stage is changed: whether a check list is filled (in case of progress)

        Methods:
         * _check_cheklist_rights of check.list
         * _register_history
         * _check_checklist_complete
         * _recover_filled_checklist
        """
        # 1
        if vals.get("check_list_line_ids") and not self.env.context.get("automatic_checks"):
            new_check_line_ids = self.env["helpdesk.check.list"].browse(vals.get("check_list_line_ids")[0][2])
            for ticket_id in self:
                old_check_line_ids = ticket_id.check_list_line_ids
                to_add_items = (new_check_line_ids - old_check_line_ids)
                to_remove_items = (old_check_line_ids - new_check_line_ids)
                changed_items = to_add_items | to_remove_items
                changed_items._check_cheklist_rights()
                ticket_id._register_history(to_add_items, "done")
                ticket_id._register_history(to_remove_items, "reset")
        # 2
        if vals.get("stage_id"):
            self._check_checklist_complete(vals)
            self._recover_filled_checklist(vals.get("stage_id"))

        return super(helpdesk_ticket, self).write(vals)

    @api.multi
    def _register_history(self, changed_items, done_action="done"):
        """
        The method to register check list history by leads

        Args:
         * changed_items - dict of filled in or reset items
         * done_action - either 'done', or 'reset'
        """
        for ticket_id in self:
            for item in changed_items:
                history_item_vals = {
                    "ticket_id": ticket_id.id,
                    "check_list_id": item.id,
                    "done_action": done_action,
                }
                self.env["helpdesk.check.history"].create(history_item_vals)

    @api.multi
    def _check_checklist_complete(self, vals):
        """
        The method to make sure checklist is filled in case of lead progress

        Args:
         * vals - dict of of written values
        """
        if not self.env.user.has_group("helpdesk_checklist.group_helpdesk_checklist_superuser"):
            new_stage_id = self.env["helpdesk.stage"].browse(vals.get("stage_id"))
            for ticket_id in self:
                if new_stage_id.sequence >= ticket_id.stage_id.sequence and not new_stage_id.no_need_for_checklist:
                    entered_len = vals.get("check_list_line_ids") and len(vals.get("check_list_line_ids")) or \
                                  len(ticket_id.check_list_line_ids)
                    required_len = vals.get("check_list_len") and vals.get("check_list_len") or ticket_id.check_list_len
                    if entered_len != required_len:
                        raise ValidationError(STAGEVALIDATIONERRORMESSAGE.format(ticket_id.name))

    @api.multi
    def _recover_filled_checklist(self, stage_id):
        """
        The method to recover already done check list from history

        Args:
         * stage_id - int - new crm.stage.type
        """
        for ticket_id in self:
            to_recover = []
            already_considered = []
            for history_item in ticket_id.check_list_history_ids:
                check_item_id = history_item.check_list_id
                if check_item_id.helpdesk_stage_st_id.id == stage_id \
                        and not check_item_id.should_be_reset \
                        and check_item_id.id not in already_considered \
                        and history_item.done_action == "done":
                    to_recover.append(check_item_id.id)
                already_considered.append(check_item_id.id)
            ticket_id.with_context(automatic_checks=True).check_list_line_ids = [(6, 0, to_recover)]
