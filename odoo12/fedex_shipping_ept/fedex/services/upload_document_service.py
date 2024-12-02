"""
Ship Service Module

This package contains the shipping methods defined by Fedex's 
ShipService WSDL file. Each is encapsulated in a class for easy access. 
For more details on each, refer to the respective class's documentation.
"""

import datetime
from ..base_service import FedexBaseService


class FedexProcessUploadDocumentRequest(FedexBaseService):
    """
    This class allows you to process (create) a new FedEx shipment. You will
    need to populate the data structures in self.RequestedShipment, then
    send the request. Label printing is supported and very configurable,
    returning an ASCII representation with the response as well.
    """

    def __init__(self, config_obj, *args, **kwargs):
        """
        The optional keyword args detailed on L{FedexBaseService} 
        apply here as well.

        @type config_obj: L{FedexConfig}
        @param config_obj: A valid FedexConfig object.        
        """

        self._config_obj = config_obj
        # Holds version info for the VersionId SOAP object.
        self._version_info = {
            'service_id': 'ship',
            'major': '17',
            'intermediate': '0',
            'minor': '0'
        }
        self.RequestedShipment = None
        """@ivar: Holds the RequestedShipment WSDL object."""
        # Call the parent FedexBaseService class for basic setup work.
        super(FedexProcessUploadDocumentRequest, self).__init__(
                self._config_obj, 'UploadDocumentService_v11.wsdl', *args, **kwargs)

    def _prepare_wsdl_objects(self):
        """
        This is the data that will be used to create your shipment. Create
        the data structure and get it ready for the WSDL request.
        """

        # This is the primary data structure for processShipment requests.
        self.RequestedShipment = self.client.factory.create('UploadDocumentsRequest')


        #self.send_request(send_function=self._assemble_and_send_UploadDocuments_request)

    def _assemble_and_send_request(self):
        """
        Fires off the Fedex shipment validation request.
        
        @warning: NEVER CALL THIS METHOD DIRECTLY. CALL 
            send_validation_request(), WHICH RESIDES ON FedexBaseService 
            AND IS INHERITED.
        """

        # Fire off the query.
        return self.client.service.uploadDocuments(
                WebAuthenticationDetail=self.WebAuthenticationDetail,
                ClientDetail=self.ClientDetail,
                TransactionDetail=self.TransactionDetail,
                Version=self.VersionId,
                RequestedShipment=self.RequestedShipment
)

