odoo.define('aspl_pos_create_so_extension_ee.popup', function (require) {
    "use strict";

    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    var _t = core._t;
    var utils = require('web.utils');
var field_utils = require('web.field_utils');
    var SaleOrderConfirmPopupWidget = PopupWidget.extend({
        template: 'SaleOrderConfirmPopupWidget',
    });
    gui.define_popup({name:'saleOrder', widget: SaleOrderConfirmPopupWidget});

    var SaleOrderPopup = PopupWidget.extend({
        template: 'SaleOrderPopup',
        events: _.extend({}, PopupWidget.prototype.events, {
            'click .remove-image': 'remove_file',
        }),
        show: function(options){
            var self = this;
            this._super(options);
            this.delivery_done = options.delivery_done ? true : false;
            var order = self.pos.get_order();
            var options = options || {};
            this.sale_order_button = options.sale_order_button ||
            self.pos.gui.screen_instances.products.action_buttons.EditQuotationButton || false
            self.payment_obj = self.pos.chrome.screens.payment || false;
            if (self.payment_obj){
                window.document.body.removeEventListener('keypress',self.payment_obj.keyboard_handler);
                window.document.body.removeEventListener('keydown',self.payment_obj.keyboard_keydown_handler);
            }
            if (order.get_client()){
                self.get_client_detail(order.get_client()).then(function(){
                    self.contacts = self.pos.get('contacts');
                    self.renderElement();
                });
            }
            self.renderElement();
            if(order.get_edit_quotation()){
                if(order.get_sale_order_payment_method()){
                    $('#payment_method').val(order.get_sale_order_payment_method());
                }
                if(order.get_sale_order_date()){
                    var date_order = moment(order.get_sale_order_date(), 'YYYY-MM-DD HH:mm');
                    $('#orderdate-datepicker').val(date_order.format('YYYY-MM-DD HH:mm'));
                }
                if(order.set_sale_order_requested_date()){
                    var date_order = moment(order.get_sale_order_requested_date(), 'YYYY-MM-DD HH:mm');
                    $('#requesteddate-datepicker').val(date_order.format('YYYY-MM-DD HH:mm'));
                }
                var shipping_contact = _.find(self.contacts, function(o){
                    return o.id == order.get_shipping_address();
                })
                $('.shipping_contact_selection').val(shipping_contact ? shipping_contact.id : 0);
                var invoice_contact = _.find(self.contacts, function(o){
                    return o.id == order.get_invoice_address();
                })
                $('.invoicing_contact_selection').val(invoice_contact ? invoice_contact.id : 0);
            }

            $('textarea.sale_order_note').focus(function() {
                if(self.payment_obj){
                     $('body').off('keypress', self.keyboard_handler);
                     $('body').off('keydown', self.keyboard_keydown_handler);
                     window.document.body.removeEventListener('keypress',self.keyboard_handler);
                     window.document.body.removeEventListener('keydown',self.keyboard_keydown_handler);
                 }
            });
        },
        remove_file : function(event){
            $(event.currentTarget).closest("div" ).remove();
        },
        resize_image_to_dataurl: function(img, maxwidth, maxheight, callback){
            img.onload = function(){
                var canvas = document.createElement('canvas');
                var ctx    = canvas.getContext('2d');
                var ratio  = 1;

                if (img.width > maxwidth) {
                    ratio = maxwidth / img.width;
                }
                if (img.height * ratio > maxheight) {
                    ratio = maxheight / img.height;
                }
                var width  = Math.floor(img.width * ratio);
                var height = Math.floor(img.height * ratio);

                canvas.width  = width;
                canvas.height = height;
                ctx.drawImage(img,0,0,width,height);

                var dataurl = canvas.toDataURL();
                callback(dataurl);
            };
        },

    // Loads and resizes a File that contains an image.
    // callback gets a dataurl in case of success.
        load_image_file: function(file, callback){
            var self = this;
            if (!file.type.match(/image.*/)) {
                this.gui.show_popup('error',{
                    title: _t('Unsupported File Format'),
                    body:  _t('Only web-compatible Image formats such as .png or .jpeg are supported'),
                });
                return;
            }
            utils.getDataURLFromFile(file).then(function (dataurl) {
                var img     = new Image();
                img.src = dataurl;
                self.resize_image_to_dataurl(img,800,600,callback);
            }).guardedCatch(function () {
                self.gui.show_popup('error',{
                    title :_t('Could Not Read Image'),
                    body  :_t('The provided file could not be read due to an unknown error'),
                });
            });
        },
        upload_files: function(event){
            var self = this;
            var total_file=document.getElementById("upload_file").files.length;
            var contents = this.$el[0].querySelector('.flex-container');
            for(var i=0;i<total_file;i++)
            {
                var file_name = event.target.files[i] ? event.target.files[i].name: '';
                self.load_image_file(event.target.files[i],function(res){
                    if (res) {
                        var html = QWeb.render('imagePreviewWidget',{widget: this, url:res, name:file_name});
                        var div = document.createElement('div');
                        div.innerHTML = html;
                        div = div.childNodes[1];
                        contents.appendChild(div);
                    }
                 })
            }
        },

        get_client_detail: function(partner){
            var self = this;
            return new Promise(function (resolve, reject) {
               var params = {
                    model: 'res.partner',
                    method: 'search_read',
                    domain: [['parent_id', '=', partner.id]],
                    fields: self.fieldNames,
               }
               rpc.query(params, {
                    timeout: 3000,
                    shadow: true,
               })
               .then(function (contacts) {
                    if(contacts){
                        self.pos.set({'contacts': contacts})
                        resolve();
                    }else {
                        reject();
                    }
               }, function (type, err) { reject(); });
            });
        },
        click_confirm: function(){
            var self = this;
            var order = self.pos.get_order();
            var attachments = []
            $('.image-src').each(function(index, value) {
                attachments.push([this.title, this.src]);
            });
            if(attachments){
                order.set_attachments(attachments);
            }else{
                order.set_attachments([]);
            }
            var value = self.$("#signature").jSignature("getData", "image");
            if(value && value[1]){
                order.set_signature(value[1]);
            }
            if($('.sale_order_note').val()){
                order.set_sale_note($.trim($('.sale_order_note').val()));
            }
            order.set_sale_order_payment_method($('#payment_method').val() || false);
            order.set_sale_order_date($('#orderdate-datepicker').val() || false);
            order.set_sale_order_requested_date($('#requesteddate-datepicker').val() || false)
            order.set_sale_payment_method($('#payment_method').find(":selected").text());
            self.shipping_contact().then(function(){
                self.invoice_contact().then(function(){
                    if(self.sale_order_button){
                        self.sale_order_button.renderElement();
                    }
                    if(self.payment_obj){
                        order.set_paying_sale_order(true);
                    }
                    self.gui.close_popup();
                    self.pos.create_sale_order(self.delivery_done);
                });
            });
        },
        click_cancel: function(){
            var self = this;
            if(self.payment_obj){
                window.document.body.addEventListener('keypress',self.payment_obj.keyboard_handler);
                window.document.body.addEventListener('keydown',self.payment_obj.keyboard_keydown_handler);
                $('#btn_so').show();
            }
            this.gui.close_popup();
        },

        renderElement: function(){
            var self = this;
            this._super();
            $('#upload_file').change(_.bind(self.upload_files, self));
            $('#orderdate-datepicker').datetimepicker({format:'Y-m-d H:i'}).val(new moment ().format("YYYY-MM-DD HH:mm"));
            $('#requesteddate-datepicker').datetimepicker({format:'Y-m-d H:i'}).val(new moment ().format("YYYY-MM-DD HH:mm"));
            $(".tabs-menu a").click(function(event) {
                event.preventDefault();
                $(this).parent().addClass("current");
                $(this).parent().siblings().removeClass("current");
                var tab = $(this).attr("href");
                $(".tab-content").not(tab).css("display", "none");
                $(tab).fadeIn();

            });
            $(".tabs-menu .signature_tab").click(function(event) {
                if(!self.$("#signature").jSignature("getData", "image")){
                    self.$("#signature").jSignature();
                }
            });
            this.$('.clear').click(function(){
                self.$("#signature").jSignature("reset");
            });
            $('.invoice_diff_address').click(function(){
                if($(this).prop('checked')){
                    if(self.payment_obj){
                        $('body').off('keypress', self.payment_obj.keyboard_handler);
                        $('body').off('keydown', self.payment_obj.keyboard_keydown_handler);
                        window.document.body.removeEventListener('keypress',self.payment_obj.keyboard_handler);
                        window.document.body.removeEventListener('keydown',self.payment_obj.keyboard_keydown_handler);
                    }
                    $('.invoicing_contact_selection').attr({'disabled': 'disabled'});
                    $('div.invoice_create_contact').show();
                } else {
                    $('.invoicing_contact_selection').removeAttr('disabled');
                    $('div.invoice_create_contact').hide();
                }
            });
            $('.ship_diff_address').click(function(){
                if($(this).prop('checked')){
                    if(self.payment_obj){
                        $('body').off('keypress', self.payment_obj.keyboard_handler);
                        $('body').off('keydown', self.payment_obj.keyboard_keydown_handler);
                    }
                    $('.shipping_contact_selection').attr({'disabled': 'disabled'});
                    $('div.ship_create_contact').show();
                } else {
                    $('.shipping_contact_selection').removeAttr('disabled');
                    $('div.ship_create_contact').hide();
                }
            });
            $('.ship_create_contact').find('.client_state').autocomplete({
                source: self.pos.states || false,
                select: function (event, ui) {
                    self.shipping_state = ui.item.id;
                    return ui.item.value
                }
            });
            $('.ship_create_contact').find('.client_country').autocomplete({
                source: self.pos.countries || false,
                select: function (event, ui) {
                    self.shipping_country = ui.item.id;
                    return ui.item.value
                }
            });
            $('.invoice_create_contact').find('.client_state').autocomplete({
                source: self.pos.states || false,
                select: function (event, ui) {
                    self.invoice_state = ui.item.id;
                    return ui.item.value
                }
            });
            $('.invoice_create_contact').find('.client_country').autocomplete({
                source: self.pos.countries || false,
                select: function (event, ui) {
                    self.invoice_country = ui.item.id;
                    return ui.item.value
                }
            });
        },
        get_diff_shipping_address: function(){
            var self = this;
            var order = self.pos.get_order();
            var shipping_contact = $('.shipping_contact_selection option:selected').val();
            if(shipping_contact > 0 && !$('.ship_diff_address').prop('checked')){
                order.set_shipping_address(shipping_contact);
                return true;
            } else if($('.ship_diff_address').prop('checked')){
                var name = $('.ship_create_contact').find('.client_name');
                if(!name.val()){
                    $(name).attr('style', 'border: thin solid red !important');
                    return false
                }
                var state = self.shipping_state || false;
                var country = self.shipping_country || false;
                var vals = {
                    'name': $('.ship_create_contact').find('.client_name').val(),
                    'email': $('.ship_create_contact').find('.client_email').val(),
                    'city': $('.ship_create_contact').find('.client_city').val(),
                    'state_id':  state,
                    'zip': $('.ship_create_contact').find('.client_zip').val(),
                    'country_id':  country,
                    'mobile': $('.ship_create_contact').find('.client_mobile').val(),
                    'phone': $('.ship_create_contact').find('.client_phone').val(),
                    'parent_id': order.get_client().id,
                    'type': 'delivery',
                }
                self.get_diff_shipping_address(vals).then(function(){
                    var diff_address = self.pos.get('diff_address');
                    order.set_shipping_address(diff_address);
                });
            }
            return true;
        },
        shipping_contact: function(vals){
            var self = this;
            var order = self.pos.get_order();
            return new Promise(function (resolve, reject) {
                var shipping_contact = $('.shipping_contact_selection option:selected').val();
                if(shipping_contact > 0 && !$('.ship_diff_address').prop('checked')){
                    order.set_shipping_address(shipping_contact);
                    resolve();
                } else if($('.ship_diff_address').prop('checked')){
                    var name = $('.ship_create_contact').find('.client_name');
                    if(!name.val()){
                        $(name).attr('style', 'border: thin solid red !important');
                        reject();
                    }
                    var state = self.shipping_state || false;
                    var country = self.shipping_country || false;
                    var vals = {
                        'name': $('.ship_create_contact').find('.client_name').val(),
                        'email': $('.ship_create_contact').find('.client_email').val(),
                        'city': $('.ship_create_contact').find('.client_city').val(),
                        'state_id':  state,
                        'zip': $('.ship_create_contact').find('.client_zip').val(),
                        'country_id':  country,
                        'mobile': $('.ship_create_contact').find('.client_mobile').val(),
                        'phone': $('.ship_create_contact').find('.client_phone').val(),
                        'parent_id': order.get_client().id,
                        'type': 'delivery',
                    }
                   var params = {
                        model: 'res.partner',
                        method: 'create',
                        args: [vals],
                    }
                   rpc.query(params, {
                        timeout: 3000,
                        shadow: true,
                   })
                   .then(function (res) {
                        if(res){
                            order.set_shipping_address(res);
                            resolve();
                        }else {
                            reject();
                        }
                   }, function (type, err) { reject(); });
                }else{
                    resolve();
                }
            });
        },
        invoice_contact: function(){
            var self = this;
            var order = self.pos.get_order();
            return new Promise(function (resolve, reject) {
                var invoice_contact = $('.invoicing_contact_selection option:selected').val();
                if(invoice_contact > 0 && !$('.invoice_diff_address').prop('checked')){
                    order.set_invoice_address(invoice_contact);
                    resolve();
                } else if($('.invoice_diff_address').prop('checked')){
                    var name = $('.invoice_create_contact').find('.client_name');
                    if(!name.val()){
                        $(name).attr('style', 'border: thin solid red !important');
                        reject();
                    }
                    var state = self.invoice_state || false;
                    var country = self.invoice_country || false;
                    var vals = {
                        'name': $('.invoice_create_contact').find('.client_name').val(),
                        'email': $('.invoice_create_contact').find('.client_email').val(),
                        'city': $('.invoice_create_contact').find('.client_city').val(),
                        'state_id':  state,
                        'zip': $('.invoice_create_contact').find('.client_zip').val(),
                        'country_id':  country,
                        'mobile': $('.invoice_create_contact').find('.client_mobile').val(),
                        'phone': $('.invoice_create_contact').find('.client_phone').val(),
                        'parent_id': order.get_client().id,
                        'type': 'invoice',
                    }
                     var params = {
                        model: 'res.partner',
                        method: 'create',
                        args: [vals],
                    }
                   rpc.query(params, {
                        timeout: 3000,
                        shadow: true,
                   })
                   .then(function (res) {
                        if(res){
                            order.set_shipping_address(res);
                            resolve();
                        }else {
                            reject();
                        }
                   }, function (type, err) { reject(); });
                }else{
                    resolve();
                }
            });
        },
    });
    gui.define_popup({name:'sale_order_popup', widget: SaleOrderPopup});

    var SOConfirmPopup = PopupWidget.extend({
        template: 'SOConfirmPopup',
        show: function(options){
           var self = this;
           this.options = options;
           this.deliver_products = options.deliver_products;
           this._super(options);
        },
        click_confirm: function(){
           var self = this;
           self.gui.show_popup('sale_order_popup', {'sale_order_button': self.options.sale_order_buttonm,'delivery_done':true});
        },
    });
    gui.define_popup({name:'so_confirm_popup', widget: SOConfirmPopup});

    var SOReturnPopup = PopupWidget.extend({
        template: 'SOReturnPopup',
        show: function(options){
            var self = this;
            this._super();
            this.lines = options.lines || "";
            this.sale_order = options.sale_order || "";
            this.renderElement();
        },
        renderElement: function(){
            var self = this;
            self._super();
            $('.js_return_qty').click(function(ev){
                ev.preventDefault();
                var $link = $(ev.currentTarget);
                var $input = $link.parent().parent().find("input");
                var min = parseFloat($input.data("min") || 1);
                var max = parseFloat($input.data("max") || $input.val());
                var total_qty = parseFloat($input.data("total-qty") || 0);
                var quantity = ($link.has(".fa-minus").length ? -1 : 1) + parseFloat($input.val(),10);
                $input.val(quantity > min ? (quantity < max ? quantity : max) : min);
                $input.change();
                return false;
            });
            $('.remove_line').click(function(event){
                $(this).parent().remove();
            });
        },
        click_confirm: function(){
            var self = this;
            var filter_records = [];
            $(".popup-product-return-list tbody tr").map(function(){
                var id = Number($(this).attr('id'));
                var qty = Number($(".popup-product-return-list tbody tr#"+id+"").find('.js_quantity').val());
                var line = _.find(self.lines, function(obj) { return obj.id == id });
                if(qty && qty > 0 && line){
                    line['return_qty'] = qty;
                    if(line){
                        filter_records.push(line);
                    }
                }
            });
            if(filter_records && filter_records[0]){
                var self = this;
                var params = {
                    model: 'sale.order',
                    method: 'return_sale_order',
                    args: [filter_records],
                }
                rpc.query(params, {async: false}).then(function(result){
                    if(result){
                        alert("Sale order return successfully!");
                        self.gui.close_popup();
                    }
                });
            }
        },
        click_cancel: function(){
            this.gui.close_popup();
        }
    });
    gui.define_popup({name:'sale_return_popup', widget: SOReturnPopup});


});