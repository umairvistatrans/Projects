# -*-coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
import pytz
from odoo.tools import date_utils
import io

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

FORMAT_DATE = "%Y-%m-%d %H:%M:%S"
ERREUR_FUSEAU = _("Set your timezone in preferences")


def convert_UTC_TZ(self, UTC_datetime):
    if not self.env.user.tz:
        raise UserError(ERREUR_FUSEAU)
    local_tz = pytz.timezone(self.env.user.tz)
    date = UTC_datetime
    date = pytz.utc.localize(date, is_dst=None).astimezone(local_tz)
    return date.strftime(FORMAT_DATE)


def get_values(self, data):
    quant_obj = self.env["stock.quant"]
    products = self.env['product.product']

    start = data['start']
    end = data['end']
    date_start = data['date_start']
    date_end = data['date_end']
    location_id = data['location_id']
    category_id = data['category_id']
    filter_products = data['products']
    is_zero = data['is_zero']
    filter_by = data['filter_by']
    group_by_category = data['group_by_category']

    # domains
    quant_domain = [('location_id', 'child_of', location_id)]
    moves_domain = [
        ('date', '>=', start),
        ('date', '<=', end),
        ('state', '=', 'done'),
        '|',
        ('location_dest_id', 'child_of', location_id),
        ('location_id', 'child_of', location_id)]
    moves_now_domain = [
        ('date', '>=', end),
        ('date', '<=', fields.Datetime.now()),
        ('state', '=', 'done'),
        '|',
        ('location_dest_id', 'child_of', location_id),
        ('location_id', 'child_of', location_id)]

    if filter_by == 'product' and filter_products:
        quant_domain.append(('product_id', 'in', filter_products))
        moves_domain.append(('product_id', 'in', filter_products))
        moves_now_domain.append(('product_id', 'in', filter_products))

    elif filter_by == 'category' and category_id:
        quant_domain.append(('product_id.categ_id', 'child_of', category_id))
        moves_domain.append(('product_id.categ_id', 'child_of', category_id))
        moves_now_domain.append(('product_id.categ_id', 'child_of', category_id))

    quants = quant_obj.search(quant_domain)
    moves = self.env['stock.move'].search(moves_domain)
    moves_to_now = self.env['stock.move'].search(moves_now_domain)

    location = self.env['stock.location'].browse(location_id)
    location_ids = self.env['stock.location'].search([
        ('parent_path', '=like', location.parent_path + "%")])

    mv_in = moves.filtered(
        lambda x: x.location_dest_id.id in location_ids.ids)
    mv_out = moves.filtered(
        lambda x: x.location_id.id in location_ids.ids)
    mv_tonow_in = moves_to_now.filtered(
        lambda x: x.location_dest_id.id in location_ids.ids)
    mv_tonow_out = moves_to_now.filtered(
        lambda x: x.location_id.id in location_ids.ids)

    products |= quants.mapped('product_id')
    products |= mv_in.mapped("product_id")
    products |= mv_out.mapped("product_id")

    datas = {}
    datas['warehouse'] = data['warehouse_name']
    datas['location'] = data['location_name']
    datas['date_from'] = date_start
    datas['date_to'] = date_end
    datas['details'] = data['details']
    datas['group_by_category'] = data['group_by_category']

    # title filter
    datas['filter_title_label'] = ""
    datas['filter_title_value'] = ""
    if filter_by == 'product' and filter_products:
        datas['filter_title_label'] = "Filter Products"
        datas['filter_title_value'] = data['products_name']
    elif filter_by == 'category' and category_id:
        datas['filter_title_label'] = "Filter Categories"
        datas['filter_title_value'] = data['category_name']

    result = []
    categories = products.mapped('categ_id')

    result = []
    categories = products.mapped('categ_id')

    for categ in categories:
        line_categ = {}
        line_categ['name'] = categ.name
        line_categ['lines'] = []

        if group_by_category:
            products_categ = products.filtered(
                lambda x: x.categ_id.id == categ.id)
            line_categ['show'] = True
        else:
            products_categ = products
            line_categ['show'] = False

        for product in products_categ.sorted(lambda r: r.name):
            line = {}
            line['name'] = product.name
            line['ref'] = product.default_code
            line['uom'] = product.uom_id.name

            mv_in_pro = mv_in.filtered(
                lambda x: x.product_id.id == product.id)
            mv_out_pro = mv_out.filtered(
                lambda x: x.product_id.id == product.id)
            mv_tonow_in_pro = mv_tonow_in.filtered(
                lambda x: x.product_id.id == product.id)
            mv_tonow_out_pro = mv_tonow_out.filtered(
                lambda x: x.product_id.id == product.id)

            if not is_zero and not mv_in_pro and not mv_out_pro:
                continue

            product_uom = product.uom_id
            tot_in = 0
            for elt in mv_in_pro:
                if product_uom.id != elt.product_uom.id:
                    factor = product_uom.factor / elt.product_uom.factor
                else:
                    factor = 1.0
                tot_in += elt.product_uom_qty * factor

            tot_out = 0
            for elt in mv_out_pro:
                if product_uom.id != elt.product_uom.id:
                    factor = product_uom.factor / elt.product_uom.factor
                else:
                    factor = 1.0
                tot_out += elt.product_uom_qty * factor

            tot_tonow_in = 0
            for elt in mv_tonow_in_pro:
                if product_uom.id != elt.product_uom.id:
                    factor = product_uom.factor / elt.product_uom.factor
                else:
                    factor = 1.0
                tot_tonow_in += elt.product_uom_qty * factor

            tot_tonow_out = 0
            for elt in mv_tonow_out_pro:
                if product_uom.id != elt.product_uom.id:
                    factor = product_uom.factor / elt.product_uom.factor
                else:
                    factor = 1.0
                tot_tonow_out += elt.product_uom_qty * factor

            actual_qty = product.with_context(
                {'location': location_id}).qty_available
            actual_qty += tot_tonow_out - tot_tonow_in

            line['si'] = actual_qty - tot_in + tot_out
            line['in'] = tot_in
            line['out'] = tot_out
            line['bal'] = tot_in - tot_out
            line['fi'] = actual_qty

            move_in_show = mv_in_pro - mv_tonow_in_pro
            move_out_show = mv_out_pro - mv_tonow_out_pro

            move_to_show = self.env['stock.move']
            move_to_show |= move_in_show
            move_to_show |= move_out_show
            move_to_show.sorted(lambda r: r.date)
            line['lines'] = []
            val_in = actual_qty - tot_in + tot_out
            val_fin = val_in
            for mv in move_to_show:
                src = mv.location_id.id
                dst = mv.location_dest_id.id
                qty = mv.product_uom_qty

                val_in = qty if dst in location_ids.ids else 0
                val_out = qty if src in location_ids.ids else 0
                val_bal = val_in - val_out
                val_fin += val_bal

                mvdate = convert_UTC_TZ(self, mv.date) if mv.date else ""
                mvname = mv.picking_id.name or mv.name or "-"

                elt = {}
                elt['mv'] = mvname
                elt['date'] = str(mvdate) or "-"
                elt['in'] = val_in
                elt['out'] = val_out
                elt['bal'] = val_bal
                elt['fi'] = val_fin
                line['lines'].append(elt)
            line_categ['lines'].append(line)
        result.append(line_categ)
        if not group_by_category:
            break
    datas['lines'] = result
    return datas


class StockCardDetailsReport(models.AbstractModel):
    _name = 'report.hyd_stock_card.stock_card_details_template'
    _description = "Report Stock Card Details Template"

    def _get_report_values(self, docids, data=None):
        return {'doc_ids': docids, 'data': get_values(self, data)}


class StockCardDetailsReportXls(models.AbstractModel):
    _name = 'report.hyd_stock_card.stock_card_details_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Stock Card Details Xls"

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet('Stock Card')
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format1_nobold = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': False})
        format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'align': 'left', 'bold': True})
        format21_nobold = workbook.add_format({'font_size': 10, 'align': 'left', 'bold': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        format4 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        font_size_8 = workbook.add_format({'font_size': 8, 'align': 'center'})
        font_size_8_l = workbook.add_format({'font_size': 8, 'align': 'left'})
        font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right'})
        font_size_8_blue = workbook.add_format({'font_size': 8, 'align': 'right', 'bg_color': '#95A5A6'})
        red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
        justify = workbook.add_format({'font_size': 12})
        format3.set_align('center')
        justify.set_align('justify')
        format1.set_align('center')
        red_mark.set_align('center')

        format_tab_entete = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
        format_tab_entete.set_bg_color('#333333')
        format_tab_entete.set_font_color('white')
        format_tab_entete.set_align('center')

        sheet.merge_range(2, 1, 2, 3, 'Warehouse', format21)
        sheet.merge_range(2, 4, 2, 5, data['warehouse'], format21_nobold)

        if data['filter_title_label']:
            sheet.write(3, 1, 'Location', format21)
            sheet.merge_range(3, 2, 3, 3, data['location'], format21_nobold)
            sheet.write(3, 4, data['filter_title_label'], format21)
            sheet.merge_range(3, 5, 3, 6, data['filter_title_value'], format21_nobold)
        else:
            sheet.merge_range(3, 1, 3, 3, 'Location', format21)
            sheet.merge_range(3, 4, 3, 5, data['location'], format21_nobold)

        sheet.write(4, 1, 'Date from', format21)
        sheet.merge_range(4, 2, 4, 3, data['date_from'], format21_nobold)
        sheet.write(4, 4, 'Date to', format21)
        sheet.merge_range(4, 5, 4, 6, data['date_to'], format21_nobold)

        sheet.write(6, 1, 'Reference', format_tab_entete)
        sheet.write(6, 2, 'Designation', format_tab_entete)
        sheet.write(6, 3, 'Uom', format_tab_entete)
        sheet.write(6, 4, 'Move', format_tab_entete)
        sheet.write(6, 5, 'Date', format_tab_entete)
        sheet.write(6, 6, 'Stock initial', format_tab_entete)
        sheet.write(6, 7, 'In', format_tab_entete)
        sheet.write(6, 8, 'Out', format_tab_entete)
        sheet.write(6, 9, 'Balance', format_tab_entete)
        sheet.write(6, 10, 'Final stock', format_tab_entete)

        i = 7
        for categ in data['lines']:

            if categ['show']:
                sheet.merge_range(i, 1, i, 2, "Category", font_size_8_l)
                sheet.merge_range(i, 3, i, 10, categ['name'], format21)
                i += 1

            for line in categ['lines']:

                slines = line['lines']
                size_slines = len(slines)

                sheet.write(i, 1, line['ref'], font_size_8_l)
                sheet.write(i, 2, line['name'], font_size_8_l)
                sheet.write(i, 3, line['uom'], font_size_8_l)
                sheet.write(i, 6, line['si'], font_size_8_blue)
                i += 1

                for sline in slines:
                    sheet.write(i, 4, sline['mv'], font_size_8_r)
                    sheet.write(i, 5, sline['date'], font_size_8_r)
                    sheet.write(i, 7, sline['in'], font_size_8_r)
                    sheet.write(i, 8, sline['out'], font_size_8_r)
                    sheet.write(i, 9, sline['bal'], font_size_8_r)
                    sheet.write(i, 10, sline['fi'], font_size_8_r)
                    i += 1

                sheet.write(i, 10, line['fi'], font_size_8_blue)
                i += 1
