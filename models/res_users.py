# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    manual_im_status = fields.Selection(
        [("away", "Away"), ("busy", "Do Not Disturb"), ("offline", "Offline")],
        string="IM status manually set by the user",
    )
    presence_ids = fields.One2many("bus.presence", "user_id", string="Presences")

    @api.depends("manual_im_status", "presence_ids.status")
    def _compute_im_status(self):
        # Force a fresh read of the DND override: in multi-worker/gevent
        # deployments a long-lived Environment can otherwise serve a cached
        # value that predates a very recent DND toggle made by another
        # worker, causing the status to briefly appear "online".
        self.invalidate_recordset(["manual_im_status"])
        presence_by_user = {
            presence.user_id: presence.status
            for presence in self.env["bus.presence"].search([("user_id", "in", self.ids)])
        }
        for user in self:
            presence_status = presence_by_user.get(user, "offline")
            user.im_status = "busy" if user.manual_im_status == "busy" else (presence_status or "offline")
