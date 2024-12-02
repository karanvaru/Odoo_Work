import base64
import logging
from datetime import timedelta

import requests
from requests.exceptions import ConnectionError as RequestConnectionError, Timeout as RequestTimeout

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RDDProductFetchImageWizard(models.TransientModel):
    _inherit = 'product.fetch.image.wizard'
    _description = "Fetch product images from Google Images based on the product's part number and description."

    _session = requests.Session()

    def _process_products(self, products_to_process):
        """ Fetch an image from the Google Custom Search API for each product.

        We fetch the 10 first image URLs and save the first valid image.

        :param recordset products_to_process: The products for which an image must be fetched, as a
                                              `product.product` recordset
        :return: The number of products for which a matching image was found
        :rtype: int
        :raises UserError: If the project is misconfigured on Google's side
        :raises UserError: If the API Key or Search Engine ID is incorrect
        """
        if not products_to_process:
            return 0

        nb_service_unavailable_codes = 0
        nb_timeouts = 0
        for product in products_to_process:
            # Fetch image URLs and handle eventual errors
            query = ''
            if product.default_code and product.name:
                query = product.default_code + " " + product.name
            else:
                query = product.name
            try:
                response = self._fetch_image_urls_from_google(query)
                if response.status_code == requests.codes.forbidden:
                    raise UserError(_(
                        "The Custom Search API is not enabled in your Google project. Please visit "
                        "your Google Cloud Platform project page and enable it, then retry. If you "
                        "enabled this API recently, please wait a few minutes and retry."
                    ))
                elif response.status_code == requests.codes.service_unavailable:
                    nb_service_unavailable_codes += 1
                    if nb_service_unavailable_codes <= 3:  # Temporary loss of service
                        continue  # Let the image of this product be fetched by the next cron run

                    # The service has not responded more  than 3 times, stop trying for now and wait
                    # for the next cron run.
                    self.with_context(automatically_triggered=True)._trigger_fetch_images_cron(
                        fields.Datetime.now() + timedelta(hours=1.0)
                    )
                    _logger.warning(
                        "received too many service_unavailable responses. delegating remaining "
                        "images to next cron run."
                    )
                    break
                elif response.status_code == requests.codes.too_many_requests:
                    self.with_context(automatically_triggered=True)._trigger_fetch_images_cron(
                        fields.Datetime.now() + timedelta(days=1.0)
                    )
                    _logger.warning(
                        "search quota exceeded. delegating remaining images to next cron run."
                    )
                    break
                elif response.status_code == requests.codes.bad_request:
                    raise UserError(_(
                        "Your API Key or your Search Engine ID is incorrect."
                    ))
            except (RequestConnectionError, RequestTimeout):
                nb_timeouts += 1
                if nb_timeouts <= 3:  # Temporary loss of service
                    continue  # Let the image of this product be fetched by the next cron run

                # The service has not responded more  han 3 times, stop trying for now and wait for
                # the next cron run.
                self.with_context(automatically_triggered=True)._trigger_fetch_images_cron(
                    fields.Datetime.now() + timedelta(hours=1.0)
                )
                _logger.warning(
                    "encountered too many timeouts. delegating remaining images to next cron run."
                )
                break

            # Fetch image and handle possible error
            response_content = response.json()
            if int(response_content['searchInformation']['totalResults']) > 0:
                for item in response_content['items']:  # Only populated if totalResults > 0
                    try:
                        image = self._get_image_from_url(item['link'])
                        if image:
                            product.image_1920 = image
                            break  # Stop at the first valid image
                    except (
                            RequestConnectionError,
                            RequestTimeout,
                            UserError,  # Raised when the image couldn't be decoded as base64
                    ):
                        pass  # Move on to the next image

            product.image_fetch_pending = False
            self.env.cr.commit()  # Commit every image in case the cron is killed

        return len(products_to_process.filtered('image_1920'))

    @api.model
    def default_get(self, fields_list):
        # Check that the cron has not been deleted and raise an error if so
        ir_cron_fetch_image = self.env.ref(
            'product_images.ir_cron_fetch_image', raise_if_not_found=False
        )
        if not ir_cron_fetch_image:
            raise UserError(_(
                "The scheduled action \"Product Images: Get product images from Google\" has "
                "been deleted. Please contact your administrator to have the action restored "
                "or to reinstall the module \"product_images\"."
            ))

        # Check that the cron is not already triggered and raise an error if so
        cron_triggers_count = self.env['ir.cron.trigger'].search_count(
            [('cron_id', '=', ir_cron_fetch_image.id)]
        )
        if cron_triggers_count > 0:
            raise UserError(_(
                "A task to process products in the background is already running. Please try again"
                "later."
            ))

        # Check if API keys are set without retrieving the values to avoid leaking them
        ICP = self.env['ir.config_parameter']
        google_pse_id_is_set = bool(ICP.get_param('google.pse.id'))
        google_custom_search_key_is_set = bool(ICP.get_param('google.custom_search.key'))
        if not (google_pse_id_is_set and google_custom_search_key_is_set):
            raise UserError(_(
                "The API Key and Search Engine ID must be set in the General Settings."
            ))

        # Compute default values
        if self._context.get('active_model') == 'product.template':
            product_ids = self.env['product.template'].browse(
                self._context.get('active_ids')
            ).product_variant_ids
        else:
            product_ids = self.env['product.product'].browse(
                self._context.get('active_ids')
            )
        nb_products_selected = len(product_ids)
        products_to_process = product_ids.filtered(lambda p: not p.image_1920)
        nb_products_to_process = len(products_to_process)
        nb_products_unable_to_process = nb_products_selected - nb_products_to_process
        defaults = super().default_get(fields_list)
        defaults.update(
            products_to_process=products_to_process,
            nb_products_selected=nb_products_selected,
            nb_products_to_process=nb_products_to_process,
            nb_products_unable_to_process=nb_products_unable_to_process,
        )
        return defaults

    def _get_products_to_process(self, limit=10000):
        """ Get the products that need to be processed and meet the criteria.

        The criteria are to have a barcode and no image. If `products_to_process` is not populated,
        the DB is searched to find matching product records.

        :param int limit: The maximum number of records to return, defaulting to 10000 to match
                          Google's API default rate limit
        :return: The products that meet the criteria
        :rtype: recordset of `product.product`
        """
        products_to_process = self.products_to_process or self.env['product.product'].search(
            [('image_fetch_pending', '=', True)], limit=limit
        )
        return products_to_process.filtered(
            # p.image_fetch_pending needed for self.products_to_process's records that might already
            # have been processed but not yet removed from the list when called from
            # action_fetch_image.
            lambda p: not p.image_1920 and p.image_fetch_pending
        )[:limit]  # Apply the limit after the filter with self.products_to_process for more results

