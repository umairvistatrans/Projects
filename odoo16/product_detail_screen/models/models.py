# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    ecommerce_description = fields.Html("Ecommerce Description")
    customer_review_lines = fields.One2many("product.custom.review",
                                            'product_id', string="Custom Reviews")
    terms_and_conditions = fields.Html("Terms And Condition")
    instagram_link = fields.Char(string='Video Link')
    average_rating = fields.Integer("Average Rating", compute="_get_average_rating", store=True)
    star_rating_html = fields.Html(compute='_get_star_rating_html')

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False,
                              parent_combination=False, only_template=False):
        result = super()._get_combination_info(combination, product_id, add_qty, pricelist, parent_combination,
                                               only_template)
        show_line_subtotals_tax_selection = self.env['ir.config_parameter'].sudo().get_param(
            'account.show_line_subtotals_tax_selection')
        product_temp = self.env['product.product'].search([('id', '=', result['product_id'])])
        if pricelist and show_line_subtotals_tax_selection != 'tax_included':
            self = self.sudo()
            rec = self.sudo().taxes_id.compute_all(result.get('price', 0), product=self,
                                                   partner=self.env['res.partner'])
            tax_amount = rec['taxes'][0].get('amount', 0) if rec['taxes'] else 0
            tax_converted = pricelist.currency_id._convert(tax_amount, pricelist.currency_id,
                                                           pricelist.website_id.company_id,
                                                           fields.Date.today())

            result['amount_with_vat'] = round((result['price'] + tax_converted) * (add_qty if add_qty <= product_temp.available_qty_wh else 1), 2)
        else:
            result['amount_with_vat'] = round((result['price'] * (add_qty if add_qty <= product_temp.available_qty_wh else 1)), 2)
        product_product_id = self.env['product.product'].search([('id', '=', result['product_id'])])
        result['product_sku'] = product_product_id.default_code if product_product_id else self.env[
            'product.template'].search([('id', '=', result['product_template_id'])]).default_code
        return result

    @api.depends('customer_review_lines')
    def _get_average_rating(self):
        for rec in self:
            ratings = rec.customer_review_lines.mapped('rating')
            valid_ratings = [rating for rating in ratings if 1 <= rating <= 5]
            if valid_ratings:
                total_rating = sum(valid_ratings)
                num_ratings = len(valid_ratings)
                average_rating = total_rating / num_ratings
                rec.average_rating = min(average_rating, 5)
            else:
                rec.average_rating = 1

    @api.depends('average_rating')
    def _get_star_rating_html(self):
        for rec in self:
            full_stars = int(rec.average_rating)
            half_star = (rec.average_rating - full_stars) >= 0.5
            empty_stars = 5 - full_stars - (1 if half_star else 0)

            star_html = '<span class="star-rating">'

            # Add full stars
            star_html += '<i class="fa fa-star rating-color"></i>' * full_stars

            # Add half star if needed
            if half_star:
                star_html += '<i class="fa fa-star-half-alt rating-color"></i>'

            # Add empty stars
            star_html += '<i class="fa fa-star"></i>' * empty_stars

            star_html += '</span>'

            rec.star_rating_html = star_html


class EcommerceCustomerReview(models.Model):
    _name = 'product.custom.review'

    name = fields.Char("Customer Name")
    email = fields.Char("Custom Email")
    title = fields.Char("Title")
    comments = fields.Text("Comments")
    rating = fields.Integer("Rating")
    product_id = fields.Many2one('product.template', 'Product')
    user_id = fields.Many2one("res.users", "User ID")
    image = fields.Binary("Image", related='product_id.image_1920', store=True)
