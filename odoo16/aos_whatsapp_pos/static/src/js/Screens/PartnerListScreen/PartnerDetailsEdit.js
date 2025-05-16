odoo.define('aos_whatsapp_pos.PartnerDetailsEdit', function (require) {
    'use strict';

    const { _t } = require('web.core');
    // const PosComponent = require('point_of_sale.PosComponent');
    const PartnerDetailsEdit = require('point_of_sale.PartnerDetailsEdit');
    // const PosComponent = require('point_of_sale.PosComponent');
    // const {useState} = owl.hooks;
    // const {useListener} = require('web.custom_hooks');
    // const models = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    //class PartnerDetailsEdit extends PosComponent
    
    const WhatsappPartnerDetailsEdit = PartnerDetailsEdit =>
        class extends PartnerDetailsEdit {
			constructor() {
				super(...arguments);
				let self = this;
                console.log('===EDIT GAN====')
			}
            saveChanges() {
                let processedChanges = {};
                for (let [key, value] of Object.entries(this.changes)) {
                    if (this.intFields.includes(key)) {
                        processedChanges[key] = parseInt(value) || false;
                    } else {
                        processedChanges[key] = value;
                    }
                }
                if ((!this.props.partner.name && !processedChanges.name) ||
                    processedChanges.name === '' ){
                    return this.showPopup('ErrorPopup', {
                      title: _t('A Customer Name Is Required'),
                    });
                }
                if ((!this.props.whatsaapp && !processedChanges.whatsapp) || processedChanges.whatsapp === '0' || processedChanges.whatsapp === '' ){
                    return this.showPopup('ErrorPopup', {
                      title: _t('A Whatsapp Number Is Required or Cannot 0'),
                    });
                }
                processedChanges.id = this.props.partner.id || false;
                this.trigger('save-changes', { processedChanges });
            }
		};
    Registries.Component.extend(PartnerDetailsEdit, WhatsappPartnerDetailsEdit);

    return WhatsappPartnerDetailsEdit;
});
