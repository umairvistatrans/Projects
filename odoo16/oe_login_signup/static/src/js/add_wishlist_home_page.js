odoo.define('oe_login_signup.updateWishlistCountHomePage', function(require) {
    'use strict';

    var sAnimations = require('website.content.snippets.animation');
    var ajax = require('web.ajax');

    sAnimations.registry.updateWishlistCountHomePage = sAnimations.Class.extend({
        selector: '.o_homepage_add_wishlist',
        events: {
            'click': '_onAddToWishlist',
        },

        _onAddToWishlist: function(ev) {
            ev.preventDefault();
            var $link = $(ev.currentTarget);
            var $icon = $link.find('i');
            var product_id = $link.data('product-product-id');
            ajax.jsonRpc('/shop/wishlist/add', 'call', {
                'product_id': product_id
            }).then(function(data) {
                if (data) {
                    // Update the wishlist count
                    var p_len =  parseInt($('.my_wish_quantity').text(), 10) + 1;
                    $('.my_wish_quantity').text(p_len);

                    // Toggle the heart icon
                    if ($icon.hasClass('fa-heart-o')) {
                        $icon.removeClass('fa-heart-o').addClass('fa-heart');
                    } else {
                        // In case you want to toggle it back if already in the wishlist
                        $icon.removeClass('fa-heart').addClass('fa-heart-o');
                    }
                }
            });
        },
    });
});
