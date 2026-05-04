/* @odoo-module */

import { Component } from "@odoo/owl";
import { ImStatus } from "@mail/core/common/im_status";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ImStatusDropdown extends Component {
    static template = "gpi_mail_im_status.ImStatusDropdown";
    static components = { Dropdown, DropdownItem, ImStatus };
    static props = [];

    setup() {
        this.store = useService("mail.store");
        this.rpc = useService("rpc");
        this.readableImStatusByCode = {
            online: _t("Online"),
            away: _t("Away"),
            busy: _t("Do Not Disturb"),
            offline: _t("Offline"),
        };
    }

    async setManualImStatus(status) {
        const wasBusy = Boolean(this.store.self?.im_status?.includes("busy"));
        await this.rpc("/mail/set_manual_im_status", { status });
        if (wasBusy && status === "online") {
            browser.location.reload();
        }
    }

    get readableImStatus() {
        const imStatus = this.store.self?.im_status || "offline";
        for (const status in this.readableImStatusByCode) {
            if (imStatus.includes(status)) {
                return this.readableImStatusByCode[status];
            }
        }
        return _t("Unknown Status");
    }
}

function imStatusItem() {
    return {
        type: "component",
        contentComponent: ImStatusDropdown,
        sequence: 45,
    };
}

registry.category("user_menuitems").add("im_status", imStatusItem, { force: true });
