/** @odoo-module **/

import ProductsWidget from "point_of_sale.ProductsWidget";
import Registries from "point_of_sale.Registries";

const POSStockProductsWidget = (ProductsWidget) =>
    class POSStockProductsWidget extends ProductsWidget {
        setup() {
            super.setup();
            this.env.services.bus_service.addChannel(this._getChannelName());
            this.env.services.bus_service.addEventListener(
                "notification",
                this._onNotification.bind(this)
            );
        }
        _getChannelName() {
            return JSON.stringify([
                "pos_stock_quantity",
                String(this.env.pos.config.id),
            ]);
        }
        _onNotification({detail: notifications}) {
            var payloads = [];
            for (const {payload, type} of notifications) {
                if (type === "pos.config/product_update") {
                    debugger;
                    payloads.push(payload);
                }
            }
            this._handleNotification(payloads);
        }
        async _handleNotification(payloads) {
            if (this.env.isDebug()) {
                console.log("Payloads:", payloads);
            }
            let self = this;
            let product_ids = []
            for (const payload of payloads) {
                for (const message of payload) {
                    product_ids.push(message.product_id);
                }
            }
            if (this.env.pos.config && (this.env.pos.config.show_qty_available || this.env.pos.config.show_qty_available_res) && product_ids.length > 0) {
               product_ids = _.uniq(product_ids);
               await self.env.pos.qty_sync(product_ids);
               this.render(true);
            }
        }
//        async qty_sync(product_ids) {
//            var self = this;
//            if (this.env.pos.config && (this.env.pos.config.show_qty_available || this.env.pos.config.show_qty_available_res) && this.env.pos.config.location_only) {
//                console.log('with product_ids rpc call', product_ids);
//                console.log("self.env.pos.config.location_id[0]>>>>>>", self.env.pos.config.location_id[0]);
//                let res = await this.rpc({
//                    model: 'stock.quant',
//                    method: 'get_qty_available',
//                    args: [self.env.pos.config.location_id[0], false, product_ids]
//                })
//                if (res){
//                    self.recompute_qty_in_pos_location(product_ids, res);
//                    alert("Result called")
//                    console.log("rpc called result come up", product_ids, res);
//                }
//
//
//            } else if (this.env.pos.config && (this.env.pos.config.show_qty_available || this.env.pos.config.show_qty_available_res)) {
//                await this.rpc({
//                    model: 'product.product',
//                    method: 'read',
//                    args: [product_ids, ['qty_available']]
//                }).then(function (res) {
//                    res.forEach(function (item) {
//                        console.log("item>>>>>", item);
//                        var product_id = item.id;
//                        var qty = item.qty_available
//                        if(!self.env.pos.config.show_qty_available){
//                           qty = item.qty_available - item.reserved_quantity
//                        }
//                        var product = self.env.pos.db.get_product_by_id(product_id);
//                        if (product) {
//                            console.log("product>>>>>>", product);
//                            console.log("qty>>>>>>", qty);
//                            product.qty_available = qty
//                        }
//                    });
//                    self.render(true);
//                });
//            }
//            return true
//        }
//        recompute_qty_in_pos_location(product_ids, res) {
//            var self = this;
//            var res_product_ids = res.map(function (item) {
//                return item.product_id[0];
//            });
//
//            let gropped_data = _.groupBy(res, lst => lst.product_id[0]);
//            console.log("gropped_data>>>>>>", gropped_data);
//            for (let key in gropped_data){
//                console.log("key>>>>", key);
//                let sum = 0;
//                let total_reserved = 0;
//                let total_qty = 0
//                gropped_data[key].forEach(value => {total_qty += value.quantity});
//
//                gropped_data[key].forEach(value => {total_reserved += value.reserved_quantity});
//                let qty = total_qty;
//                if(!self.env.pos.config.show_qty_available){
//                   qty = total_qty - total_reserved
//                }
//                var product = self.env.pos.db.get_product_by_id(key);
//                if (product) {
//                    product.qty_available = qty
//                }
//            }
//            this.render(true);
//        }
    };

Registries.Component.extend(ProductsWidget, POSStockProductsWidget);
