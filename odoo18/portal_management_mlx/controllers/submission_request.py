# -*- coding: utf-8 -*-

import base64
import re
import werkzeug

from odoo import http, SUPERUSER_ID, _
from odoo.http import request
from werkzeug.exceptions import Forbidden


def extract_data(values):
    data = {
        'record': {},  # Values to create record
        'attachments': {},  # Attachments grouped by field
    }

    for field_name, field_value in values.items():
        # Decode field name
        field_name = re.sub('&quot;', '"', field_name)

        # Check if the value is a file
        if hasattr(field_value, 'filename'):
            # Determine the original field name
            original_field_name = field_name.split('[', 1)[0]

            # Group attachments by field name
            if original_field_name not in data['attachments']:
                data['attachments'][original_field_name] = []
            field_value.field_name = original_field_name
            data['attachments'][original_field_name].append(field_value)

    return data


class SubmissionRequestsController(http.Controller):

    @http.route('/submission/thank-you', auth='public', website=True, type='http', cors='*', methods=['GET'])
    def submission_thank_you(self):
        return request.render("portal_management_mlx.thank_you_submission")

    @http.route(['/requests/prompt'], auth='public', website=True)
    def supplier_submission_form_product(self, redirect=None, **post):
        request_id = request.params.get('request_id')
        return request.render("portal_management_mlx.product_submission_prompt", {
            'request_id': request_id if request_id else None,
        })

    @http.route(['/requests/supplier', '/requests/supplier/<string:model_name>'], auth='public', website=True,
                methods=['GET', 'POST'])
    def supplier_submission_form(self, redirect=None, **post):
        env = request.env
        # Fetch countries for the dropdown
        countries = request.env['res.country'].sudo().search([])
        values = {
            'countries': countries,
            'redirect': redirect,
        }

        view = env.ref('portal_management_mlx.submit_supplier')
        view = view.sudo()

        if post.get('visibility_password') and (request.website.is_public_user() or view.id not in request.session.get('views_unlock', [])):
            pwd = post['visibility_password']
            if pwd and env.user._crypt_context().verify(
                    pwd, view.visibility_password):
                request.session.setdefault('views_unlock', list()).append(view.id)
                return request.render("portal_management_mlx.submit_supplier", values)
            error = Forbidden('website_visibility_password_required')
            raise error

        # Handle form submission (POST)
        if post and request.httprequest.method == 'POST':
            submission_values = {
                'supplier_name': post.get('supplier_name'),
                'supplier_phone': post.get('supplier_phone'),
                'supplier_email': post.get('supplier_email'),
                'supplier_city': post.get('supplier_city'),
                'supplier_country': post.get('supplier_country'),
                'supplier_address': post.get('supplier_address'),
                'factory_name': post.get('factory_name'),
                'factory_location': post.get('factory_location'),
                'factory_capacity': post.get('factory_capacity'),
                'submission_type': 'supplier',
                'state': 'in_approval',
            }

            # Check if a partner with the same email already exists
            existing_partner = request.env['res.partner'].sudo().search([('email', '=', post.get('supplier_email'))],
                                                                        limit=1)
            if existing_partner:
                partner = existing_partner
            else:
                # Create a new partner record if no existing one is found
                partner_values = {
                    'name': post.get('supplier_name'),
                    'phone': post.get('supplier_phone'),
                    'email': post.get('supplier_email'),
                    'city': post.get('supplier_city'),
                    'country_id': post.get('supplier_country'),
                    'street': post.get('supplier_address'),
                }
                partner = request.env['res.partner'].sudo().create(partner_values)

            submission_values['partner_id'] = partner.id

            submission_request = request.env['submission.request'].sudo().create(submission_values)
            partner.submission_id = submission_request.id

            data = extract_data(post)
            # Process and attach files for each attachment field
            for field_name, files in data['attachments'].items():
                attachment_ids = []
                for file in files:
                    # Convert file to base64 and create attachment
                    file_base64 = base64.b64encode(file.read()).decode('utf-8')

                    if field_name in ['image_1920']:
                        submission_request.sudo().write({'supplier_image': file_base64})
                        partner.sudo().write({'image_1920': file_base64})
                        continue

                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': file.filename,
                        'type': 'binary',
                        'datas': file_base64,
                        'mimetype': file.mimetype,
                        'res_model': 'submission.request',
                        'res_id': submission_request.id,
                    })
                    attachment_ids.append(attachment.id)

                # Link attachments to the appropriate many2many field
                if field_name in ['factory_certifications', 'factory_documents']:
                    submission_request.sudo().write({field_name: [(6, 0, attachment_ids)]})

            # submission request id passed from here to process the product submission against it.
            return request.redirect(f'/requests/prompt?request_id={submission_request.id}')

        # Render template with countries
        return request.render("portal_management_mlx.submit_supplier", values)

    @http.route(['/requests/factory', '/requests/factory/<string:model_name>'], auth='public', website=True,
                methods=['GET', 'POST'], type='http', cors='*')
    def factory_submission_form(self, redirect=None, **post):
        if post and request.httprequest.method == 'POST':
            # Extract data including attachments
            data = extract_data(post)

            # Prepare the submission values
            submission_values = {
                'factory_name': post.get('factory_name'),
                'factory_location': post.get('factory_location'),
                'factory_capacity': post.get('factory_capacity'),
                'partner_id': request.env.user.partner_id.id,
                'submission_type': 'factory',
                'state': 'in_approval',
            }

            # Create the submission record
            submission_request = request.env['submission.request'].sudo().create(submission_values)

            # Process and attach files for each attachment field
            for field_name, files in data['attachments'].items():
                attachment_ids = []
                for file in files:
                    # Convert file to base64 and create attachment
                    file_base64 = base64.b64encode(file.read()).decode('utf-8')
                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': file.filename,
                        'type': 'binary',
                        'datas': file_base64,
                        'mimetype': file.mimetype,
                        'res_model': 'submission.request',
                        'res_id': submission_request.id,
                    })
                    attachment_ids.append(attachment.id)

                # Link attachments to the appropriate many2many field
                if field_name in ['factory_certifications', 'factory_documents']:
                    submission_request.sudo().write({field_name: [(6, 0, attachment_ids)]})

            # Handle redirection after form submission
            if redirect:
                return request.redirect(redirect)
            return request.redirect('/submission/thank-you')

        # Render template with necessary values for GET requests
        values = {
            'redirect': redirect,
        }
        return request.render("portal_management_mlx.submit_factory", values)

    @http.route(['/requests/product', '/requests/product/<string:model_name>'], auth='public', website=True,
                methods=['GET', 'POST'])
    def product_submission_form(self, redirect=None, **post):
        if post and request.httprequest.method == 'POST':
            # Extract data including attachments
            data = extract_data(post)
            product_category = post.get('product_category')

            # Prepare the submission values
            submission_values = {
                'product_model_no': post.get('product_model_no'),
                'product_unique_identifier': post.get('product_unique_identifier'),
                'product_category': int(product_category) if product_category else False,
            }
            request_id = post.get('request_id')
            if request_id and request_id != 'None':
                submission_request = request.env['submission.request'].sudo().browse(int(request_id))
                submission_request.write(submission_values)
            else:
                submission_values.update({
                    'partner_id': request.env.user.partner_id.id,
                    'submission_type': 'product',
                    'state': 'in_approval'
                })
                # Create the submission record
                submission_request = request.env['submission.request'].sudo().create(submission_values)

            # Process and attach files for each attachment field
            for field_name, files in data['attachments'].items():
                # Handle product documents (many2many field)
                if field_name in ('product_documents', 'product_images'):
                    attachment_ids = []
                    for file in files:
                        file_base64 = base64.b64encode(file.read()).decode('utf-8')
                        attachment = request.env['ir.attachment'].sudo().create({
                            'name': file.filename,
                            'type': 'binary',
                            'datas': file_base64,
                            'mimetype': file.mimetype,
                            'res_model': 'submission.request',
                            'res_id': submission_request.id,
                        })
                        attachment_ids.append(attachment.id)
                    submission_request.sudo().write({field_name: [(6, 0, attachment_ids)]})

            # Handle redirection after form submission
            if redirect:
                return request.redirect(redirect)
            return request.redirect('/submission/thank-you')

        # Handle GET request: Fetch categories and render the form
        categories = request.env['product.category'].sudo().search([])  # Adjust domain if needed
        values = {
            'categories': categories,
            'redirect': redirect,
            'request_id': request.params.get('request_id', None)
        }
        return request.render("portal_management_mlx.submit_product", values)

    @http.route(['/requests/category', '/requests/category/<string:model_name>'], auth='public', website=True,
                methods=['GET', 'POST'])
    def category_submission_form(self, redirect=None, **post):
        if request.httprequest.method == 'POST':
            # Handle form submission
            category_name = post.get('category_name')
            parent_category_id = post.get('parent_category')

            # Prepare the values for the new category
            submission_values = {
                'category_name': category_name,
                'category_parent_category': parent_category_id if parent_category_id else False,
                'partner_id': request.env.user.partner_id.id,
                'submission_type': 'category',  # Example of a custom field, if needed
                'state': 'in_approval',  # Example of a custom field, if needed
            }

            # Create the new category
            request.env['submission.request'].sudo().create(submission_values)

            return request.redirect('/submission/thank-you')

        # Handle GET request: Render the form with available parent categories
        categories = request.env['product.category'].sudo().search([])  # Adjust domain if needed
        values = {
            'categories': categories,
        }
        return request.render("portal_management_mlx.submit_category", values)
