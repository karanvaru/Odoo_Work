# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from geopy.geocoders import Nominatim


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    check_in_latitude = fields.Float(digits="Location", readonly=True)
    check_in_latitude_text = fields.Char(
        "Check-in Latitude", compute="_compute_check_in_latitude_text"
    )
    check_in_longitude = fields.Float(digits="Location", readonly=True)
    check_in_longitude_text = fields.Char(
        "Check-in Longitude", compute="_compute_check_in_longitude_text"
    )
    check_out_latitude = fields.Float(digits="Location", readonly=True)
    check_out_latitude_text = fields.Char(
        "Check-out Latitude", compute="_compute_check_out_latitude_text"
    )
    check_out_longitude = fields.Float(digits="Location", readonly=True)
    check_out_longitude_text = fields.Char(
        "Check-out Longitude", compute="_compute_check_out_longitude_text"
    )
    check_in_address_details = fields.Text(
        string='Check in Address',
        compute="_compute_check_in_address_details",
        store=True,
    )
    response_check_in_address = fields.Text(
        string=' ResponseCheck In Address',
        compute='_compute_check_in_address_details',
        store=True
    )
    check_out_address_details = fields.Text(
        string='Check out Address',
        compute='_compute_check_out_address_details',
        store=True,
    )
    response_check_out_address = fields.Text(
        string='Response Check Out Address',
        compute='_compute_check_out_address_details',
        store=True
    )

    def _get_raw_value_from_geolocation(self, dd):
        d = int(dd)
        m = int((dd - d) * 60)
        s = (dd - d - m / 60) * 3600.00
        z = round(s, 2)
        return "%sº %s' %s'" % (abs(d), abs(m), abs(z))

    def _get_latitude_raw_value(self, dd):
        return "%s %s" % (
            "N" if int(dd) >= 0 else "S",
            self._get_raw_value_from_geolocation(dd),
        )

    def _get_longitude_raw_value(self, dd):
        return "%s %s" % (
            "E" if int(dd) >= 0 else "W",
            self._get_raw_value_from_geolocation(dd),
        )

    @api.depends("check_in_latitude")
    def _compute_check_in_latitude_text(self):
        for item in self:
            item.check_in_latitude_text = (
                self._get_latitude_raw_value(item.check_in_latitude)
                if item.check_in_latitude
                else False
            )

    @api.depends("check_in_longitude")
    def _compute_check_in_longitude_text(self):
        for item in self:
            item.check_in_longitude_text = (
                self._get_longitude_raw_value(item.check_in_longitude)
                if item.check_in_longitude
                else False
            )

    @api.depends("check_in_latitude", "check_in_longitude")
    def _compute_check_in_address_details(self):
        for rec in self:
            if rec.check_in_latitude and rec.check_in_longitude:
                app = Nominatim(user_agent="tutorial")
                aa = app.reverse((rec.check_in_latitude, rec.check_in_longitude), language='en').raw
                rec.check_in_address_details = aa['display_name']
                rec.response_check_in_address = aa
            else:
                rec.check_in_address_details = ''
                rec.response_check_in_address = ''

    @api.depends("check_out_latitude")
    def _compute_check_out_latitude_text(self):
        for item in self:
            item.check_out_latitude_text = (
                self._get_latitude_raw_value(item.check_out_latitude)
                if item.check_out_latitude
                else False
            )

    @api.depends("check_out_longitude")
    def _compute_check_out_longitude_text(self):
        for item in self:
            item.check_out_longitude_text = (
                self._get_longitude_raw_value(item.check_out_longitude)
                if item.check_out_longitude
                else False
            )

    @api.depends("check_out_longitude", "check_out_latitude")
    def _compute_check_out_address_details(self):
        for rec in self:
            if rec.check_out_latitude and rec.check_out_longitude:
                app = Nominatim(user_agent="tutorial")
                aa = app.reverse((rec.check_out_latitude, rec.check_out_longitude), language='en').raw
                rec.check_out_address_details = aa['display_name']
                rec.response_check_out_address = aa
            else:
                rec.check_out_address_details = ''
                rec.response_check_out_address = ''
