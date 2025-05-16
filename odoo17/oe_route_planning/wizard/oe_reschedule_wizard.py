from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import date

class RescheduleWizard(models.TransientModel):

    _name = 'oe.reschedule.wizard'
    _description = 'Reschedule Wizard'

    reschedule_date = fields.Date(string='Reschedule Date', required=True)

    @api.constrains('reschedule_date')
    def _check_reschedule_date(self):
        for record in self:
            if record.reschedule_date < date.today():
                raise ValidationError("You can not schedule visits for past date !..")

    def action_reschedule(self):
        active_id = self.env.context.get('active_id')
        visit = self.env['oe.visits'].browse(active_id)
        visit.write({'state': 'planned', 'scheduled_date': self.reschedule_date})
        return {'type': 'ir.actions.act_window_close'}
