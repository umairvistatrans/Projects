from odoo import fields, models, api


class Subscription(models.Model):
    _name = 'subscription.config'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('subscription.config'))
    customer_id = fields.Many2one('res.partner', string='Customer')
    product_id = fields.Many2one('product.product', string='subscription Type', domain=[('is_subscription', '=', True)])
    create_date = fields.Datetime(string='Create Date')
    subscription_start_date = fields.Datetime(string='Subscription start Date')
    subscription_end_date = fields.Datetime(string='Subscription end Date')
    price_list_id = fields.Many2one('product.pricelist', string='Price List')
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'), ('expire', 'Expired')],default='draft', string='State')

    def reset_to_draft(self):

        self.state = 'draft'

    def action_activate(self):
        self.state = 'active'


    def check_subscription_expiry(self):
        subscriptions = self.search([('state', '=', 'active')])
        for subscription in subscriptions:
            if subscription.subscription_end_date <= fields.Datetime.now():
                subscription.write({'state': 'expire'})
                subscription.customer_id.property_product_pricelist = subscription.price_list_id.id