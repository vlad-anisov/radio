from odoo import models, fields, api, _
import pyradios
import requests
import base64
from odoo.exceptions import UserError
from odoo.tools.image import image_process
from odoo.http import request


class Station(models.Model):
    _name = "station"

    name = fields.Char(string="Название")
    url = fields.Char(string="URL")
    country_id = fields.Many2one("res.country", string="Страна")
    state_id = fields.Many2one("res.country.state", string="Область")
    favicon = fields.Image(string="Иконка", max_width=512, max_height=512)
    lang_ids = fields.Many2many(
        comodel_name="res.lang", relation="res_lang_station_rel", column1="station_id", column2="res_lang_id",
        string="Языки",
    )
    homepage = fields.Char(string="Домашняя страница")
    tags = fields.Char(string="Теги")
    votes = fields.Integer(string="Рейтинг")
    user_ids = fields.Many2many(
        comodel_name="res.users", relation="res_users_station_rel", column1="station_id", column2="user_id",
        string="Пользователи",
    )
    is_favorite = fields.Boolean(string="Избранное", compute="_compute_is_favorite")
    countdown = fields.Float(string="Оставшийся срок")
    listening_datetime = fields.Datetime(string="Дата последнего прослушивания", compute="_compute_listening_datetime")

    def _compute_listening_datetime(self):
        for record in self:
            record.listening_datetime = self.env["user.station.history"].search(
                [("station_id", "=", record.id), ("user_id", "=", self.env.user.id)], order="datetime desc", limit=1
            ).datetime

    def _compute_is_favorite(self):
        for record in self:
            record.is_favorite = self.env.user in record.user_ids

    def fetch_all_stations(self):
        try:
            self.search([]).unlink()
            rb = pyradios.RadioBrowser()
            stations = rb.stations()
            for station in stations[:1000]:
                if station["favicon"]:
                    try:
                        favicon = base64.b64encode(requests.get(station["favicon"].strip(), timeout=10).content).replace(
                            b"\n", b"")
                        img = base64.b64decode(favicon or '') or False
                        base64.b64encode(image_process(img, size=(512, 512), verify_resolution=True) or b'')
                    except Exception:
                        favicon = False
                else:
                    favicon = False
                if not favicon:
                    continue

                if not station["url"]:
                    continue

                country_id = self.env["res.country"].search([("code", "=", station["countrycode"])], limit=1)

                state_id = self.env["res.country.state"]
                if country_id:
                    state_id = self.env["res.country.state"].search(
                        [("name", "=", station["state"]), ("country_id", "=", country_id.id)], limit=1
                    )
                    if not state_id:
                        code_id = self.env["res.country.state"].search(
                            [("code", "=", station["state"]), ("country_id", "=", country_id.id)], limit=1
                        )
                        if code_id:
                            code = station["state"] + " "
                        else:
                            code = station["state"]

                        state_id = self.env["res.country.state"].create({
                            "name": station["state"],
                            "code": code,
                            "country_id": country_id.id,
                        })

                lang_ids = self.env["res.lang"]
                if station.get("languagecodes"):
                    for lang_code in station.get("languagecodes").split(","):
                        lang_id = self.env["res.lang"].with_context(active_test=False).search(
                            [("iso_code", "=", lang_code)], limit=1)
                        lang_id.active = True
                        lang_ids |= lang_id
                if station.get("language"):
                    lang_id = self.env["res.lang"].with_context(active_test=False).search(
                        [("iso_code", "=", station.get("language"))], limit=1)
                    lang_id.active = True
                    lang_ids |= lang_id


                self.create({
                    "name": station["name"],
                    "url": station["url"],
                    "country_id": country_id.id,
                    "state_id": state_id.id,
                    "favicon": favicon,
                    "lang_ids": lang_ids.ids,
                    "homepage": station.get("homepage", ""),
                    "tags": station.get("tags", ""),
                    "votes": station.get("votes", 0),
                })
        except Exception as e:
            print(e)

    def open_homepage(self):
        # self.fetch_all_stations()
        self.ensure_one()
        if not self.homepage:
            raise UserError(_('No homepage defined for this station.'))
        return {
            "type": "ir.actions.act_url",
            "url": self.homepage,
            "target": "new",
        }

    def change_station(self):
        request.future_response.set_cookie("id_station", str(self.id))
        request.future_response.set_cookie("station_name", self.name.encode('utf-8'))
        request.future_response.set_cookie("station_favicon", f"/web/image?model=station&id={self.id}&field=favicon")
        request.future_response.set_cookie("station_url", self.url)
        history_id = self.env["user.station.history"].search([("station_id", "=", self.id), ("user_id", "=", self.env.user.id)], order="datetime desc", limit=1)
        if not history_id:
            self.env["user.station.history"].create({
                "station_id": self.id,
                "user_id": self.env.user.id,
                "datetime": fields.Datetime.now(),
            })
        else:
            history_id.write({
                "datetime": fields.Datetime.now(),
            })

    def open_station(self):
        return {
            "type": "ir.actions.act_window",
            "name": self.name,
            "res_model": "station",
            "views": [[False, "form"]],
            "res_id": self.id,
            "target": "current",
        }

    @api.model
    def open_running_station(self):
        id_station = int(request.httprequest.cookies.get("id_station", 10565))
        station_id = self.browse(id_station)
        return {
            "type": "ir.actions.act_window",
            "name": station_id.name,
            "res_model": "station",
            "views": [[False, "form"]],
            "res_id": station_id.id,
            "target": "current",
        }

    def read(self, fields=None, load="_classic_read"):
        if self.env.context.get("country_filter"):
            country_id = self.env.user.country_id
            self = self.filtered(lambda s: s.country_id == country_id)
        if self.env.context.get("listened_filter"):
            self = self.env.user.station_history_ids.sorted(lambda s: s.datetime, reverse=True).station_id
        return super(Station, self).read(fields, load)

    def add_to_favorite(self):
        self.ensure_one()
        self.user_ids = [(4, self.env.user.id)]

    def remove_from_favorite(self):
        self.ensure_one()
        self.user_ids = [(3, self.env.user.id)]

