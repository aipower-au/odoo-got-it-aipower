# SPRINT 1 - REQUIREMENTS

## 1. Customer/Merchant/Supplier Management

- Check duplicate Tax ID (MST)
- Salesperson assignment
    + Auto assign Sales user according to rules. No Tax ID: assign user (Telesale) -> Sale verify (Tele/Meeting) -> Convert (Sale)
    + Check duplicate contact information (Phone, email), Tax ID, constraint to same Sales person in charge
    + Bulk change salesperson for customers
- Update customer information by Tax ID.
    + Connect to third party service, retrieve detailed customer information by Tax ID.
- Customer (status: client, lost): Automatically change status from "Potential" to "Client". Status change timing: when account creation is completed
- Information management:
    + Terms
    + Entity
    + Customer code
    + Display list of contracts for that customer
    + Quotation
    + Purchase revenue
    + Sales policy
    + Invoice account information (one or multiple accounts)
    + Company group (customer group, key group information from both subsidiary and parent company to be able to check from both ends.)
    + Delivery address
- Migrate old data into system
- Receive customer data from multiple sources (Web/Hotline) to create in system

## 2. Lead Management

- Add lead caretaker information field when this lead's customer and sales have not been identified yet. When identified, return the lead to the Sales person in charge of that customer.
- Auto assign leads according to Gotit rules (by region; value; lead priority order). Distribute by (1) INDUSTRY GROUP, (2) REGION, (3) CUSTOMER TYPE (4) ORDER VALUE.
    + This rule set will change at different times.
- Have alert system for duplicate leads or duplicate data compared to Dayone's existing customer information
- Notification when assigned a Lead
- Bulk change salesperson for leads
- Migrate old data into system
- Websites call API to create leads in system

## 3. Opportunity Management

- Migrate old data into system

## 4. Product Management

- Product information on Fast is general information: edit according to template saved in FAST
- Suitable for sales order export part of SO System.
- Product discount, 1 product can have multiple selling prices depending on different programs
- Product classification: create invoice/receipt; additional product information, discount
- Custom physical gift: check inventory, reconcile difference between selling price and cost price, support controller in approving code export price
- CCS (set up messages)
- Migrate old data into system

## 5. Task Management

- Create task on CRM: assign to relevant departments

## 6. Discussion

- Use odoo's discussion module to communicate with each other directly on the system.
