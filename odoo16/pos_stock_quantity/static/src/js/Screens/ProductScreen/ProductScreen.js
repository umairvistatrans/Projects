odoo.define('pos_stock_quantity.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    const POSStockProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            async _barcodeProductAction(code) {
                // Restrict add product from barcode scan without customer
                let product = this.env.pos.db.get_product_by_barcode(code.code);
                if ((this.env.pos.config.show_qty_available || this.env.pos.config.show_qty_available_res) && (product && (!product.qty_available || product.qty_available <= 0))) {
                    return this.showNotification(
                        _.str.sprintf(this.env._t('Stock is not available in system for scanned product.')),
                        5000
                    );
                }
                await super._barcodeProductAction(...arguments);
            }
            async _onClickPay() {
                let self = this;
                const order = self.env.pos.get_order();
                for (let order_line of order.get_orderlines()) {
                    if(self.env.pos.config.show_qty_available || self.env.pos.config.show_qty_available_res) {
                        let product = self.env.pos.db.get_product_by_id(order_line.product.id);
                        let qty_available = product.qty_available;

                        var all_product_line = order.orderlines.filter(function (orderline) {
                            return product.id === orderline.product.id;
                        });

                        if (all_product_line.indexOf(order_line) === -1) {
                            all_product_line.push(order_line);
                        }

                        var sum_qty = 0;
                        all_product_line.forEach(function (line) {
                            sum_qty += line.quantity;
                        });
                        debugger;
                        if (product.type == "product"){
                            if (qty_available - sum_qty < self.env.pos.config.limit_qty) {
                                let allowed_qty = qty_available - sum_qty + order_line.quantity - self.env.pos.config.limit_qty
                                const { confirmed } = await self.showPopup('ConfirmPopup', {
                                    title: self.env._t('Out of Stock Warning'),
                                    body: _.str.sprintf(self.env._t('%s .\n Maximum Available Quantity is %s.'), product.display_name, allowed_qty),
                                    confirmText: self.env._t('Order'),
                                })
                                if (confirmed){
                                    order_line.set_quantity(allowed_qty)
                                } else{
                                    order.remove_orderline(order_line);
                                }
                            }
                        }
                    }
                }
                order.to_invoice = true;
                return super._onClickPay(...arguments);
            }
        }
     Registries.Component.extend(ProductScreen, POSStockProductScreen);

    return ProductScreen;
});
