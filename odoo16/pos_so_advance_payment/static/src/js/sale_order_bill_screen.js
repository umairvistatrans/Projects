/** @odoo-module **/

const Registries = require('point_of_sale.Registries');
const ReceiptScreen = require('point_of_sale.ReceiptScreen');
const OrderReceipt = require('point_of_sale.OrderReceipt');
const { onWillUpdateProps } = owl;    
const { onMounted } = owl;
const SaleOrderBillScreenWidget = (ReceiptScreen) => {
	class SaleOrderBillScreenWidget extends ReceiptScreen {
		setup() {
			console.log("\nsetup method called inside the sale order bill screen widget!!\n");
			super.setup();			

			onMounted(() => {
				console.log("Mounted this: ",this);
				$('.receipt-change').remove();
				$('.receipt-paymentlines').remove();
			});
		}

	    click_next(){
	    	var order = self.env.pos.selectedOrder;
	    	this.env.pos.add_new_order();
	    	this.showScreen('ProductScreen');
	    }
	    
	    click_back(){
	    	this.showScreen('ProductScreen');
	    }
		
   }
		SaleOrderBillScreenWidget.template = 'SaleOrderBillScreenWidget';
		return SaleOrderBillScreenWidget;
}

Registries.Component.addByExtending(SaleOrderBillScreenWidget, ReceiptScreen);

return SaleOrderBillScreenWidget;
