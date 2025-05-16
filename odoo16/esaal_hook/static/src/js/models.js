odoo.define('custom_pos_receipt.models', function (require) {
    "use strict";

    const { Order, PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require('point_of_sale.Gui');
    const rpc = require('web.rpc');
    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    var esaal_printed = false;

    const CustomOrder = (Order) => class CustomOrder extends Order {
        export_for_printing() {
            const result = super.export_for_printing(...arguments);
            const partner = this.get_partner();
            const partnerName = partner ? partner.name : null;
            const partnerPhone = partner ? partner.phone || partner.mobile : null;
            var partnerEmail = partner ? partner.email : null;
            result.client = partner;
            var formattedPhone = partnerPhone;
            var esaal_enabled = false;

            const update_state = async () => {
                const esaalMapperMode = await rpc.query({
                    model: 'ir.config_parameter',
                    method: 'get_param',
                    args: ['esaal_hook.esaal_mapper_mode'],
                });
                this.esaal_mapper_mode = esaalMapperMode === 'True';
    
                const esaalMapperState = await rpc.query({
                    model: 'ir.config_parameter',
                    method: 'get_param',
                    args: ['esaal_hook.esaal_mapper_state'],
                });
                this.esaal_mapper_state = esaalMapperState === 'True';

                if (this.pos.esaal_registration_info) {
                    if (esaalMapperMode && !esaalMapperState) {
                        esaal_enabled = false;
                        console.log('Disabled Esaal');
                    } else {
                        esaal_enabled = true;
                        console.log('Enabled Esaal');
                        // Run Esaal
                        run_esaal();
                    }
                } else {
                    esaal_enabled = false;
                    console.log('Disabled Esaal');
                }
            }

            const run_esaal = async () => {
                if (esaal_enabled) {
                    if (!partner) {
                        if (this.pos.esaal_customer_info) {
                            let errorMsg = 'Customer Information not provided.';
                            Gui.showPopup('ErrorPopup', {
                                title: 'Esaal',
                                body: errorMsg,
                            });
                        }
                    } else {
                        if (this.pos.esaal_customer_info) {
                            if (!partner || !partnerPhone) {
                                let errorMsg = 'Customer Information not provided.';
                                if (partner && !partnerPhone) {
                                    errorMsg = 'Customer Phone number is missing';
                                }
                                Gui.showPopup('ErrorPopup', {
                                    title: 'Esaal',
                                    body: errorMsg,
                                });
                            }
                        }
                    }
        
                    const regexPhone = () => {
                        // Try to format phone number and skip if no one is provided
                        if (partnerPhone) {
                            if (partnerPhone.startsWith('05') && partnerPhone.length === 10) {
                                formattedPhone = '+971' + partnerPhone.substring(1);  // Format to +9715xxxxxxxx
                            } else if (partnerPhone.startsWith('+971') && partnerPhone.length === 13) {
                                formattedPhone = partnerPhone;
                            } else if (partnerPhone.startsWith('00971') && partnerPhone.length === 14) {
                                formattedPhone = '+971' + partnerPhone.substring(5);  // Format to +9715xxxxxxxx
                            } else if (partnerPhone.length === 9) { //5xxxxxxxx
                                formattedPhone = '+971' + partnerPhone;  // Format to +971xxxxxxxxx
                            } else {
                                formattedPhone = null;
                            }
                        } else {
                            setTimeout(regexPhone, 500); // Check again after 100ms
                        }
                    }
        
                    // Update elements when visible
                    const checkElementsInitialized = () => {
                        const esaal_ui = document.getElementById('esaal-partner-info');
                        const partnerPhoneInput = document.getElementById('esaal-partner-phone');
                        const partnerNameInput = document.getElementById('esaal-partner-name');
                        const partnerEmailInput = document.getElementById('esaal-partner-email');
                        const genderMaleInput = document.getElementById('genderMale');
                        // Branding
                        const esaal_branding_ui = document.getElementById('esaal-branding');
                        const esaal_branding_qr_ui = document.getElementById('esaal-branding-qr');
                        if (esaal_ui && esaal_enabled) {
                            if (this.pos.esaal_registration_info) {
                                esaal_ui.style.display = 'block';
                                if (this.pos.esaal_branding && esaal_branding_ui){
                                    esaal_branding_ui.style.display = 'block';
                                    if (this.pos.esaal_branding_qr && esaal_branding_qr_ui){
                                        esaal_branding_qr_ui.style.display = 'block';
                                    }
                                }
                            }
                            partnerPhoneInput.value = formattedPhone || partnerPhone || '' ;
                            genderMaleInput.checked = true;
                            if (!partnerPhone){ // if no phone then it wont auto validate anyway
                                partnerNameInput.value = partnerName;
                                partnerEmailInput.value = partnerEmail || '';
                            }
                            if (!this.pos.esaal_auto_send){
                                partnerNameInput.value = partnerName || '';
                                partnerEmailInput.value = partnerEmail  || '';
                            }
                        } else {
                            // Elements not initialized, wait and check again
                            setTimeout(checkElementsInitialized, 1000); // Check again after 100ms
                        }
                    };            
        
                    const auto_print_esaal = async () => {
                        self.esaal_printed = true
                        // Check if customer exists
                        const validate_api = await rpc.query({
                            model: 'pos.order',
                            method: 'validate_api',
                            args: [partnerName, formattedPhone],
                        });
                        const [esaalId, firstName, lastName, phone, email] = validate_api;
                
                        if (validate_api && esaalId && esaalId.length == 6) {
                            var esaal_name = `${firstName} ${lastName || ''}`;
                            document.getElementById('esaal-partner-name').value = esaal_name;
                            document.getElementById('esaal-partner-phone').value = phone;
                            document.getElementById('esaal-partner-email').value = email || '';
        
                            // Auto print the receipt
                            const esaal_auto_print = await rpc.query({
                                model: 'pos.order',
                                method: 'print_receipt_Esaal',
                                args: [esaal_name, esaalId, "AutoPrint", "placeholder"],
                            });
                            if (!esaal_auto_print.success && esaal_auto_print.type == "AutoPrintErr") {
                                Gui.showPopup('ErrorPopup', {
                                    title: 'Esaal',
                                    body: 'Esaal PoS not configured in settings.',
                                });
                            } else if (!esaal_auto_print.success && esaal_auto_print.type == "MerErr") {
                                Gui.showPopup('ErrorPopup', {
                                    title: 'Esaal',
                                    body: 'Esaal PoS not configured in settings.',
                                });
                            } else if (!esaal_auto_print.success && esaal_auto_print.type == "receipt_data") {
                                Gui.showPopup('ErrorPopup', {
                                    title: 'Esaal',
                                    body: 'Failed to read receipt items.',
                                });
                            } else if (!esaal_auto_print.success && esaal_auto_print.type == "mapper_not_found") {
                                esaal_enabled = false;
                                document.getElementById('esaal-partner-info').esaal_ui.style.display = 'none';
                            } else if (esaal_auto_print && esaal_auto_print.success) {
                                document.getElementById('Esaal_print').style.display = 'none';
                                document.getElementById('esaal-partner-name').readOnly = true;
                                document.getElementById('esaal-partner-phone').readOnly = true;
                                document.getElementById('esaal-partner-email').readOnly = true;
                                document.getElementById('esaal-partner-name').value = esaal_name;
                                document.getElementById('esaal-partner-email').value = email || partnerEmail || '';
                                Gui.showPopup('ConfirmPopup', {
                                    title: 'Esaal',
                                    body: 'Receipt has been sent to existing Esaal Customer ' + esaal_name + ' at ' + phone,
                                });
                            } else if (!esaal_auto_print.success && esaal_auto_print.type == "AuthErr") {
                                Gui.showPopup('ErrorPopup', {
                                    title: 'Esaal',
                                    body: 'Authorization Error: Unauthorized access',
                                });
                            } else if (!esaal_auto_print.success && esaal_auto_print.type == "invalid") {
                                Gui.showPopup('ErrorPopup', {
                                    title: 'Esaal',
                                    body: 'Invalid phone number provided',
                                });
                            } else {
                                Gui.showPopup('ErrorPopup', {
                                    title: 'Esaal',
                                    body: 'Failed to send the receipt.',
                                });
                            }
                            self.esaal_printed = false
                        } else {
                            self.esaal_printed = false
                            document.getElementById('esaal-partner-name').value = partnerName || '';
                        }
                    };
        
                    // Adjust phone number
                    regexPhone();
        
                    // Check PoS Registration, Auto send config, regex phone and didn't run before
                    // TODO: add auto_Send toggle
                    if (esaal_enabled && this.pos.esaal_auto_send && formattedPhone && !self.esaal_printed) {
                        auto_print_esaal();
                    } else {
                        // No auto entry
                    }
        
                    // Check UI
                    checkElementsInitialized();
                }
            }

            // Check State
            update_state();
    
            return result;
        }
    };

    const CustomPosGlobalState = (PosGlobalState) => class CustomPosGlobalState extends PosGlobalState {
        async _processData(loadedData) {
            await super._processData(...arguments);

            const esaalCustomerInfo = await rpc.query({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['esaal_hook.esaal_customer_info'],
            });
            this.esaal_customer_info = esaalCustomerInfo === 'True';

            const esaalRegistration = await rpc.query({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['esaal_hook.esaal_registered'],
            });
            this.esaal_registration_info = esaalRegistration === 'True';

            const esaalAutoPrint = await rpc.query({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['esaal_hook.esaal_auto_send'],
            });
            this.esaal_auto_send = esaalAutoPrint === 'True';

            const esaalMapperMode = await rpc.query({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['esaal_hook.esaal_mapper_mode'],
            });
            this.esaal_mapper_mode = esaalMapperMode === 'True';

            const esaalMapperState = await rpc.query({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['esaal_hook.esaal_mapper_state'],
            });
            this.esaal_mapper_state = esaalMapperState === 'True';

            const esaalBranding = await rpc.query({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['esaal_hook.esaal_branding'],
            });
            this.esaal_branding = esaalBranding === 'True';

            const esaalBrandingQR = await rpc.query({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['esaal_hook.esaal_branding_qr'],
            });
            this.esaal_branding_qr = esaalBrandingQR === 'True';
        }
    };

    const EsaalReceiptScreen = ReceiptScreen =>
        class extends ReceiptScreen {
            async printEsaal() {
                const partnerName = document.getElementById('esaal-partner-name').value;
                let partnerPhone = document.getElementById('esaal-partner-phone').value;
                let partnerEmail = document.getElementById('esaal-partner-email').value || '';
                const gender = document.querySelector('input[name="gender"]:checked').value;

                if (!partnerName || partnerName == " " || partnerName == "Customer Name") {
                    Gui.showPopup('ErrorPopup', {
                        title: 'Esaal',
                        body: 'Please enter Customer Name.',
                    });
                    return;
                }

                function validate(partnerName, partnerPhone, partnerEmail) {
                    // Regular expressions
                    const phoneRegex = /^(0[0-9]{9}|\+971[0-9]{9})$/;
                    const emailRegex = /^\S+@\S+\.\S+$/; //anything@anything.anything
                    const nameRegex = /^[a-zA-Z]+( [a-zA-Z]+)?$/; // FirstName or FirstName SecondName
                    const fnameRegex = /^[a-zA-Z]+$/; // FirstName only
                
                    // Validate name
                    if (!nameRegex.test(partnerName)) {
                        if (!fnameRegex.test(partnerName)) {
                            Gui.showPopup('ErrorPopup', {
                                title: 'Invalid Name',
                                body: 'Please check name (firstName lastName or firstName only).',
                            });
                            document.getElementById('esaal-partner-name').focus();
                            return false;
                        }
                    }
                
                    // Validate phone number
                    if (!phoneRegex.test(partnerPhone) || !partnerPhone) {
                        Gui.showPopup('ErrorPopup', {
                            title: 'Invalid Phone Number',
                            body: 'Please enter a valid UAE phone number (0501234567 or +971501234567).',
                        });
                        document.getElementById('esaal-partner-phone').focus();
                        return false;
                    }
                
                    // Validate email
                    if (partnerEmail && !emailRegex.test(partnerEmail)) {
                        Gui.showPopup('ErrorPopup', {
                            title: 'Invalid Email format',
                            body: 'Please enter a valid email address or leave it empty.',
                        });
                        document.getElementById('esaal-partner-email').focus();
                        return false;
                    }
                
                    // All validations passed
                    return true;
                }

                if (validate(partnerName, partnerPhone, partnerEmail)) {
                    var self = this;
                    const { confirmed, payload } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Esaal'),
                        body: this.env._t('Process Esaal Receipt for Customer : ' + partnerName + " at " + partnerPhone),
                    });
                    if (confirmed) {
                        console.log(payload, 'payload')
                        const result = await rpc.query({
                            model: 'pos.order',
                            method: 'print_receipt_Esaal',
                            args: [partnerName, partnerPhone, gender, partnerEmail],
                        });
    
                        if (!result.success && result.type == "MerErr") {
                            Gui.showPopup('ErrorPopup', {
                                title: 'Esaal',
                                body: 'Esaal PoS not configured in settings.',
                            });
                        } else if (!result.success && result.type == "receipt_data") {
                            Gui.showPopup('ErrorPopup', {
                                title: 'Esaal',
                                body: 'Failed to read receipt items.',
                            });
                        } else if (!result.success && result.type == "mapper_not_found") {
                            self.esaal_enabled = false;
                            esaal_ui.style.display = 'none';
                        } else if (result && result.success) {
                            document.getElementById('Esaal_print').style.display = 'none';
                            document.getElementById('esaal-partner-name').readOnly = true;
                            document.getElementById('esaal-partner-phone').readOnly = true;
                            document.getElementById('esaal-partner-email').readOnly = true;
                            Gui.showPopup('ConfirmPopup', {
                                title: 'Esaal',
                                body: 'Receipt has been sent to Esaal Customer ' + partnerName + ' at ' + partnerPhone,
                            });
                        } else if (!result.success && result.type == "AuthErr") {
                            Gui.showPopup('ErrorPopup', {
                                title: 'Esaal',
                                body: 'Authorization Error: Unauthorized access',
                            });
                        } else if (!result.success && result.type == "invalid") {
                            Gui.showPopup('ErrorPopup', {
                                title: 'Esaal',
                                body: 'Invalid phone number provided. +971xx or 05xx allowed.',
                            });
                        } else {
                            Gui.showPopup('ErrorPopup', {
                                title: 'Esaal',
                                body: 'Failed to send the receipt.',
                            });
                        }
                    }
                } else {
                    console.log('Validation failed');
                }
            }    

            mounted() {
                super.mounted();
            }
        };

    Registries.Model.extend(PosGlobalState, CustomPosGlobalState);
    Registries.Model.extend(Order, CustomOrder);
    Registries.Component.extend(ReceiptScreen, EsaalReceiptScreen);

    return CustomPosGlobalState, CustomOrder;
});
