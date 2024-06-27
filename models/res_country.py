from odoo import models, fields, api


class ResCountry(models.Model):
    _inherit = "res.country"

    station_ids = fields.One2many("station", "country_id", string="Stations")

    def open_stations(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "По странам",
            "view_mode": "kanban",
            "res_model": "station",
            "limit": 1000,
            "domain": [("country_id", "=", self.id)],
        }