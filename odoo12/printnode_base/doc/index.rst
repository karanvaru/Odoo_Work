Odoo Direct Print module
========================

|

**We moved our documentation to the https://print.ventor.tech/docs**

Please, follow above link for up-to-date doc.

|

Change Log
##########

|

* 2.1.6 (2022-02-23)
    - Convert print job ID to text (to provide compatibility with 64 bits PrintNode IDs)

* 2.1.5 (2021-12-31)
    - Improve scenario "Print Picking Document after Sales Order Confirmation" to print only Ready Picking
    - Add "Printed/Not Printed" filters to supported models
    - Fix synchronization with DPC/PrintNode: update computer or printer names when they changed
    - Fix printing multiple ZPL labels: it only printed the first label from all labels
    - Add Rate Us link to status menu

* 2.1.4 (2021-12-01)
    - Fixed issue with access rights for "ir.model" model

* 2.1.3 (2021-11-24)
    - Fixed compatibility with OCA report_xlsx module
    - Added standard Odoo icon to all company specific options
    - Fixed error when save settings with empty API Key
    - Added special method to print attachments from the Ventor app
    - Added new demo scenario to print report for all outgoing transfers (after validation)
    - Added auto disable the "Print Package just after Shipping Label" setting with warning if the user disables the "Packages" setting
    - Added notifications about new releases

* 2.1.2 (2021-10-07)
    - Removed redundant report to print Pricelist from Product Label Print wizard

* 2.1.1 (2021-10-04)
    - Added Print Scenario to print Invoice document after it is Validated (Posted)

* 2.1.0 (2021-09-24)
    - Added Scales integration during 'Put In Pack' action on Delivery Order (to send proper weight to Carrier)
    - Improved compatability with Odoo Native Mobile App
    - (Beta) Added Support for py3o (OCA module) generated reports (ONLY PDF)

* 2.0.1 (2021-09-17)
    - Fixed issue with auto-printing of the complex reports (e.g. POS Sales Reports)

* 2.0.0 (2021-09-13)
    - Add support of Direct Print Client platform

* 1.9.4 (2021-09-02)
    - Fix issue with SO and PO not returning actions on Confirmation

* 1.9.3 (2021-08-23)
    - Added "Print Scenario" to print document after Purchase order confirmation
    - Added "Print Scenario" to print "Receipt Document" after Purchase Order Validation

* 1.9.2 (2021-08-13)
    - Added possibility to exclude particular report from printing in "Print Settings"

* 1.9.1 (2021-07-29)
    - Fixed error in module installation with other modules that are changing user's form view
    - Fixed regression issue with impossibility to quick print product label via wizard
    - Fixed issue with debug mode not properly working

* 1.9.0 (2021-07-27)
    - Download Printer Bins Information (Paper Trays).
    - Allow to define Printer Bin (Tray) to be used in all places (Print Actions, Print Scenarios, User Rules)
    - When deleting account - delete all related objects (Computers, Printers, Print Jobs, User Rules, Printer Bins)

* 1.8.1 (2021-07-20)
    - Switching off "Print via Printnode" on user or company also should switch off auto-printing of shipping label on DO Validation

* 1.8.0 (2021-07-14)
    - Added possibility to print Package Document together with the Shipping Label
    - Added Print Scenario to Print all Packages after Transfer Validation

* 1.7.3 (2021-07-13)
    - Fix issue with auto-test for purchase order flow and user access rights

* 1.7.2 (2021-07-08)
    - Fix issue with printing multiple documents using scenarios with the same action

* 1.7.1 (2021-06-30)
    - Fix issue with automatic Shipping Label printing from attachments via "Print Last Shipping Label" button on Delivery Order
    - Adding possibility to enable debug logging on the account to log requests that are sent to PrintNode (needed to communicate with support)

* 1.7 (2021-06-14)
    - When automatic printing is enabled in User Preferences, display near "Print" menu new dropdown "Download" that will allow to Download reports as in Odoo standard.

* 1.6.3 (2021-06-08)
    - Method _create_backorder() must return a recordset like the original method does, so that other modules could extend it as well.

* 1.6.2 (2021-06-05)
    - Fixed issue with download of printers when there is big amount of printers in Printnode account.
    - When deleting account also delete inactive computers and printers

* 1.6.1 (2021-05-31)
    - Fixed issue that makes module incompatible with modules redefining Controller for report download (e.g. report_xlsx).

* 1.6 (2021-04-16)
    - Added  possibility to define Universal Print Attachments Wizard for any model in the Odoo.
    - (Experimental) Added settings to allow auto-printing of shipping labels from attachments. To support shipping carriers implemented not according to Odoo standards.
    - Fix printing error when sending to PrintNode many documents at the same time.

* 1.5.2 (2021-03-26)
    - Added print scenarios to print "Lot labels" or "Product Labels" in real time when receiving items.
      It allows either to print single label (to stick on box) OR multiple labels equal to quantity of received items

* 1.5.1 (2021-03-13)
    - Fixed an issue with Report Download controller interruption
    - Fixed an issue with printing document with scenarios for different report model

* 1.5 (2021-02-25)
    - Removed warning with Unit tests when installing module on Odoo.sh.
    - Added new scenario: print product labels for validated transfers.
    - Added new scenario: print picking document after sale order confirmation.

* 1.4.2 (2021-01-13)
    - Added possibility to view the number of prints consumed from the printnode account (experimental).

* 1.4.1 (2021-01-12)
    - Updating the "printed" flag on stock.picking model after Print Scenario execution.

* 1.4 (2020-12-21)
    - Added possibility to define number of copies to be printed in "Print Action Button" menu.
    - Added Print Scenarios which allows to print reports on pre-programmed actions.

* 1.3.1 (2020-11-10)
    - Added constraints not to allow creation of not valid "Print Action Buttons" and "Methods".
    - On product label printing wizard pre-select printer in case only 1 suitable was found.

* 1.3 (2020-10-09)
    - Added possibility to print product labels while processing Incoming Shipment into your Warehouse.
      Also you can mass print product labels directly from individual product or product list.
    - Show info message on User Preferences in case there are User Rules that can redefine Default user Printer.
    - Added examples to Print Action menu for some typical use cases for Delivery Order and Sales Order printing.

* 1.2.1 (2020-10-07)
    - When direct-printing via Print menu, there is popup message informing user about successful printing.
      Now this message can be disabled via Settings.
    - Fixed issue with wrong Delivery Slip printing, after backorder creation.

* 1.2 (2020-07-28)
    -  Make Printer non-required in "Print action buttons" menu. If not defined, than printer will be selected
       based on user or company printer setting.
    -  Added Support for Odoo Enterprise Barcode Interface. Now it is compatible with "Print action buttons" menu.
    -  "Print action buttons" menu now allows to select filter for records, where reports should be auto-printed.
       E.g. Print Delivery Slip only for Pickings of Type = Delivery Order.

* 1.1 (2020-07-24)
    -  Added Support for automatic/manual printing of Shipping Labels.
       Supporting all Odoo Enterprise included Delivery Carries (FedEx, USPS, UPS, bpost and etc.).
       Also Supporting all custom carrier integration modules that are written according to Odoo Standards.

* 1.0 (2020-07-20)
    - Initial version providing robust integration of Odoo with PrintNode for automatic printing.

|

