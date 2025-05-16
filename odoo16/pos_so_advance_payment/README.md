# Create Sale Order, Delivery Address, Advance Payment from POS

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Issues & Bugs
- Development
- Tests
- Dependencies

---

## Features

- This module allows the cashier to create Quotation/Sales Order directly from POS, collect Delivery Address of the customer and Register Advance Payment from POS.

---

## Configuration

- Under Main menu Point of Sale > Dashboard > Particular Card -> Select 3 dots -> Edit, you need to enable 'Enable Creating SO from POS' boolean from POS Config.
- Under Configuration, you can select the state which you want the SO to create and also enable the advance payment collection if needed.
- In the Main POS screen, user will see a new button "Create Quotation". Cashier can click on it if incase he wants to register a Quotation/SO in backend for the current order from the POS.
- Upon clicking the Create Quotation Button on the Main POS Screen, a POP up will appear for Selecting or Creating a New Delivery Address.
- The Existing Delivery Address will display the Parent Partner's Existing Delivery Address
- Cashier can directly collect advance payment from the customer from the POS screen.
User can also select the appropriate Journal from the available list.


---

## Dependencies

### Odoo modules dependencies

| Module         | Why used?                          | Side effects
|----------------|------------------------------------|--------------|
| Point of Sale  | To use feature of POS              |              |
| Sales          | To create Sale Order from the POS  |              |

### Python library dependencies

The module doesn't require any external Python library

---

## Limitations, Issues & Bugs

The module doesn't require any Limitations, Issues & Bugs

---

