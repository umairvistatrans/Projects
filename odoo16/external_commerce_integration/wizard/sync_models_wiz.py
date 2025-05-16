# -*- coding: utf-8 -*-
from __future__ import division
import base64
import logging
import requests
from datetime import datetime, timedelta

from odoo import models, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class SyncModels(models.TransientModel):
    _name = 'res.website.sync'

    def get_config_params(self):
        companies = self.env['res.company'].sudo().search([('is_ex_active', '=', True)])
        for company in companies:
            if company.ex_website_url:
                return company
            
    @api.model
    def website_auth_token(self):
        url = self.get_config_params().ex_website_url
        email = self.get_config_params().ex_user_name
        password = self.get_config_params().ex_password
        login_url = '{0}{1}'.format(url, '/api/v1/login')
        payload = {'email': email,
                   'password': password}
        response = requests.request("POST", login_url, data=payload,verify=False)
        if response.status_code == 200:
            auth_response = response.json()
            if auth_response.get('data'):
                token = auth_response['data']['token']
            else:
                token = ''
            if not token:
                raise UserError(_("Invalid username or password while obtaining token"))
            return token

    @api.model
    def website_auth_logout_token(self, token):
        url = self.get_config_params().ex_website_url
        url = "%s/api/v1/logout?api_token=%s" % (url, token)
        requests.request("POST", url,verify=False)
        return True

    @api.model
    def sync_create_log(self,message,status):
        ks_vals = {
            "message": message,
            "user_id": self.env.user.id,
            "status": status,
        }
        self.sudo().env["sync.ecommerce.logs"].create(ks_vals)

    @api.model
    def get_all_brands(self):
        url = self.get_config_params().ex_website_url
        api_token = self.website_auth_token()
        brand_url = '{0}{1}?api_token={2}'.format(url, '/api/v1/odoo/brands', api_token)
        payload = {'from': '1900-01-01', 'to': '2060-01-01'}
        response = requests.request("POST", brand_url, data=payload,verify=False).json()
        last_page = response.get('last_page')
        brand_slugs = []
        for page in range(1, last_page + 1):
            payload_page = {'page': page, 'from': '1900-01-01', 'to': '2060-01-01'}
            response = requests.request("POST", brand_url, data=payload_page,verify=False).json()
            for record in response['data']:
                brand_slugs.append(record['slug'])

        return brand_slugs

    @api.model
    def website_sync_set_brand(self):
        url = self.get_config_params().ex_website_url
        api_token = self.website_auth_token()
        brand_add_url = '{0}{1}?api_token={2}'.format(url, '/api/v1/odoo/brands/add', api_token)
        brand_slugs = self.get_all_brands()
        for brand in self.env['product.brand'].sudo().search([]):
            if brand.brand_slug not in brand_slugs:
                payload = {'name': brand.name,
                           'is_active': '1'}
                requests.request("POST", brand_add_url, data=payload,verify=False)
        return True

    @api.model
    def get_all_categories(self):
        url = self.get_config_params().ex_website_url
        api_token = self.website_auth_token()
        category_url = '{0}{1}?api_token={2}'.format(url, '/api/v1/odoo/categories', api_token)
        payload = {'from': '1900-01-01', 'to': '2060-01-01'}
        response = requests.request("POST", category_url, data=payload,verify=False).json()
        last_page = response.get('last_page')
        category_slugs = []
        for page in range(1, last_page + 1):
            payload_page = {'page': page, 'from': '1900-01-01', 'to': '2060-01-01'}
            response = requests.request("POST", category_url, data=payload_page,verify=False).json()
            for record in response['data']:
                category_slugs.append(record['slug'])
        return category_slugs

    @api.model
    def website_sync_set_category(self):
        url = self.get_config_params().ex_website_url
        api_token = self.website_auth_token()
        category_add_url = '{0}{1}?api_token={2}'.format(url, '/api/v1/odoo/categories/add', api_token)
        categ_slugs = self.get_all_categories()
        for category in self.env['product.category'].sudo().search([]):
            if category.categ_slug not in categ_slugs:
                payload = {'name': category.name,
                           'is_active': '1',
                           'is_searchable': '1'}
                requests.request("POST", category_add_url, data=payload,verify=False)
        return True

    @api.model
    def get_all_products(self):
        url = self.get_config_params().ex_website_url
        api_token = self.website_auth_token()
        product_url = '{0}{1}?api_token={2}'.format(url, '/api/v1/odoo/products', api_token)
        # start_date = self.env['ir.config_parameter'].sudo().get_param('external_commerce_integration.last_sync',
        #                                                               str(datetime.now().date() - timedelta(days=1)))
        start_date = self.get_config_params().last_sync_date if self.get_config_params().last_sync_date else str(
            datetime.now().date() - timedelta(days=1))
        # start_date =str(datetime.strptime(str(datetime.now().date()), DEFAULT_SERVER_DATE_FORMAT)- timedelta(days=1))
        end_date = str(datetime.now().date() + timedelta(days=1))
        payload = {'from': start_date, 'to': end_date}
        response = requests.request("POST", product_url, data=payload,verify=False).json()
        last_page = response.get('last_page')
        product_skus = []
        for page in range(1, last_page + 1):
            payload_page = {'page': page, 'from': '1900-01-01', 'to': '2060-01-01'}
            try:
                response = requests.request("POST", product_url, data=payload_page,verify=False).json()
                if 'data' in response:
                    for record in response['data']:
                        product_skus.append(record['sku'])
            except:
                pass
        return product_skus

    @api.model
    def website_sync_set_product(self):
        url = self.get_config_params().ex_website_url
        api_token = self.website_auth_token()
        product_add_url = '{0}{1}?api_token={2}'.format(url, '/api/v1/odoo/products/add', api_token)
        product_skus = self.get_all_products()
        for product in self.env['product.product'].sudo().search([]):
            if product.default_code not in product_skus:
                payload = {'name': product.name,
                           'barcode': product.barcode,
                           'tax_class_id': '1',
                           'is_active': '1',
                           'price': str(product.list_price),
                           'sku': product.default_code,
                           'manage_stock': '1',
                           'qty': str(product.qty_available),
                           'in_stock': '0' if not product.qty_available else '1',
                           }
                requests.request("POST", product_add_url, data=payload,verify=False)
        return True

    @api.model
    def get_all_customers(self):
        url = self.get_config_params().ex_website_url
        api_token = self.website_auth_token()
        customer_url = '{0}{1}?api_token={2}'.format(url, '/api/v1/odoo/customers', api_token)
        # start_date = self.env['ir.config_parameter'].sudo().get_param('external_commerce_integration.last_sync',
        #                                                               str(datetime.now().date() - timedelta(days=1)))
        start_date = self.get_config_params().last_sync_date if self.get_config_params().last_sync_date else str(datetime.now().date() - timedelta(days=1))
        end_date = str(datetime.now().date() + timedelta(days=1))
        payload = {'from': start_date, 'to': end_date}
        response = requests.request("POST", customer_url, data=payload,verify=False).json()
        last_page = response.get('last_page')
        customer_emails = []
        for page in range(1, last_page + 1):
            payload_page = {'page': page, 'from': '1900-01-01', 'to': '2060-01-01'}
            response = requests.request("POST", customer_url, data=payload_page,verify=False).json()
            for record in response['data']:
                customer_emails.append(record['id'])
        return customer_emails

    @api.model
    def website_sync_set_customer(self):
        url = self.get_config_params().ex_website_url
        customer_add_url = '{0}{1}'.format(url, '/api/v1/register')
        partner_mails = self.get_all_customers()
        for partner in self.env['res.partner'].sudo().search([]):
            if partner.email not in partner_mails:
                payload = {'first_name': partner.name.split(' ')[0],
                           'last_name': partner.name.split(' ')[1] if len(
                               partner.name.split(' ')) > 1 else partner.name,
                           'email': partner.email,
                           'password': partner.email}
                requests.request("POST", customer_add_url, data=payload,verify=False)
        return True

    @api.model
    def website_sync_get_brand(self):
        url = self.get_config_params().ex_website_url
        api_token = self.website_auth_token()
        brand_url = '{0}{1}?api_token={2}'.format(url, '/api/v1/odoo/brands', api_token)
        payload = {'from': '1900-01-01', 'to': '2060-01-01'}
        response = requests.request("POST", brand_url, data=payload,verify=False).json()
        last_page = response.get('last_page')
        for page in range(1, last_page + 1):
            payload_page = {'from': '1900-01-01', 'to': '2060-01-01', 'page': page}
            response = requests.request("POST", brand_url, data=payload_page,verify=False).json()
            for record in response['data']:
                is_exist = self.env['product.brand'].sudo().search([('brand_slug', '=', record['slug'])])
                if not is_exist:
                    self.env['product.brand'].sudo().create({
                        'name': record['name'],
                        'brand_slug': record['slug'],
                        'brand_external_id': record['id']
                    })
                    self.sync_create_log("Brand %s created"%(record['name']), "success")
                else:
                    _logger.info('Brand Already exist with name  %s' % is_exist.brand_slug)
                    is_exist.write({
                        'name': record['name'],
                        'brand_external_id': int(record['id']),
                    })
        self.website_auth_logout_token(api_token)
        return True

    @api.model
    def website_sync_get_category(self):
        url = self.get_config_params().ex_website_url
        api_token = self.website_auth_token()
        category_url = '{0}{1}?api_token={2}'.format(url, '/api/v1/odoo/categories', api_token)
        payload = {'from': '1900-01-01', 'to': '2060-01-01'}
        response = requests.request("POST", category_url, data=payload,verify=False).json()
        last_page = response.get('last_page')
        for page in range(1, last_page + 1):
            payload_page = {'from': '1900-01-01', 'to': '2060-01-01', 'page': page}
            response = requests.request("POST", category_url, data=payload_page,verify=False).json()

            for record in response['data']:
                is_exist = self.env['product.category'].sudo().search([('categ_slug', '=', record['slug'])])
                if not is_exist:
                    self.env['product.category'].sudo().create({
                        'name': record.get('name') or 'Website Category#',
                        'categ_slug': record.get('slug'),
                        'categ_external_id': int(record.get('id')),
                        'categ_image_url': record['logo']['path']
                    })
                    self.sync_create_log("Category %s created" % (record['name']), "success")
                else:
                    _logger.info('Category Already exist with category slug %s' % is_exist.categ_slug)
        self.website_auth_logout_token(api_token)
        return True

    @api.model
    def website_sync_get_product(self):
        url = self.get_config_params().ex_website_url
        company = self.get_config_params()
        _logger.info('Company is >>> {}'.format(company))
        api_token = self.website_auth_token()
        product_url = '{0}{1}?api_token={2}'.format(url, '/api/v1/odoo/products', api_token)
        # start_date = self.env['ir.config_parameter'].sudo().get_param('external_commerce_integration.last_sync',
        #                                                               str(datetime.now().date() - timedelta(days=3)))
        # start_date =str(datetime.strptime(str(datetime.now().date()), DEFAULT_SERVER_DATE_FORMAT)- timedelta(days=3))
        start_date = self.get_config_params().last_sync_date if self.get_config_params().last_sync_date else str(
            datetime.now().date() - timedelta(days=3))
        end_date = str(datetime.now().date() + timedelta(days=4))
        payload = {'from': start_date, 'to': end_date}
        response = requests.request("POST", product_url, data=payload,verify=False).json()
        last_page = response.get('last_page')
        for page in range(1, last_page + 1):
            payload_page = {'from': start_date, 'to': end_date, 'page': page}
            response = requests.request("POST", product_url, data=payload_page,verify=False)
            _logger.warn(response.text)
            response=response.json()
            for record in response['data']:
                if record.get('sku'):
                    attributes = record['options']
                    brand_id = self.env['product.brand'].sudo().search([('brand_external_id', '=', record['brand_id'])],
                                                                       limit=1)
                    categ_id = self.env.ref('product.product_category_all')
                    if 'category_id' in record:
                        categ_id = self.env['product.category'].sudo().search(
                            [('brand_external_id', '=', record['category_id'])],
                            limit=1) or categ_id


                    list_of_attrs = []
                    for item in attributes:
                        attribute_id = self.env['product.attribute'].search([('name', '=', item.get('name'))],
                                                                            limit=1) or self.env[
                                           'product.attribute'].create({'name': item.get('name'), 'sequence': 1})
                        value_ids = []
                        for val_item in item.get('values'):
                            val_rec = self.env['product.attribute.value'].search(
                                [('name', '=', val_item.get('label')), ('attribute_id', '=', attribute_id.id)],
                                limit=1) or self.env['product.attribute.value'].create({
                                'name': val_item.get('label'),
                                'attribute_id': attribute_id.id,
                                'sequence': 1,
                            })
                            value_ids.append(val_rec.id)
                        list_of_attrs.append({
                            'attribute_id': attribute_id.id,
                            'value_ids': [(6, 0, value_ids)],
                        })
                    image_url = record['files'][0]['path'] if record['files'] else False
                    is_exist = self.env['product.template'].sudo().search([('external_id', '=', record.get('id'))], limit=1)
                    if not is_exist:
                        is_exist = self.env['product.template'].sudo().create({
                            'name': record.get('name'),
                            'special_price': record.get('special_price', {}).get('amount', 0) if record.get('special_price') else 0,
                            # 'barcode': record.get('barcode'),
                            'image_1920': base64.b64encode(requests.get(image_url, verify=False).content) if image_url and 'webp' not in image_url else False,
                            'special_price_type': str(record['special_price_type']) or '',
                            'special_price_start': str(record['special_price_start']) or '',
                            'special_price_end': str(record['special_price_end']) or '',
                            'default_code': str(record['sku']) if not list_of_attrs else '',
                            'attribute_line_ids': [(0, 0, attr_item) for attr_item in list_of_attrs],
                            'external_id': str(record['id']),
                            'list_price': record['price']['amount'] if type(
                                record['price']['amount']) is float else 0.0,
                            'product_brand_rec_id': brand_id.id if brand_id else False,
                            'uom_id': self.env.ref('uom.product_uom_unit').id,
                            'categ_id': categ_id.id,
                            'type': 'product',
                            'company_id': company.id
                        })
                        self.sync_create_log("Product %s created" % (record['name']), "success")
                        if list_of_attrs :
                            for item in attributes:
                                for val_item in item.get('values'):
                                    for product in is_exist.product_variant_ids:
                                        for product_rec in product.product_template_attribute_value_ids:
                                            if product_rec.name.lower() == val_item.get('label').lower():
                                                product.write({
                                                    'default_code': str(val_item['sku']),
                                                    # 'barcode': str(val_item['barcode']),
                                                    # 'external_id': str(val_item['id']),
                                                    'list_price': val_item['price']['amount'] if type(
                                                        val_item['price']['amount']) is float else 0.0,
                                                })
                    else:
                        _logger.info('Product already exist with the same external id %s' % is_exist.external_id)
                        is_exist.write({
                            'list_price': float(record['price']['amount']),
                            'company_id': company.id
                            # 'default_code': str(record['sku']),
                        })
        self.website_auth_logout_token(api_token)
        return True

    @api.model
    def website_sync_get_customers(self):
        url = self.get_config_params().ex_website_url
        api_token = self.website_auth_token()
        customer_url = '{0}{1}?api_token={2}'.format(url, '/api/v1/odoo/customers', api_token)
        # start_date = self.env['ir.config_parameter'].sudo().get_param('external_commerce_integration.last_sync',
        #                                                               str(datetime.now().date() - timedelta(days=1)))
        start_date = self.get_config_params().last_sync_date if self.get_config_params().last_sync_date else str(
            datetime.now().date() - timedelta(days=1))
        # start_date =str(datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)- timedelta(days=1))

        end_date = str(datetime.now().date() + timedelta(days=1))

        payload = {'from': start_date, 'to': end_date}
        response = requests.request("POST", customer_url, data=payload,verify=False).json()
        last_page = response.get('last_page')
        for page in range(1, last_page + 1):
            payload_page = {'from': '1900-01-01', 'to': '2060-12-01', 'page': page}
            response = requests.request("POST", customer_url, data=payload_page,verify=False)
            _logger.warn(response.text)
            response=response.json()
            for record in response['data']:
                is_exist = self.env['res.partner'].sudo().search([('ref_customer_id', '=', str(record['id']))])
                if not is_exist:
                    self.env['res.partner'].sudo().create({
                        'ref_customer_id': record.get('id'),
                        'name': record.get('first_name') + ' ' + record.get('last_name'),
                        'email': record.get('email'),
                        'phone': record['phone_number']
                    })
                    self.sync_create_log("Customer %s created" % (record['first_name']), "success")
                else:
                    _logger.info('Customer Already exist with id  %s' % is_exist.ref_customer_id)
        self.website_auth_logout_token(api_token)
        return True

    @api.model
    def website_sync_get_orders(self):
        url = self.get_config_params().ex_website_url
        api_token = self.website_auth_token()
        orders_url = '{0}{1}?api_token={2}'.format(url, '/api/v1/odoo/orders', api_token)
        # start_date = self.env['ir.config_parameter'].sudo().get_param('external_commerce_integration.last_sync',
        #                                                               str(datetime.now().date() - timedelta(days=1)))
        start_date = self.get_config_params().last_sync_date if self.get_config_params().last_sync_date else str(
            datetime.now().date() - timedelta(days=10))
        # start_date =str(datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)- timedelta(days=1))
        end_date = str(datetime.now().date() + timedelta(days=1))
        payload = {'from': start_date, 'to': end_date}
        response = requests.request("POST", orders_url, data=payload,verify=False)
        if response.status_code == 200:
            response = response.json()
            last_page = response.get('last_page')

            for page in range(1, last_page + 1):
                payload_page = {'from': start_date, 'to': end_date, 'page': page}
                response = requests.request("POST", orders_url, data=payload_page,verify=False)
                _logger.info("Response Data Obj {}".format(response.content))
                response = response.json()
                for record in response['data']:
                    if record['status']=='order_submitted':
                        sale_exist = self.env['sale.order'].sudo().search([('external_id', '=', record['id'])])
                        if not sale_exist:
                            sale_lines = []
                            partner_id = self.env['res.partner'].sudo().search(
                                [('email', '=', record['customer_email'])], limit=1)
                            if not partner_id:
                                partner_id = self.env['res.partner'].sudo().create({
                                    "name": record['customer_first_name'],
                                    "email": record['customer_email'],
                                    "phone": record['customer_phone'],
                                    "ref_customer_id": record['customer_id'],
                                })
                                _logger.info('new partner created for sale order   ')
                            cus_address_id = self.env['res.partner.cus.address'].search([('partner_id', '=', partner_id.id),
                                                                                         ('customer_email', '=', record['customer_email'])])
                            if not cus_address_id:
                                self.env['res.partner.cus.address'].create({
                                    "partner_id": partner_id.id,
                                    "customer_first_name": record['customer_first_name'],
                                    "customer_email": record['customer_email'],
                                    "customer_phone": record['customer_phone'],
                                    "customer_last_name": record['customer_last_name'],
                                    "billing_first_name": record['billing_first_name'],
                                    "billing_last_name": record['billing_last_name'],
                                    "billing_address_1": record['billing_address_1'],
                                    "billing_address_2": record['billing_address_2'],
                                    "billing_city": record['billing_city'],
                                    "billing_state": record['billing_state'],
                                    "billing_zip": record['billing_zip'],
                                    "billing_country": record['billing_country'],
                                    "shipping_first_name": record['shipping_first_name'],
                                    "shipping_last_name": record['shipping_last_name'],
                                    "shipping_address_1": record['shipping_address_1'],
                                    "shipping_address_2": record['shipping_address_2'],
                                    "shipping_city": record['shipping_city'],
                                    "shipping_state": record['shipping_state'],
                                    "shipping_zip": record['shipping_zip'],
                                    "shipping_country": record['shipping_country'],
                                })
                            sale_order = {
                                'partner_id': partner_id.id,
                                'external_id': record['id'],
                                'extern_id': str(record['id']),
                                'payment_method_desc':record['payment_method'],
                                "customer_first_name": record['customer_first_name'],
                                "customer_email": record['customer_email'],
                                "customer_phone": record['customer_phone'],
                                "customer_last_name": record['customer_last_name'],
                                "billing_first_name": record['billing_first_name'],
                                "billing_last_name": record['billing_last_name'],
                                "billing_address_1": record['billing_address_1'],
                                "billing_address_2": record['billing_address_2'],
                                "billing_city": record['billing_city'],
                                "billing_state": record['billing_state'],
                                "billing_zip": record['billing_zip'],
                                "billing_country": record['billing_country'],
                                "shipping_first_name": record['shipping_first_name'],
                                "shipping_last_name": record['shipping_last_name'],
                                "shipping_address_1": record['shipping_address_1'],
                                "shipping_address_2": record['shipping_address_2'],
                                "shipping_city": record['shipping_city'],
                                "shipping_state": record['shipping_state'],
                                "shipping_zip": record['shipping_zip'],
                                "shipping_country": record['shipping_country'],
                            }
                            for item in record['products']:
                                dict_line = dict()
                                if item.get('options'):
                                    _logger.warning(item['options'])
                                    sku=item['options'][0]['values'][0]['sku']
                                else:
                                    sku = item['product']['sku']
                                product_id = self.env['product.product'].sudo().search([('default_code', '=', str(sku))],
                                                                                       limit=1)
                                if product_id:
                                    dict_line.update({
                                        'name': product_id.name,
                                        'product_id': product_id.id,
                                        'product_uom_qty': item['qty'],
                                        'product_uom': product_id.uom_id.id,
                                        'price_unit': item['line_total']['inCurrentCurrency']['amount']/item['qty'],
                                    })
                                    sale_lines.append(dict_line)

                            if record.get('shipping_cost'):
                                product= self.env.ref('delivery.product_product_delivery')
                                sale_lines.append({
                                    'name':'Delivery Charge',
                                    'product_id': product.id,
                                    'product_uom_qty': 1,
                                    'product_uom': product.uom_id.id,
                                    'price_unit': float(record['shipping_cost']['amount']),
                                })

                            if record.get('discount'):
                                if record['discount']['inCurrentCurrency']['amount']:
                                    product= self.env.ref('external_commerce_integration.product_product_discount')
                                    sale_lines.append({
                                        'name':'Discount Charge',
                                        'product_id': product.id,
                                        'product_uom_qty': -1,
                                        'product_uom': product.uom_id.id,
                                        'price_unit': float(record['discount']['amount']),
                                    })
                            sale_order.update({
                                'order_line': [(0, 0, rec_item) for rec_item in sale_lines]
                            })
                            sale_id=self.env['sale.order'].sudo().create(sale_order)
                            self.sync_create_log("Order %s created" % (str(record['id'])), "success")
                            try:
                                sale_id.action_confirm()
                            except:
                                pass
                        else:
                            _logger.info('Sale order already exist with same external id')
            self.website_auth_logout_token(api_token)
        else:
            raise ValidationError(
                _(str(response.reason)))
        return True

    def sync_brand(self):
        self.website_sync_get_brand()
    def sync_categ(self):
        self.website_sync_get_category()
    def sync_product(self):
        self.website_sync_get_product()
    def sync_customer(self):
        self.website_sync_get_customers()
    def sync_orders(self):
        _logger.info('updating from wizarddddddddddddddddddd')
        self.website_sync_get_orders()
        self.env['ir.config_parameter'].sudo().set_param("external_commerce_integration.last_sync",
                                                         str(datetime.now().date()))



    # def start_sync(self):
    #     import time
    #     self.website_sync_get_brand()
    #     time.sleep(10)
    #     self.website_sync_get_category()
    #     time.sleep(10)
    #     self.website_sync_get_product()
    #     time.sleep(15)
    #     self.website_sync_get_customers()
    #     time.sleep(10)
    #     self.website_sync_get_orders()
    #     self.env['ir.config_parameter'].sudo().set_param("external_commerce_integration.last_sync",
    #                                                      str(datetime.now().date()))

    def set_start_sync(self):
        pass
        # self.website_sync_set_brand()
        # self.website_sync_set_category()
        # self.website_sync_set_product()
        # self.website_sync_set_customer()
        # self.env['ir.config_parameter'].sudo().set_param("external_commerce_integration.last_sync_set",
        #                                                  str(datetime.now().date()))
