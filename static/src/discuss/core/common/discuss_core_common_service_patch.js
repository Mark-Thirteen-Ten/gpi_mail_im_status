/* @odoo-module */

import { DiscussCoreCommon } from "@mail/discuss/core/common/discuss_core_common_service";
import { patch } from "@web/core/utils/patch";

patch(DiscussCoreCommon.prototype, {
    async _handleNotificationNewMessage(notif) {
        const isDnd = Boolean(this.store.self?.im_status?.includes("busy"));

        if (!isDnd) {
            return super._handleNotificationNewMessage(notif);
        }

        // During DND: insert message and update channel state, but skip the unread counter increment
        const { id, message: messageData } = notif.payload;
        let channel = this.store.Thread.get({ model: "discuss.channel", id });
        if (!channel || !channel.type) {
            channel = await this.threadService.fetchChannel(id);
            if (!channel) {
                return;
            }
        }
        this.store.Message.get(messageData.temporary_id)?.delete();
        messageData.temporary_id = null;
        const message = this.store.Message.insert(messageData, { html: true });
        if (message.notIn(channel.messages)) {
            if (!channel.loadNewer) {
                channel.messages.push(message);
            } else if (channel.status === "loading") {
                channel.pendingNewMessages.push(message);
            }
            if (message.isSelfAuthored) {
                channel.seen_message_id = message.id;
            }
            // NOTE: intentionally skip channel.message_unread_counter++ during DND
        }
        if (
            !channel.chatPartner?.eq(this.store.odoobot) &&
            channel.type !== "channel" &&
            this.store.user
        ) {
            this.threadService.markAsFetched(channel);
        }
        if (
            !channel.loadNewer &&
            !message.isSelfAuthored &&
            channel.composer.isFocused &&
            !this.store.guest &&
            channel.newestPersistentMessage?.eq(channel.newestMessage)
        ) {
            this.threadService.markAsRead(channel);
        }
        this.env.bus.trigger("discuss.channel/new_message", { channel, message });
    },
});
