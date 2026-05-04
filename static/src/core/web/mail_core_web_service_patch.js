/* @odoo-module */
/* The mail.message/inbox counter suppression is handled server-side:
 * gpi_mail_im_status/models/mail_thread.py overrides _notify_thread_by_inbox
 * to skip the bus push entirely for users with manual_im_status == 'busy'.
 * No JS patching of MailCoreWeb is needed here. */
