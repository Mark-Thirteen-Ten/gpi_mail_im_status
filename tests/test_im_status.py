from unittest.mock import patch

from odoo.tests import HttpCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestImStatus(HttpCase):
    def test_dnd_survives_reload(self):
        user = new_test_user(
            self.env, login="gpi_dnd_user", context={"no_reset_password": True}
        )
        other_user = new_test_user(
            self.env, login="gpi_other_user", partner_id=user.partner_id.id,
            context={"no_reset_password": True},
        )
        presences = self.env["bus.presence"]
        for account in user | other_user:
            presences._update_presence(0, "user_id", account.id)
        self.authenticate(user.login, user.login)
        self.make_jsonrpc_request("/mail/set_manual_im_status", {"status": "busy"})

        # Refresh initializes the UI from the partner, not res.users.im_status.
        self.assertEqual(
            self.make_jsonrpc_request("/mail/init_messaging", {})["current_partner"]["im_status"],
            "busy",
        )
        self.env.invalidate_all()
        self.assertEqual(user.manual_im_status, "busy")
        self.assertEqual(user.im_status, "busy")
        presence = presences.search([("user_id", "=", user.id)])
        for status in ("offline", "online", "away"):
            presence.status = status
            with patch.object(type(self.env["bus.bus"]), "_sendone") as send:
                presence._send_presence(bus_target=user.partner_id)
            self.assertEqual(send.call_args.args[2]["im_status"], "busy")

        # DND is a saved choice, even if presence cleanup removes the row.
        presences.search([("user_id", "in", (user | other_user).ids)]).unlink()
        self.assertEqual(
            self.make_jsonrpc_request("/mail/init_messaging", {})["current_partner"]["im_status"],
            "busy",
        )
        self.make_jsonrpc_request("/mail/set_manual_im_status", {"status": "online"})
        self.env.invalidate_all()
        self.assertFalse(user.manual_im_status)
        self.assertEqual(user.partner_id.im_status, "offline")
        presences._update_presence(0, "user_id", user.id)
        self.assertEqual(user.partner_id.im_status, "online")
