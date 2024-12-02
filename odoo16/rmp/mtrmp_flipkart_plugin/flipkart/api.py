# -*- coding: utf-8 -*-
import json
import logging
from urllib.parse import urlencode
from functools import partial

import requests


class FlipkartAPI(object):
    """
    Flipkart Marketplace Seller API Client.

    This client provides access to flipkart objects (orders, skus) in a generic
    way.

    You can read more about `Flipkart Marketplace API here
    <https://seller.flipkart.com/api-docs/FMSAPI.html>`_

    :param access_token: Access token received at the end of an Authorization
                         Code Flow or Client Credentials Flow.
    :param sandbox: True/False to connect to sandbox or not (Default: connects
                    to production)
    :param debug: If enabled, spits out debug logs.

    Example::

        from flipkart import FlipkartAPI
        flipkart = FlipkartAPI(access_token='your_access_token')

    """
    def __init__(self, access_token, sandbox=False, debug=False):
        self.access_token = access_token
        self.sandbox = sandbox
        self.debug = debug

        self.session = self.get_session()
        self.logger = self.get_logger()

    def get_session(self):
        """
        Build a requests session that can be used to hold
        the authorization
        """
        session = requests.Session()
        session.headers.update({
            'Authorization': 'Bearer %s' % self.access_token,
            'Content-type': 'application/json',
        })
        return session

    def get_logger(self):
        """
        Return a logger
        """
        logger = logging.getLogger('flipkart')
        logger.setLevel(logging.DEBUG if self.debug else logging.INFO)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG if self.debug else logging.INFO)
        logger.addHandler(ch)

        return logger

    def build_url(self, path, params=None):
        """
        Given a path construct the full URL for sandbox or production

        :param params: Should be a list of key value pairs or dictionary
        """
        if path.startswith('/'):
            path = path[1:]

        if params is not None:
            path += '?' + urlencode(params)

        if self.sandbox:
            return 'https://sandbox-api.flipkart.net/sellers/' + path
        else:
            return 'https://api.flipkart.net/sellers/' + path

    def request(
            self, path, params=None, body=None, method="GET",
            process_response=True):
        """
        Makes a request and sends the response body back.

        :param process_response: Parse JSON from the response and raise errors
                                 if any in the response from flipkart.
        """
        url = self.build_url(path, params)
        self.logger.debug("Request:URL: %s", url)
        self.logger.debug("Request:Method: %s", method)

        if body is not None:
            payload = json.dumps(body)
        else:
            payload = None

        self.logger.debug("Request:Payload: %s", payload)

        if method == 'GET':
            response = self.session.get(url, data=payload, verify=False)
        elif method == 'POST':
            response = self.session.post(url, data=payload, verify=False)
        else:
            raise ValueError('Unknown method %s' % method)

        self.logger.debug("Response:code: %s", response.status_code)
        self.logger.debug("Response:content: %s", response.content)

        if process_response is False:
            # Don't process the response
            return response

        # Raise an error if the response is not 2XX
        response.raise_for_status()

        response_json = response.json()

        if response_json.get('status') == 'failure':
            raise FlipkartMultiError(response_json['response']['errors'])

        return response_json

    def sku(self, sku_id, fsn=None):
        """
        Get a SKU
        """
        return SKU(sku_id, self, fsn)

    def listing(self, listing_id):
        """
        Get a listing
        """
        return Listing(listing_id, sku=None, client=self, lazy=False)

    def bulk_listing(self, listings):
        """
        Create and update listing attributes such as stock, price, and
        procurement SLA for multiple SKUs. A maximum of 10 listings can be
        updated.
        """
        raise Exception('Not implemented yet')

    def search_orders(self, filters=None, page_size=None, sort=None):
        """
        Search through the orders
        """
        return OrderItem.search(self, filters, page_size, sort)

    def order_item(self, order_item_id):
        """
        Fetch a specific order item
        """
        return OrderItem(order_item_id, self)

    def order_items(self, *order_item_ids):
        """
        Fetch multiple order items
        """
        return OrderItem.get_many(self, order_item_ids)

    def label_request(self, label_request_id):
        """
        Get the Label object corresponding to a request id
        """
        return LabelRequest(label_request_id, self)

    def create_test_orders(self, *orders):
        """
        Flipkart provides a convenient API to create test orders on sandbox.

        Returns a list of order_item objects.

        Example::

            flipkart.create_test_orders(
                # Listing ID, quantity
                ('listing_id_1', 2),
                ('listing_id_2', 4),
            )

        :param orders: list of pair of listing and quantity
        """
        assert self.sandbox, "You must be on sandbox to use create_test_orders"

        body = {'orders': []}
        for listing, quantity in orders:
            if isinstance(listing, Listing):
                listing = listing.listing_id
            body['orders'].append({
                'listing_id': listing,
                'quantity': quantity
            })
        response = self.request(
            'orders/test/create_orders', method="POST", body=body
        )
        return map(self.order_item, response['orderItemIds'])


class BaseFlipkartError(Exception):
    """
    Base class for all flipkart exceptions
    """
    pass


class FlipkartError(BaseFlipkartError):
    """
    Base class for Flipkart exceptions
    """
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super(FlipkartError, self).__init__(code, message)


class FlipkartMultiError(BaseFlipkartError):
    """
    An API request could result in multiple errors. This abstracts away the
    detail by showing multiple errors
    """
    def __init__(self, errors):
        self.errors = []
        for error in errors:
            self.errors.append(
                FlipkartError(error['errorCode'], error['message'])
            )
        super(FlipkartMultiError, self).__init__(
            '%d errors in request\n' % len(self.errors) + '\n'.join([
                'ERR::%s: %s' % error.args for error in self.errors
            ])
        )


class FlipkartCollection(object):
    """
    Common parent class for collections like orders
    """
    pass


class FlipkartResource(object):
    """
    Common parent class for flikart resources like SKUs, listing etc
    """
    pass


class SKU(FlipkartResource):
    """
    Represents a SKU ientified by a SKU ID.

    :param sku_id: ID of the SKU
    :param client: The client connection the SKU will use to fetch and update
    """
    def __init__(self, sku_id, client, fsn=None):
        self.sku_id = sku_id
        self.client = client
        self.fsn = fsn

    def create_listing(self, **attributes):
        """
        Creates a listing for the SKU with the given attributes. The listing
        is not saved and must be explicitly saved by the user.

        Example::

            new_listing = sku.create_listing(
                mrp=100
            )
            new_listing.save()
        """
        return Listing(
            listing_id=None, client=self.client,
            sku=self, attributes=attributes
        )

    @property
    def listings(self):
        """
        Return a list of listings, but it seems like flipkart allows only
        one listing per seller. So this should usually return just one listing.
        However, to keep the API consistent, this will return a list
        """
        response = self.client.request(
            'skus/%s/listings' % self.sku_id,
        )
        return [
            Listing(
                response['listingId'],
                self, self.client,
                attributes=response['attributeValues']
            )
        ]

    @property
    def listing(self):
        """
        Return the listing of the product
        """
        listings = self.listings
        return listings[0] if listings else None


class OrderItem(FlipkartResource):
    """
    Represents an order item with ID order_item_id.
    An order represented by OrderId could have items from multiple sellers
    and the seller only has access to order_item_id(s).
    """

    def __init__(self, order_item_id, client, attributes=None):
        self.order_item_id = order_item_id
        self.attributes = attributes
        self.client = client

        if self.order_item_id and self.attributes is None:
            self.refresh_attributes()

    @property
    def listing(self):
        """
        Return the listing object corresponding to the order
        """
        return self.client.listing(
            self.attributes['listingId'],
            self.attributes['sku']
        )

    @property
    def sku(self):
        """
        Return the SKU object
        """
        return self.client.sku(
            self.attributes['sku'], self.attributes['fsn']
        )

    @property
    def sub_items(self):
        """
        Return sub items of an order
        """
        return [
            self.__class__(
                subitem['orderItemId'], self.client, subitem
            ) for subitem in self.attributes.get('subItems')
        ]

    def refresh_attributes(self):
        """
        Fetch the order attributes from flipkart
        """
        response = self.client.request(
            'orders/%s' % self.order_item_id
        )
        self.attributes = response

    @classmethod
    def get_many(cls, client, order_item_ids):
        """
        Get multiple order items at once
        """
        response = client.request(
            'orders', params={'orderItemIds': ','.join(order_item_ids)}
        )
        return [
            cls(order_item['orderItemId'], client, order_item)
            for order_item in response
        ]

    @classmethod
    def search(cls, client, filters=None, page_size=None, sort=None):
        """
        Search for orders that meet the criteria.

        :param sort: A tuple of field and sort order Ex: `('orderDate', 'asc')`
        """
        body = {
            'filter': filters or {},
        }

        if page_size is not None:
            body['pagination'] = {
                'pageSize': page_size
            }

        if sort is not None:
            body['sort'] = {
                'field': sort[0],
                'order': sort[1],
            }

        response = client.request(
            'v2/orders/search',
            body=body,
            method="POST"
        )
        return PaginationIterator(
            client, response,
            'orderItems',
            lambda item: partial(cls, client=client)(
                item['orderItemId'], attributes=item
            )
        )

    def generate_label(
            self, invoice_date, invoice_number, serial_numbers=None,
            tax=None, sub_items=None):
        """
        marks orders as packed and creates a labelRequest for multiple
        order items. It takes the invoice details in the request as input.
        If the orderItemId requires a serial number or IMEI number (also
        known as serialized product), that input is also required when calling
        this API.

        :param invoice_date: datetime.Date object for invoice date
        :param invoice_number: string representing invoice number
        :param serial_number: See note below
        :param tax: Amount of tax
        :param sub_items: List of dictionary, See not below

        .. note::

            While the first level order item information is encoded from the
            arguments passed to this method, sub_items must be manually
            constructed by the user. A list of dictionary like in the example
            should be sufficient.

        .. note::

            Specifying serial numbers is tricky. It is trickiest for mobile
            phones that have multiple sim support and hence multiple IMEIs.
            here is a rough idea on how to construct one::

                serial_numbers = []
                for each_unit in quantity:
                    unit_imeis = [unit1_sim1_imei, unit1_sim2_imei]
                    serial_numbers.append(unit_imeis)

            If a customer bought two dual sim phones::

                [
                    [unit1_sim1_imei, unit1_sim2_imei],
                    [unit2_sim1_imei, unit2_sim2_imei],
                ]

        """
        if serial_numbers is None:
            serial_numbers = []
        data = {
            "orderItemId": self.order_item_id,  # Order item ID,
            "serialNumbers": serial_numbers,
            "invoiceDate": invoice_date.isoformat(),
            "invoiceNumber": invoice_number,
            "tax": tax,
            "subItems": [],
        }
        if sub_items is not None:
            data['subItems'] = sub_items

        # Unlike other APIs this one is awkward. Expects you to look into
        # the response header for a Location header and then get the
        # label request ID from it. Yucks!
        response = self.client.request(
            'orders/labels', body=[data],
            method='POST', process_response=False
        )
        response.raise_for_status()
        return LabelRequest.from_location(
            response.headers['Location'], self.client
        )

    def get_label(self):
        """
        Get the label for the order item. The returned object is a PDF file
        content.
        """
        response = self.client.request(
            'orders/labels',
            params=[('orderItemId', self.order_item_id)],
            process_response=False,
        )
        response.raise_for_status()
        return response.content

    def cancel(self, reason):
        """
        The Cancel Orders API enables the seller to cancel an order that may
        already have been approved by the Flipkart Marketplace.

        For valid reasons refer:
        https://seller.flipkart.com/api-docs/order-api-docs/OMAPIRef.html#id12
        """
        response = self.client.request(
            'orders/cancel', method="POST", body=[
                {
                    'orderItemId': self.order_item_id,
                    'reason': reason
                }
            ]
        )
        return response

    def dispatch(self, quantity=None):
        """
        The Dispatch Orders API marks order items as “Ready to Dispatch” and
        communicates to the logistics partners that the order is ready for
        pick up.

        :param quantity: If the quantity is not specified, the quantity of the
                         order is taken as the quantity.
        """
        if quantity is None and not self.attributes.get('quantity'):
            raise Exception('Quantity could not be inferred from order data')

        if quantity is None:
            quantity = self.attributes['quantity']

        return self.dispatch_many(
            self.client, [(self.order_item_id, quantity)]
        )[0]

    @classmethod
    def dispatch_many(cls, client, order_item_qty_pairs):
        """
        Mark several order items to dispatch at once

        :param order_item_qty_pairs: pairs of ('item_id', quantity)
                                     Ex: [('id1', 2), ('id3', 1)]
        """
        response = client.request(
            'orders/dispatch', method="POST", body={
                'orderItems': [{
                    'orderItem': item_qty_pair[0],
                    'quantity': item_qty_pair[1],
                } for item_qty_pair in order_item_qty_pairs]
            }
        )
        return response['orderItems']

    def get_shipment_details(self):
        """
        Returns the shipment details of the order item
        """
        return self.get_shipment_details_many(
            self.client, [self.order_item_id]
        )[0]

    @classmethod
    def get_shipment_details_many(cls, client, order_item_ids):
        """
        get shipment details of several order items at once
        """
        response = client.request(
            'orders/shipments',
            params=[('orderItemsIds', ','.join(order_item_ids))]
        )
        return response['shipments']


class LabelRequest(FlipkartResource):
    """
    A Label for a order item
    """
    def __init__(self, label_request_id, client):
        self.label_request_id = label_request_id
        self.client = client

    @classmethod
    def from_location(cls, location, client):
        """
        Parses the label_request_id from the location and returns an instance
        of the label request object
        """
        return cls(location.rsplit('/', 1)[-1], client)

    def refresh_status(self):
        """
        Returns the status of the label.

        The Label Request API checks the packing request status. It gets the
        label request status of the order items as marked by the sellers and
        returns the number of items, completed or invalidated, and the overall
        completion status.
        """
        response = self.client.request(
            '/orders/labelRequest/%s' % self.label_request_id,
        )
        return response


class PaginationIterator(object):
    """
    An iterable that lets the user infinitely browse through pages of a
    paginated response

    :param client: The API client to make subsequent requests with
    :param response: The dictionary of response with pagination
    :param key: The key that identifies the item iterable (ex:orderItems)
    :param cast_func: Each item in iterable is casted with this function
                      if specidied
    """
    def __init__(self, client, response, key, cast_func=None):
        self.client = client
        self.items = []
        self.key = key

        if cast_func is None:
            cast_func = lambda item: item
        self.cast_func = cast_func

        self._nextPageUrl = None

        self.update_items_from(response)

    def update_items_from(self, response):
        """
        Given a response dictionary, update the items and urls
        """
        self.items.extend(response[self.key])
        self._nextPageUrl = response.get('nextPageUrl')

    def __iter__(self):
        self._current_index = -1
        return self

    @property
    def count(self):
        return len(self.items)

    def __next__(self):
        self._current_index += 1

        if self._current_index >= self.count and self._nextPageUrl:
            # If the iterator has reached its end and there is a
            # nextPageUrl then get the fresh items and update
            self.update_items_from(self.client.request(self._nextPageUrl))

        if self._current_index < self.count:
            return self.cast_func(self.items[self._current_index])
        else:
            raise StopIteration()

    next = __next__


class Listing(FlipkartResource):
    """
    Represents a Listing for a SKU
    """
    def __init__(self, listing_id, sku, client, attributes=None, lazy=True):
        self.listing_id = listing_id
        self.sku = sku
        self.client = client
        self.attributes = attributes

        if self.listing_id and not self.attributes and not lazy:
            self.refresh_attributes()

    @classmethod
    def new(cls, client, sku, attributes):
        """
        Create a new listing with the given attributes. This is not meant to
        be called directly, but through `sku.create_listing(mrp=100)` style.
        """
        return cls(listing_id=None, sku=sku, attributes=attributes)

    def refresh_attributes(self):
        """
        Fetch the attributes from flipkart
        """
        if self.listing_id is None:
            raise ValueError('Cannot fetch attributes for an unsaved listing')

        response = self.client.request(
            'skus/listings/%s' % self.listing_id
        )

        if self.sku is None:
            # Set the sku if the SKU was not known before
            self.sku = SKU(response['skuId'], self.client)

        self.attributes = response['attributeValues']
        return response

    def update(self, attributes=None, **kwargs):
        """
        Update listing attributes such as stock, price, and pocurement SLA
        for a particular ListingID. For a more convenient API use
        `listing.save()` once the attributes have been changed.
        """
        if attributes is None:
            attributes = {}
        attributes.update(kwargs)
        self.attributes = self.client.request(
            'skus/listings/%s' % self.listing_id,
            body={'attributeValues': attributes},
            method="POST"
        )['response']['attributeValues']
        return self.attributes

    def save(self):
        """
        Save any changes to the listing by updating it
        """
        if self.listing_id:
            return self.update(self.attributes)
        else:
            # This is a new listing. So create a new listing
            self.client.request(
                "skus/%s/listings" % self.sku.sku_id,
                body={
                    'skuId': self.sku.sku_id,
                    'fsn': self.sku.fsn,
                    'attributeValues': self.attributes,
                },
                method="POST"
            )
            # XXX: Though the API docs seem to say there is a response
            # in the response, there is no such thing. So return
            # the first listing of the SKU
            self.listing_id = self.sku.listings[0].listing_id
            return self.refresh_attributes()
