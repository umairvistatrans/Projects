odoo.define('oe_pos_product_availability_by_location.ProductAvailabilityPopupWidget', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    const { onMounted, useRef, useState } = owl;

    class ProductAvailabilityPopupWidget extends AbstractAwaitablePopup {
    }

    ProductAvailabilityPopupWidget.template = 'ProductAvailabilityPopupWidget';
    ProductAvailabilityPopupWidget.defaultProps = {
        confirmText: _lt('Ok'),
        title: '',
        body: '',
    };
    Registries.Component.add(ProductAvailabilityPopupWidget);

    return ProductAvailabilityPopupWidget
});
