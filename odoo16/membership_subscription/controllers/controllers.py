# -*- coding: utf-8 -*-
import base64

from odoo.http import request
from odoo import http


class membership7md(http.Controller):
    @http.route('/memberships', auth='public', type='http', website=True)
    def index(self, **kw):
        product_ids = request.env['product.template'].sudo().search([('is_subscription', '=', True)], limit=2)
        products = {'product_ids': product_ids}
        return request.render('membership_subscription.membership_subscription', products)
