/* @odoo-module */

import { MessagingMenu } from "@mail/core/web/messaging_menu";
import { patch } from "@web/core/utils/patch";

/**
 * When the current user is in "Do Not Disturb" (busy) mode, suppress the
 * messaging menu badge counter entirely so the chat bubble shows nothing.
 *
 * The underlying counters (inbox.counter, message_unread_counter) are still
 * incremented in memory, so they become visible the moment DND is disabled
 * without any page refresh needed.
 */
patch(MessagingMenu.prototype, {
    get counter() {
        const isDnd = Boolean(this.store.self?.im_status?.includes("busy"));
        if (isDnd) {
            return 0;
        }
        return super.counter;
    },
});
