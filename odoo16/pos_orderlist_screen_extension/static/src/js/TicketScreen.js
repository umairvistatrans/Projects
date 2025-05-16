/** @odoo-module **/

import TicketScreen from 'point_of_sale.TicketScreen';
import Registries from 'point_of_sale.Registries';

export const OLOrderListExtTicketScreen = (TicketScreen) =>
class OLOrderListExtTicketScreen extends TicketScreen {
    _getSearchFields() {
        let fields = super._getSearchFields(...arguments);
        fields['PARTNERMOBILE'] = {
            repr: (order) => order.get_partner_mobile(),
            displayName: this.env._t('Customer Mobile'),
            modelField: 'partner_id.mobile',
        }
        fields['PARTNERPHONE'] = {
            repr: (order) => order.get_partner_phone(),
            displayName: this.env._t('Customer Phone'),
            modelField: 'partner_id.phone',
        };
        return fields
    }

    getPartnermobile(order) {
            return order.get_partner_mobile();
        }
};

Registries.Component.extend(TicketScreen, OLOrderListExtTicketScreen);
