from odoo import models, fields, api


class ResLang(models.Model):
    _inherit = "res.lang"

    station_ids = fields.Many2many(
        comodel_name="station", relation="res_lang_station_rel", column1="res_lang_id", column2="station_id",
        string="Stations",
    )

    def open_stations(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "По языкам",
            "view_mode": "kanban",
            "res_model": "station",
            "limit": 1000,
            "domain": [("lang_ids", "in", self.id)],
        }