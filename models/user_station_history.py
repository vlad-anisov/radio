from odoo import models, fields, api, _


class UserStationHistory(models.Model):
    _name = "user.station.history"

    user_id = fields.Many2one(
        "res.users",
        string="Пользователь",
        required=True,
    )
    station_id = fields.Many2one(
        "station",
        string="Станция",
        required=True,
    )
    datetime = fields.Datetime(string="Дата и время", required=True, default=fields.Datetime.now)
