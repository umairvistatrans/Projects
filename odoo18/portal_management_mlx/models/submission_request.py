# -*- coding: utf-8 -*-

import string
import random

from odoo import models, fields, api
from odoo.exceptions import UserError


def _generate_password(length=12):
    """
    Generate a random secure password of the given length.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


class SubmissionRequest(models.Model):
    _name = 'submission.request'
    _description = 'Submission Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Reference No.",
        required=True,
        tracking=True,
        copy=False,
        default='/'
    )
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, default=lambda self: self.env.company)
    submission_type = fields.Selection([
        ('supplier', 'Supplier'),
        ('factory', 'Factory'),
        ('product', 'Product'),
        ('category', 'Category'),
    ], string="Submission Type", required=True, tracking=True, copy=False, default='supplier')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_approval', 'In Approval'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancelled', 'Cancelled'),
    ], string="Status", default='draft', required=True, tracking=True, copy=False)
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one('res.partner')

    # Factory Fields
    factory_name = fields.Char(string="Factory Name", tracking=True, copy=False)
    factory_location = fields.Char(string="Location", tracking=True, copy=False)
    factory_certifications = fields.Many2many(
        'ir.attachment', 'factory_certifications_rel',
        string="Factory Certifications",
        help="Attach up to 4 certifications related to the factory.",
        copy=False,
    )
    factory_documents = fields.Many2many(
        'ir.attachment', 'factory_documents_rel',
        string="Factory Documents",
        help="Attach up to 4 documents related to the factory.",
        copy=False,
    )
    factory_capacity = fields.Char(string="Capacity", tracking=True, copy=False)

    # Supplier Fields
    supplier_name = fields.Char(string="Supplier Name", tracking=True, copy=False)
    supplier_phone = fields.Char(string="Phone Number", tracking=True, copy=False)
    supplier_email = fields.Char(string="Email", tracking=True, copy=False)
    supplier_address = fields.Text(string="Address", tracking=True, copy=False)
    supplier_city = fields.Char(string="City", tracking=True, copy=False)
    supplier_country = fields.Many2one('res.country', string="Country", tracking=True, copy=False)
    supplier_image = fields.Binary()

    # Product Fields
    product_model_no = fields.Char(string="Model No", tracking=True, copy=False)
    product_unique_identifier = fields.Char(string="Code", tracking=True, copy=False)
    product_category = fields.Many2one('product.category', string="Category", tracking=True, copy=False)
    product_parent_category = fields.Many2one('product.category', string="Parent Category", tracking=True, copy=False)
    product_documents = fields.Many2many(
        'ir.attachment', 'product_documents_rel',
        string="Product Documents",
        help="Attach up to 7 documents related to the product.",
        copy=False,
    )
    product_images = fields.Many2many(
        'ir.attachment', 'product_images_rel',
        string="Product Images",
        help="Attach up to 7 images related to the product.",
        copy=False,
    )
    # Category Fields
    category_name = fields.Char(string="Category Name", tracking=True, copy=False)
    category_parent_category = fields.Many2one('product.category', string="Parent Category", tracking=True, copy=False)

    product_documents_count = fields.Integer(
        string="Product Documents Count",
        compute="_compute_product_attachments_count",
        store=False
    )
    product_images_count = fields.Integer(
        string="Product Documents Count",
        compute="_compute_product_attachments_count",
        store=False
    )

    factory_certifications_count = fields.Integer(
        string="Factory Certifications Count",
        compute="_compute_factory_attachments_count",
        store=False
    )
    factory_documents_count = fields.Integer(
        string="Factory Documents Count",
        compute="_compute_factory_attachments_count",
        store=False
    )

    @api.depends('product_documents', 'product_images')
    def _compute_product_attachments_count(self):
        for record in self:
            record.product_documents_count = len(record.product_documents)
            record.product_images_count = len(record.product_images)

    @api.depends('factory_certifications', 'factory_documents')
    def _compute_factory_attachments_count(self):
        for record in self:
            record.factory_certifications_count = len(record.factory_certifications)
            record.factory_documents_count = len(record.factory_documents)

    def action_view_product_documents(self):
        """Redirect to the attachments related to product_documents"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Product Documents',
            'view_mode': 'kanban',
            'res_model': 'ir.attachment',
            'domain': [('id', 'in', self.product_documents.ids)],
            'context': {'create': 0, 'edit': 0, 'delete': 0},
            'target': 'current',
        }

    def action_view_product_images(self):
        """Redirect to the attachments related to product_documents"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Product Images',
            'view_mode': 'kanban',
            'res_model': 'ir.attachment',
            'domain': [('id', 'in', self.product_images.ids)],
            'context': {'create': 0, 'edit': 0, 'delete': 0},
            'target': 'current',
        }

    def action_view_factory_certifications(self):
        """Redirect to the attachments related to factory_certifications"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Factory Certifications',
            'view_mode': 'kanban',
            'res_model': 'ir.attachment',
            'domain': [('id', 'in', self.factory_certifications.ids)],
            'context': {'create': 0, 'edit': 0, 'delete': 0},
            'target': 'current',
        }

    def action_view_factory_documents(self):
        """Redirect to the attachments related to factory_documents"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Factory Documents',
            'view_mode': 'kanban',
            'res_model': 'ir.attachment',
            'domain': [('id', 'in', self.factory_documents.ids)],
            'context': {'create': 0, 'edit': 0, 'delete': 0},
            'target': 'current',
        }

    @api.model_create_multi
    def create(self, vals_list):
        template = self.env.ref('portal_management_mlx.email_template_submission_received')
        base_user = self.env.ref('base.user_admin')
        for vals in vals_list:
            if not vals.get('name'):
                sequence_code = f'submission.request.{vals.get("submission_type")}'
                vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code) or '/'

        records = super(SubmissionRequest, self).create(vals_list)
        for record in records:
            if template:
                template.with_user(base_user).send_mail(record.id, force_send=True)

        return records

    # Smart Button Methods
    def action_view_product(self):
        """Smart button to search and show the associated product record."""
        product = self.env['product.template'].search([('submission_id', '=', self.id)], limit=1)
        if product:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Product',
                'res_model': 'product.template',
                'view_mode': 'form',
                'res_id': product.id,
            }
        else:
            raise UserError('Product not found!\n\nThe product associated with this submission has either been deleted or archived by Management.')

    def action_view_category(self):
        """Smart button to search and show the associated category record."""
        category = self.env['product.category'].search([('submission_id', '=', self.id)], limit=1)
        if category:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Category',
                'res_model': 'product.category',
                'view_mode': 'form',
                'res_id': category.id,
            }
        else:
            raise UserError('Product Category not found!\n\nThe Category associated with this submission has either been deleted or archived by Management.')

    def action_view_supplier(self):
        """Smart button to search and show the associated supplier record."""
        supplier = self.env['res.partner'].search([('submission_id', '=', self.id)], limit=1)
        if supplier:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Supplier',
                'res_model': 'res.partner',
                'view_mode': 'form',
                'res_id': supplier.id,
            }
        else:
            raise UserError('Supplier not found!\n\nThe supplier associated with this submission has either been deleted or archived by Management.')

    def action_view_factory(self):
        """Smart button to search and show the associated factory record."""
        factory = self.env['supplier.factory'].search([('submission_id', '=', self.id)], limit=1)
        if factory:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Factory',
                'res_model': 'supplier.factory',
                'view_mode': 'form',
                'res_id': factory.id,
            }
        else:
            raise UserError('Factory not found!\n\nThe factory associated with this submission has either been deleted or archived by Management.')

    def action_cancel(self):
        self._action_cancel()

    def _action_confirm(self):
        """
        Handle submission confirmation based on submission_type.
        Approves the request and creates records in corresponding models.
        """
        self.state = 'approved'
        template = self.env.ref('portal_management_mlx.email_template_submission_approved')
        base_user = self.env.ref('base.user_admin')

        for record in self:
            if record.submission_type == 'product':
                record._create_product()
            elif record.submission_type == 'category':
                record._create_category()
            elif record.submission_type == 'factory':
                record._create_factory()
            elif record.submission_type == 'supplier':
                record._create_supplier_details()
            # Send approval email
            if template:
                template.with_user(base_user).send_mail(record.id, force_send=True)

    def _create_supplier_details(self):
        """
        Handle supplier submission:
        - Create a factory.
        - Check for product details and create a product if present.
        - Associate the partner with a portal user.
        - Add the user to the submission access group.
        - Send an email with generated credentials to the supplier.
        """
        self = self.sudo()

        # Step 1: Create the factory
        self._create_factory()

        # Step 2: Check for product details and create a product if present
        if self.product_model_no:  # Mandatory product field to check presence
            self._create_product()

        partner_user = self.env['res.users'].search([('partner_id', '=', self.partner_id.id)])
        if partner_user:
            portal_group = self.env.ref('base.group_portal')
            if partner_user in portal_group.users:
                return

        portal_wizard = self.env['portal.wizard'].create({})
        portal_user = self.env['portal.wizard.user'].create({
            'wizard_id': portal_wizard.id,
            'partner_id': self.partner_id.id,
            'email': self.partner_id.email
        })
        portal_user.action_grant_access()
        partner_user = self.env['res.users'].search([('partner_id', '=', self.partner_id.id)])
        partner_user.groups_id = [(4, self.env.ref('portal_management_mlx.group_submission_access').id)]

    def _create_product(self):
        """
        Create a product in `product.template` based on submission fields.
        """
        self = self.sudo()

        product_documents = []
        for document in self.product_documents:
            product_documents.append((0, 0, {'ir_attachment_id': document.id, 'res_model': 'product.template'}))

        # Handle product images
        image_fields = [f'product_image_{i}' for i in range(1, 8)]  # Fields from product_image_1 to product_image_7
        images = list(self.product_images)  # Convert Many2many to a list for sequential access
        image_values = {}

        # Loop through images and assign them to corresponding fields
        for idx, image in enumerate(images):
            if idx < len(image_fields):  # Map only up to 7 images
                image_values[image_fields[idx]] = image.datas  # Use the binary data of the image

        # Set the first image as the main image
        if images:
            image_values['image_1920'] = images[0].datas

        product_values = {
            'name': self.product_model_no,
            'default_code': self.product_unique_identifier,
            'categ_id': self.product_category.id,
            'submission_id': self.id,
            'product_document_ids': product_documents
        }
        if image_values:
            product_values.update(image_values)

        self.env['product.template'].sudo().create(product_values)

    def _create_category(self):
        """
        Create a product category in `product.category` based on submission fields.
        """
        category_values = {
            'name': self.category_name,
            'parent_id': self.category_parent_category.id,
        }
        self.env['product.category'].sudo().create(category_values)

    def _create_factory(self):
        """
        Create a factory in `supplier.factory` based on submission fields.
        """
        factory_values = {
            'name': self.factory_name,
            'submission_id': self.id,
            'supplier_id': self.partner_id.id,
            'location': self.factory_location,
            'capacity': self.factory_capacity,
        }
        factory = self.env['supplier.factory'].sudo().create(factory_values)

        for document in self.factory_documents:
            self.factory_documents = [(3, document.id)]
            factory.documents = [(4, document.id)]
        for cert in self.factory_certifications:
            self.factory_certifications = [(3, cert.id)]
            factory.certifications = [(4, cert.id)]

    def _action_refuse(self):
        self.state = 'refused'

    def _action_cancel(self):
        self.state = 'cancelled'
        template = self.env.ref('portal_management_mlx.email_template_submission_cancelled')
        if template:
            for record in self:
                template.send_mail(record.id, force_send=True)




class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier = fields.Boolean()
    submission_id = fields.Many2one('submission.request', string='Related Submission')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    submission_id = fields.Many2one('submission.request', string='Related Submission')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    submission_id = fields.Many2one('submission.request', string='Related Submission', related='product_tmpl_id.submission_id')


class ProductCategory(models.Model):
    _inherit = 'product.category'

    submission_id = fields.Many2one('submission.request', string='Related Submission')
