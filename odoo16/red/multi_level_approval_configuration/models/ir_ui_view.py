# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################
import json
from lxml import etree
from odoo import api, fields, models, tools, _


class View(models.Model):
    _inherit = 'ir.ui.view'

    @api.model
    def set_modified_invisible(self, ele, invi_dm):
        if ele.get("modifiers"):
            modifiers = json.loads(ele.get("modifiers"))
        else:
            modifiers = {}
        if modifiers.get('invisible') and isinstance(
                modifiers['invisible'], bool):
            return
        if modifiers.get('invisible') and isinstance(
                modifiers['invisible'], (list, tuple)):
            modifiers['invisible'] = ['|', '&'] + invi_dm + modifiers['invisible']
        else:
            modifiers['invisible'] = invi_dm
        ele.set("modifiers", json.dumps(modifiers))

    @api.model
    def postprocess_and_fields(self, node, model=None, **options):
        '''
        1. check if the view loads x_need_approval and x_review_result
        2. check if the approval type is working
        3. add/update the 'modifiers': invisible for the button
        '''
        arch, fs = super(View, self).postprocess_and_fields(
            node, model, **options)
        if node.tag not in ('kanban', 'tree', 'form'):
            return arch, fs
        if 'x_need_approval' not in fs.get(model, set()) or \
                'x_review_result' not in fs.get(model, set()):
            return arch, fs

        # Find the approval type
        approval_types = self.env['multi.approval.type']._get_types(model)
        if not approval_types or all(
                not x.hide_button for x in approval_types):
            return arch, fs

        doc = etree.XML(arch)

        invi_dm = [('x_need_approval', '=', True),
                   ('x_review_result', 'in', ('refused', False))]

        for btn in doc.xpath("//button"):
            if btn.get('approval_btn'):
                continue
            self.set_modified_invisible(btn, invi_dm)

        arch = etree.tostring(doc, encoding='unicode')
        return arch, fs
