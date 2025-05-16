import logging
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.http import request
from odoo.exceptions import AccessError

logger = logging.getLogger(__name__)

PRODUCT_LIMIT = 20


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    top_selling_limit = fields.Integer("Top Selling Limit", config_parameter='dynamic_url_data.top_selling_limit',
                                       default=20)
    new_arrival_limit = fields.Integer("New Arrival Limit", config_parameter='dynamic_url_data.new_arrival_limit',
                                       default=20)

    new_arrival_days = fields.Integer("New Arrival Days", config_parameter='dynamic_url_data.new_arrival_days',
                                      default=60)

    sale_discount_limit = fields.Integer("Sale (Discount) Products Limit",
                                         config_parameter='dynamic_url_data.sale_discount_limit',
                                         default=50)


class WebsiteSearchableMixin(models.AbstractModel):
    """Mixin to be inherited by all models that need to searchable through website"""
    _inherit = 'website.searchable.mixin'

    @api.model
    def _search_build_domain(self, domain_list, search, fields, extra=None):
        domain = super(WebsiteSearchableMixin, self)._search_build_domain(domain_list, search, fields, extra)

        user = self.env.user
        is_internal_user = user.has_group('base.group_user')
        param_env = self.env['ir.config_parameter'].sudo()

        if request.params.get('top_selling'):
            top_selling_limit = int(param_env.get_param('dynamic_url_data.top_selling_limit', 20))
            product_ids = request.env['sale.order.line'].with_user(request.uid).get_top_selling_products_templates(
                top_selling_limit)
            domain += [('id', 'in', product_ids.ids)]

        elif request.params.get('new_arrival'):
            '''Get the Products that is Created within Last 60 days'''

            new_arrival_limit = int(param_env.get_param('dynamic_url_data.new_arrival_limit', 20))
            new_arrival_days = int(param_env.get_param('dynamic_url_data.new_arrival_days', 60))

            now = datetime.now()
            start_date = (now - timedelta(days=new_arrival_days)).strftime('%Y-%m-%d %H:%M:%S')
            product_domain = [('create_date', '>=', start_date), ('detailed_type', '=', 'product'),
                              ('sale_ok', '=', True)]

            if not is_internal_user:
                product_domain += [('is_published', '=', True)]

            # Search for products created in the last 60 days
            product_ids = request.env['product.template'].with_user(request.uid).search(product_domain,
                                                                                        order='create_date desc')
            domain += [('id', 'in', product_ids.ids[:new_arrival_limit])]

        elif request.params.get('sale'):
            '''Filtration done based on selected price list'''

            discount_product_limit = int(param_env.get_param('dynamic_url_data.sale_discount_limit', 100))
            products = request.env['product.template'].sudo()
            pricelist = request.env['product.pricelist'].browse(request.session.get('website_sale_current_pl'))
            # if price applied on all products
            all_products = pricelist.item_ids.filtered(
                lambda line: line.compute_price == 'percentage' and line.applied_on == '3_global')
            if all_products:
                products += request.env['product.template'].search(domain)

            # if applied on template
            product_templates = pricelist.item_ids.filtered(
                lambda line: line.compute_price == 'percentage' and line.applied_on == '1_product').mapped(
                'product_tmpl_id')
            if product_templates:
                products += product_templates

            # if applied on product variant
            product_variants_template = pricelist.item_ids.filtered(
                lambda line: line.compute_price == 'percentage' and line.applied_on == '0_product_variant').mapped(
                'product_tmpl_id')
            if product_variants_template:
                products += product_variants_template

            # if applied on category
            categ_ids = pricelist.item_ids.filtered(
                lambda line: line.compute_price == 'percentage' and line.applied_on == '2_product_category').mapped(
                'categ_id')
            categ_products = request.env['product.template'].search(
                [('categ_id', 'in', categ_ids.ids), ('is_published', '=', True)])
            if categ_ids:
                products += categ_products

            if not is_internal_user:
                # filtered record based on is_published and sale ok
                products = products.filtered(lambda p: p.is_published is True and p.sale_ok is True)
            domain += [('id', 'in', products.ids[:discount_product_limit])]

        if not is_internal_user and self._name in ['product.template', 'product.product']:
            domain += [('is_published', '=', True)]

        return domain


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order.line'

    def get_top_selling_products_templates(self, limit=10):
        user = self.env.user
        is_internal_user = user.has_group('base.group_user')

        # Base query
        query = """
               SELECT 
                    pp.product_tmpl_id,
                    SUM(sol.product_uom_qty) AS total_quantity 
                FROM 
                    sale_order_line AS sol
                JOIN 
                    product_product AS pp
                ON 
                    sol.product_id = pp.id
                JOIN 
                    product_template AS pt
                ON 
                    pp.product_tmpl_id = pt.id
                WHERE 
                    sol.state IN ('sale', 'done') 
                    AND pt.detailed_type = 'product'
                    AND pt.sale_ok = True
               """

        # Add the is_published condition if the user is not an internal user
        if not is_internal_user:
            query += "AND pt.is_published = True "

        # Add grouping and ordering
        query += """
                GROUP BY 
                    pp.product_tmpl_id 
                ORDER BY 
                    total_quantity DESC 
                LIMIT 
                    %s;
               """

        self.env.cr.execute(query, (limit,))
        result = self.env.cr.fetchall()

        template_ids = [product[0] for product in result]
        return self.env['product.template'].browse(template_ids)
