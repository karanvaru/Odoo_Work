# -*- coding: utf-8 -*-

import urllib
import urllib.parse

try:
    import json
except ImportError:
    import simplejson as json

from odoo.tools.translate import _
from odoo.exceptions import UserError


def fetch_json(query_url, params={}, headers={}):
    """Retrieve a JSON object from a (parameterized) URL.
    
    :param query_url: The base URL to query
    :type query_url: string
    :param params: Dictionary mapping (string) query parameters to values
    :type params: dict
    :param headers: Dictionary giving (string) HTTP headers and values
    :type headers: dict 
    :return: A `(url, json_obj)` tuple, where `url` is the final,
    parameterized, encoded URL fetched, and `json_obj` is the data 
    fetched from that URL as a JSON-format object. 
    :rtype: (string, dict or array)
    ::::::USEFULL LINKS:::::::::::::::::::::
    http://maps.googleapis.com/maps/api/distancematrix/json?origins=Vancouver+BC|Seattle&destinations=San+Francisco|Victoria+BC&mode=bicycling&language=fr-FR&key=API_KEY
    https://developers.google.com/maps/documentation/distancematrix/
    http://maps.googleapis.com/maps/api/directions/json?origin=Chicago,IL&destination=Los+Angeles,CA&waypoints=Joplin,MO|Oklahoma+City,OK&key=API_KEY

    """
    encoded_params = urllib.parse.urlencode(params)
    url = query_url + encoded_params
    # print "url.........",url
    request = urllib.request(url, headers=headers)
    response = urllib.request.urlopen(request)
    return (url, json.load(response))


class google_maps_distance(object):
    _DIRECTIONS_QUERY_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?'

    def __init__(self, referrer_url=''):
        self.referrer_url = referrer_url

    def directions(self, origins, destinations, mode='driving', **kwargs):
        """ Get directions from 'origin' to 'destination'. """
        api_key = False
        if kwargs:
            for key, value in kwargs.items():
                api_key = value if key == 'key' else False
        params = {
            'origins': origins,
            'destinations': destinations,
            'mode': mode,
            'key': api_key
        }
        #        print "params++++++++++++++++++++++++++++++++",params
        params.update({'departure_time': kwargs.get('departure_time', False)})
        # complete_response = []
        # print "start......."
        url, response = fetch_json(self._DIRECTIONS_QUERY_URL, params=params)
        #        print "url ,response.......",url,response
        # complete_response.append
        status_code = response['status']
        if status_code != 'OK':
            raise UserError(_('Impossible to access data !'))
        return response

    #    {'response':response, 'api_count':api_count, 'last_count':last_count}

    def duration(self, origin, destination, mode='driving', **kwargs):
        response = self.directions(origin, destination, mode, **kwargs)
        duration = 0
        rows = response.get('rows')
        if rows:
            elements = rows[0].get('elements')
            if elements:
                duration = elements[0].get('duration', {}).get('text', 0)
        return duration

    def distance(self, origins, destinations, mode='driving', **kwargs):
        response = self.directions(origins, destinations, mode, **kwargs)
        result = {}
        result['duration'] = []
        result['distance'] = []
        rows = response.get('rows')
        if rows:
            for each_row in rows:
                # print "rows......",rows
                elements = each_row.get('elements')
                # print "elements.........",elements
                if elements:
                    # print "elements.........",elements[0]
                    result['distance'].append(elements[0].get('distance', {}).get('value', 0))
                    result['duration'].append(elements[0].get('duration', {}).get('text', 0))
                else:
                    result['distance'].append(0)
                    result['duration'].append(0)
        #                result['api_count']= response.get('api_count',False)
        #                result['last_count']= response.get('last_count',False)
        return result
