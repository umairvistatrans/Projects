odoo.define('pos_so_advance_payment.CreateSaleOrderPopupWidget', function (require) {
    'use strict';
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');
    const {_t} = require('web.core');
    class CreateSaleOrderPopupWidget extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            this.controlButtons = this.props.controlButtons;
        }

        enable_disable_inputs(status) {
            var self = this;
            if (status == false){
            $('.street1').val("")
            $('.street2').val("")
            $('.add_city').val("")
            $('.add_phone').val("")
            $('.add_mobile').val("")
            }
        }

        async onchange_ptr_contacts() {
            var self = this;
            var contact_id = parseInt($('#ptr_contacts').val());
            let partner_data = await this.rpc({
              model: 'res.partner',
              method: 'search_read',
              args: [[['id', '=', contact_id]],['id', 'name', 'street','street2', 'phone' ,'city', 'mobile']],
              })
            if (contact_id){
                self.enable_disable_inputs(false);
            }
            $('.street1').val(partner_data[0]['street'] ? partner_data[0]['street']: "");
            $('.street2').val(partner_data[0]['street2'] ? partner_data[0]['street2']: "");
            $('.add_city').val(partner_data[0]['city'] ? partner_data[0]['city']: "");
            $('.add_phone').val(partner_data[0]['phone'] ? partner_data[0]['phone']: "");
            $('.add_mobile').val(partner_data[0]['mobile'] ? partner_data[0]['mobile']: "");
            
        }

        async OnClickAddressRadio(ev) {
            var radio_add_val = $(ev.currentTarget).val();
            var contact_id = $('#ptr_contacts');
            $("#error_msg").css("display", "none");
            $(".error_msg_delivery").css("display", "none");
            $(".error_msg_create").css("display", "none");
            if (radio_add_val == 'create_new_delivery') {
                $("#delivery_selection_row").css({ 'display': "none" });
                this.enable_disable_inputs(false);
                $("#new_contact_name").css({ 'display': "table-row" }); 
            }
            if (radio_add_val == 'use_ex_delivery') {
                $("#delivery_selection_row").css({ 'display': "table-row" });
                if (!contact_id) {
                    this.enable_disable_inputs(true);
                }
                $("#new_contact_name").css({ 'display': "none" });
            }
        }

        prepare_sale_order_data() {
            var self = this;
            var order = self.env.pos.selectedOrder;
            const radio_add_val = document.querySelector('input[name="radio_address"]:checked').value;
            order.partner_shiping_id = $('#ptr_contacts').val();
            if (radio_add_val == 'use_ex_delivery' && !order.partner_shiping_id) {
                document.querySelector("#error_msg").setAttribute("style", "display:block");
                var err_msg_delivery = $(document.querySelector(".error_msg_delivery"));
                err_msg_delivery.css({
                    'display': 'block',
                    'color': 'red',
                    'text-align': 'center',
                    'font-size': '13px'
                });
                document.querySelector(".error_msg_create").style.display = 'none';
                return false;
            }

            else if (radio_add_val == 'create_new_delivery' && !$(".c_name").val()) {
                document.querySelector("#error_msg").setAttribute("style", "display:block");
                var err_msg_create = $(document.querySelector(".error_msg_create"));
                err_msg_create.css({
                    'display': 'block',
                    'color': 'red',
                    'text-align': 'center',
                    'font-size': '13px'
                });
                document.querySelector(".error_msg_delivery").style.display = 'none';
                return false;
            }
            else if (this.env.pos.config.allow_advance_payment) {
                var adv_pay_value = $(document.querySelector(".adv_pay_value")).val();

                if (parseFloat(adv_pay_value) > order.get_subtotal()) {
                    this.showPopup('ConfirmPopup', {
                        body: this.env._t("Advance payment can't be greater than total payable amount.")
                    });
                    return false;
                }
                else {
                    var order = self.env.pos.selectedOrder;
                    var data = order.export_as_JSON();
                    var new_update_delivery_addr = {
                        'c_name': $(document.querySelector(".c_name")).val(),
                        'street': $(document.querySelector(".street1")).val(),
                        'street2': $(document.querySelector(".street2")).val(),
                        'city': $(document.querySelector(".add_city")).val(),
                        'phone': $(document.querySelector(".add_phone")).val(),
                        'mobile': $(document.querySelector(".add_mobile")).val(),
                        'parent_id': order.partner.id,
                        'advance_pay': $(document.querySelector(".adv_pay_value")).val(),
                        'payment_journal': parseInt($(document.querySelector("#payment_journal")).val()),
                        'type': 'delivery',
                        'pos_invoice_journal_id': self.env.pos.config.invoice_journal_id[0],
                        'note' : $(".so_notes").val(),
                        'partner_shiping_id' : order.partner_shiping_id
                    }

                }
            }
            else {
                var order = self.env.pos.selectedOrder;
                var data = order.export_as_JSON();
                var new_update_delivery_addr = {
                    'c_name': $(document.querySelector(".c_name")).val(),
                    'street': $(document.querySelector(".street1")).val(),
                    'street2': $(document.querySelector(".street2")).val(),
                    'city': $(document.querySelector(".add_city")).val(),
                    'phone': $(document.querySelector(".add_phone")).val(),
                    'mobile': $(document.querySelector(".add_mobile")).val(),
                    'parent_id': order.partner.id,
                    'payment_journal': parseInt($(document.querySelector("#payment_journal")).val()),
                    'type': 'delivery',
                    'pos_invoice_journal_id': self.env.pos.config.invoice_journal_id[0],
                    'note' : $(".so_notes").val(),
                    'partner_shiping_id' : order.partner_shiping_id
                }

            }
            $.extend(data, new_update_delivery_addr);
            return data;
        }

        async save_order() {
            const submitButton = document.querySelector('.button.save_quotation_bill');
            if (submitButton.disabled) {
                return;
            }
            submitButton.disabled = true;
            var self = this;
            var data = self.prepare_sale_order_data();
            if (data) {
                const files = document.getElementById('upload_file').files;
                const attachmentData = [];
                if (files.length > 0) {
                    for (const file of files) {
                            const fileData = await self.readFileAsync(file);
                            attachmentData.push(fileData);
                        };
//                        reader.readAsDataURL(file);
                    }
                debugger;
                let quotation_result = await this.rpc({
                    model: 'sale.order',
                    method: 'create_new_quotation',
                    args: [data,attachmentData]
                });

                if (quotation_result) {
                    this.env.pos.selectedOrder.finalized = true;
                    // After finalizing the Current POS the Order cannot be modified.
                    this.onClickCancel();
                    const { confirmed, payload } = await this.showPopup('CreateCompleteSaleOrderPopupWidget', { 'title': 'Sale Order', 'order_ref': quotation_result });
                    if(confirmed){
                        this.env.pos.add_new_order();
                        this.showScreen("ProductScreen");
                    }
                }
            }
            // else{
            //     return this.showPopup("ErrorPopup", {
            //         'title': _t('Error: Could not Save Changes'),
            //         'body': _t('Your Internet connection is probably down.'),
            //     });
            // }
            submitButton.disabled = false;
        }


        readFileAsync(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = function(event) {
            const fileData = {
                name: file.name,
                data: event.target.result.split(',')[1], // Extract base64 data
                filename: file.name
            };
            resolve(fileData);
        };
        reader.onerror = function(event) {
            reject(event.target.error);
        };
        reader.readAsDataURL(file);
    });
}
        async save_and_print() {
            const submitButton = document.querySelector('.print_quotation_bill');
            debugger;
            if (submitButton.disabled) {
                return;
            }
            submitButton.disabled = true;
            self = this;
            var order = self.env.pos.selectedOrder;
            var data = self.prepare_sale_order_data();
            if (data) {
                const files = document.getElementById('upload_file').files;
                const attachmentData = [];
                if (files.length > 0) {
                    for (const file of files) {
                            const fileData = await self.readFileAsync(file);
                            attachmentData.push(fileData);
                        };
                    }
                let quotation_data = await this.rpc({
                    model: 'sale.order',
                    method: 'create_new_quotation',
                    args: [data, attachmentData],
                });
                if (quotation_data){
                    this.env.pos.selectedOrder.finalized = true;
                    self.env.pos.selectedOrder.order_ref = quotation_data['result'];
                    this.onClickCancel();
                    this.showScreen("SaleOrderBillScreenWidget",{order_ref: quotation_data , so_notes:order.so_notes});
                }
            }
            // else{
            //     return this.showPopup("ErrorPopup", {
            //         'title': _t('Error: Could not Save Changes'),
            //         'body': _t('Your Internet connection is probably down.'),
            //     });
            // }
            submitButton.disabled = false;
        }


        async onClickSave() {
            var self = this;
            self.save_order();
        }

        async onClickSavePrint() {
            var self = this;
            var order = self.env.pos.selectedOrder;

            if (order.partner != null) {
                order.so_notes = $(".so_notes").val();
                order.partner_shiping_id = $('#ptr_contacts').val();
                if (!self.env.pos.config.iface_print_via_proxy) {
                    self.save_and_print();
                }
            }
            else {
                this.showPopup('ConfirmPopup', {
                    body: this.env._t('Customer is required for sale order. Please select customer first !!!!')
                });
            }
        }


        async onClickCancel() {
            this.env.posbus.trigger('close-popup', {
                popupId: this.props.id,
                response: { confirmed: false, payload: null },
            });
        }
    }
    CreateSaleOrderPopupWidget.template = 'CreateSaleOrderPopupWidget';

    Registries.Component.add(CreateSaleOrderPopupWidget);
    return CreateSaleOrderPopupWidget;
});