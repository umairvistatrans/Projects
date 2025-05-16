odoo.define('pos_orderlist_screen_extension.models', function (require) {
"use strict";

const { Order, Orderline } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');

const PosOrderlistScreenExtensionOrder = (Order) => class PosOrderlistScreenExtensionOrder extends Order {
    get_partner_mobile() {
        let partner = this.partner;
        return partner ? partner.mobile : "";
    }
    get_partner_phone() {
        let partner = this.partner;
        return partner ? partner.phone : "";
    }
}
Registries.Model.extend(Order, PosOrderlistScreenExtensionOrder);

});
