# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, fields,  _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from datetime import datetime
from odoo.tools.json import scriptsafe as json_scriptsafe
import time


class WebsiteSalePreorder(WebsiteSale):

    @http.route(['/preorder/check'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def preorder_cart_check(self, qty, product_id):
        order = request.website.sale_get_order()
        preorder = request.env["website.preorder"].search([('status','=',True)])
        if order:
            if not order.is_sent:
                order_currency = request.env['res.currency'].search([('name', '=', order.currency_id.name)])
                for line in order.order_line:
                    if line.product_id.is_preorder and line.product_id.qty_available <= line.product_id.allowed_preorder_qty:
                        if line.product_id.preorder_payment_type == 'partial':
                            product_currency = request.env['res.currency'].search([('name', '=', line.product_id.currency_id.name)])
                            price = product_currency._convert(line.product_id.list_price,order_currency,order.company_id, datetime.today().strftime('%Y-%m-%d'))
                            line.price_unit = price*(line.product_id.percent/100)
                            line.is_preorder = True	
                            order.preorder = True
                            order.payment_status = 'half'
                            order.preorder_payment_type = 'partial'

            if len(order.order_line)==0:
                return True
            if len(order.order_line)==1:
                if order.order_line.product_id.id == product_id: 
                    if order.order_line.product_uom_qty + float(qty) > order.order_line.product_id.maximum_preorder_qty:
                        return "You are trying to add more than available quantity for this product"
                    return True
                return preorder.conditional_message
            else:
                return preorder.conditional_message
        else:
            return True
        
    @http.route(['/order/check'], type='json', auth="public", methods=['POST'], website=True,
                csrf=False)
    def order_check_for_add_to_cart(self, product_id):
        order = request.website.sale_get_order(force_create=True)
        preorder = request.env["website.preorder"].search([('status', '=', True)])
        product = request.env["product.product"].browse(product_id)
        if order:
            if len(order.order_line) == 0:
                return 0
            if len(order.order_line) == 1:
                if order.order_line.is_preorder and order.order_line.product_id.id != product.id:
                    return preorder.conditional_message
                else:
                    return 0
            if len(order.order_line) > 1:
                return 0
        else:
            return 0
        
    @http.route(['/preorder/payment/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def complete_preorder_remaining_payment(self, sale_order):
        sale_order = request.env["sale.order"].sudo().browse(int(sale_order))
        sale_order.write({'state' : 'draft'})
        sale_order.payment_status = 'remain'
        request.session['sale_order_id'] = sale_order.id
        request.session['sale_last_order_id'] = sale_order.id
        request.session['preorder_id'] = sale_order.id
        order = request.website.with_context(preorder=sale_order.id).sale_get_order()
        return request.redirect("/shop/payment")
    
    @http.route('/shop/payment', type='http', auth='public', website=True, sitemap=False)
    def shop_payment(self, **post):
        """ Payment step. This page proposes several payment means based on available
        payment.acquirer. State at this point :

         - a draft sales order with lines; otherwise, clean context / session and
           back to the shop
         - no transaction in context / session, or only a draft one, if the customer
           did go to a payment.acquirer website but closed the tab without
           paying / canceling
        """
        order = request.website.sale_get_order()
        if not order and 'preorder_id' in request.session:
            order = request.env['sale.order'].browse(int(request.session['preorder_id']))
        if not order.is_sent:
            order_currency = request.env['res.currency'].search([('name', '=', order.currency_id.name)])
            for line in order.order_line:
                if line.product_id.is_preorder and line.product_id.qty_available <= line.product_id.allowed_preorder_qty:
                    if line.product_id.preorder_payment_type == 'partial':
                        product_currency = request.env['res.currency'].search([('name', '=', line.product_id.currency_id.name)])
                        price = product_currency._convert(line.product_id.list_price,order_currency,order.company_id, datetime.today().strftime('%Y-%m-%d'))
                        line.price_unit = price*(line.product_id.percent/100)
                        line.is_preorder = True
                        order.preorder = True
                        order.payment_status = 'half'
                        order.preorder_payment_type = 'partial'
        # redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
        # if redirection:
        #     return redirection

        # render_values = self._get_shop_payment_values(order, **post)
        # render_values['only_services'] = order and order.only_services or False
        #
        # if render_values['errors']:
        #     render_values.pop('acquirers', '')
        #     render_values.pop('tokens', '')

        return super(WebsiteSalePreorder,self).shop_payment(**post)
    

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True, **kw):
        """
        This route is called :
            - When changing quantity from the cart.
            - When adding a product from the wishlist.
            - When adding a product to cart on the same page (without redirection).
        """
        order = request.website.sale_get_order(force_create=1)
        if order.state != 'draft':
            request.website.sale_reset()
            if kw.get('force_create'):
                order = request.website.sale_get_order(force_create=1)
            else:
                return {}

        pcav = kw.get('product_custom_attribute_values')
        nvav = kw.get('no_variant_attribute_values')
        value = order._cart_update(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=json_scriptsafe.loads(pcav) if pcav else None,
            no_variant_attribute_values=json_scriptsafe.loads(nvav) if nvav else None
        )

        # value['notification_info'] = self._get_cart_notification_information(order, [value['line_id']])
        # value['notification_info']['warning'] = value.pop('warning', '')

        if not order.cart_quantity:
            request.website.sale_reset()
            return value

        order = request.website.sale_get_order()
        order_line_id = order.order_line.filtered(lambda x: x.product_id.preorder_payment_type == 'full')
        if order_line_id:
            order.preorder = True
            order.preorder_payment_type = 'full'
            order.payment_status == 'complete'
            for line in order.order_line:
                line.is_preorder = True
        if not order.is_sent:
            order_currency = request.env['res.currency'].search([('name', '=', order.currency_id.name)])
            for line in order.order_line:
                if line.product_id.is_preorder and line.product_id.qty_available <= line.product_id.allowed_preorder_qty:
                    if line.product_id.preorder_payment_type == 'partial':
                        product_currency = request.env['res.currency'].search([('name', '=', line.product_id.currency_id.name)])
                        price = product_currency._convert(line.product_id.list_price,order_currency,order.company_id, datetime.today().strftime('%Y-%m-%d'))
                        line.price_unit = price*(line.product_id.percent/100)
                        line.is_preorder = True	
                        order.preorder = True
                        order.payment_status = 'half'
                        order.preorder_payment_type = 'partial'
        value['cart_quantity'] = order.cart_quantity

        if not display:
            return value

        # value['cart_ready'] = order._is_cart_ready()
        value['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template("website_sale.cart_lines", {
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': order._cart_accessories()
        })
        value['website_sale.total'] = request.env['ir.ui.view']._render_template("website_sale.total", {
            'website_sale_order': order,
        })
        return value


    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def shop_payment_validate(self, sale_order_id=None, **post):
        rec = super(WebsiteSalePreorder,self).shop_payment_validate(sale_order_id, **post)
        if sale_order_id is None:
            order = request.website.sale_get_order()
        else: 
            order = request.env['sale.order'].sudo().browse(sale_order_id)
        if order.preorder and order.payment_status == 'complete':
            order_currency = request.env['res.currency'].search([('name', '=', order.currency_id.name)])
            for line in order.order_line:
                if line.is_preorder:
                    if line.product_id.preorder_payment_type == 'partial':
                        product_currency = request.env['res.currency'].search([('name', '=', line.product_id.currency_id.name)])
                        price = product_currency._convert(line.product_id.list_price,order_currency,order.company_id, datetime.today().strftime('%Y-%m-%d'))
                        line.price_unit = price
                        order.payment_status = 'complete'
                        order.preorder_payment_type = 'full'
            order._compute_amounts()
        if 'preorder_id' in request.session:
            order = request.env['sale.order'].browse(int(request.session.get('preorder_id')))
            if order.preorder and order.payment_status == 'complete':
                order_currency = request.env['res.currency'].search([('name', '=', order.currency_id.name)])
                for line in order.order_line:
                    if line.is_preorder:
                        if line.product_id.preorder_payment_type == 'partial':
                            product_currency = request.env['res.currency'].search([('name', '=', line.product_id.currency_id.name)])
                            price = product_currency._convert(line.product_id.list_price,order_currency,order.company_id, datetime.today().strftime('%Y-%m-%d'))
                            line.price_unit = price
                            order.payment_status = 'complete'
                            order.preorder_payment_type = 'full'
                order._compute_amounts()
        elif order.preorder and order.payment_status == 'complete':
            order.preorder_payment_type = 'full'
        return rec

    @http.route(['/preorder/qty'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def preorder_qty_info(self,product_id):
        product = request.env["product.product"].sudo().browse(product_id)
        preorder = request.env["website.preorder"].search([('status','=',True)])
        if product and product.product_tmpl_id.get_preorder_label() == 'preorder':
            if product.is_default and  product.qty_available <= product.allowed_preorder_qty:
                return product.minimum_preorder_qty, product.maximum_preorder_qty
            else:
                return preorder.minimum_preorder_qty, preorder.maximum_preorder_qty
        return 0
        
    @http.route(['/product/qty/check'], type='json', auth="public", website=True, csrf=False)
    def product_qty_check(self, product_id):
        product = request.env['product.template'].browse(int(product_id))
        preorder = request.env["website.preorder"].search([('status','=',True)])
        qty = 1
        if product.on_hand_qty != product.qty_available:
            product.sudo().update({'on_hand_qty': product.qty_available})
        if product and product.get_preorder_label() == 'preorder':
            if product.is_default:
                qty = product.minimum_preorder_qty
            else:
                qty = preorder.minimum_preorder_qty
            return qty, product.get_preorder_label()
        else:
            return qty, product.get_preorder_label()
