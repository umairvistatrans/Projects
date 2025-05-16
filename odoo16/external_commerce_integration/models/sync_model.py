# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
class Picking(models.Model):
    _inherit = 'stock.picking'
    external_id = fields.Integer(string='Reference')
    invoice_number = fields.Char()
    website_invoice_number = fields.Char()
    total_invoice_amount = fields.Char()

    def button_custom_action(self):
        for picking in self:
            # Check if the picking state is 'done'
            if picking.state == 'done':
                # Loop through move lines
                for move_line in picking.move_line_ids:
                    # Check if move line state is not equal to done
                    if move_line.state != 'done':
                        # Update the note field with a string
                        picking.state = "assigned"
                        picking.button_validate()

class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_method_desc = fields.Char(string="Payment Method", compute="_compute_sale_order_payment_method")

    def _compute_sale_order_payment_method(self):
        for rec in self:
            so_obj = False
            for line in rec.invoice_line_ids:
                if line.sale_line_ids:
                    so_obj = line.sale_line_ids.mapped('order_id')
                    rec.payment_method_desc = so_obj.payment_method_desc if so_obj.payment_method_desc else so_obj.pos_payment_method.name
                    break
            if not so_obj:
                rec.payment_method_desc = False


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    external_id = fields.Integer(string='External ID')
    extern_id = fields.Char(string='WooCommerce ID')
    payment_method_desc=fields.Char(string='Payment Method')
    customer_first_name = fields.Char()
    customer_last_name = fields.Char()
    billing_first_name = fields.Char()
    billing_last_name = fields.Char()
    billing_address_1 = fields.Char()
    billing_address_2 = fields.Char()
    billing_city = fields.Char()
    billing_state = fields.Char()
    billing_zip = fields.Char()
    billing_country = fields.Char()
    shipping_first_name = fields.Char()
    shipping_last_name = fields.Char()
    shipping_address_1 = fields.Char()
    shipping_address_2 = fields.Char()
    shipping_city = fields.Char()
    shipping_state = fields.Char()
    shipping_zip = fields.Char()
    shipping_country = fields.Char()
    customer_email = fields.Char()
    customer_phone = fields.Char()

class PartnerAddress(models.Model):
    _name = 'res.partner.cus.address'
    partner_id = fields.Many2one(comodel_name='res.partner')

    customer_first_name = fields.Char()
    customer_last_name = fields.Char()
    billing_first_name = fields.Char()
    billing_last_name = fields.Char()
    billing_address_1 = fields.Char()
    billing_address_2 = fields.Char()
    billing_city = fields.Char()
    billing_state = fields.Char()
    billing_zip = fields.Char()
    billing_country = fields.Char()
    shipping_first_name = fields.Char()
    shipping_last_name = fields.Char()
    shipping_address_1 = fields.Char()
    shipping_address_2 = fields.Char()
    shipping_city = fields.Char()
    shipping_state = fields.Char()
    shipping_zip = fields.Char()
    shipping_country = fields.Char()
    customer_email = fields.Char()
    customer_phone = fields.Char()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    special_price = fields.Float()
    special_price_type = fields.Char()
    special_price_start = fields.Char()
    special_price_end = fields.Char()
    external_id = fields.Char(string='External ID')
    free_per_location = fields.Float(compute='_get_free_qty', store=1)

    def action_refresh_qty(self):
        products = self.env['product.template'].search([])
        for product in products:
            product._get_free_qty()

    def _get_free_qty(self):
        for rec in self:

            location_id = False
            # companies = self.env['res.company'].search([('ex_location_id', '!=', False)])
            # for company in companies:
            _logger.info("11111111111111")
            if self.env.company.ex_location_id:
                location_id = self.env.company.ex_location_id
                _logger.info('product>>>>>>>{},{}'.format(location_id,self.env.company))
                # break
            # location_id = self.env['ir.config_parameter'].sudo().get_param(
            #     'external_commerce_integration.ex_location_id',
            #     self.env.ref('stock.stock_location_stock').id)
            qty = 0
            if location_id:
                qty += rec.product_variant_id.with_context(location=location_id.id).free_qty
                if location_id.sub_location_ids:
                    for sub in location_id.sub_location_ids:
                        qty += rec.product_variant_id.with_context(location=sub.id).free_qty

            rec.free_per_location = qty


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_qty_updated=fields.Boolean()
    free_per_location = fields.Float(compute='_get_free_qty', store=1)

    @api.depends('free_qty')
    def _get_free_qty(self):
        for rec in self:

            location_id = False
            # companies = self.env['res.company'].sudo().search([('ex_location_id', '!=', False)])
            # for company in companies:
            if self.env.company.ex_location_id:
                location_id = self.env.company.ex_location_id
                _logger.info('product product>>>>>>>{},{}'.format(location_id,self.env.company))

                    # break

            # location_id = self.env['ir.config_parameter'].sudo().get_param(
            #     'external_commerce_integration.ex_location_id',
            #     self.env.ref('stock.stock_location_stock').id)
            qty = 0
            if location_id:
                qty += rec.with_context(location=location_id.id).free_qty
                if location_id.sub_location_ids:
                    for sub in location_id.sub_location_ids:
                        qty += rec.with_context(location=sub.id).free_qty

            rec.free_per_location = qty

    @api.model
    def create(self, vals):
        vals['product_qty_updated']=True
        res = super(ProductProduct, self).create(vals)
        return res

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def create(self,vals):
        res=super(StockQuant,self).create(vals)
        if vals.get('quantity') !=0:
            res.product_id.product_qty_updated=True
        return res

    def write(self,vals):
        res=super(StockQuant,self).write(vals)
        if vals.get('quantity'):
            for item in self:
                item.product_id.product_qty_updated=True
        return res


class Brand(models.Model):
    _inherit = 'product.brand'
    brand_external_id = fields.Integer(string='Brand External ID')
    brand_slug = fields.Char(string='Brand External Slug')

    @api.model
    def create(self, vals):
        res = super(Brand, self).create(vals)
        if not res.brand_slug:
            res.brand_slug = '-'.join([x for x in res.name.split(' ')])
        return res


class Category(models.Model):
    _inherit = 'product.category'

    categ_external_id = fields.Integer(string=' External ID')
    categ_slug = fields.Char(string='Category External Slug')
    categ_image_url = fields.Char()

    @api.model
    def create(self, vals):
        res = super(Category, self).create(vals)
        if not res.categ_slug:
            res.categ_slug = '-'.join([x for x in res.name.split(' ')])
        return res


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ref_customer_id = fields.Char()
    customer_address_ids = fields.One2many(comodel_name='res.partner.cus.address', inverse_name='partner_id')


# ResPartner()