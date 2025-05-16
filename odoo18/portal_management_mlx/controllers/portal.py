# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class CustomerPortal(payment_portal.PaymentPortal):

    def _get_request_detail(self, request_id):
        # Fetch the visit record from the database
        sub_request = request.env['submission.request'].sudo().browse(request_id)
        if not sub_request.exists():
            return request.not_found()
        data_value = {
            'access_token': request.env['submission.request'].sudo().with_user(request.env.user),
            'sub_request_id': sub_request,
            'page_name':sub_request.submission_type
        }
        if sub_request.submission_type == 'factory':
            return request.render('portal_management_mlx.factory_portal_template', data_value)
        elif sub_request.submission_type == 'product':
            return request.render('portal_management_mlx.product_portal_template', data_value)
        elif sub_request.submission_type == 'category':
            return request.render('portal_management_mlx.category_portal_template', data_value)

    def _prepare_request_domain(self, partner, request_type):
        return [
            ('partner_id', '=', partner.id),
            ('submission_type', '=', request_type),
        ]

    def _get_submission_request_searchbar_sortings(self):
        return {
            'create_date': {'label': _('Submission Date'), 'order': 'create_date desc'},
            'name': {'label': _('Reference No.'), 'order': 'name'},
            'state': {'label': _('State'), 'order': 'state'},
        }

    def _prepare_submission_request_portal_rendering_values(
            self, page=1, date_begin=None, date_end=None, sortby=None, request_type=None, **kwargs
    ):
        SubmissionRequest = request.env['submission.request']

        if not sortby:
            sortby = 'create_date'

        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()
        if request_type == 'factory':
            url = "/my/factories"
            domain = self._prepare_request_domain(partner, request_type)
        elif request_type == 'product':
            url = "/my/products"
            domain = self._prepare_request_domain(partner, request_type)
        elif request_type == 'category':
            url = "/my/categories"
            domain = self._prepare_request_domain(partner, request_type)

        searchbar_sortings = self._get_submission_request_searchbar_sortings()

        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        pager_values = portal_pager(
            url=url,
            total=SubmissionRequest.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
        )
        submission_requests = SubmissionRequest.search(domain, order=sort_order, limit=self._items_per_page,
                                                       offset=pager_values['offset'])

        values.update({
            'date': date_begin,
            'requests': submission_requests.sudo(),
            'page_name': request_type,
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return values

    @http.route(['/my/factories'], type='http', auth="user", website=True)
    def portal_my_factories(self, **kwargs):
        values = self._prepare_submission_request_portal_rendering_values(request_type='factory', **kwargs)
        return request.render("portal_management_mlx.portal_my_factories", values)

    @http.route('/my/factories/<int:factory_id>', type='http', auth='user', website=True)
    def factory_detail(self, factory_id, **kwargs):
        return self._get_request_detail(factory_id)

    @http.route(['/my/products'], type='http', auth="user", website=True)
    def portal_my_products(self, **kwargs):
        values = self._prepare_submission_request_portal_rendering_values(request_type='product', **kwargs)
        return request.render("portal_management_mlx.portal_my_products", values)

    @http.route('/my/products/<int:product_id>', type='http', auth='user', website=True)
    def product_detail(self, product_id, **kwargs):
        return self._get_request_detail(product_id)

    @http.route(['/my/categories'], type='http', auth="user", website=True)
    def portal_my_categories(self, **kwargs):
        values = self._prepare_submission_request_portal_rendering_values(request_type='category', **kwargs)
        return request.render("portal_management_mlx.portal_my_categories", values)

    @http.route('/my/categories/<int:category_id>', type='http', auth='user', website=True)
    def fcategory_detail(self, category_id, **kwargs):
        return self._get_request_detail(category_id)
