# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    is_subscription = fields.Boolean("Is Subscription")
    subscription_type = fields.Selection([
        ('lily_subscription', 'Lily Subscription'),
        ('7md_subscription', '7md Subscription')
    ])
    subscription_option_lines = fields.One2many('subscription.option.line', 'product_id',
                                               'Subscription Options')
    validity_type = fields.Selection([('monthly', 'Monthly Subscription'), ('yearly', 'Yearly Subscription')])
    validity_count = fields.Integer('Validity Count')
    pricelist_id = fields.Many2one('product.pricelist', 'Price List')


class SubscriptionOptions(models.Model):
    _name = 'subscription.option.line'

    name = fields.Char('Name', translate=True)
    product_id = fields.Many2one('product.template', string="Product ID")
