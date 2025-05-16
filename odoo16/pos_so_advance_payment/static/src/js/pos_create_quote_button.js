/** @odoo-module **/  
  const { Gui } = require('point_of_sale.Gui');
  const PosComponent = require('point_of_sale.PosComponent');
  const { identifyError } = require('point_of_sale.utils');
  const ProductScreen = require('point_of_sale.ProductScreen');
  const { useListener } = require("@web/core/utils/hooks");
  const Registries = require('point_of_sale.Registries');
  const PaymentScreen = require('point_of_sale.PaymentScreen');
  import {standardFieldProps} from '@web/views/fields/standard_field_props';

  class CreateQuotationButton extends PosComponent {
      setup() {
          super.setup();
      }
      async onClick() {
        console.log("Test");
        //On click of the button create quote.
        var order = this.env.pos.selectedOrder;
        var partner_id = order.partner
        if(order.orderlines.length === 0)
          {
            this.showPopup('ConfirmPopup', {
                title: this.env._t('Product Warning'),
                body: this.env._t('Please add some products to proceed.')
            });
          }
        else
        {
          if(partner_id != null)
            {
            // fetching partner-data section
            let partner_data = await this.rpc({
              model: 'res.partner',
              method: 'search_read',
              args: [[['parent_id', '=', partner_id.id],['type', '=', 'delivery']],['id', 'name', 'street', 'street2','city','phone','mobile']],
              })
            console.log("partner-data: ",partner_data);

            let payment_methods = await this.rpc({
              model: 'pos.payment.method',
              method: 'search_read',
              args: [[['id', 'in',this.env.pos.config.sale_payment_method_ids ]],['name']],
            })
            console.log("payment_methods: ",payment_methods);

            const vals = {
              adv_pay : this.env.pos.config.allow_advance_payment,
              journals : payment_methods,
              currency_symbol : this.env.pos.currency.symbol,
              contacts : partner_data
            }
            console.log("vals: ",vals);
            let { confirmed, payload: code }=await this.showPopup('CreateSaleOrderPopupWidget',vals);

            }//end of partner id not null!

          else{
            this.showPopup('ConfirmPopup', {
                body: this.env._t('Please select the customer to proceed.')
            });
          }
        }      
  }
  }
  CreateQuotationButton.template = 'pos_so_advance_payment.CreateQuotationButton';
  
  ProductScreen.addControlButton({
      component: CreateQuotationButton,
      condition: function() {
          return true;
      },
  });
  Registries.Component.add(CreateQuotationButton);
  return CreateQuotationButton;