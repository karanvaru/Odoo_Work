# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################
from odoo.tools.misc import ustr
from lxml.builder import E
from lxml import etree
from odoo import api, models, fields, tools, _
from odoo.tools import config
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.exceptions import UserError, ValidationError
# Libs for safe_eval
import datetime
import time
from pytz import timezone

import logging

_logger = logging.getLogger(__name__)


class MultiApprovalType(models.Model):
    _inherit = 'multi.approval.type'
    _order = 'priority'

    apply_for_model = fields.Boolean('Apply for Model?')
    is_configured = fields.Boolean('Configured?', copy=False)
    approve_python_code = fields.Text('Approved Action')
    refuse_python_code = fields.Text('Refused Action')

    domain = fields.Text(default='[]', string='Domain')
    model_id = fields.Selection(selection='_list_all_models', string='Model')
    view_id = fields.Many2one('ir.ui.view', string='Extension View')
    is_free_create = fields.Boolean('Free Create?')
    hide_button = fields.Boolean('Hide Buttons from Model View?')
    state_field_id = fields.Many2one(
        'ir.model.fields', string="State / Stage Field")
    state_field = fields.Char()
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company')
    group_ids = fields.Many2many(
        'res.groups', 'ma_type_group_rel', 'ma_type_id', 'group_id',
        string="Groups")
    is_global = fields.Boolean(
        compute="_compute_global", store=True)
    priority = fields.Integer(default=100)

    @api.model
    def _get_default_description(self):
        return '''
        Hi,
        </br> </br>
        Please review my request.</br> 
        Click <a target="__blank__" href="{record_url}"> {record.display_name}</a> to view more !
        </br> </br>
        Thanks,
        '''
    request_tmpl = fields.Html(default=_get_default_description)

    @api.constrains('approve_python_code', 'refuse_python_code')
    def _check_python_code(self):
        for rec in self.sudo().filtered('approve_python_code'):
            try:
                msg = test_python_expr(expr=rec.approve_python_code.strip(),
                                       mode="exec")
            except:
                raise ValidationError(_('Invalid python syntax'))
            if msg:
                raise ValidationError(msg)
        for rec in self.sudo().filtered('refuse_python_code'):
            try:
                msg = test_python_expr(expr=rec.refuse_python_code.strip(),
                                       mode="exec")
            except:
                raise ValidationError(_('Invalid python syntax'))
            if msg:
                raise ValidationError(msg)

    @api.depends('group_ids')
    def _compute_global(self):
        for rule in self:
            rule.is_global = not rule.group_ids

    @api.model
    def _get_types(self, model_name):
        type_ids = self._fetch_types(model_name)
        res = self.browse(type_ids)
        return res

    @api.model
    @tools.conditional(
        'xml' not in config['dev_mode'],
        tools.ormcache('self.env.uid', 'self.env.user.company_id.id',
                       'self.env.su', 'model_name'),
    )
    def _fetch_types(self, model_name):
        """
        Returns all the types matching the model
        """
        # if self.env.su:
        #    return self.browse(())
        query = """
            SELECT t.id FROM multi_approval_type t
            WHERE t.model_id='{model_name}'
                AND t.active
                AND t.is_configured
                AND (t.id IN (
                        SELECT ma_type_id
                        FROM ma_type_group_rel mg
                        JOIN res_groups_users_rel gu
                            ON (mg.group_id=gu.gid)
                        WHERE gu.uid={uid})
                    OR t.is_global)
                AND (t.company_id ISNULL
                    OR t.company_id={company_id})
            ORDER BY t.priority, t.id
        """.format(model_name=model_name, uid=self.env.uid,
                   company_id=self.env.user.company_id.id)
        self._cr.execute(query)
        res = [row[0] for row in self._cr.fetchall()]
        return res

    def _compute_domain_keys(self):
        """
        Return the list of context keys to use for caching ``_compute_domain``.
        """
        return ['allowed_company_ids']

    def _compute_domain_context_values(self):
        for k in self._compute_domain_keys():
            v = self._context.get(k)
            if isinstance(v, list):
                v = tuple(v)
            yield v

    @api.model
    @tools.conditional(
        'xml' not in config['dev_mode'],
        tools.ormcache('self.env.uid', 'self.env.user.company_id.id',
                       'self.env.su', 'model_name',
                       'tuple(self._compute_domain_context_values())'),
    )
    def _compute_domain(self, model_name):
        rules = self._get_types(model_name)
        if not rules:
            return []

        # browse user and rules as SUPERUSER_ID to avoid access errors!
        all_domains = []                     # list of domains
        for rule in rules.sudo():
            # evaluate the domain for the current user
            dom = safe_eval(rule.domain) if rule.domain else []
            dom = expression.normalize_domain(dom)
            all_domains.append(dom)

        # combine global domains and group domains
        return expression.OR(all_domains)

    @api.model
    def domain_get(self, model_name, get_not=False):
        dom = self._compute_domain(model_name)
        if dom and get_not:
            return expression.AND(['!'] + [dom])
        return dom

    def unlink(self):
        res = super(MultiApprovalType, self).unlink()
        self.clear_caches()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super(MultiApprovalType, self).create(vals_list)
        self.clear_caches()
        return res

    def write(self, vals):
        res = super(MultiApprovalType, self).write(vals)
        self.clear_caches()
        return res

    @api.onchange('apply_for_model')
    def _reset_values(self):
        if self.apply_for_model:
            self.document_opt = 'Optional'
            self.contact_opt = 'None'
            self.date_opt = 'None'
            self.period_opt = 'None'
            self.item_opt = 'None'
            self.quantity_opt = 'None'
            self.amount_opt = 'None'
            self.reference_opt = 'None'
            self.payment_opt = 'None'
            self.location_opt = 'None'

    def action_archive(self):
        res = super(MultiApprovalType, self).action_archive()
        # Untick "Is Config?"
        # Delete view
        for r in self:
            r = r.sudo()
            vals = {
                'is_configured': False,
                'state_field_id': False,
                'state_field': False
            }
            view = None
            if r.view_id:
                vals.update({'view_id': False})
                view = r.view_id
            r.write(vals)
            if view:
                # search
                args = [('view_id', '=', view.id),
                        ('id', '!=', r.id)]
                exist = self.search(args, limit=1)
                if not exist:
                    view.unlink()
        return res

    @api.model
    def _list_all_models(self):
        lang = self.env.lang or 'en_US'
        self._cr.execute(
            "SELECT model, COALESCE(name->>%s, name->>'en_US') FROM ir_model ORDER BY 2",
            [lang],
        )
        return self._cr.fetchall()

    def open_submitted_request(self):
        self.ensure_one()
        view_id = self.env.ref(
            'multi_level_approval.multi_approval_view_form', False)
        res = {
            'name': _('Submitted Requests'),
            'view_mode': 'tree,form',
            'res_model': 'multi.approval',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('type_id', '=', self.id), ('state', '=', 'Submitted')],
        }
        if not self.apply_for_model:
            res.update({'context': {
                'default_type_id': self.id,
            }})
        return res

    def _domain(self):
        self.ensure_one()
        dmain = safe_eval(self.domain)
        return dmain

    def create_fields(self, f_names, model_id):
        ResField = self.env['ir.model.fields']
        for f_name, ttype in f_names.items():
            field_record = ResField._get(self.model_id, f_name)
            if not field_record:
                f_vals = {
                    'name': f_name,
                    'field_description': f_name,
                    'ttype': ttype,
                    'copied': False,
                    'model_id': model_id}
                ResField.create(f_vals)

    def get_compute_val(self, f_name):
        vals = '''
for rec in self:
  rec['{f_name}'] = rec.env['multi.approval.type'].compute_need_approval(rec)
        '''.format(f_name=f_name)
        return vals

    def create_compute_field(self, f_name, model_id):
        ResField = self.env['ir.model.fields']
        compute_f = ResField._get(self.model_id, f_name)
        compute_val = self.get_compute_val(f_name)
        if not compute_f:
            f_vals = {
                'name': f_name,
                'field_description': f_name,
                'ttype': 'boolean',
                'copied': False,
                'store': False,
                'model_id': model_id,
                'compute': compute_val
                }
            ResField.create(f_vals)
        else:
            # Update compute function
            compute_f.write({'compute': compute_val})

    def get_default_view(self):
        view_id = self.env['ir.ui.view'].default_view(self.model_id, 'form')
        return view_id

    def get_existed_view(self):
        self.ensure_one()
        args = [('model_id', '=', self.model_id),
                ('view_id', '!=', False)]
        exist = self.search(args, limit=1)
        return exist.view_id

    def create_view(self, f_name, f_name1, f_name2):
        '''
        1. Find a base view
        2. Check if it has a header path already?
        3. If not, create new header path
        4. Insert 2 button inside the header path
            - Request Approval: if there is no request yet
            - View Approval: if already has some
        '''
        if self.view_id:
            return False
        existed_view = self.get_existed_view()
        if existed_view:
            self.view_id = existed_view
            return False
        IrView = self.env['ir.ui.view']
        model_id = self.env['ir.model']._get_id(self.model_id)
        view_id = self.get_default_view()
        if not view_id:
            raise UserError(_('This model has no form view !'))
        view_content = self.env[self.model_id]._get_view(view_id)
        view_arch = view_content[0]
        node = IrView.locate_node(
            view_arch,
            E.xpath(expr="//form/header"),
        )
        wiz_act = self.env.ref(
            'multi_level_approval_configuration.request_approval_action',
            False)
        wiz_view_act = self.env.ref(
            'multi_level_approval_configuration.action_open_request', False)
        wiz_rework_act = self.env.ref(
            'multi_level_approval_configuration.rework_approval_action', False)
        if not wiz_act or not wiz_view_act or not wiz_rework_act:
            raise UserError(_('Not found the action !'))

        f_node = E.field(name=f_name, invisible="1")
        f1_node = E.field(name=f_name1, invisible="1")
        f2_node = E.field(name=f_name2, invisible="1")
        btn_req_node = E.button(
            {'class': "oe_highlight", 'approval_btn': '1'},
            name=str(wiz_act.id),
            type="action",
            string="Request Approval",
            # groups="multi_level_approval.group_approval_user",
            attrs=str({
                'invisible': ['|', (f_name, '=', False), (f_name2, '=', True)]
            }),
        )
        btn_vie_node = E.button(
            {'approval_btn': '1'},
            name=str(wiz_view_act.id),
            type="action",
            string="View Approval",
            # groups="multi_level_approval.group_approval_user",
            attrs=str({
                'invisible': [(f_name2, '=', False)]
            })
        )
        btn_refuse_node = E.button(
            {'approval_btn': '1'},
            name=str(wiz_rework_act.id),
            type="action",
            string="Rework",
            # groups="multi_level_approval.group_approval_user",
            attrs=str({
                'invisible': [(f_name1, '!=', 'refused')]
            })
        )

        # div is insert right after the header
        div_node1 = E.div(
            'This document need to be approved !',
            {'class': "alert alert-info", 'style': 'margin-top: 5px;',
             'role': 'alert'},
            attrs=str({
                'invisible': ['|', (f_name, '=', False), (f_name1, '!=', False)]
            })
        )
        div_node2 = E.div(
            'This document has been approved !',
            {'class': "alert alert-info", 'style': 'margin-top: 5px;',
             'role': 'alert'},
            attrs=str({
                'invisible': ['|', (f_name, '=', False), (f_name1, '!=', 'approved')]
            })
        )
        div_node3 = E.div(
            'This document has been refused !',
            {'class': "alert alert-danger", 'style': 'margin-top: 5px;',
             'role': 'alert'},
            attrs=str({
                'invisible': ['|', (f_name, '=', False), (f_name1, '!=', 'refused')]
            })
        )
        div_node = E.div(
            div_node1,
            div_node2,
            div_node3
        )

        # Create header tag if there is not yet
        if node is None:
            header_node = E.header(
                f_node,
                f1_node,
                f2_node,
                btn_req_node,
                btn_vie_node,
                btn_refuse_node
            )
            # find a sheet
            sheet_node = IrView.locate_node(
                view_arch,
                E.xpath(expr="//form/sheet"),
            )
            expr = "//form/sheet"
            position = "before"
            if sheet_node is None:
                expr = "//form"
                position = "inside"
            xml = E.xpath(
                header_node,
                div_node,
                expr=expr, position=position)
        else:
            xml0 = E.xpath(
                f_node,
                f1_node,
                f2_node,
                btn_req_node,
                btn_vie_node,
                btn_refuse_node,
                expr="//form/header", position="inside")
            xml1 = E.xpath(
                div_node,
                expr="//form/header", position="after")
            xml = E.data(
                xml0,
                xml1
            )
        xml_content = etree.tostring(
            xml, pretty_print=True, encoding="unicode")
        new_view_name = 'approval_view_' + fields.Datetime.now().strftime(
            '%Y%m%d%H%M%S')
        new_view = IrView.create({
            'name': new_view_name,
            'model': self.model_id,
            'inherit_id': view_id,
            'arch': xml_content})

        # create new field for model
        self.env['ir.model.data'].create({
            'module': 'multi_level_approval_configuration',
            'name': new_view_name,
            'model': 'ir.ui.view',
            'noupdate': True,
            'res_id': new_view.id,
        })
        self.view_id = new_view

    def check_state_field(self):
        '''
        if no state field is detected, return a window action
        '''
        if self.state_field_id:
            if not self.state_field:
                self.state_field = self.state_field_id.name
            return False
        dmain = self._domain()
        if not dmain:
            raise UserError(_('Domain is required !'))
        potential_f = ['state', 'state_id', 'stage', 'stage_id', 'status',
                       'status_id']
        state_field = ''
        dmain_fields = []
        for d in dmain:
            if not d or not isinstance(d, (list, tuple)):
                continue
            dmain_fields += [d[0]]
            if d[0] in potential_f:
                state_field = d[0]
                break
        if state_field:
            ResField = self.env['ir.model.fields']
            field_record = ResField._get(self.model_id, state_field)
            self.write({
                'state_field_id': field_record.id,
                'state_field': state_field
            })
        else:
            view = self.env.ref('multi_level_approval_configuration.multi_approval_type_view_form_popup')
            ResModel = self.env['ir.model']
            model_id = ResModel._get_id(self.model_id)
            ctx = {
                'dmain_fields': dmain_fields,
                'res_model_id': model_id
            }
            return {
                'name': _('Select State Field'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'multi.approval.type',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'res_id': self.id,
                'target': 'new',
                'context': ctx,
            }

    def action_configure(self):
        self.ensure_one()
        self = self.sudo()
        if not self.active:
            return False
        ResModel = self.env['ir.model']

        # Check state / stage field
        ret_act = self.check_state_field()
        if ret_act:
            return ret_act

        # Create new fields
        f_name_dict = {
            'x_review_result': 'char',
            'x_has_request_approval': 'boolean'
        }
        f_names = ['x_review_result', 'x_has_request_approval']
        model_id = ResModel._get_id(self.model_id)
        self.create_fields(f_name_dict, model_id)

        # Create compute field
        compute_field = 'x_need_approval'
        self.create_compute_field(compute_field, model_id)

        # create extension view
        self.create_view(compute_field, f_names[0], f_names[1])
        self.is_configured = True

    @api.model
    def compute_need_approval(self, rec):
        dmain = self.domain_get(rec._name)
        if not dmain:
            return False
        dmain = [('id', '=', rec.id)] + dmain
        try:
            res = rec.sudo().search_count(dmain)
            if res:
                return True
        except ValueError:
            _logger.error(_('Domain of an Approval type is not set properly!'))
        return False

    @api.model
    def update_x_field(self, obj, fi, val=True):
        if hasattr(obj, fi):
            obj.sudo().write({fi: val})
        else:
            raise UserError(_('Something wrong !'))

    @api.model
    def _get_eval_context(self, record=None):
        """ evaluation context to pass to safe_eval """
        if not record:
            raise UserError (_('Something is wrong !'))
        def log(message, level="info"):
            message = str(message)
            with self.pool.cursor() as cr:
                cr.execute("""
                    INSERT INTO ir_logging(create_date, create_uid, type, dbname, name, level, message, path, line, func)
                    VALUES (NOW() at time zone 'UTC', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (self.env.uid, 'server', self._cr.dbname, __name__, level, message, "approval", record.id, record.name))

        model_name = record._name
        model = self.env[model_name]
        ctx = self._context.copy()
        ctx.update({'run_python_code': 1})
        eval_context = {
            'uid': self._uid,
            'user': self.env.user,
            # orm
            'env': self.env,
            'model': model,
            # Exceptions
            'UserError': UserError,
            # record
            'record': record.with_context(ctx),
            # helpers
            'log': log,
        }
        return eval_context

    def run(self, record=None, action='approve'):
        """
        """
        res = False
        for rec in self:
            if record.x_need_approval:
                res = rec._run(record, action)
        return res

    def _run(self, record, action):
        self.ensure_one() 
        res = False
        func_name = 'get_action_%s_code' % action
        if hasattr(self, func_name):
            func = getattr(self, func_name)
            python_code = func(action)
            if not python_code:
                return res
            eval_context = self._get_eval_context(record)
            res = self.exec_func(python_code, eval_context)
        return res

    def get_action_approve_code(self, action):
        return self.approve_python_code

    def get_action_refuse_code(self, action):
        return self.refuse_python_code

    @api.model
    def exec_func(self, python_code='', eval_context=None):
        try:
            safe_eval(python_code.strip(), eval_context, mode="exec",
                      nocopy=True)  # nocopy allows to return 'action'
        except Exception as e:
            raise UserError(ustr(e))
        except:
            raise UserError(_('''
Approval Type is not configured properly, contact your administrator for help!
'''))
        if 'action' in eval_context:
            return eval_context['action']

    @api.model
    @tools.ormcache()
    def _get_applied_models(self):
        args = [('is_configured', '=', True)]
        types = self.search(args)
        model_names = types.mapped('model_id')
        return model_names

    @api.model
    def check_rule(self, records, vals):
        '''
        1. Get approval type if possible
        2. check (not x_review_result and x_need_approval)
        3. prevent from editing the fields in domain
        '''
        if self.env.su or self._context.get('run_python_code'):
            return True
        # Find the approval type
        model_name = records._name
        if model_name in ('multi.approval.type', 'ir.module.module'):
            return True
        available_models = self._get_applied_models()
        if model_name not in available_models:
            return True
        approval_types = self._get_types(model_name)
        if not approval_types:
            return True
        approval_type = approval_types[0]
        for rec in records:
            if not rec.x_need_approval or rec.x_review_result == 'approved':
                continue
            if rec.x_review_result == 'refused':
                raise UserError(self._make_err_msg(True))
            # Could not update state field
            if approval_type.state_field and approval_type.state_field in vals:
                raise UserError(self._make_err_msg())
        return True

    def _make_err_msg(self, refused=False):
        error = _('This document need to be approved by manager !')
        if refused:
            error = _('This document has been refused by manager !')
        return error

    @api.model
    def filter_type(self, types, model_name, res_id):
        for t in types:
            args = t._domain() or []
            args = expression.AND([args] + [[('id', '=', res_id)]])
            existed = self.env[model_name]._search(args, limit=1)
            if existed:
                return t
        return self
