/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";

export function useModelRecord() {
    const view = useService("view");

    const loadModelRecords = (resModel) => {
        return view.loadRecords(resModel, {
            attributes: [
            ],
        });
    };
    return {
        loadModelRecords
    };
}
