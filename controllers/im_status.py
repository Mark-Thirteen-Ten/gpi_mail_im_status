# -*- coding: utf-8 -*-

from odoo import _, http
from odoo.http import request


class ImStatusController(http.Controller):
    @http.route("/mail/set_manual_im_status", methods=["POST"], type="json", auth="user")
    def set_manual_im_status(self, status):
        if status not in ["online", "away", "busy", "offline"]:
            raise ValueError(_("Unexpected IM status %(status)s", status=status))
        user = request.env.user
        user.manual_im_status = "busy" if status == "busy" else False
        presence = request.env["bus.presence"].sudo().search([("user_id", "=", user.id)], limit=1)
        request.env["bus.bus"]._sendone(
            (user.partner_id, "presence"),
            "bus.bus/im_status_updated",
            {
                "debounce": False,
                "presence_status": presence.status if presence else "offline",
                "im_status": user.partner_id.im_status,
                "partner_id": user.partner_id.id,
            },
        )
