odoo.define('oe_pos_spotii.PaymentScreen', function(require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { onMounted } = owl;

    const PosSpotiiPaymentScreen = PaymentScreen => class extends PaymentScreen {
        deletePaymentLine(event) {
            var self = this;
            const { cid } = event.detail;
            const line = this.paymentLines.find((line) => line.cid === cid);

            // If a paymentline with a payment terminal linked to
            // it is removed, the terminal should get a cancel
            // request.
            if (['waiting', 'waitingCard', 'timeout'].includes(line.get_payment_status())) {
                line.set_payment_status('waitingCancel');
                line.payment_method.payment_terminal.send_payment_cancel(this.currentOrder, cid).then(function() {
                    self.currentOrder.remove_paymentline(line);
                    NumberBuffer.reset();
                    self.render(true);
                })
            }
            else if (line.get_payment_status() !== 'waitingCancel') {
                if (this.env.pos.config.allow_spotii) {
                    var pay_method = line.payment_method.has_service_charge
                    if (pay_method) {
                        let order = this.env.pos.get_order();
                        let sc_index = order.get_orderlines().length - 1
                        let s = order.get_orderlines()[sc_index]
                        order.remove_orderline(s)
                    }
                }
                this.currentOrder.remove_paymentline(line);
                NumberBuffer.reset();
                this.render(true);
            }
        }

        addNewPaymentLine({ detail: paymentMethod }) {
            // original function: click_paymentmethods from v13
            if (this.env.pos.config.allow_spotii) {
				if (paymentMethod.has_service_charge) {
					var val = this.env.pos.config.spotii_pc
					this.apply_spotii(val);
				}
			}
            let result = this.currentOrder.add_paymentline(paymentMethod);
            if (result){
                NumberBuffer.reset();
                return true;
            }
            else{
                this.showPopup('ErrorPopup', {
                    title: this.env._t('Error'),
                    body: this.env._t('There is already an electronic payment in progress.'),
                });
                return false;
            }
        }
        apply_spotii(pc) {
			let order = this.env.pos.get_order();
			let product = this.env.pos.db.get_product_by_id(this.env.pos.config.spotii_product_id[0]);
			if (product === undefined) {
				this.showPopup('ErrorPopup', {
					title: this.env._t("No Spotii product found"),
					body: this.env._t("The Spotii product seems misconfigured. Make sure it is flagged as 'Can be Sold' and 'Available in Point of Sale'."),
				});
				return;
			}

			let base_price = order.get_total_without_tax();
			if (product.taxes_id.length) {
				let first_tax = this.env.pos.taxes_by_id[product.taxes_id[0]];
				if (first_tax.price_include) {
					base_price = order.get_total_with_tax();
				}
			}
			let spotii = pc / 100.0 * base_price;
			if (spotii > 0) {
				order.add_product(product, {
					price: spotii,
					lst_price: spotii,
					extras: {
						price_manually_set: false,
					},
				});
			}
		}
    };

    Registries.Component.extend(PaymentScreen, PosSpotiiPaymentScreen);

    return PaymentScreen;
});
