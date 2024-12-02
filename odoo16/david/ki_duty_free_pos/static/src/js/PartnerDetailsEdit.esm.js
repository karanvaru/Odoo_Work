/** @odoo-module **/
import PartnerDetailsEdit from "point_of_sale.PartnerDetailsEdit";
import Registries from "point_of_sale.Registries";

const PartnerDetailsEditPassport = (OriginalPartnerDetailsEdit) =>
    class extends OriginalPartnerDetailsEdit {
        setup() {
            super.setup();
            this.changes = {
                ...this.changes,
                customer_passport_number: this.props.partner.customer_passport_number || "",
            };
        }
    };

Registries.Component.extend(PartnerDetailsEdit, PartnerDetailsEditPassport);
