# -*- coding: utf-8 -*-
from odoo import models


class BusPresence(models.Model):
    _inherit = "bus.presence"

    def _send_presence(self, im_status=None, bus_target=None):
        """Force a fresh read of the DND override before broadcasting.

        In multi-worker/gevent deployments, the long-lived websocket worker
        can hold on to an Environment whose cached ``manual_im_status`` value
        predates a very recent DND toggle (handled by a different HTTP
        worker). Without this, the bus notification pushed right after a
        page refresh can briefly report the raw presence status (e.g.
        "online") instead of "busy", causing the status icon to flash before
        self-correcting on the next update. Invalidating here forces the
        override to be re-read from the database instead of any stale
        in-process cache.
        """
        users = self.mapped("user_id")
        if users:
            users.invalidate_recordset(["manual_im_status"])
            users.partner_id.invalidate_recordset(["im_status"])
        return super()._send_presence(im_status=im_status, bus_target=bus_target)
