# -*- coding: utf-8 -*-
import base64
import json
from odoo.http import request, route
from odoo import http
from odoo.tools import lazy
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from functools import partial
from odoo.addons.website_sale_wishlist.controllers.main import WebsiteSaleWishlist
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class MdWebsite(http.Controller):

    # def get_product_prices(self, products):
    #     prices = {}
    #     pricelist = request.website.get_current_pricelist()
    #     for product in products:
    #         prices[product.id] = product.with_context(pricelist=pricelist.id).price_get()[pricelist.id]
    #     return prices

    @http.route('/', auth='public', type='http', website=True)
    def index(self, **kw):
        category = kw.get('category')
        search = kw.get('search')
        source = kw.get('source', '')
        navbar_categories = request.env['navbar.category.config'].sudo().search([])
        pricelist = request.website.get_current_pricelist()

        offer_product_ids = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.new_offered_product_ids', default='').split(',') if i.isdigit()]
        new_offered_category_ids = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.new_offered_category_ids', default='').split(',') if i.isdigit()]
        new_offered_product_type = request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.new_offered_product_type', default='')
        # -------------------------------------------------------------------------------------------------------------

        best_selling_product_ids = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.best_selling_product_ids', default='').split(',') if i.isdigit()]
        best_selling_category_ids = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.best_selling_category_ids', default='').split(',') if i.isdigit()]
        best_selling_product_type = request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.best_selling_product_type', default='')

        # -------------------------------------------------------------------------------------------------------------

        product_category_ids = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.product_category_ids', default='').split(',') if i.isdigit()]
        # -------------------------------------------------------------------------------------------------------------
        card_product_ids = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.card_product_ids', default='').split(',') if i.isdigit()]
        card_product_category_ids = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.card_product_category_ids', default='').split(',') if i.isdigit()]
        card_product_type = request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.card_product_type', default='')
        # -------------------------------------------------------------------------------------------------------------
        top_brand_ids = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.top_pro_brand_ids', default='').split(',') if i.isdigit()]
        top_categories_ids = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.top_categories_ids', default='').split(',') if i.isdigit()]

        # -------------------------------------------------------------------------------------------------------------
        sidecards_products = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.sidecards_products', default='').split(',') if i.isdigit()]
        sidecards_product_category_ids = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.sidecards_product_category_ids', default='').split(',') if i.isdigit()]
        sidecards_product_type = request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.sidecards_product_type', default='')
        # -------------------------------------------------------------------------------------------------------------
        sidecards_products_r = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.sidecards_products_r', default='').split(',') if i.isdigit()]
        sidecards_product_r_category_ids = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.sidecards_product_r_category_ids', default='').split(',') if i.isdigit()]
        sidecards_product_r_type = request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.sidecards_product_r_type', default='')
        # -------------------------------------------------------------------------------------------------------------
        second_sidecards_products = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.second_sidecards_products', default='').split(',') if i.isdigit()]
        second_sidecards_product_category_ids = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.second_sidecards_product_category_ids', default='').split(',') if i.isdigit()]
        second_sidecards_product_type = request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.second_sidecards_product_type', default='')
        # -------------------------------------------------------------------------------------------------------------
        second_sidecards_products_r = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.second_sidecards_products_r', default='').split(',') if i.isdigit()]
        second_sidecards_product_r_category_ids = [int(i) for i in request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.second_sidecards_product_r_category_ids', default='').split(',') if i.isdigit()]
        second_sidecards_product_r_type = request.env['ir.config_parameter'].sudo().get_param(
            'oe_login_signup.second_sidecards_product_r_type', default='')
        # -------------------------------------------------------------------------------------------------------------

        values = {}
        product_template_custom = request.env['product.template'].sudo().search([])
        new_offered_products = request.env['product.product'].sudo().search(
            [('id', 'in', offer_product_ids)]) if offer_product_ids else False
        if new_offered_category_ids and new_offered_product_type == 'by_category':
            new_offered_products = request.env['product.product'].search([('product_tmpl_id', 'in',
                                                                           request.env[
                                                                               'product.template'].search([(
                                                                               'public_categ_ids',
                                                                               'in',
                                                                               new_offered_category_ids)]).ids)])

        # -------------------------------------------------------------------------------------------------------------

        best_selling_product = request.env['product.product'].sudo().search(
            [('id', 'in', best_selling_product_ids)]) if best_selling_product_ids else False
        if best_selling_category_ids and best_selling_product_type == 'by_category':
            best_selling_product = request.env['product.product'].search([('product_tmpl_id', 'in',
                                                                           request.env[
                                                                               'product.template'].search([(
                                                                               'public_categ_ids',
                                                                               'in',
                                                                               best_selling_category_ids)]).ids)])
        # --------------------------------------------------------------------------------------------------------------

        card_product_ids = request.env['product.product'].sudo().search(
            [('id', 'in', card_product_ids)]) if card_product_ids else False
        if card_product_category_ids and card_product_type == 'by_category':
            card_product_ids = request.env['product.product'].search([('product_tmpl_id', 'in',
                                                                       request.env[
                                                                           'product.template'].search([(
                                                                           'public_categ_ids',
                                                                           'in',
                                                                           card_product_category_ids)]).ids)])
        # --------------------------------------------------------------------------------------------------------------
        values["product_category"] = request.env['product.public.category'].sudo().search(
            [('id', 'in', product_category_ids)]) if product_category_ids else False
        values["top_brand_ids"] = request.env['product.brand'].sudo().search(
            [('id', 'in', top_brand_ids)]) if top_brand_ids else False
        values["top_categories"] = request.env['product.public.category'].sudo().search(
            [('id', 'in', top_categories_ids)]) if top_categories_ids else False
        # --------------------------------------------------------------------------------------------------------------
        sidecard_product = request.env['product.product'].sudo().search(
            [('id', 'in', sidecards_products)]) if sidecards_products else False
        if sidecards_product_category_ids and sidecards_product_type == 'by_category':
            sidecard_product = request.env['product.product'].search([('product_tmpl_id', 'in',
                                                                       request.env[
                                                                           'product.template'].search([(
                                                                           'public_categ_ids',
                                                                           'in',
                                                                           sidecards_product_category_ids)]).ids)])
        # --------------------------------------------------------------------------------------------------------------
        sidecard_product_r = request.env['product.product'].sudo().search(
            [('id', 'in', sidecards_products_r)]) if sidecards_products_r else False
        if sidecards_product_r_category_ids and sidecards_product_r_type == 'by_category':
            sidecard_product_r = request.env['product.product'].search([('product_tmpl_id', 'in',
                                                                         request.env[
                                                                             'product.template'].search([(
                                                                             'public_categ_ids',
                                                                             'in',
                                                                             sidecards_product_r_category_ids)]).ids)])
        # --------------------------------------------------------------------------------------------------------------
        s_sidecard_product = request.env['product.product'].sudo().search(
            [('id', 'in', second_sidecards_products)]) if second_sidecards_products else False
        if second_sidecards_product_category_ids and second_sidecards_product_type == 'by_category':
            s_sidecard_product = request.env['product.product'].search([('product_tmpl_id', 'in',
                                                                         request.env[
                                                                             'product.template'].search([(
                                                                             'public_categ_ids',
                                                                             'in',
                                                                             second_sidecards_product_category_ids)]).ids)])

        # --------------------------------------------------------------------------------------------------------------
        s_sidecard_product_r = request.env['product.product'].sudo().search(
            [('id', 'in', second_sidecards_products_r)]) if second_sidecards_products_r else False
        if second_sidecards_product_r_category_ids and second_sidecards_product_r_type == 'by_category':
            s_sidecard_product_r = request.env['product.product'].search([('product_tmpl_id', 'in',
                                                                           request.env[
                                                                               'product.template'].search([(
                                                                               'public_categ_ids',
                                                                               'in',
                                                                               second_sidecards_product_r_category_ids)]).ids)])
        # --------------------------------------------------------------------------------------------------------------

        if navbar_categories:
            values['navbar_categories'] = navbar_categories
        if source:
            category = request.env['navbar.category.config'].sudo().search([('name', '=', source)], limit=1)
            if category:
                values["todays_deals_products"] = category.product_ids

        # all_products = request.env['product.template'].sudo().search([])
        # all_products_peice_list = lazy(lambda: all_products._get_sales_prices(pricelist))

        product_ids = []
        product_ids.extend(new_offered_products.ids)
        product_ids.extend(best_selling_product.ids)
        product_ids.extend(card_product_ids.ids)
        product_ids.extend(sidecard_product.ids)
        product_ids.extend(sidecard_product_r.ids)
        product_ids.extend(s_sidecard_product.ids)
        product_ids.extend(s_sidecard_product_r.ids)
        product_ids.extend(request.env['product.product'].search([], limit=12).ids)

        for cat in request.env['navbar.category.config'].sudo().search([]):
            if cat.product_type == 'by_category':
                product_ids.extend(request.env['product.product'].sudo().search(
                    [('product_tmpl_id', 'in', request.env['product.template'].sudo().search(
                        [('public_categ_ids', 'in', cat.product_category_ids.ids)]).ids)]).ids)
            elif cat.product_type == 'by_product':
                product_ids.extend(cat.product_ids.ids)
            wishlist_items = request.env['product.wishlist'].sudo().search([])
            product_ids.extend(wishlist_items.mapped('product_id').ids)
        product_variants = request.env['product.product'].sudo().search([('id', 'in', product_ids)])
        template_ids = product_variants.mapped('product_tmpl_id.id')

        all_products = request.env['product.template'].sudo().search([('id', 'in', template_ids)])
        all_products_peice_list = all_products._get_sales_prices(pricelist)

        # raise ValidationError(_('You: %s') % all_products)

        # Define a simple function to get product prices
        # def get_product_prices(product):
        #     return all_products_peice_list.get(product)

        if not request.env.user.has_group('base.group_user'):
            new_offered_products = [product for product in new_offered_products if product.is_published]
            best_selling_product = [product for product in best_selling_product if product.is_published]
            card_product_ids = [product for product in card_product_ids if product.is_published]
            sidecard_product = [product for product in sidecard_product if product.is_published]
            sidecard_product_r = [product for product in sidecard_product_r if product.is_published]
            s_sidecard_product = [product for product in s_sidecard_product if product.is_published]
            s_sidecard_product_r = [product for product in s_sidecard_product_r if product.is_published]

        values.update({
            "all_products_peice_list": all_products_peice_list,
            'get_product_prices': all_products_peice_list,
            "new_offered_products": new_offered_products,
            "best_selling_product": best_selling_product,
            "card_product_ids": card_product_ids,
            "sidecard_product": sidecard_product,
            "sidecard_product_r": sidecard_product_r,
            "s_sidecard_product": s_sidecard_product,
            "s_sidecard_product_r": s_sidecard_product_r,
        })

        if category and not search:
            return request.render('7md_website.home', all_products_peice_list)
        if category and search:
            return request.redirect('/shop?category=%s&search=%s' % (category, search))
        if search and not category:
            return request.redirect('/shop?search=%s' % search)
        return request.render('7md_website.home', values)


class contact7md(http.Controller):
    @http.route('/contact', auth='public', type='http', website=True)
    def index(self, **kw):
        return request.render('7md_website.contact')


class websitePolicies(http.Controller):

    @http.route('/about', auth='public', type='http', website=True)
    def about7md(self, **kw):
        return request.render('7md_website.about')

    @http.route('/privacy-policy', auth='public', type='http', website=True)
    def privacyPolicy7md(self, **kw):
        return request.render('7md_website.privacy_policy_7md')

    @http.route('/return-policy', auth='public', type='http', website=True)
    def returnPolicy(self, **kw):
        return request.render('7md_website.return_policy_7md')

    @http.route('/terms-and-conditions', auth='public', type='http', website=True)
    def termAndCondition(self, **kw):
        return request.render('7md_website.terms_and_condition_7md')


class brand7md(http.Controller):
    @http.route('/brands', auth='public', type='http', website=True)
    def index(self, **kw):
        return request.render('7md_website.brand')

# class membership7md(http.Controller):
#     @http.route('/memberships', auth='public', type='http', website=True)
#     def index(self, **kw):
#         return request.render('7md_website.membership_subscription')


class WishlistController(WebsiteSaleWishlist):
    

    @route(['/shop/wishlist'], type='http', auth="public", website=True, sitemap=False)
    def get_wishlist(self, count=False, **kw):
        values = request.env['product.wishlist'].with_context(display_default_code=False).current()
        if count:
            return request.make_response(json.dumps(values.mapped('product_id').ids))

        # if not len(values):
        #     return request.redirect("/shop")
        # val ={
        #     "wishlis":values,
        # }
        return request.render("website_sale_wishlist.product_wishlist", dict(wishes=values))

class CustomerPortal(CustomerPortal):

    @http.route('/my/subscription', type='http', auth="user", website=True)
    def user_subscription(self, **kw):
        current_customer = request.env.user.partner_id.id
        subscription_ids = request.env['subscription.config'].sudo().search([('state', '=', 'active'),('customer_id','=',current_customer)])
        return request.render('7md_website.template_user_subscription', {
            'subscriptions': subscription_ids
        })
        
class socialLinks(http.Controller):
    @http.route('/social-links', auth='public', type='http', website=True)
    def index(self, **kw):
        return request.render('7md_website.social_links')