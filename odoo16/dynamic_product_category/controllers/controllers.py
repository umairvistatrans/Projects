# from odoo import http
# from odoo.http import request
# from odoo.addons.website_sale.controllers.main import WebsiteSale
#
#
# class WebsiteSaleInherit(WebsiteSale):
#
#     @http.route([
#         '''/shop''',
#         '''/shop/page/<int:page>''',
#         '''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>''',
#         '''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>/page/<int:page>'''
#     ], type='http', auth="public", website=True)
#     def shop(self, page=0, category=None, search='', ppg=False, **post):
#         res = super(WebsiteSaleInherit, self).shop(page=0, category=None, search='', ppg=False, **post)
#         with_user = request.env['ir.config_parameter'].sudo()
#         setting_categories = with_user.get_param('oe_login_signup.product_category_ids')
#         selected_categories_ids = [int(num) for num in setting_categories.split(',')]
#         res.qcontext['selected_category'] = selected_categories_ids
#         return res
