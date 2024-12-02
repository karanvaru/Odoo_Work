# Copyright 2021 VentorTech OU
# See LICENSE file for full copyright and licensing details.

import logging
import requests

from odoo import fields, models, release


_logger = logging.getLogger(__name__)


class PrintNodeRelease(models.Model):
    """
    PrintNode Release entity
    """
    _name = 'printnode.release'
    _description = 'PrintNode Release'

    version = fields.Char(
        string="Module Version",
        readonly=True,
    )

    release_notes = fields.Text(
        string='Release Notes',
        readonly=True
    )

    is_critical_update = fields.Boolean(
        string='Is Critical Update'
    )

    def update_releases(self):
        """
        Fetch releases through API
        """
        # Send request
        dpc_url = self.env['ir.config_parameter'].sudo().get_param('printnode_base.dpc_api_url')
        module_version = self.env['ir.module.module'].search(
            [['name', '=', 'printnode_base']]).latest_version
        odoo_version = release.major_version

        resp = requests.get(
            '{}/{}'.format(dpc_url, 'releases'),
            {'module_version': module_version, 'odoo_version': odoo_version})

        if resp.status_code == 200:
            data = resp.json()
            module_releases = data.get('data', []).get('changelog')

            # Remove old releases
            self.search([]).unlink()

            # Create new releases
            for module_release in module_releases:
                self.create({
                    'version': module_release.get('module_version', ''),
                    'release_notes': module_release.get('release_notes', ''),
                    'is_critical_update': module_release.get('is_critical_update', False),
                })
        else:
            # Something went wrong
            _logger.warning(
                "Direct Print: Can't fetch list of releases ({})".format(resp.status_code))
