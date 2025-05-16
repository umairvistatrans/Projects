# -*- coding: utf-8 -*-

from odoo import _, http, exceptions
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)


class POS(http.Controller):

    def _return_401_unauthorized(self):
        return {
            "errors": [{
                "message": "Unauthorized",
                "code": 401,
                "reason": "The necessary authentication credentials are not present in the request or are incorrect."
            }]
        }

    def _return_400_bad_request(self):
        return {
            "errors": [{
                "message": "Bad Request",
                "code": 400,
                "reason": "'transaction_date' or 'pos_name' parameter is not found!"
            }]
        }

    def _return_404_not_found(self):
        return {
            "errors": [{
                "message": "Not Found",
                "code": 404,
                "reason": "The requested resource was not found but could be available again in the future."
            }]
        }

    @http.route('/pos/transactions', type='json', auth='none', methods=['GET'])
    def get_pos_transactions(self, **post):
        post = request.get_json_data()
        transaction_date = post.get('transaction_date')
        pos_name = post.get('pos_name')
        if not transaction_date or not pos_name:
            return self._return_400_bad_request()

        headers = request.httprequest.headers
        authorization_token = headers.get("Authorization")
        if not authorization_token:
            return self._return_401_unauthorized()
        elif len(authorization_token.split(' ')) == 1:
            return self._return_401_unauthorized()

        bearer, token = authorization_token.split(' ')
        if bearer.lower() != 'bearer':
            return self._return_401_unauthorized()

        user = request.env['res.users'].sudo()._check_egoal_aldar_token(token)
        if not user:
            return self._return_401_unauthorized()

        allowed_point_of_sales = user.oe_config_ids.mapped('name')
        if pos_name in allowed_point_of_sales:
            pos_config = request.env['pos.config'].sudo().search([('name', '=', pos_name)], limit=1)
            if not pos_config:
                return self._return_404_not_found()

            domain = [
                ('config_id', '=', pos_config.id),
                ('date_order', '>=', transaction_date),
                ('date_order', '<=', transaction_date),
                ('state', 'in', ('paid', 'done', 'invoiced'))
            ]
            pos_orders = request.env['pos.order'].sudo().search(domain)
            return {
                "transaction_count": len(pos_orders),
                "net_sales": sum(pos_order.amount_total - pos_order.amount_tax for pos_order in pos_orders),
                "transaction_date": transaction_date
            }
        return self._return_404_not_found()
