from odoo import models, fields, api

class EsaalRegisterWizard(models.TransientModel):
    _name = 'esaal.register.wizard'
    _description = 'Esaal Register Wizard'

    message = fields.Text(string="Message", readonly=True)

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}