from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home
from odoo.addons.website_sale.controllers.main import WebsiteSale, TableCompute
from odoo.tools import lazy
from datetime import datetime
import importlib
import json

contact7md = importlib.import_module("odoo.addons.7md_website.controllers.controllers").contact7md
brand7md = importlib.import_module("odoo.addons.7md_website.controllers.controllers").brand7md


class AuthRemember(Home):  # Inherit from Home instead of http.Controller

    @http.route()  # Use the same route as the original web_login
    def web_login(self, redirect=None, **kw):
        response = super(AuthRemember, self).web_login(redirect, **kw)  # Now super() correctly refers to Home
        if request.params.get('login_success'):
            if 'remember_me' in request.params:  # Make sure this matches your checkbox's name attribute
                # Generate and store token logic goes here
                # Remember to set the cookie in the response
                user = request.env['res.users'].sudo().search([('login', '=', request.params['login'])])
                if user:
                    token = "GENERATED_SECURE_TOKEN"  # Replace with actual token generation logic
                    response.set_cookie('remember_token', token, max_age=30 * 24 * 60 * 60)  # Example: 30 days expiry
        return response


class ExtendedContact7md(contact7md):
    @http.route([
        '/contact',
        '/contact/<string:store_name>',
    ], auth='public', type='http', website=True)
    def index(self, store_name=None, **kw):
        values = {
            'stores': request.env['oe.store.location'].sudo().search([]),
            'store_url': store_name if store_name else False

        }
        return request.render('7md_website.contact', values)


class ContactFormController(http.Controller):
    @http.route([
        '/contact/submit',
    ], type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def contact_submit(self, store_name=None, **post):
        # You can do some data validation here if necessary
        name = post.get('first_name') + " " + post.get('last_name')

        # Create lead in CRM
        request.env['crm.lead'].sudo().create({
            'name': name + "(Website Form)",
            'contact_name': name,
            'email_from': post.get('email'),
            'phone': post.get('phone_number'),
            'description': post.get('message_text'),
            'web_store_id': request.env['oe.store.location'].sudo().search(
                [('url_name', '=', post.get('store_url_name'))]).id if post.get('store_url_name') else False,
        })

        # Redirect to a 'Thank You' page or back to the contact page with a success message
        return request.render('oe_login_signup.template_success_message', {})


class CustomWebsiteSale(WebsiteSale):
    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
        '/shop/brand/',
        '/shop/brand/<model("product.brand"):brand>',
        '/shop/brand/<model("product.brand"):brand>/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap=True)
    def shop(self, page=0, category=None, brand=None, search='', ppg=False, **post):
        response = super(CustomWebsiteSale, self).shop(page, category, search, ppg, **post)
        website = request.env['website'].get_current_website()

        # Latest Products Start
        shop_products_three = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.shop_products_three', default='').split(',') if i.isdigit()]
        s_product_three = request.env['product.product'].sudo().search(
            [('id', 'in', shop_products_three)]) if shop_products_three else False

        if not request.env.user.has_group('base.group_user'):
            s_product_three = [product for product in s_product_three if product.is_published]

        response.qcontext["s_product_three"] = s_product_three

        # Latest Products End
        print(shop_products_three)

        if brand:
            now = datetime.timestamp(datetime.now())
            pricelist = request.env['product.pricelist'].browse(request.session.get('website_sale_current_pl'))
            if not pricelist or request.session.get('website_sale_pricelist_time',
                                                    0) < now - 60 * 60:  # test: 1 hour in session
                pricelist = website.get_current_pricelist()
                request.session['website_sale_pricelist_time'] = now
                request.session['website_sale_current_pl'] = pricelist.id
            ppg = 20
            pager = website.pager(url='/shop/brand/' + str(brand.id), total=len(
                request.env['product.template'].sudo().search([('product_brand_rec_id', '=', brand.id)])), page=page,
                                  step=ppg, scope=5, url_args=post)
            offset = pager['offset']
            domain = [('product_brand_rec_id', '=', brand.id)]
            user = request.env.user
            is_internal_user = user.has_group('base.group_user')
            if not is_internal_user:
                domain += [('is_published', '=', True)]
            products = request.env['product.template'].sudo().search(domain)[
                       offset:offset + ppg]
            products_prices = lazy(lambda: products._get_sales_prices(pricelist))
            response.qcontext['products'] = products
            response.qcontext['search_product'] = products
            response.qcontext['search_count'] = len(products)
            response.qcontext['bins'] = lazy(lambda: TableCompute().process(products, ppg, 4))
            response.qcontext['ppg'] = ppg
            response.qcontext['ppr'] = 4
            response.qcontext['pager'] = pager
            response.qcontext['products_prices'] = products_prices,
            response.qcontext['get_product_prices'] = lambda product: lazy(lambda: products_prices[product.id])

        return response
        # return request.render(response,values)




class brand7md(brand7md):
    @http.route('/brands', auth='public', type='http', website=True)
    def index(self, **kw):
        values = {
            'brand_ids': request.env['product.brand'].sudo().search([]),
        }
        return request.render('7md_website.brand', values)


class BrandSearchController(http.Controller):
    @http.route('/brand_search', type='json', auth="public", methods=['POST'], csrf=False)
    def brand_search(self, **kw):
        params = json.loads(request.httprequest.data.decode('utf-8'))
        search_term = params.get('params', {}).get('search_brand', '')

        # If search_term is empty, return all brands, else search by name
        domain = [('name', 'ilike', search_term)] if search_term else []

        brands = request.env['product.brand'].sudo().search(domain)
        results = [{'id': brand.id, 'name': brand.name, 'logo': brand.logo} for brand in brands]

        return results

