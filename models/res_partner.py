# -*- coding: utf-8 -*-

from collections import defaultdict

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends("user_ids.manual_im_status", "user_ids.presence_ids.status", "user_ids")
    def _compute_im_status(self):
        super()._compute_im_status()
        self.user_ids.invalidate_recordset(["manual_im_status"])
        status_by_partner = defaultdict(list)
        presences = self.env["bus.presence"].search([("user_id", "in", self.user_ids.ids)])
        for presence in presences:
            partner = presence.user_id.partner_id
            status_by_partner[partner].append(
                "busy" if presence.user_id.manual_im_status == "busy" else (presence.status or "offline")
            )
        for partner in self:
            if partner.im_status == "bot":
                continue
            all_status = status_by_partner.get(partner, [])
            if "online" in all_status:
                partner.im_status = "online"
            elif "away" in all_status:
                partner.im_status = "away"
            elif "busy" in all_status:
                partner.im_status = "busy"
            elif partner.user_ids:
                partner.im_status = "offline"
            else:
                partner.im_status = "im_partner"
