odoo.define('pos_orderlist_screen_extension.chrome', function (require) {
    'use strict';

    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');

    const OrderListScreenExtChrome = (Chrome) =>
    class extends Chrome {
        get headerButtonIsShown() {
            super.headerButtonIsShown;
            return true
        }
    };

    Registries.Component.extend(Chrome, OrderListScreenExtChrome);

    return Chrome;
});
