# Copyright 2021 VentorTech OU
# See LICENSE file for full copyright and licensing details.


def migrate(cr, version):
    cr.execute('ALTER TABLE "printnode_account" RENAME COLUMN "username" TO "api_key"')
