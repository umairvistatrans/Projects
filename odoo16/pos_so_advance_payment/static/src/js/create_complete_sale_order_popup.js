odoo.define('pos_so_advance_payment.CreateCompleteSaleOrderPopupWidget', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');
    const { onMounted, useRef, useState } = owl;

    class CreateCompleteSaleOrderPopupWidget extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            this.state = useState({ inputValue: this.props.startingValue });
            this.inputRef = useRef('input');
            onMounted(this.onMounted);
        }
        onMounted() {
            this.inputRef.el.focus();
        }
        getPayload() {
            return this.state.inputValue;
        }
    }
    CreateCompleteSaleOrderPopupWidget.template = 'CreateCompleteSaleOrderPopupWidget';
    CreateCompleteSaleOrderPopupWidget.defaultProps = {
        confirmText: _lt('Ok'),
        cancelText: _lt('Cancel'),
        title: '',
        body: '',
    };

    Registries.Component.add(CreateCompleteSaleOrderPopupWidget);

    return CreateCompleteSaleOrderPopupWidget;
});