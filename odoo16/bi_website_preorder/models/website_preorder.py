# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WebsitePreOrder(models.Model):
    _name = 'website.preorder'
    _description = 'Website Pre-order'


    def compute_email_template(self):
        template_id = self.env.ref('bi_website_preorder.preorder_notification_template').id
        template = self.env['mail.template'].browse(template_id)
        self.email_template = template

    name = fields.Text(required=True, default="Pre Order")
    status = fields.Boolean()
    preorder_payment_type = fields.Selection([
                                            ('partial', 'Percentage of price'),
                                            ('full', 'Fixed Amount(Full payment)'),
                                            ], string='Payment Type', default='full',required=True)
    percent = fields.Float(string='Amount')
    add_to_button_text = fields.Char(string='Add To Cart Button Label', required=True, default="Pre Order")
    available_date_on_preorder_product = fields.Boolean(string='Allow to show expiry date for Pre-order product')
    preorder_expiry = fields.Date(string="Expiry date")
    display_preorder_qty_range = fields.Boolean(string='Allow to show min and max quantity for Pre-order')
    allowed_preorder_qty = fields.Float(string='Allow preorder when product quantity Less then or Equal', required=True, default=1.0)
    minimum_preorder_qty = fields.Float(string='Minimum Quantity',required=True, default=1.0)
    maximum_preorder_qty = fields.Float(string='Maximum Quantity',required=True, default=1.0)
    custom_message = fields.Text(string="Custom Message")
    warning_message = fields.Text(string="Warning Message")
    conditional_message = fields.Text(string="conditional Message", default="You can not add other product in cart with preorder product.")
    preoreder_amount_visible = fields.Boolean(string='Pre-ordering Amount Visible on Website')
    send_mail = fields.Selection([
                                ('auto', 'Auto'),
                                ('manual', 'Manual'),
                                ], string='Send Email', default='auto',required=True)
    email_template = fields.Many2one("mail.template", string="Email Template",compute=compute_email_template ,readonly=True)


    @api.onchange('status')
    def _onchange_status(self):
        products = self.env['product.template'].search([('is_preorder','=',True)]);		
        for product in products:
            if not product.is_default and self.status:
                product.write({'preorder_payment_type' : self.preorder_payment_type,
                                'percent' : self.percent,
                                'preorder_expiry': self.preorder_expiry,
                                'allowed_preorder_qty' : self.allowed_preorder_qty,
                                'minimum_preorder_qty' : self.minimum_preorder_qty,
                                'maximum_preorder_qty' : self.maximum_preorder_qty,})



    def auto_mail_notification(self):
        template_id = self.env.ref('bi_website_preorder.preorder_notification_template').id
        template = self.env['mail.template'].browse(template_id)
        preorder = self.env['website.preorder'].search([('status','=',True)])
        sale_order = self.env['sale.order'].search([('preorder','=',True)])
        if preorder.send_mail == 'auto':
            for order in sale_order:
                if not order.is_sent:
                    for line in order.order_line:
                        if line.is_preorder and line.product_id.qty_available>line.product_id.allowed_preorder_qty:
                            order.is_sent = True
                            template.send_mail(line.id,force_send=True)

    @api.constrains ('minimum_preorder_qty')
    def _check_minimum_preorder_qty(self):
            if self.minimum_preorder_qty <= 0.0:
                raise ValidationError(_("You can not add minimum quantity less than 1.0 !!...."))

    @api.constrains ('maximum_preorder_qty')
    def _check_maximum_preorder_qty(self):
            if self.maximum_preorder_qty < self.minimum_preorder_qty:
                raise ValidationError(_("You can not add maximum quantity less than minimum quantity !!...."))
        
    @api.model
    def create(self,value):
        res = super(WebsitePreOrder, self).create(value)
        obj = self.env['website.preorder'].search([])
        checked = obj.filtered(lambda s: s.status == True)
        if 'status' in value:
            if len(checked) > 1 and value["status"]:
                raise ValidationError(_("Only one preorder configration can be active."))
    
        if value["status"]:
            products = self.env['product.template'].search([('is_preorder','=',True)])
            for product in products:
                product.preorder_payment_type = value['preorder_payment_type']
                product.percent = value['percent']
                product.allowed_preorder_qty = value['allowed_preorder_qty']
                product.minimum_preorder_qty = value['minimum_preorder_qty']
                product.maximum_preorder_qty = value['maximum_preorder_qty']
                product.preorder_expiry = value['preorder_expiry']
        return res

    def write(self, value):
        res = super(WebsitePreOrder, self).write(value)
        obj = self.env['website.preorder'].search([])
        checked = obj.filtered(lambda s: s.status == True)
        if 'status' in value:
            if len(checked) > 1 and value["status"]:
                raise ValidationError(_("Only one preorder configration can be active."))
        return res

    @api.onchange('preorder_payment_type')
    def onchange_preorder_payment_type(self):
        products = self.env['product.template'].search([('is_preorder','=',True)])
        for product in products:
            if not product.is_default and self.status:
                product.preorder_payment_type = self.preorder_payment_type


    @api.onchange('percent')
    def onchange_percent(self):
        products = self.env['product.template'].search([('is_preorder','=',True)])
        for product in products:
            if not product.is_default and self.status:
                product.percent = self.percent


    @api.onchange("allowed_preorder_qty")
    def onchange_allowed_preorder_qty(self):
        products = self.env['product.template'].search([('is_preorder','=',True)])
        for product in products:
            if not product.is_default and self.status:
                product.allowed_preorder_qty = self.allowed_preorder_qty


    @api.onchange("minimum_preorder_qty")
    def onchange_minimum_preorder_qty(self):
        products = self.env['product.template'].search([('is_preorder','=',True)])
        for product in products:
            if not product.is_default and self.status:
                product.minimum_preorder_qty = self.minimum_preorder_qty


    @api.onchange("maximum_preorder_qty")
    def onchange_maximum_preorder_qty(self):
        products = self.env['product.template'].search([('is_preorder','=',True)])
        for product in products:
            if not product.is_default and self.status:
                product.maximum_preorder_qty = self.maximum_preorder_qty

    @api.onchange("preorder_expiry")
    def onchange_preorder_expiry(self):
        products = self.env['product.template'].search([('is_preorder','=',True)])
        for product in products:
            if not product.is_default and self.status:
                product.preorder_expiry = self.preorder_expiry