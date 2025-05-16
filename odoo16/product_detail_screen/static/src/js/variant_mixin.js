odoo.define('product_detail_screen.VariantMixin', function (require) {

    'use strict';
    var VariantMixin = require('website_sale.VariantMixin');
    const originalOnChangeCombination = VariantMixin._onChangeCombination;
    VariantMixin._onChangeCombination = function (ev, $parent, combination) {
        if (combination.amount_with_vat) {
            $('.oe_amount_with_vat span').text(combination.amount_with_vat);
            $('#product_sku').text(combination.product_sku);
        }
        originalOnChangeCombination.apply(this, [ev, $parent, combination]);

    }

    return VariantMixin
})