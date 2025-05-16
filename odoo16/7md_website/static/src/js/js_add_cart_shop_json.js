odoo.define('7md_website.js_add_cart_shop_json', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.AddToCart = publicWidget.Widget.extend({
    selector: '.js_add_cart_shop_json',
    events: {
        'click': '_onAddToCartClick',
    },

    _onAddToCartClick: function (ev) {
        ev.preventDefault();
        var productID = $(ev.currentTarget).data('product-id');
        if (!productID) {
            return;
        }
        this._rpc({
            route: "/shop/cart/update_json",
            params: {
                product_id: productID,
                add_qty: 1
            },
        }).then(function (data) {
            // Success - you can handle UI feedback here
            console.log(data);
            if (data.cart_quantity) {
                var $cartQuantity = $('.my_cart_quantity');
                $cartQuantity.text(data.cart_quantity);
            }
        });
    },
});

});
