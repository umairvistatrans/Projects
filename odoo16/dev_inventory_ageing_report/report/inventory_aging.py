# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.tools.misc import formatLang


class stock_inv_ageing_report(models.AbstractModel):
    _name = 'report.dev_inventory_ageing_report.dev_inv_ageing_temp'
    _description = "Inventory Ageing Report"

    def get_loop(self):
        return ['6', '5', '4', '3', '2', '1', '0']

    def get_aging_quantity(self, product, obj, to_date=False):
        if to_date:
            product = product.with_context(to_date=to_date)
        if obj.warehouse_ids:
            product = product.with_context(warehouse=obj.warehouse_ids.ids)
        if obj.location_ids:
            product = product.with_context(location=[obj.location_ids.id])
        return product.qty_available

    def set_total_value(self, total, val, count):
        res = total
        res[str(count)] = res[str(count)] + val
        return res

    def get_values(self, obj, product):
        res = {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0}
        res = obj.get_aging_detail()
        for i in range(7)[::-1]:
            from_qty = to_qty = 0
            from_qty = self.get_aging_quantity(product, obj, res[str(i)]['stop'])
            if res[str(i)]['start']:
                to_qty = self.get_aging_quantity(product, obj, res[str(i)]['start'])
            qty = from_qty - to_qty
            res.update({
                str(i): qty or 0.0,
            })
        return res

    def get_formate_amount(self, amount):
        amount = formatLang(self.env, amount)
        return amount

    def _get_report_values(self, docids, data=None):
        docs = self.env['inventory.age.wizard'].browse(data['form'])
        return {
            'doc_ids': docs.ids,
            'doc_model': 'inventory.age.wizard',
            'docs': docs,
            'get_loop': self.get_loop,
            'get_values': self.get_values,
            'get_formate_amount': self.get_formate_amount,
            'set_total_value': self.set_total_value,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: