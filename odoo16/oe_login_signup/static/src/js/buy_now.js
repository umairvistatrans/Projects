odoo.define('oe_login_signup.buy_home', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.customHomePage = publicWidget.Widget.extend({
        selector: '.buy-now-btn',
        events: {
            'click': '_onClickBuyNow',
        },

        _onClickBuyNow: function (ev) {
            ev.preventDefault();
            var productId = $(ev.currentTarget).data('product-id');

            // Call Odoo RPC to add the product to the cart
            this._rpc({
                route: '/shop/cart/update_json',
                params: {
                    product_id: productId,
                    set_qty: 1,
                },
            }).then(function () {
                // Redirect to the checkout page
                window.location.href = '/shop/cart';
            });
        },
    });
});
