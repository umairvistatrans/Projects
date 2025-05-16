# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    preorder_payment_type = fields.Selection([('partial', 'Partial'),
                                              ('full', 'Complete'),
                                              ], string='Pre-order Payment Status')
    payment_status = fields.Selection([ ('half', 'Half'),
                                        ('remain', 'Remain'),
                                        ('complete', 'Complete'),
                                        ], string='Payment Status')
    is_sent = fields.Boolean()
    preorder = fields.Boolean()
    remaining_amount = fields.Monetary()
    order_url = fields.Char(string="Order url", compute="_compute_order_url")
    
    def _compute_order_url(self):
        for rec in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            static_url = "/my/orders/"
            id = "%s" % (rec.id)
            order_url_id = str(base_url) + static_url + id 
            rec.update({
                'order_url' : order_url_id
            })
            
    def compute_remaining_amount(self, order):
        amount = 0.0
        order_currency = self.env['res.currency'].search([('name', '=', order.currency_id.name)])
        for line in order.order_line:
            if line.is_preorder:
                product_currency = order.env['res.currency'].search([('name', '=', line.product_id.currency_id.name)])
                price = product_currency.compute(line.product_id.list_price,order_currency)
                amount += (price*line.product_uom_qty) - line.price_subtotal
        order.remaining_amount = amount

    def button_send_notification_mail(self):
        template_id = self.env.ref('bi_website_preorder.preorder_notification_template').id
        template = self.env['mail.template'].browse(template_id)
        preorder = self.env['website.preorder'].search([('status','=',True)])
        for line in self.order_line:
            if len(line) == 1 and line.product_id.is_preorder and line.product_id.qty_available <= preorder.allowed_preorder_qty and line.product_id.detailed_type == 'product':
                raise ValidationError(_('Product is not available in stock !!..'))
            if len(line) == 1 and line.product_id.is_preorder and line.product_id.qty_available > preorder.allowed_preorder_qty:
                self.is_sent = True
                template.send_mail(line.id,force_send=True)

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    is_preorder = fields.Boolean(string="Pre-order")