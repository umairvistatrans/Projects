# -*- coding: utf-8 -*-
from odoo import fields, models, api


class  OECancelRemark(models.TransientModel):
	_name = 'oe.cancel.remark'
	_description = 'Cancel Remark Wizard'

	cancel_remarks = fields.Text(string='Remarks',required=True)


	def action_cancel_remark(self):
		active_id = self.env.context.get('active_id')
		rec = self.env['oe.visits'].browse(int(active_id))
		rec.write({'cancelled_remarks':self.cancel_remarks, 'state':'cancelled'})
		