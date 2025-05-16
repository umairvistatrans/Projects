odoo.define('aspl_pos_create_so_extension_ee.screen', function (require) {
	"use strict";

	var screens = require('point_of_sale.screens');
	var gui = require('point_of_sale.gui');
	var core = require('web.core');
	var models = require('point_of_sale.models');
	var rpc = require('web.rpc');

	var QWeb = core.qweb;
	var _t = core._t;

	var SaleOrderButton = screens.ActionButtonWidget.extend({
	    template: 'SaleOrderButton',
	    button_click: function(){
	        var self = this;
	        var order = this.pos.get_order();
	        var currentOrderLines = order.get_orderlines();
	        var lines = [];
           _.each(currentOrderLines, function(line){
               if(line.product.invoice_policy == "delivery"){
               	lines.push(line)
               }
           })
	        if(currentOrderLines.length <= 0){
	            alert('No product selected !');
	        } else if(order.get_client() == null) {
	            var answer = confirm('Please select customer !')
	            if(answer){
	                self.gui.show_screen('clientlist');
	            }
	        } else if (lines.length != 0){
	        	self.gui.show_popup('so_confirm_popup', {'sale_order_button': self,'deliver_products':lines});
	        } else{
	        	self.gui.show_popup('sale_order_popup', {'sale_order_button': self});
	        }
	    },
	});

	screens.define_action_button({
	    'name': 'saleorder',
	    'widget': SaleOrderButton,
	    'condition': function(){
	        return this.pos.config.sale_order_operations == "draft" || this.pos.config.sale_order_operations == "confirm" || this.pos.get_order().get_edit_quotation();
	    },
	});

	var ViewSaleOrdersButton = screens.ActionButtonWidget.extend({
	    template: 'ViewSaleOrdersButton',
	    button_click: function(){
            this.gui.show_screen('saleorderlist');
	    },
	});

	screens.define_action_button({
	    'name': 'viewsaleorder',
	    'widget': ViewSaleOrdersButton,
	    'condition': function(){
	        return this.pos.config.sale_order_operations;
	    },
	});

	var ViewInvoicesButton = screens.ActionButtonWidget.extend({
	    template: 'ViewInvoicesButton',
	    button_click: function(){
            this.gui.show_screen('invoice_list');
	    },
	});

	screens.define_action_button({
	    'name': 'viewinvoices',
	    'widget': ViewInvoicesButton,
	    'condition': function(){
	        return this.pos.config.sale_order_invoice;
	    },
	});

	var EditQuotationButton = screens.ActionButtonWidget.extend({
	    template: 'EditQuotationButton',
	    button_click: function(){
            var self = this;
	        var order = this.pos.get_order();
	        var currentOrderLines = order.get_orderlines();
	        if(currentOrderLines.length <= 0){
	            alert('No product selected !');
	        } else if(order.get_client() == null) {
	            alert('Please select customer !');
	        } else {
	        	self.gui.show_popup('sale_order_popup', {'sale_order_button': self});
	        }
	    },
	});

	screens.define_action_button({
	    'name': 'EditQuotationButton',
	    'widget': EditQuotationButton,
	});

	screens.PaymentScreenWidget.include({
		renderElement: function() {
			var self = this;
	        this._super();
            this.$('#btn_so').click(function(){
            	var order = self.pos.get_order();
            	var lines = [];
                if(order){
                	var currentOrderLines = order.get_orderlines();
                	_.each(currentOrderLines, function(line){
                        if(line.product.invoice_policy == "delivery"){
                        	lines.push(line)
                        }
                    })
                	var paymentline_ids = [];
                    if(order.get_paymentlines().length > 0){
                        if(currentOrderLines.length <= 0){
                            alert('Empty order');
                        } else if(order.get_client() == null) {
                            var answer = confirm('Please select customer !')
                            if(answer){
                                self.gui.show_screen('clientlist');
                            }
                        } else {
                            $('#btn_so').hide();
                            order.set_paying_sale_order(true);
                            if(!order.get_order_id() || order.get_edit_quotation()){
                            	if (lines.length != 0){
                    	        	self.gui.show_popup('so_confirm_popup', {'payment_obj': self,'deliver_products':lines});
                    	        } else{
                    	        	self.gui.show_popup('sale_order_popup', {'payment_obj': self});
                    	        }
                            } else {
                                self.pos.create_sale_order();
                            }
                        }
                    }
                }
            });
            this.$('#btn_invoice_pay').click(function(){
            	var order = self.pos.get_order();
            	var invoice_id = order.get_invoice_id();
            	if(order.get_due() <= 0 ){
                    var paymentlines = [];
                    _.each(order.get_paymentlines(), function(paymentline){
                        paymentlines.push({
                        'journal_id': paymentline.payment_method.id,
                        'amount': paymentline.amount,
                        })
                    });
                    var params = {
                        model: 'sale.order',
                        method: 'pay_invoice',
                        args: [{ "invoice_id" : invoice_id , "paymentlines" : paymentlines }],
                    }
                    rpc.query(params, {async: false}).then(function(result){
                        if(result){
                            self.gui.show_screen('receipt');
                        }
                    })
                }
            });
		},
		order_changes: function(){
	        var self = this;
	        var order = this.pos.get_order();
	        var total = order ? order.get_total_with_tax() : 0;
	        if (!order) {
	            return;
	        } else if (order.is_paid()) {
	            self.$('.next').addClass('highlight');
	            self.$('#btn_invoice_pay').addClass('highlight');
	        } else if(order.get_due() == 0 || order.get_due() == total ){
	            self.$('#btn_so').removeClass('highlight');
	        } else {
	            self.$('.next').removeClass('highlight');
	            self.$('#btn_invoice_pay').removeClass('highlight');
	            self.$('#btn_so').addClass('highlight');
	        }
	    },
	    click_set_customer: function(){
	        var self = this;
	        var order = this.pos.get_order();
	        if(!order.get_sale_order_pay() || !order.get_invoice_pay()){
	            self._super();
	        }
	    },
	    click_back: function(){
	        var self = this;
	        var order = this.pos.get_order();
	        if(order.get_sale_order_pay()){
                this.gui.show_popup('confirm',{
                    title: _t('Discard Sale Order'),
                    body:  _t('Do you want to discard the payment of sale order '+ order.get_sale_order_name() +' ?'),
                    confirm: function() {
                        order.finalize();
                    },
                });
	        }else if(order.get_invoice_pay()){
	            this.gui.show_popup('confirm',{
                    title: _t('Discard Invoice'),
                    body:  _t('Do you want to discard the payment of invoice '+ order.get_invoice_name() +' ?'),
                    confirm: function() {
                        order.finalize();
                    },
                });
	        }else {
	            self._super();
	        }
	    },
	    validate_order: function(force_validation) {
	    	var self = this;
	    	var order = self.pos.get_order();
	    	if(order.get_sale_order_pay() || order.get_invoice_pay()){
	    		return
	    	} else{
	    		this._super(force_validation);
	    	}
	    },
	});

	/* Sale Order list screen */
	var SaleOrderListScreenWidget = screens.ScreenWidget.extend({
	    template: 'SaleOrderListScreenWidget',
	    init: function(parent, options){
	    	var self = this;
	        this._super(parent, options);
	        this.reload_btn = function(){
	        	$('.fa-refresh').toggleClass('rotate', 'rotate-reset');
	        	self.reloading_orders();
	        };
	    },
	    filter:"all",
        date: "all",
	    start: function(){
	    	var self = this;
            this._super();

            this.$('.back').click(function(){
                self.gui.back();
            });
            var orders = self.pos.get('pos_sale_order_list');
            self.reloading_orders().then(function(){
                var orders=self.pos.get('pos_sale_order_list');
                self.render_list(orders);
            });
            $('input#datepicker').datepicker({
           	    dateFormat: 'yy-mm-dd',
                autoclose: true,
                closeText: 'Clear',
                showButtonPanel: true,
                onSelect: function (dateText, inst) {
                	var date = $(this).val();
					if (date){
					    self.date = date;
					    self.render_list(orders);
					}
				},
				onClose: function(dateText, inst){
                    if( !dateText ){
                        self.date = "all";
                        self.render_list(orders);
                    }
                }
            }).focus(function(){
                var thisCalendar = $(this);
                $('.ui-datepicker-close').click(function() {
                    thisCalendar.val('');
                    self.date = "all";
                    self.render_list(orders);
                });
            });
            this.$('.sale-order-list-contents').delegate('#pay_amount','click',function(event){
            	var order_id = parseInt($(this).data('id'));
                var result = self.pos.db.get_sale_order_by_id(order_id);
                if(result.state == "cancel"){
                	alert("Sorry, This order is cancelled");
                	return
                }
                if(result.state == "done"){
                	alert("Sorry, This Order is already locked");
                	return
                }

                var selectedOrder = self.pos.get_order();
                if (result && result.order_line.length > 0) {
                    var count = 0;
               	 	var currentOrderLines = selectedOrder.get_orderlines();
               	 	if(currentOrderLines.length > 0) {
	                 	selectedOrder.set_order_id('');
	                    for (var i=0; i <= currentOrderLines.length + 1; i++) {
							_.each(currentOrderLines,function(item) {
								selectedOrder.remove_orderline(item);
							});
	                    }
               	 	}
                    var partner = null;
                    if (result.partner_id && result.partner_id[0]) {
                        var partner = self.pos.db.get_partner_by_id(result.partner_id[0])
                    }
                    selectedOrder.set_client(partner);
               	 	selectedOrder.set_sale_order_name(result.name);
                    // Partial Payment
                    if(self.pos.config.paid_amount_product){
                        var paid_amount = 0.00;
                        var first_invoice = false;
                        if(result.invoice_ids.length > 0){
                            var MovePromise = new Promise(function(resolve, reject){
                                rpc.query({
                                    model: 'account.move',
                                    method: 'search_read',
                                    domain: [['id', 'in', result.invoice_ids],['state', 'not in', ['paid']]],
                                    fields: self.fieldNames,
                                })
                                .then(function(invoices) {
                                    console.log("Not PAidINVOICES",invoices)
                                    if(invoices){
                                        resolve(invoices);
                                    }else{
                                        reject();
                                    }
                                });
                            })
                            MovePromise.then(function(invoices){
                                if(invoices){
                                    first_invoice = invoices[0];
                                    _.each(invoices, function(invoice){
                                    	paid_amount += invoice.amount_total - invoice.amount_residual
                                    })
                                }
                                if(paid_amount){
                                    var product = self.pos.db.get_product_by_id(self.pos.config.paid_amount_product[0]);
                                    selectedOrder.add_product(product, {price: paid_amount, quantity: -1});
                                }
                                if (first_invoice){
                                    selectedOrder.set_inv_id(first_invoice.id)
                                }
                                 // Partial Payment over
                                if (result.order_line) {
                                    self.get_sale_orderline(result.order_line).then(function(){
                                        selectedOrder.set_order_id(order_id);
                                        selectedOrder.set_sequence(result.name);
                                        selectedOrder.set_sale_order_pay(true);
                                        self.pos.gui.screen_instances.payment.renderElement();
                                        self.gui.show_screen('payment');
                                        $(self.pos.gui.screen_instances.payment.el).find('.button.next, .button.js_invoice').hide();
                                    });
                                }
                            })
                        } else {
                            // Partial Payment over
                            if (result.order_line) {
                                self.get_sale_orderline(result.order_line).then(function(){
                                    selectedOrder.set_order_id(order_id);
                                    selectedOrder.set_sequence(result.name);
                                    selectedOrder.set_sale_order_pay(true);
                                    self.pos.gui.screen_instances.payment.renderElement();
                                    self.gui.show_screen('payment');
                                    $(self.pos.gui.screen_instances.payment.el).find('.button.next, .button.js_invoice').hide();
                                    /*self.contacts = self.pos.get('contacts');
                                    self.renderElement();*/
                                });
                            }
                        }
                    } else {
                    	self.gui.show_popup('error-traceback',{
							title: _t("Configuration Required"),
							body:  _t("Please configure dummy product for paid amount from POS configuration"),
						});
						return
                    }
                }
            });

            this.$('.sale-order-list-contents').delegate('#edit_quotation','click',function(event){
                var order_id = parseInt($(this).data('id'));
                var result = self.pos.db.get_sale_order_by_id(order_id);
                if(result.state == "cancel"){
                	alert("Sorry, This order is cancelled");
                	return
                }
                if(result.state == "done"){
                	alert("Sorry, This Order is already locked");
                	return
                }
                if(result.state == "sale"){
                	alert("Sorry, This Order is confirmed");
                	return
                }
                var selectedOrder = self.pos.get_order();
                if (result && result.order_line.length > 0) {
                    var count = 0;
               	 	var currentOrderLines = selectedOrder.get_orderlines();
               	 	if(currentOrderLines.length > 0) {
	                 	selectedOrder.set_order_id('');
	                    for (var i=0; i <= currentOrderLines.length + 1; i++) {
							_.each(currentOrderLines,function(item) {
								selectedOrder.remove_orderline(item);
							});
	                    }
               	 	}
                    var partner = null;
                    if (result.partner_id && result.partner_id[0]) {
                        var partner = self.pos.db.get_partner_by_id(result.partner_id[0])
                    }
                    selectedOrder.set_client(partner);
                    selectedOrder.set_shipping_address(result.partner_shipping_id ? result.partner_shipping_id[0] : 0)
                    selectedOrder.set_invoice_address(result.partner_invoice_id ? result.partner_invoice_id[0] : 0)
               	 	selectedOrder.set_sale_order_name(result.name);
               	 	selectedOrder.set_sale_order_payment_method(result.payment_method_desc);
               	 	selectedOrder.set_sale_order_date(result.date_order);
               	 	selectedOrder.set_sale_order_requested_date(result.requested_date);
               	 	new Promise(function (resolve, reject) {
                        var params = {
                            model: 'sale.order.line',
                            method: 'search_read',
                            domain: [['id', 'in', result.order_line]],
                            fields: self.fieldNames,
                        }
                        rpc.query(params, {
                            timeout: 3000,
                            shadow: true,
                        })
                        .then(function (result_lines) {
                            _.each(result_lines, function(res){
                                 count += 1;
                                 var product = self.pos.db.get_product_by_id(Number(res.product_id[0]));
                                 if(product){
                                     var line = new models.Orderline({}, {pos: self.pos, order: selectedOrder, product: product});
                                     line.set_quantity(res.product_uom_qty);
                                     line.set_unit_price(res.price_unit);
                                     line.set_discount(res.discount);
                                     selectedOrder.add_orderline(line);
                                     selectedOrder.select_orderline(selectedOrder.get_last_orderline());
                                 }
                            });
                            resolve();
                        }, function (type, error) { reject(); });
                    });
               	}
                selectedOrder.set_order_id(order_id);
                selectedOrder.set_edit_quotation(true);
                selectedOrder.set_sequence(result.name);
                self.pos.gui.screen_instances.payment.renderElement();
                $(self.pos.gui.screen_instances.payment.el).find('.button.next, .button.js_invoice').hide();
                self.gui.show_screen('products');
            });

            this.$('.sale-order-list-contents').delegate('#return_so','click',function(event){
            	var order_id = parseInt($(this).data('id'));
            	if(order_id){
                    var sale_order = self.pos.db.get_sale_order_by_id(order_id);
                    if(sale_order){
                        var params = {
                        	model: "sale.order",
                        	method: "get_return_product",
                        	args: [order_id]
                        }
                        rpc.query(params, {async: false}).then(function(result){
                            if(result && result[0]){
                                var flag = false;
                                result.map(function(line){
                                    if(line.qty > 0){
                                        flag = true;
                                    }
                                });
                                if(flag){
                                    self.gui.show_popup('sale_return_popup',{
                                        'lines':result,
                                        'sale_order':sale_order
                                    });
                                }else{
                                    alert("Sorry, No items avilable for return sale order!");
                                }
                            }else{
                                alert("Sorry, No items avilable for return sale order!");
                            }
                        });
                    }
                }
            });

        //search box
            var search_timeout = null;
            if(this.pos.config.iface_vkeyboard && self.chrome.widget.keyboard){
            	self.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }
            this.$('.searchbox input').on('keyup',function(event){
                clearTimeout(search_timeout);
                var query = this.value;
                search_timeout = setTimeout(function(){
                    self.perform_search(query,event.which === 13);
                },70);
            });

            this.$('.searchbox .search-clear').click(function(){
                self.clear_search();
            });

	    },
	    get_sale_orderline: function(id){
	        var self = this;
	        var selectedOrder = self.pos.get_order();
	        return new Promise(function (resolve, reject) {
                var params = {
                    model: 'sale.order.line',
                    method: 'search_read',
                    domain: [['id', 'in', id]],
                    fields: self.fieldNames,
                }
                rpc.query(params, {
                    timeout: 3000,
                    shadow: true,
                })
                .then(function (result_lines) {
                    var count = 0;
                    _.each(result_lines, function(res){
                         count += 1;
                         var product = self.pos.db.get_product_by_id(Number(res.product_id[0]));
                         if(product){
                             var line = new models.Orderline({}, {pos: self.pos, order: selectedOrder, product: product});
                             line.set_quantity(res.product_uom_qty);
                             line.set_unit_price(res.price_unit)
                             line.set_discount(res.discount)
                             selectedOrder.add_orderline(line);
                             selectedOrder.select_orderline(selectedOrder.get_last_orderline());
                         }
                    });
                    resolve();
                }, function (type, error) { reject(); });
            });
	    },
	    show: function(){
	        var self = this;
	        this._super();
	        this.reload_orders();
	        $('.button.my_orders').trigger('click');
	        var orders = self.pos.get('pos_sale_order_list');
	        self.render_list(orders);

	    },
	    perform_search: function(query, associate_result){
	        var self = this;
            if(query){
                var orders = this.pos.db.search_sale_order(query);
                if ( associate_result && orders.length === 1){
                    this.gui.back();
                }
                if(orders){
                    var contents = this.$el[0].querySelector('.sale-order-list-contents');
	                contents.innerHTML = "";
                    for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
                        var order    = orders[i];
                        order.amount_total = parseFloat(order.amount_total).toFixed(2);
                        var clientline_html = QWeb.render('SaleOrderlistLine',{widget: this, order:order});
                        var clientline = document.createElement('tbody');
                        clientline.innerHTML = clientline_html;
                        clientline = clientline.childNodes[1];
                        contents.appendChild(clientline);
                    }
                }
            }else{
                var orders = self.pos.get('pos_sale_order_list');
                this.render_list(orders);
            }
        },
        clear_search: function(){
            var orders = this.pos.get('pos_sale_order_list');
            this.render_list(orders);
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },
	    render_list: function(orders){
        	var self = this;
        	var orders;
            var contents = this.$el[0].querySelector('.sale-order-list-contents');
            contents.innerHTML = "";
            if(self.filter !== "" && self.filter !== "all" && self.filter != "my_orders"){
                var orders = self.pos.get('pos_sale_order_list');
	            orders = $.grep(orders,function(order){
	            	return order.state === self.filter;
	            });
            }
            if(self.date !== "" && self.date !== "all"){
            	var x = [];
            	var orders = self.pos.get('pos_sale_order_list');
            	for(var i=0; i<orders.length;i++){
                    var date_order = $.datepicker.formatDate("yy-mm-dd",new Date(orders[i].date_order));
            		if(self.date === date_order){
            			x.push(orders[i]);
            		}
            	}
            	orders = x;
                for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
                    var order    = orders[i];
                    order.amount_total = parseFloat(order.amount_total).toFixed(2);
                    var clientline_html = QWeb.render('SaleOrderlistLine',{widget: this, order:order});
                    var clientline = document.createElement('tbody');
                    clientline.innerHTML = clientline_html;
                    clientline = clientline.childNodes[1];
                    contents.appendChild(clientline);
                }
            }else{
                if(orders){
                    for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
                        var order    = orders[i];
                        order.amount_total = parseFloat(order.amount_total).toFixed(2);
                        var clientline_html = QWeb.render('SaleOrderlistLine',{widget: this, order:order});
                        var clientline = document.createElement('tbody');
                        clientline.innerHTML = clientline_html;
                        clientline = clientline.childNodes[1];
                        contents.appendChild(clientline);
                    }
                }else{
                    var orders = self.pos.get('pos_sale_order_list');
                    for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
                        var order    = orders[i];
                        order.amount_total = parseFloat(order.amount_total).toFixed(2);
                        var clientline_html = QWeb.render('SaleOrderlistLine',{widget: this, order:order});
                        var clientline = document.createElement('tbody');
                        clientline.innerHTML = clientline_html;
                        clientline = clientline.childNodes[1];
                        contents.appendChild(clientline);
                    }
                }
            }
            if(self.filter == 'my_orders'){
                var user_id = self.pos.user.id;
                if(user_id && orders.length > 0){
                    var user_orders = [];
                    orders = $.grep(orders,function(order){
                        return order.user_id[0] === user_id;
                    });
                }
            }
            $("table.sale-order-list").simplePagination({
				previousButtonClass: "btn btn-danger",
				nextButtonClass: "btn btn-danger",
				previousButtonText: '<i class="fa fa-angle-left fa-lg"></i>',
				nextButtonText: '<i class="fa fa-angle-right fa-lg"></i>',
				perPage:Number(self.pos.config.sale_order_record_per_page) > 0 ? Number(self.pos.config.sale_order_record_per_page) : 10
			});
        },
        reload_orders: function(){
        	var self = this;
             self.reloading_orders().then(function(){
                var orders=self.pos.get('pos_sale_order_list');
                self.render_list(orders);
            });
        },
	    reloading_orders: function(){
	    	var self = this;
	    	return new Promise(function (resolve, reject) {
                var params = {
                    model: 'sale.order',
                    method: 'search_read',
                    domain: self.pos.domain_sale_order,
                    fields: self.fieldNames,
                }
                rpc.query(params, {
                    timeout: 3000,
                    shadow: true,
                })
                .then(function (result) {
                    self.pos.db.add_sale_orders(result);
                    if(self.pos.user.display_own_sales_order){
                        var user_orders = [];
                        result.map(function(sale_order){
                            if(sale_order.user_id[0] == self.pos.user.id){
                                user_orders.push(sale_order);
                            }
                        });
                        result = user_orders;
                    }
                    result.map(function(data){
                        var dt = new Date(new Date(data.date_order) + "GMT");
                        var n = dt.toLocaleDateString();
                        var crmon = self.pos.addZero(dt.getMonth()+1);
                        var crdate = self.pos.addZero(dt.getDate());
                        var cryear = dt.getFullYear();
                        var crHour = self.pos.addZero(dt.getHours());
                        var crMinute = self.pos.addZero(dt.getMinutes());
                        var crSecond = self.pos.addZero(dt.getSeconds());
                         data.date_order = cryear + '/' + crmon +'/'+ crdate +' '+crHour +':'+ crMinute +':'+ crSecond;
                    });
                    self.pos.set({'pos_sale_order_list' : result});
                    resolve();
                }, function (type, error) { reject(); });
            });
	    },
	    renderElement: function(){
	    	var self = this;
	    	self._super();
	    	self.$('.button.paid').click(function(){
        		var orders=self.pos.get('pos_sale_order_list');
        		if(self.$(this).hasClass('selected')){
        			if(!self.pos.user.display_own_sales_order){
		        		self.$(this).removeClass('selected');
		        		$('.pay_button').show();
		        		$('.return_button').hide();
		        		$('.quotation_edit_button').show();
		        		self.filter = "all";
        			}
        		}else{
        			if(self.$('.button.draft').hasClass('selected')){
            			self.$('.button.draft').removeClass('selected');
            		}
        			if(self.$('.button.confirm').hasClass('selected')){
            			self.$('.button.confirm').removeClass('selected');
            		}
        			if(self.$('.button.my_orders').hasClass('selected')){
            			self.$('.button.my_orders').removeClass('selected');
            		}
        			self.$(this).addClass('selected');
        			$('.pay_button').hide();
                    $('.return_button').show();
        			$('.quotation_edit_button').hide();
	        		self.filter = "done";
        		}
        		self.render_list(orders);
            });
            self.$('.button.confirm').click(function(){
            	var orders = self.pos.get('pos_sale_order_list');
            	if(self.$(this).hasClass('selected')){
            		if(!self.pos.user.display_own_sales_order){
		        		self.$(this).removeClass('selected');
		        	    $('.pay_button, .quotation_edit_button').show();
		        	    $('.return_button').hide();
		        		self.filter = "all";
            		}
        		}else{
        			if(self.$('.button.paid').hasClass('selected')){
            			self.$('.button.paid').removeClass('selected');
            		}
        			if(self.$('.button.draft').hasClass('selected')){
            			self.$('.button.draft').removeClass('selected');
            		}
        			if(self.$('.button.my_orders').hasClass('selected')){
            			self.$('.button.my_orders').removeClass('selected');
            		}
            		$('.pay_button').show();
            		$('.return_button').hide();
            		$('.quotation_edit_button').hide();
        			self.$(this).addClass('selected');
	        		self.filter = "sale";
        		}
        		self.render_list(orders);
            });

            self.$('.button.my_orders').click(function(){
        		var orders = self.pos.get('pos_sale_order_list');
            	if(self.$(this).hasClass('selected')){
            		if(!self.pos.user.display_own_sales_order){
		        		self.$(this).removeClass('selected');
		        	    $('.pay_button, .quotation_edit_button').show();
		        	    $('.return_button').hide();
		        		self.filter = "all";
            		}
        		}else{
        			if(self.$('.button.paid').hasClass('selected')){
            			self.$('.button.paid').removeClass('selected');
            		}
        			if(self.$('.button.draft').hasClass('selected')){
            			self.$('.button.draft').removeClass('selected');
            		}
        			if(self.$('.button.confirm').hasClass('selected')){
            			self.$('.button.confirm').removeClass('selected');
            		}
            		$('.pay_button').hide();
            		$('.return_button').hide();
            		$('.quotation_edit_button').hide();
        			self.$(this).addClass('selected');
                	self.filter = "my_orders";
        		}
            	self.render_list(orders);
            });
            self.$('.button.draft').click(function(){
            	var orders=self.pos.get('pos_sale_order_list');
            	if(self.$(this).hasClass('selected')){
            		if(!self.pos.user.display_own_sales_order){
		        		self.$(this).removeClass('selected');
		        		$('.return_button').hide();
		        		$('.pay_button, .quotation_edit_button').show();
		        		self.filter = "all";
            		}
        		}else{
        			if(self.$('.button.paid').hasClass('selected')){
            			self.$('.button.paid').removeClass('selected');
            		}
        			if(self.$('.button.confirm').hasClass('selected')){
            			self.$('.button.confirm').removeClass('selected');
            		}
        			if(self.$('.button.my_orders').hasClass('selected')){
            			self.$('.button.my_orders').removeClass('selected');
            		}
            		$('.return_button').hide();
            		$('.pay_button, .quotation_edit_button').show();
        			self.$(this).addClass('selected');
	        		self.filter = "draft";
        		}
        		self.render_list(orders);
            });
	    	self.el.querySelector('.button.reload').addEventListener('click',this.reload_btn);
	    },
	});
	gui.define_screen({name:'saleorderlist', widget: SaleOrderListScreenWidget});

	// Invoice list screen
	var InvoiceListScreenWidget = screens.ScreenWidget.extend({
	    template: 'InvoiceListScreenWidget',
	    init: function(parent, options){
	    	var self = this;
	        this._super(parent, options);
	        this.reload_btn = function(){
	        	$('.fa-refresh').toggleClass('rotate', 'rotate-reset');
	        	self.reloading_invoices();
	        };
	    },
	    filter:"all",
        date: "all",
	    start: function(){
	    	var self = this;
            this._super();

            this.$('.back').click(function(){
                self.gui.back();
            });

            self.reloading_invoices();

            this.$('.button.draft').click(function(){
            	 var invoices = self.pos.get('sale_invoices');
            	if(self.$(this).hasClass('selected')){
                    self.$(this).removeClass('selected');
                    self.filter = "all";
        		}else{
        			if(self.$('.button.open').hasClass('selected')){
            			self.$('.button.open').removeClass('selected');
            		}
        			self.$(this).addClass('selected');
	        		self.filter = "draft";
        		}
        		self.render_invoice_list(invoices);
            });

            this.$('.button.open').click(function(){
            	 var invoices = self.pos.get('sale_invoices');
            	if(self.$(this).hasClass('selected')){
                    self.$(this).removeClass('selected');
                    self.filter = "all";
        		}else{
        			if(self.$('.button.draft').hasClass('selected')){
            			self.$('.button.draft').removeClass('selected');
            		}
        			self.$(this).addClass('selected');
	        		self.filter = "posted";
        		}
        		self.render_invoice_list(invoices);
            });

            this.$('.invoice-list-contents').delegate('#pay_invoice','click',function(event){
            	var invoice_id = parseInt($(this).data('id'));
            	var pay_amount = parseFloat($(this).data('amount'));
            	var partner_id = parseInt($(this).data('partner'));
            	var invoice_name = $(this).data('name');
            	if(self.pos.config.paid_amount_product){
                    var selectedOrder = self.pos.get_order();
                    var order_lines = selectedOrder.get_orderlines();

                    if(order_lines.length > 0) {
                        for (var i=0; i <= order_lines.length + 1; i++) {
                            _.each(order_lines  ,function(item) {
                                selectedOrder.remove_orderline(item);
                            });
                        }
                    }

                    var product = self.pos.db.get_product_by_id(self.pos.config.paid_amount_product[0]);
                    var partner = self.pos.db.get_partner_by_id(partner_id)
                    selectedOrder.add_product(product, {price: pay_amount, quantity: 1});
                    selectedOrder.set_invoice_id(invoice_id);
                    selectedOrder.set_client(partner);
                    selectedOrder.set_invoice_name(invoice_name);
                    selectedOrder.set_invoice_pay(true);
                    self.gui.show_screen('payment');
                    self.pos.gui.screen_instances.payment.renderElement();
                    $(self.pos.gui.screen_instances.payment.el).find('.button.next, .button.js_invoice').hide();
                }else{
                    self.gui.show_popup('error-traceback',{
                        title: _t("Configuration Required"),
                        body:  _t("Please configure dummy product for paid amount from POS configuration"),
                    });
                    return
                }
            });

             this.$('.invoice-list-contents').delegate('#print_invoice','click',function(event){
                var invoice_id = [parseInt($(this).data('id'))];
                self.pos.chrome.do_action('account.account_invoices',{
                    additional_context:{
                        active_ids:invoice_id,
                    }
                }).guardedCatch(function(){
                    alert("Connection lost");
                });
             });

            this.$('.sale-order-list-contents').delegate('#edit_quotation','click',function(event){
                var order_id = parseInt($(this).data('id'));
                var result = self.pos.db.get_sale_order_by_id(order_id);
                if(result.state == "cancel"){
                	alert("Sorry, This order is cancelled");
                	return
                }
                if(result.state == "done"){
                	alert("Sorry, This Order is already locked");
                	return
                }
                if(result.state == "sale"){
                	alert("Sorry, This Order is confirmed");
                	return
                }
                var selectedOrder = self.pos.get_order();
                if (result && result.order_line.length > 0) {
                    var count = 0;
               	 	var currentOrderLines = selectedOrder.get_orderlines();
               	 	if(currentOrderLines.length > 0) {
	                 	selectedOrder.set_order_id('');
	                    for (var i=0; i <= currentOrderLines.length + 1; i++) {
							_.each(currentOrderLines,function(item) {
								selectedOrder.remove_orderline(item);
							});
	                    }
               	 	}
                    var partner = null;
                    if (result.partner_id && result.partner_id[0]) {
                        var partner = self.pos.db.get_partner_by_id(result.partner_id[0])
                    }
                    selectedOrder.set_client(partner);
                    selectedOrder.set_shipping_address(result.partner_shipping_id ? result.partner_shipping_id[0] : 0)
                    selectedOrder.set_invoice_address(result.partner_invoice_id ? result.partner_invoice_id[0] : 0)
               	 	selectedOrder.set_sale_order_name(result.name);
               	 	selectedOrder.set_sale_order_payment_method(result.payment_method_desc);
               	 	selectedOrder.set_sale_order_date(result.date_order);
               	 	selectedOrder.set_sale_order_requested_date(result.requested_date);
               	 	var params = {
         				model: 'sale.order.line',
         				method: 'search_read',
         				domain: [['id', 'in', result.order_line]],
                        fields: self.fieldNames,
         			}
         			rpc.query(params, {async: false}).then(function(result_lines){
                        _.each(result_lines, function(res){
                             count += 1;
                             var product = self.pos.db.get_product_by_id(Number(res.product_id[0]));
                             if(product){
                                 var line = new models.Orderline({}, {pos: self.pos, order: selectedOrder, product: product});
                                 line.set_quantity(res.product_uom_qty);
                                 line.set_unit_price(res.price_unit);
                                 line.set_discount(res.discount);
                                 selectedOrder.add_orderline(line);
                                 selectedOrder.select_orderline(selectedOrder.get_last_orderline());
                             }
                        });
                     });
               	}
                selectedOrder.set_order_id(order_id);
                selectedOrder.set_edit_quotation(true);
                selectedOrder.set_sequence(result.name);
                self.pos.gui.screen_instances.payment.renderElement();
                $(self.pos.gui.screen_instances.payment.el).find('.button.next, .button.js_invoice').hide();
                self.gui.show_screen('products');
            });


            //search box
            var search_timeout = null;
            if(this.pos.config.iface_vkeyboard && self.chrome.widget.keyboard){
            	self.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }
            this.$('.searchbox input').on('keyup',function(event){
                clearTimeout(search_timeout);
                var query = this.value;
                search_timeout = setTimeout(function(){
                    self.perform_search(query,event.which === 13);
                },70);
            });

            this.$('.searchbox .search-clear').click(function(){
                self.clear_search();
            });

	    },
	    perform_search: function(query, associate_result){
	        var self = this;
            if(query){
                var invoices = this.pos.db.search_invoice(query);
                if ( associate_result && invoices.length === 1){
                    this.gui.back();
                }
                this.render_invoice_list(invoices);
            }else{
                var invoices = self.pos.get('sale_invoices');
                this.render_invoice_list(invoices);
            }
        },
        clear_search: function(){
            var invoices = this.pos.get('sale_invoices');
            this.render_invoice_list(invoices);
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },
	    render_invoice_list: function(invoices){
	        if(invoices){
                var self = this;
                console.log('self', self)
                var contents = this.$el[0].querySelector('.invoice-list-contents');
                contents.innerHTML = "";
                if(self.filter !== "" && self.filter !== "all"){
                    invoices = $.grep(invoices,function(invoice){
                        return invoice.state === self.filter;
                    });
                }
                if(self.date !== "" && self.date !== "all"){
                    var x = [];
                    for (var i=0; i<invoices.length;i++){
                        var date_invoice = $.datepicker.formatDate("yy-mm-dd",new Date(invoices[i].invoice_date));
                        if(self.date === date_invoice){
                            x.push(invoices[i]);
                        }
                    }
                    invoices = x;
                }
                for(var i = 0, len = Math.min(invoices.length,1000); i < len; i++){
                    var invoice    = invoices[i];
                    invoice.amount_total = parseFloat(invoice.amount_total).toFixed(2);
                    var clientline_html = QWeb.render('InvoicelistLine',{widget: this, invoice:invoice});
                    var clientline = document.createElement('tbody');
                    clientline.innerHTML = clientline_html;
                    clientline = clientline.childNodes[1];
                    contents.appendChild(clientline);
                }
	        }
        },
        reload_invoices: function(){
        	var self = this;
            var invoices = self.pos.get('sale_invoices');
            console.log("self.pos", self.pos)
            this.render_invoice_list(invoices);
        },
        reloading_invoices: function(){
             console.log("first")
            var self = this;
            var date = new Date();
	    	if(this.pos.config.sale_order_last_days){
                date.setDate(date.getDate() - this.pos.config.sale_order_last_days);
            }
            var start_date = date.toJSON().slice(0,10);
            return new Promise(function (resolve, reject) {
               var params = {
    				model: 'account.move',
                    method: 'search_read',
                    domain: [['state', 'in', ['posted']],['type', '=', 'out_invoice'], ['create_date', '>=', start_date], ['invoice_payment_state', '=', 'not_paid']],
                    fields: self.fieldNames,
    		   }
               rpc.query(params)
               .then(function (invoices) {
                    console.log("INVOICES",invoices)
                    if(invoices){
                        self.pos.db.add_sale_invoices(invoices);
                        self.render_invoice_list(invoices);
                        self.pos.set({'sale_invoices' : invoices});
                        self.reload_invoices();
                        resolve();
                    }else {
                        reject();
                    }
               }, function (type, err) { reject(); });

            });
        },
	    show: function(){
	        var self = this;
	        this._super();
            self.reloading_invoices().then(function(){
                var invoices = self.pos.get('sale_invoices');
                self.render_invoice_list(invoices);
                $('input#invdatepicker').datepicker({
                    dateFormat: 'yy-mm-dd',
                    autoclose: true,
                    closeText: 'Clear',
                    showButtonPanel: true,
                    onSelect: function (dateText, inst) {
                        var date = $(this).val();
                        if (date){
                            self.date = date;
                            self.render_invoice_list(invoices);
                        }
                    },
                    onClose: function(dateText, inst){
                        if( !dateText ){
                            self.date = "all";
                            self.render_invoice_list(invoices);
                        }
                    }
               }).focus(function(){
                    var thisCalendar = $(this);
                    $('.ui-datepicker-close').click(function() {
                        thisCalendar.val('');
                        self.date = "all";
                        self.render_invoice_list(invoices);
                    });
               });
            });
	    },
	    renderElement: function(){
	    	var self = this;
	    	self._super();
	    	self.el.querySelector('.button.reload').addEventListener('click',this.reload_btn);
	    },
	});
	gui.define_screen({name:'invoice_list', widget: InvoiceListScreenWidget});

});