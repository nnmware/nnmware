# coding: utf-8

"""
Yandex.Maps  and OSM API wrapper
"""
from __future__ import with_statement
from math import *
import xml.dom.minidom
import urllib
import urllib2
from contextlib import closing
import httplib
import json

class Geocoder(object):
    base_url = "http://nominatim.openstreetmap.org/search?format=json&polygon=1&addressdetails=1&%s"

    def geocode(self, q):

        params = { 'q': q.encode('utf-8') }

        url = self.base_url % urllib.urlencode(params)
        try:
            data = urllib2.urlopen(url)
            response = data.read()
            return self.parse_json(response)
        except :
            return None

    def parse_json(self, data):
        try:
            data = json.loads(data)
        except:
            data = []
        return data

STATIC_MAPS_URL = 'http://static-maps.yandex.ru/1.x/?'
GEOCODE_URL = 'http://geocode-maps.yandex.ru/1.x/?'



def request(method, url, data=None, headers=None, timeout=None):
    host_port = url.split('/')[2]
    timeout_set = False
    try:
        connection = httplib.HTTPConnection(host_port, timeout = timeout)
        timeout_set = True
    except TypeError:
        connection = httplib.HTTPConnection(host_port)

    with closing(connection):
        if not timeout_set:
            connection.connect()
            connection.sock.settimeout(timeout)
            timeout_set = True

        connection.request(method, url, data, headers)
        response = connection.getresponse()
        return response.status, response.read()

def get_map_url(api_key, longitude, latitude, zoom, width, height):
    """ returns URL of static yandex map """
    params = [
       'll=%0.7f,%0.7f' % (float(longitude), float(latitude),),
       'size=%d,%d' % (width, height,),
       'z=%d' % zoom,
       'l=map',
       'pt=%0.7f,%0.7f' % (float(longitude), float(latitude),),
       'key=%s' % api_key
    ]
    return STATIC_MAPS_URL + '&'.join(params)

def geocode(api_key, address, timeout=2):
    """ returns (longtitude, latitude,) tuple for given address """
    try:
        xml = _get_geocode_xml(api_key, address, timeout)
        return _get_coords(xml)
    except IOError:
        return None, None

def _get_geocode_xml(api_key, address, timeout=2):
    url = _get_geocode_url(api_key, address)
    status_code, response = request('GET', url, timeout=timeout)
    return response

def _get_geocode_url(api_key, address):
    if isinstance(address, unicode):
        address = address.encode('utf8')
    params = urllib.urlencode({'geocode': address, 'key': api_key})
    return GEOCODE_URL + params

def _get_coords(response):
    try:
        dom = xml.dom.minidom.parseString(response)
        pos_elem = dom.getElementsByTagName('pos')[0]
        pos_data = pos_elem.childNodes[0].data
        return tuple(pos_data.split())
    except IndexError:
        return None, None


RADIUS = 6371 #Earth's mean radius in km

def distance(origin, destiny):
    (latitude1, longitude1) = (origin[0], origin[1])
    (latitude2, longitude2) = (destiny[0], destiny[1])

    dLat = radians(latitude1 - latitude2)
    dLong = radians(longitude1 - longitude2)

    # matter of faith
    a = sin(dLat/2)*sin(dLat/2)+cos(radians(latitude1))*cos(radians(latitude2))*sin(dLong/2)*sin(dLong/2)
    c = 2*atan2(sqrt(a), sqrt(1-a))

    return RADIUS*c

def distance_to_object(origin, destiny):
    (latitude1, longitude1) = (origin.latitude, origin.longitude)
    (latitude2, longitude2) = (destiny.latitude, destiny.longitude)

    dLat = radians(latitude1 - latitude2)
    dLong = radians(longitude1 - longitude2)

    # matter of faith
    a = sin(dLat/2)*sin(dLat/2)+cos(radians(latitude1))*cos(radians(latitude2))*sin(dLong/2)*sin(dLong/2)
    c = 2*atan2(sqrt(a), sqrt(1-a))

    return RADIUS*c


def places_near_object(origin, radius, model_db_name):
    query= """SELECT id, 3956 * 2 * ASIN(SQRT(POWER(SIN((%s - latitude) *
        0.0174532925 / 2), 2) + COS(%s * 0.0174532925) * COS(latitude * 0.0174532925) *
        POWER(SIN((%s - longitude) * 0.0174532925 / 2), 2) )) as distance from %s
        having distance < %s ORDER BY distance ASC """ % ( origin.latitude, origin.latitude,
                    origin.longitude, model_db_name, radius)
    return query

