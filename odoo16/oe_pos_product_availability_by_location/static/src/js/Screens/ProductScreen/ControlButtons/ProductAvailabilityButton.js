odoo.define('oe_pos_product_availability_by_location.ProductAvailabilityButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class ProductAvailabilityButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick() {
            const { confirmed, payload: default_code } = await this.showPopup('TextInputPopup', {
                title: this.env._t("Please Enter Product's Internal Reference"),
            });
            if (!confirmed) return;
            if (default_code) {
                this.env.pos.get_product_availability_by_location(default_code);
            }
        }

    }

    ProductAvailabilityButton.template = 'ProductAvailabilityButton';

    ProductScreen.addControlButton({
        component: ProductAvailabilityButton,
        condition: function() {
            return this.env.pos.config.oe_product_availability;
        },
    });

    Registries.Component.add(ProductAvailabilityButton);

    return ProductAvailabilityButton;
});
