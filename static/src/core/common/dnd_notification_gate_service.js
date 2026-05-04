/* @odoo-module */

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";

const MAX_QUEUED_NOTIFICATIONS = 200;

export const dndNotificationGateService = {
    dependencies: ["bus_service", "mail.out_of_focus", "mail.store", "notification"],

    start(env, services) {
        const busService = services.bus_service;
        const outOfFocusService = services["mail.out_of_focus"];
        const store = services["mail.store"];
        const notificationService = services.notification;

        const originalNotificationAdd = notificationService.add.bind(notificationService);
        const originalOutOfFocusNotify = outOfFocusService.notify.bind(outOfFocusService);

        let queuedNotificationId = 0;
        let wasBusy = false;
        const queuedToasts = [];
        const queuedOutOfFocus = [];

        const isDndEnabled = () => Boolean(store.self?.im_status?.includes("busy"));

        const trimQueue = (queue) => {
            while (queue.length > MAX_QUEUED_NOTIFICATIONS) {
                queue.shift();
            }
        };

        const flushQueues = () => {
            if (isDndEnabled()) {
                return;
            }
            while (queuedToasts.length) {
                const { message, options } = queuedToasts.shift();
                originalNotificationAdd(message, options);
            }
            while (queuedOutOfFocus.length) {
                const args = queuedOutOfFocus.shift();
                originalOutOfFocusNotify(...args);
            }
        };

        notificationService.add = (message, options = {}) => {
            if (!isDndEnabled()) {
                return originalNotificationAdd(message, options);
            }
            const id = ++queuedNotificationId;
            queuedToasts.push({ id, message, options });
            trimQueue(queuedToasts);
            return () => {
                const idx = queuedToasts.findIndex((entry) => entry.id === id);
                if (idx >= 0) {
                    queuedToasts.splice(idx, 1);
                }
            };
        };

        outOfFocusService.notify = (...args) => {
            if (!isDndEnabled()) {
                return originalOutOfFocusNotify(...args);
            }
            queuedOutOfFocus.push(args);
            trimQueue(queuedOutOfFocus);
            return Promise.resolve();
        };

        busService.subscribe("bus.bus/im_status_updated", ({ partner_id }) => {
            if (partner_id && store.self?.id && partner_id !== store.self.id) {
                return;
            }
            const isBusy = isDndEnabled();
            if (wasBusy && !isBusy) {
                flushQueues();
            }
            wasBusy = isBusy;
        });

        const pollStatusTransition = browser.setInterval(() => {
            const isBusy = isDndEnabled();
            if (wasBusy && !isBusy) {
                flushQueues();
            }
            wasBusy = isBusy;
        }, 1000);

        wasBusy = isDndEnabled();

        return {
            flushQueuedNotifications: flushQueues,
            stop() {
                browser.clearInterval(pollStatusTransition);
            },
        };
    },
};

registry.category("services").add("gpi_mail_im_status.dnd_gate", dndNotificationGateService);
