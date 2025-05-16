# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SupplierFactory(models.Model):
    _name = 'supplier.factory'
    _description = 'Supplier Factory'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)

    name = fields.Char(string="Factory Name", tracking=True, copy=False)
    submission_id = fields.Many2one('submission.request', string='Related Submission')
    supplier_id = fields.Many2one('res.partner', string='Related Supplier')
    location = fields.Char(string="Location", tracking=True, copy=False)
    certifications = fields.Many2many('ir.attachment', 'rel_factory_cert_attachment', string="Certifications", tracking=True, copy=False)
    documents = fields.Many2many(
        'ir.attachment', 'rel_factory_documents_attachment',
        string="Documents",
        help="Attach up to 4 documents related to the factory.",
        tracking=True,
        copy=False,
    )
    capacity = fields.Char(string="Capacity", tracking=True, copy=False)
    certifications_count = fields.Integer(
        string="Certifications Count",
        compute="_compute_attachments_count",
        store=False
    )
    documents_count = fields.Integer(
        string="Documents Count",
        compute="_compute_attachments_count",
        store=False
    )

    @api.depends('certifications', 'documents')
    def _compute_attachments_count(self):
        for record in self:
            record.certifications_count = len(record.certifications)
            record.documents_count = len(record.documents)

    def action_view_certifications(self):
        """Redirect to the attachments related to factory_certifications"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Certifications',
            'view_mode': 'kanban',
            'res_model': 'ir.attachment',
            'domain': [('id', 'in', self.certifications.ids)],
            'context': {'create': 0, 'edit': 0, 'delete': 0},
            'target': 'current',
        }

    def action_view_documents(self):
        """Redirect to the attachments related to factory_documents"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'view_mode': 'kanban',
            'res_model': 'ir.attachment',
            'domain': [('id', 'in', self.documents.ids)],
            'context': {'create': 0, 'edit': 0, 'delete': 0},
            'target': 'current',
        }
