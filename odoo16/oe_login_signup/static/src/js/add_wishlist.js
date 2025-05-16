odoo.define('oe_login_signup.updateWishlistCount', function(require) {
    'use strict';

    var sAnimations = require('website.content.snippets.animation');
    var ajax = require('web.ajax');

    sAnimations.registry.updateWishlistCount = sAnimations.Class.extend({
        selector: '.o_add_wishlist',
        events: {
            'click': '_onAddToWishlist',
        },

        _onAddToWishlist: function(ev) {
            ev.preventDefault();
            var $link = $(ev.currentTarget);
            var $icon = $link.find('i');
            var product_id = $link.data('product_id');
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

        },
    });
});
