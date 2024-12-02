# -*- coding: utf-8 -*-
from jinja2.sandbox import SandboxedEnvironment
import logging
import random
import unicodedata
import re
import string
from odoo.exceptions import Warning, ValidationError, UserError
from odoo.tools import ustr
from odoo.http import request
from odoo import release

logger = logging.getLogger(__name__)

RANDOM_PASSWORD_LENGTH = 8
CONF_LINE = re.compile(r'^[^\S^t]+(.+)$')


def remove_empty_lines(data):
    res = ''
    for line in data.split('\n'):
        found = CONF_LINE.search(line)
        if not line:
            continue
        elif not line.strip(' '):
            continue
        elif found:
            new_line = '{}\n'.format(found.groups()[0])
            res += new_line
        else:
            new_line = '{}\n'.format(line)
            res += new_line
    return res


def generate_password(length=RANDOM_PASSWORD_LENGTH):
    chars = string.ascii_letters + string.digits
    password = ''
    while True:
        password = ''.join(map(lambda x: random.choice(chars), range(length)))
        if filter(lambda c: c.isdigit(), password) and \
                filter(lambda c: c.isalpha(), password):
            break
    return password


def slugify(s, max_length=None):
    s = ustr(s)
    uni = unicodedata.normalize('NFKD', s).encode(
                                            'ascii', 'ignore').decode('ascii')
    slug_str = re.sub('[\W_]', ' ', uni).strip().lower()
    slug_str = re.sub('[-\s]+', '-', slug_str)
    return slug_str[:max_length]


def is_debug_mode_enabled():
    try:
        debug = request.session.debug if release.version_info[0] >= 13 \
            else request.debug
        return debug
    except RuntimeError:
        pass


def render_conf_template(template_txt, obj):
    template_env = SandboxedEnvironment(
        lstrip_blocks=True,
        keep_trailing_newline=True,
        autoescape=False
    )
    template = template_env.from_string(ustr(template_txt))
    variables = {'object': obj}
    return template.render(variables)


def get_default_server(element):
    servers = element.env['asterisk_base.server'].search([])
    if len(servers) == 1:
        return servers[0].id
