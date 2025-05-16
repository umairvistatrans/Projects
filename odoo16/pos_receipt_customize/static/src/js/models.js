odoo.define('pos_receipt_customize.models', function (require) {
"use strict";

const { Order, Orderline } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');

const PosReceiptCustomizationOrder = (Order) => class PosReceiptCustomizationOrder extends Order {
    //@override
    export_for_printing() {
        const json = super.export_for_printing(...arguments);
        json.client = this.partner;
        return json;
    }
}
Registries.Model.extend(Order, PosReceiptCustomizationOrder);

});
