/* @odoo-module */

import { ThreadService } from "@mail/core/common/thread_service";

import { patch } from "@web/core/utils/patch";

patch(ThreadService.prototype, {
    notifyMessageToUser(thread, message) {
        return super.notifyMessageToUser(thread, message);
    },
});
