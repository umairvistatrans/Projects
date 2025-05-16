/** @odoo-module **/

import { Order, Orderline, PosGlobalState} from 'point_of_sale.models';
import Registries from "point_of_sale.Registries";
import { Gui } from 'point_of_sale.Gui';
import core from 'web.core';

const _t = core._t;

const PosStockPosGlobalState = (PosGlobalState) => class PosStockPosGlobalState extends PosGlobalState {
    async qty_sync(product_ids) {
        var self = this;
        if (this && this.config && (this.config.show_qty_available || this.config.show_qty_available_res) && this.config.location_only) {
            let res = await this.env.services.rpc({
                model: 'product.product',
                method: 'read',
                args: [product_ids, ['qty_available', 'free_qty']],
                context: {'location':self.config.location_id[0]},
            })
            if (res){
                console.log(res)
                res.forEach(function (item) {
                   var product_id = item.id;
//                   var qty = item.qty_available
//                    if(!self.config.show_qty_available){
//                        qty = item.qty_available - item.reserved_quantity
//                    }

                    var product = self.db.get_product_by_id(product_id);
                    if (product) {
                        product.free_qty = item.free_qty
                        debugger;
                    }
                });
            }
//            let res = await this.env.services.rpc({
//                model: 'stock.quant',
//                method: 'get_qty_available',
//                args: [self.config.location_id[0], false, product_ids]
//            })
//            if (res){
//                self.recompute_qty_in_pos_location(product_ids, res);
//            }
        } else if (this && this.config && (this.config.show_qty_available || this.config.show_qty_available_res)) {
            await this.env.services.rpc({
                model: 'product.product',
                method: 'read',
                args: [product_ids, ['qty_available', 'free_qty']]
            })
            if (res){
                res.forEach(function (item) {
                   var product_id = item.id;
//                   var qty = item.qty_available
//                    if(!self.config.show_qty_available){
//                        qty = item.qty_available - item.reserved_quantity
//                    }

                    var product = self.db.get_product_by_id(product_id);
                    if (product) {
                        product.free_qty = item.free_qty
                        debugger;
                    }
                });
            }
        }
        return true
    }
    recompute_qty_in_pos_location(product_ids, res) {
        var self = this;
        var res_product_ids = res.map(function (item) {
            return item.product_id[0];
        });

        let gropped_data = _.groupBy(res, lst => lst.product_id[0]);
        debugger;
        for (let key in gropped_data){
            let sum = 0;
            let total_reserved = 0;
            let total_qty = 0
            gropped_data[key].forEach(value => {total_qty += value.free_qty});

//            gropped_data[key].forEach(value => {total_reserved += value.reserved_quantity});
            let qty = total_qty;
            if(!self.config.show_qty_available){
               qty = total_qty
               debugger;
            }
            var product = self.db.get_product_by_id(key);
            if (product) {
                product.free_qty = qty
                debugger;
            }
        }
    }
}
Registries.Model.extend(PosGlobalState, PosStockPosGlobalState);

const PosStockOrderline = (Orderline) => class PosStockOrderline extends Orderline {
    set_quantity(quantity, keep_price) {
        let qty = super.set_quantity(...arguments);
        let order = this.pos.get_order();
        if(!order.get_selected_orderline()){
            return qty;
        }
        if (this.id == order.get_selected_orderline().id &&
            (!this.refunded_orderline_id && this.pos.config.show_qty_available || this.pos.config.show_qty_available_res)
            || !this.pos.config.allow_out_of_stock
            || this.product.type == 'product') {
            this.check_reminder();
        }
        return qty
    }
    async check_reminder() {
        var self = this;
        var qty_available = this.product.qty_available
        var all_product_line = this.order.orderlines.filter(function (orderline) {
            return self.product.id === orderline.product.id;
        });

        if (all_product_line.indexOf(self) === -1) {
            all_product_line.push(self);
        }

        var sum_qty = 0;
        all_product_line.forEach(function (line) {
            sum_qty += line.quantity;
        });
        debugger;
        if (this.product.type == "product"){
            if (qty_available - sum_qty < this.pos.config.limit_qty) {
                let allowed_qty = this.product.qty_available - sum_qty + self.quantity - this.pos.config.limit_qty
                const { confirmed } = await Gui.showPopup('ConfirmPopup', {
                    title: _t('Out of Stock Warning'),
                    body: _.str.sprintf(_t('%s .\n Maximum Available Quantity is %s.'), this.product.display_name, allowed_qty),
                    confirmText: _t('Order'),
                })
                if (confirmed){
                    this.set_quantity(allowed_qty)
                } else{
                    this.order.remove_orderline(this);
                }
            }
        }
    }
}

Registries.Model.extend(Orderline, PosStockOrderline);