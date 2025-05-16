from dateutil.relativedelta import relativedelta

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for order in self:
            has_service_subscription = any(
                line.product_id.detailed_type == 'service' and line.product_id.is_subscription
                for line in order.order_line
            )
            if has_service_subscription:
                validity_type = order.order_line[0].product_id.validity_type
                validity_count = order.order_line[0].product_id.validity_count

                # Calculate end date based on validity type and count
                if validity_type == 'monthly':
                    end_date = fields.Datetime.now() + relativedelta(months=validity_count)
                elif validity_type == 'yearly':
                    end_date = fields.Datetime.now() + relativedelta(years=validity_count)
                else:
                    end_date = fields.Datetime.now()

                # Create subscription record
                subscription = self.env['subscription.config'].create({
                    'customer_id': order.partner_id.id,
                    'product_id': order.order_line[0].product_id.id,
                    'price_list_id': order.partner_id.property_product_pricelist.id,
                    'subscription_start_date': fields.Datetime.now(),
                    'subscription_end_date': end_date,
                    'state': 'active',
                })
                if subscription:
                    order.partner_id.property_product_pricelist = order.order_line[0].product_id.pricelist_id.id

        return super(SaleOrder, self).action_confirm()






