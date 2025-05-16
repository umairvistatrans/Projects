# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import http


class CustomerProductReview(http.Controller):
    @http.route('/customer_review', type='http', auth='public', website=True)
    def customer_product_review(self, **kw):
        if kw.get('product_id'):
            product_id = request.env['product.template'].sudo().search([('id', '=', int(kw.get('product_id')))])
            user_id = request.env['res.users'].sudo().browse(request.uid)
            product_id.customer_review_lines = [(0, 0, {
                'name': user_id.name,
                'email': user_id.email,
                'comments': kw.get('comment'),
                'rating': int(kw.get('rating')),
                'title': kw.get('reviewer_name')
            })]
        return request.redirect(request.httprequest.referrer)


class ReviewController(http.Controller):

    @http.route('/my/reviews', type='http', auth="user", website=True)
    def portal_my_reviews(self, **kw):
        # Retrieve all reviews

        all_reviews = request.env['product.custom.review'].search([])
        # Counts
        values = {
            'reviews': all_reviews,
        }

        return request.render("product_detail_screen.reviews", values)

    @http.route('/my', type='http', auth="user", website=True)
    def my_page(self, **kw):
        # Fetch total number of comments
        total_comments = request.env['product.custom.review'].sudo().search_count([])

        # Pass the total_comments count to the template
        values = {
            'total_comments': total_comments,
        }

        # Render the template with the updated values
        return request.render("product_detail_screen.portal_my_home_comments", values)
