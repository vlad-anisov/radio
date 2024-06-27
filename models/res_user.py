from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = "res.users"

    station_ids = fields.Many2many(comodel_name="station", relation="res_users_station_rel", column1="user_id",
                                   column2="station_id", string="Stations")
    station_history_ids = fields.One2many("user.station.history", "user_id", string="История прослушивания станций")