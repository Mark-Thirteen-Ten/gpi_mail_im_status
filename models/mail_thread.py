# -*- coding: utf-8 -*-
from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_thread_by_inbox(self, message, recipients_data, msg_vals=False, **kwargs):
        """Override to suppress real-time bus push for DND (busy) users.

        The mail.notification records are still created so the messages appear
        in the user's inbox when they exit DND and refresh. Only the live
        bus push (which drives the inbox counter badge) is suppressed.
        """
        # Find all partner IDs whose linked user has manual DND status
        dnd_partner_ids = set(
            self.env['res.users'].sudo()
            .search([('manual_im_status', '=', 'busy')])
            .mapped('partner_id')
            .ids
        )

        if not dnd_partner_ids:
            return super()._notify_thread_by_inbox(
                message, recipients_data, msg_vals=msg_vals, **kwargs
            )

        # Separate inbox recipients into DND and non-DND groups
        non_dnd_recipients = [
            r for r in recipients_data if r['id'] not in dnd_partner_ids
        ]
        dnd_inbox_pids = [
            r['id'] for r in recipients_data
            if r['notif'] == 'inbox' and r['id'] in dnd_partner_ids
        ]

        # Normal flow for non-DND recipients (creates notifications + sends bus)
        super()._notify_thread_by_inbox(
            message, non_dnd_recipients, msg_vals=msg_vals, **kwargs
        )

        # For DND recipients: create the mail.notification record so the message
        # appears in inbox when they come back, but do NOT send a bus push.
        if dnd_inbox_pids:
            notif_create_values = [{
                'author_id': message.author_id.id,
                'mail_message_id': message.id,
                'notification_status': 'sent',
                'notification_type': 'inbox',
                'res_partner_id': pid,
            } for pid in dnd_inbox_pids]
            self.env['mail.notification'].sudo().create(notif_create_values)
