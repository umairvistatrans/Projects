# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime

class WebsiteInherit(models.Model):
    _inherit = "website"

    def sale_get_order(self, force_create=False, update_pricelist=False):
        sale_order = super(WebsiteInherit, self).sale_get_order(force_create, update_pricelist)
        if not sale_order.is_sent:
            sale_currency = self.env['res.currency'].search([('name', '=', sale_order.currency_id.name)])
            for line in sale_order.order_line:
                if line.product_id.is_preorder and line.product_id.qty_available <= line.product_id.allowed_preorder_qty:
                    if line.product_id.preorder_payment_type == 'partial':
                        product_currency = self.env['res.currency'].search([('name', '=', line.product_id.currency_id.name)])
                        price = product_currency._convert(line.product_id.list_price,sale_currency,sale_order.company_id, datetime.today().strftime('%Y-%m-%d'))
                        line.price_unit = price*(line.product_id.percent/100)
                        line.is_preorder = True	
                        sale_order.preorder = True
                        sale_order.payment_status = 'half'
                        sale_order.preorder_payment_type = 'partial'
        if 'preorder' in self._context:
            sale_order = self.env['sale.order'].browse(int(self._context.get('preorder')))
            if sale_order.preorder and sale_order.payment_status == 'remain':
                sale_currency = self.env['res.currency'].search([('name', '=', sale_order.currency_id.name)])
                for line in sale_order.order_line:
                    if line.is_preorder:
                        if line.product_id.preorder_payment_type == 'partial':
                            product_currency = self.env['res.currency'].search([('name', '=', line.product_id.currency_id.name)])
                            price = product_currency._convert(line.product_id.list_price,sale_currency,sale_order.company_id, datetime.today().strftime('%Y-%m-%d'))
                            line.price_unit = price*((100-line.product_id.percent)/100)
                            line.is_preorder = True	
                            sale_order.preorder = True
                            sale_order.payment_status = 'complete'
                            sale_order.preorder_payment_type = 'partial'
                sale_order._compute_amounts()
        elif sale_order.preorder and sale_order.payment_status == 'complete':
            sale_order.preorder_payment_type = 'full'
        return sale_order
