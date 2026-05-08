/* @odoo-module */

import { ThreadService } from "@mail/core/common/thread_service";

import { patch } from "@web/core/utils/patch";

patch(ThreadService.prototype, {
    notifyMessageToUser(thread, message) {
        let notify = thread.type !== "channel";
        if (thread.type === "channel" && message.recipients?.includes(this.store.user)) {
            notify = true;
        }
        if (
            thread.chatPartner?.eq(this.store.odoobot) ||
            thread.muteUntilDateTime ||
            thread.custom_notifications === "no_notif" ||
            (thread.custom_notifications === "mentions" &&
                !message.recipients?.includes(this.store.user))
        ) {
            return;
        }
        if (notify) {
            const isDnd = Boolean(this.store.self?.im_status?.includes("busy"));
            if (!isDnd) {
                this.store.ChatWindow.insert({ thread });
            }
            this.outOfFocusService.notify(message, thread);
        }
    },
});
