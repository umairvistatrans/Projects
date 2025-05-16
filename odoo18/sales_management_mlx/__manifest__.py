# -*- coding: utf-8 -*-
{
    'name': 'Sales Management (Malex)',
    'version': '1.0',
    'category': 'Website',
    'summary': "Streamline and manage sales processes.",
    'description': """The Sales Management Malex module offers a comprehensive platform for managing sales operations, customer invoices, templates, approval workflows, logistics, and quality control requests. It ensures a seamless sales process and empowers suppliers with actionable insights via dashboards.

Key Features:

- **Sales Management**:
  - Efficient handling of sales operations with tools for creating, managing, and tracking sales orders.
  - Configurable sales approval processes ensuring compliance with company policies.

- **Customer Invoices**:
  - Streamlined creation and management of customer invoices, with automated tracking of payment statuses.
  - Integration with accounting to simplify reconciliation and financial reporting.

- **Sales Templates**:
  - Centralized repository for reusable sales templates, enabling quick and consistent offer creation.
  - Customizable templates for diverse product categories and customer needs.

- **Logistics Management**:
  - End-to-end logistics management, including shipping, delivery tracking, and coordination with third-party logistics providers.
  - Integration with Quality Control workflows to ensure product standards are met before delivery.

- **Quality Control (QC) Requests**:
  - Systematic handling of QC requests to maintain product quality and customer satisfaction.
  - Tools for both internal and external QC inspections, with tracking and reporting capabilities.

- **Approval Workflows**:
  - Role-based approval workflows for sales, invoices, and logistics processes to enhance accountability and governance.

- **Supplier Dashboards and Insights**:
  - **Visualized Sales Statistics**: Real-time insights into sales performance, customer trends, and revenue breakdowns.
  - **Logistics and QC Overviews**: Detailed tracking of shipments and quality control requests.
  - **Invoice Summaries**: Simplified financial overviews for improved decision-making.

This module transforms sales management into an efficient, transparent, and user-friendly process. By integrating sales, logistics, and QC workflows with insightful dashboards, Sales Management Malex empowers suppliers to drive better business outcomes and customer satisfaction.
""",

    'author': 'Caribou CS.',
    'company': 'Caribou CS.',
    'website': "https://www.cariboucs.com",
    'license': 'Other proprietary',

    'depends': ['sale_management', 'hr'],
    'data': [
        'views/sales_management_views.xml',
    ],
    'installable': True,
    'application': True,
}
