# -*- coding: utf-8 -*-

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends("user_ids.manual_im_status", "user_ids.presence_ids.status", "user_ids")
    def _compute_im_status(self):
        super()._compute_im_status()
        self.user_ids.invalidate_recordset(["manual_im_status"])
        for partner in self:
            # A saved DND choice must not depend on a transient presence row.
            if partner.im_status != "bot" and any(
                user.manual_im_status == "busy" for user in partner.user_ids
            ):
                partner.im_status = "busy"
