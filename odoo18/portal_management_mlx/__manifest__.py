# -*- coding: utf-8 -*-
{
    'name': 'Portal Management (Malex)',
    'version': '1.0',
    'category': 'Website',
    'summary': "Streamline and manage supplier and product submissions.",
    'description': """The Portal Management MLX module introduces a robust platform for handling various submission requests such as new suppliers, factories, products, and categories. This module simplifies supplier onboarding, enhances submission handling, and automates workflow management via a supplier portal.

Key Features:

- **Submission Request Model**: A centralized model `submission.request` to handle requests for:
  - Factories: Including details like name, location, certifications, contact, and capacity.
  - Suppliers: Comprehensive details including name, contact information, and related factories.
  - Products: Detailed information including model, unique identifier, category, and attachments.
  - Categories: Simplified hierarchy management with parent category support.

- **Dynamic Fields and Validation**: Fields adjust dynamically based on the submission type, with front-end validation for required attributes.

- **Supplier Portal**:
  - Dedicated menu for submissions, with submenus for products, categories, factories, etc.
  - Access controlled via a supplier-specific user group with limited rights.

- **New Supplier Registration**:
  - Password-protected webpage for new supplier submissions.
  - Configurable link and password stored in `res.config.settings`.
  - Integrated form for supplier and factory details, redirecting to a thank-you page post-submission.

- **Automated Approvals**:
  - Requests are reviewed for approval before suppliers gain portal access.
  - New suppliers are added to `res.partner` but activated only upon approval.

- **Existing Suppliers**:
  - Seamless login to the portal for existing suppliers to manage their submissions.

- **Dashboard and Workflow Management**:
  - **Dedicated Dashboards**: Visualised insights and management of submission requests, procurement, and fulfillment processes.
  - **Offer Creation and Templates**: Centralized tools for creating and managing offers, with reusable templates.
  - **Logistics and Quality Control**: Management tools for logistics workflows and both internal and external QC inspections.
  - **Custom Workflow Management**: Streamlined workflow handling from procurement to fulfillment, ensuring efficiency and accountability.

This module transforms supplier management and submission handling, ensuring efficient workflows, improved data integrity, and an enhanced user experience across the procurement and fulfillment lifecycle.
""",
    'author': 'Caribou CS.',
    'company': 'Caribou CS.',
    'website': "https://www.cariboucs.com",
    'license': 'Other proprietary',

    'depends': ['base', 'portal', 'website', 'mail', 'product', 'contacts'],
    'data': [
        'data/data.xml',
        'data/email_templates.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_config_views.xml',
        'views/submission_request_views.xml',
        'views/internal_views.xml',
        'views/submission_templates.xml',
        'views/website_data.xml',
        'views/my_portal_inherit_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'portal_management_mlx/static/src/scss/style.scss',
        ],
    },
    'post_init_hook': '_malex_post_initialisation',
    'installable': True,
    'application': True,
}
