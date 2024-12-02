# Copyright (c) 2017 Emipro Technologies Pvt Ltd (www.emiprotechnologies.com). All rights reserved.
from odoo import models, fields, api
from odoo.exceptions import Warning,ValidationError
from odoo.addons.fedex_shipping_ept.fedex.base_service import FedexError, FedexFailure
from odoo.addons.fedex_shipping_ept.fedex.config import FedexConfig
from odoo.addons.fedex_shipping_ept.fedex.services.availability_commitment_service import FedexAvailabilityCommitmentRequest
from odoo.addons.fedex_shipping_ept.fedex.tools.conversion import basic_sobject_to_dict

class ShippingInstanceEpt(models.Model):
    _inherit = "shipping.instance.ept"
    
    provider = fields.Selection(selection_add=[('fedex_ept', 'Fedex')])
    use_address_validation_service = fields.Boolean(copy=False,string="Use Address Validation Service", help="Use Address Validation service to identify residential area or not.\nTo use address validation services, client need to request fedex to enable this service for his account.By default, The service is disable and you will receive authentication failed.")
    fedex_key = fields.Char(string="Developer Key", help="Developer key",copy=False)
    fedex_password = fields.Char(copy=False,string='Password', help="The Fedex-generated password for your Web Systems account. This is generally emailed to you after registration.")
    fedex_account_number = fields.Char(copy=False,string='Account Number', help="The account number sent to you by Fedex after registering for Web Services.")
    fedex_meter_number = fields.Char(copy=False,string='Meter Number', help="The meter number sent to you by Fedex after registering for Web Services.")
    fedex_integration_id = fields.Char(copy=False,string='Integration ID', help="The integrator string sent to you by Fedex after registering for Web Services.")

    @api.model
    def get_fedex_api_object(self, prod_environment=False):
        return FedexConfig(key = self.fedex_key,
                password = self.fedex_password,
                account_number = self.fedex_account_number,
                meter_number = self.fedex_meter_number,
                integrator_id=self.fedex_integration_id,
                use_test_server = not prod_environment)

    @api.one
    def fedex_ept_retrive_shipping_services(self, to_address):
        """ Retrive Availability and Commitment Services from the Fedex
            @param to_address: recordset of fetch.services.wizard.ept
            @return: True
            @author: Jignesh Jarsaniya on dated 30-March-2017
        """
        shipping_services_obj = self.env['shipping.services.ept']
        services = shipping_services_obj.search([('shipping_instance_id','=',self.id)])
        services.unlink()
        for company in self.company_ids :
            try :
                FedexConfig = self.get_fedex_api_object(prod_environment=False)
                availability_request = FedexAvailabilityCommitmentRequest(FedexConfig)
                availability_request.Origin.PostalCode = company.zip
                availability_request.Origin.CountryCode = company.country_id and company.country_id.code or None
                if to_address.use_toaddress_different:
                    availability_request.Destination.PostalCode = to_address.to_zip
                    availability_request.Destination.CountryCode = to_address.to_country_id and to_address.to_country_id.code or None
                else :
                    availability_request.Destination.PostalCode = company.zip
                    availability_request.Destination.CountryCode = company.country_id and company.country_id.code or None
                availability_request.send_request()
                response = basic_sobject_to_dict(availability_request.response)
            except FedexError as ERROR:
                raise ValidationError(ERROR.value)
            except FedexFailure as ERROR:
                raise ValidationError(ERROR.value)
            except Exception as e:
                raise ValidationError(e)

            shipping_service = ["EUROPE_FIRST_INTERNATIONAL_PRIORITY", "FEDEX_2_DAY", "FEDEX_2_DAY_AM",
                                "FEDEX_DISTANCE_DEFERRED", "FEDEX_EXPRESS_SAVER", "FEDEX_GROUND",
                                "FEDEX_NEXT_DAY_AFTERNOON", "FEDEX_NEXT_DAY_EARLY_MORNING", "FEDEX_NEXT_DAY_END_OF_DAY",
                                "FEDEX_NEXT_DAY_FREIGHT", "FEDEX_NEXT_DAY_MID_MORNING", "FIRST_OVERNIGHT",
                                "GROUND_HOME_DELIVERY", "INTERNATIONAL_ECONOMY", "INTERNATIONAL_FIRST",
                                "INTERNATIONAL_PRIORITY", "PRIORITY_OVERNIGHT",
                                "SMART_POST", "STANDARD_OVERNIGHT"]
            if response.get('Options') :
                for service in response.get('Options') :
                    service_code = service.get('Service',False)
                    if service_code and service_code in shipping_service :
                        service_id = shipping_services_obj.search([('service_code','=',service_code),('shipping_instance_id','=',self.id)])
                        if service_id :
                            if company.id not in service_id.company_ids.ids :
                                service_id.write({'company_ids' : [(4, company.id)]})
                        else :
                            name = service_code.replace('_',' ').capitalize()
                            shipping_services_obj.create({'service_code' : service_code, 'service_name' : name, 'shipping_instance_id' : self.id, 'company_ids' : [(4, company.id)]})
            else:
                raise Warning("There is no shipping service available!")
        return True
    
    @api.model
    def fedex_ept_quick_add_shipping_services(self, service_code, service_type):
        """ Allow you to get the default shipping services value while creating quick 
            record from the Shipping Service for Fedex
            @param service_type: Service type of Fedex
            @return: dict of default value
            @author: Jignesh Jarsaniya on dated 31-March-2017
        """
        return {'default_fedex_service_type' : service_code}
