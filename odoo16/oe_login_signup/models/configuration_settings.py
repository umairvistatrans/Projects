from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    new_offered_product_type = fields.Selection(
        [
            ('by_category', 'By Category'),
            ('by_product', 'By Product'),
        ], string="New Offered Product Selection Criteria")

    new_offered_product_ids = fields.Many2many(
        'product.product',
        string="New Offered Products", domain=[('website_published', '=', True)]
    )
    new_offered_category_ids = fields.Many2many(
        comodel_name='product.public.category',
        relation='res_config_settings_offered_category_rel',
        column1='config_id',
        column2='offered_category_id',
        string='New Offered Categories'
    )

    # ----------------------------------------------------------------
    best_selling_product_type = fields.Selection(
        [
            ('by_category', 'By Category'),
            ('by_product', 'By Product'),
        ], string="Best Selling Products Selection Criteria")

    best_selling_product_ids = fields.Many2many(
        comodel_name='product.product',
        relation='res_config_settings_best_selling_product_rel',
        column1='config_id',
        column2='product_id',
        string='Best Selling Products'
    )
    best_selling_category_ids = fields.Many2many(
        comodel_name='product.public.category',
        relation='res_config_settings_best_selling_category_rel',
        column1='config_id',
        column2='best_selling_category_id',
        string='Best Selling Categories'
    )
    # ----------------------------------------------------------------
    card_product_type = fields.Selection(
        [
            ('by_category', 'By Category'),
            ('by_product', 'By Product'),
        ], string="Products Card Products Selection Criteria")

    card_product_category_ids = fields.Many2many(
        comodel_name='product.public.category',
        relation='res_config_settings_card_product_category_rel',
        column1='config_id',
        column2='card_product_category_id',
        string='Product Card Categories'
    )

    card_product_ids = fields.Many2many(
        comodel_name='product.product',
        relation='res_config_settings_card_product_rel',
        column1='config_id',
        column2='card_product_id',
        string='Products Card'
    )

    # ----------------------------------------------------------------

    product_category_ids = fields.Many2many(
        'product.public.category',
        string="Categories"
    )
    top_pro_brand_ids = fields.Many2many(
        'product.brand',
        relation='res_config_settings_product_brand_rel',
        column1='config_id',
        column2='product_brand_id',
        string="Top Brands"
    )


    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param_env = self.env['ir.config_parameter'].sudo()
        param_env.set_param('oe_login_signup.new_offered_product_type', self.new_offered_product_type)
        param_env.set_param('oe_login_signup.new_offered_category_ids',
                            ','.join(map(str, self.new_offered_category_ids.ids)))
        param_env.set_param('oe_login_signup.new_offered_product_ids',
                            ','.join(map(str, self.new_offered_product_ids.ids)))
        # -------------------------------------------------------------------------------------------------------------
        param_env.set_param('oe_login_signup.product_category_ids', ','.join(map(str, self.product_category_ids.ids)))

        # -------------------------------------------------------------------------------------------------------------
        param_env.set_param('oe_login_signup.best_selling_product_type', self.best_selling_product_type)
        param_env.set_param('oe_login_signup.best_selling_category_ids',
                            ','.join(map(str, self.best_selling_category_ids.ids)))
        param_env.set_param('oe_login_signup.best_selling_product_ids',
                            ','.join(map(str, self.best_selling_product_ids.ids)))

        # -------------------------------------------------------------------------------------------------------------
        param_env.set_param('oe_login_signup.card_product_type', self.card_product_type)
        param_env.set_param('oe_login_signup.card_product_category_ids',
                            ','.join(map(str, self.card_product_category_ids.ids)))
        param_env.set_param('oe_login_signup.card_product_ids', ','.join(map(str, self.card_product_ids.ids)))

        # -------------------------------------------------------------------------------------------------------------
        param_env.set_param('oe_login_signup.top_pro_brand_ids', ','.join(map(str, self.top_pro_brand_ids.ids)))

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param_env = self.env['ir.config_parameter'].sudo()

        new_offered_category_ids = [int(i) for i in
                                    param_env.get_param('oe_login_signup.new_offered_category_ids', '').split(',') if
                                    i.isdigit()]
        res['new_offered_category_ids'] = [(6, 0, new_offered_category_ids)]
        res['new_offered_product_type'] = param_env.get_param('oe_login_signup.new_offered_product_type', '')
        m2m_ids = [int(i) for i in param_env.get_param('oe_login_signup.new_offered_product_ids', '').split(',') if
                   i.isdigit()]
        res['new_offered_product_ids'] = [(6, 0, m2m_ids)]

        # -------------------------------------------------------------------------------------------------------------


        category_ids = [int(i) for i in param_env.get_param('oe_login_signup.product_category_ids', '').split(',') if
                        i.isdigit()]
        res['product_category_ids'] = [(6, 0, category_ids)]

        # -------------------------------------------------------------------------------------------------------------

        best_selling_category_ids = [int(i) for i in
                                    param_env.get_param('oe_login_signup.best_selling_category_ids', '').split(',') if
                                    i.isdigit()]
        res['best_selling_category_ids'] = [(6, 0, best_selling_category_ids)]
        res['best_selling_product_type'] = param_env.get_param('oe_login_signup.best_selling_product_type', '')
        best_selling_ids = [int(i) for i in
                            param_env.get_param('oe_login_signup.best_selling_product_ids', '').split(',') if
                            i.isdigit()]
        res['best_selling_product_ids'] = [(6, 0, best_selling_ids)]

        # -------------------------------------------------------------------------------------------------------------

        card_product_category_ids = [int(i) for i in
                                     param_env.get_param('oe_login_signup.card_product_category_ids', '').split(',') if
                                     i.isdigit()]
        res['card_product_category_ids'] = [(6, 0, card_product_category_ids)]
        res['card_product_type'] = param_env.get_param('oe_login_signup.card_product_type', '')
        card_product_ids = [int(i) for i in param_env.get_param('oe_login_signup.card_product_ids', '').split(',') if
                            i.isdigit()]
        res['card_product_ids'] = [(6, 0, card_product_ids)]

        # -------------------------------------------------------------------------------------------------------------

        top_pro_brand_ids = [int(i) for i in param_env.get_param('oe_login_signup.top_pro_brand_ids', '').split(',') if
                             i.isdigit()]
        res['top_pro_brand_ids'] = [(6, 0, top_pro_brand_ids)]


        return res
