# -*- coding: utf-8 -*-
import urllib
import re
from odoo import http, models, fields, api, tools, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _compute_share_url(self):

        host_url = http.request.httprequest.host_url
        protocol = 'http' if re.search("^http", host_url) else 'https'
        base_url = http.request.httprequest.base_url
        urls = [host_url, base_url]
        protocol_replace = []
        for url in urls:
            protocol_replace.append(url.replace('http' or 'htpps', ''))
        url_format = ''
        dict = {}
        for product in self:
            url_format = urllib.parse.quote_plus(protocol_replace[1].encode('utf8'), safe="")
            url_host = urllib.parse.quote_plus(protocol_replace[0].encode('utf8'), safe="")
            dict.update({
                'facebook': 'https://www.facebook.com/sharer/sharer.php?u={}{}'.format(protocol, url_format.replace('%5C', '')),
                'twitter': 'https://twitter.com/intent/tweet?tw_p=tweetbutton&text=Amazing Product : {}{}'.format(
                    protocol, url_format.replace('%5C', '')),
                'linkedin': 'https://www.linkedin.com/shareArticle?mini=true&url={}{}'.format(protocol,
                                                                                                       url_format.replace(
                                                                                                           '%5C', '')),
                'tumblr': 'http://www.tumblr.com/share/link?url={}{}'.format(protocol,
                                                                                      url_format.replace('%5C', '')),
                'pinterest': 'http://pinterest.com/pin/create/button/?url={}{}&description={} {}{}'.format(
                    protocol, url_format.replace('%5C', ''), 'Amazin Product in', protocol,
                    url_host.replace('%5C', '')),

                })

        return dict