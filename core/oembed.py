# -*- coding: utf-8 -*-

"""
Library for OEmbed
"""

import urllib
import urllib2
import re
import json
from xml.etree import ElementTree


class OEmbedError(Exception):
    """Base class for OEmbed errors"""


class OEmbedResponse(object):
    """
    Base class for all OEmbed responses. 
    
    This class provides a factory of OEmbed responses according to the format
    detected in the type field. It also validates that mandatory fields are 
    present.
    
    """           
    def __init__(self):
        self._data = None

    def _validate_data(self, data):
        pass
               
    def __getitem__(self, name):
        return self._data.get(name)
    
    def get_data(self):
        return self._data
        
    def load_data(self, data):
        self._validate_data(data)
        self._data = data

    @classmethod
    def create_load(cls, data):
        if not all(k in data for k in ('type', 'version')):
            raise OEmbedError('Missing required fields on OEmbed response.')
        response = cls.create(data['type'])
        response.load_data(data)
        return response

    @classmethod
    def create(cls, response_type):
        return resourceTypes.get(response_type, OEmbedResponse)()

    @classmethod
    def new_from_json(cls, raw):
        data = json.loads(raw)
        return cls.create_load(data)
        
    @classmethod
    def new_from_xml(cls, raw):
        elem = ElementTree.XML(raw)
        data = dict([(e.tag, e.text) for e in elem.getiterator() if e.tag not in ['oembed']])
        return cls.create_load(data)
    
        
class OEmbedPhotoResponse(OEmbedResponse):
    """
    This type is used for representing static photos. 
        
    """
    def _validate_data(self, data):
        super(OEmbedPhotoResponse, self)._validate_data(data)
        if not all(k in data for k in ('url', 'width', 'height')):
            raise OEmbedError('Missing required fields on OEmbed photo response.')


class OEmbedVideoResponse(OEmbedResponse):
    """
    This type is used for representing playable videos.
    
    """
    def _validate_data(self, data):
        super(OEmbedVideoResponse, self)._validate_data(data)
        if not all(k in data for k in ('html', 'width', 'height')):
            raise OEmbedError('Missing required fields on OEmbed video response.')


class OEmbedLinkResponse(OEmbedResponse):
    """
    Responses of this type allow a provider to return any generic embed data 
    (such as title and author_name), without providing either the url or html 
    parameters. The consumer may then link to the resource, using the URL 
    specified in the original request.
    
    """
    pass


class OEmbedRichResponse(OEmbedResponse):
    """
    This type is used for rich HTML content that does not fall under 
    one of the other categories.
    
    """ 
    def _validate_data(self, data):
        super(OEmbedRichResponse, self)._validate_data(data)
        if not all(k in data for k in ('html', 'width', 'height')):
            raise OEmbedError('Missing required fields on OEmbed rich response.')


resourceTypes = {
    'photo': OEmbedPhotoResponse,
    'video': OEmbedVideoResponse,
    'link': OEmbedLinkResponse,
    'rich': OEmbedRichResponse
}


class OEmbedEndpoint(object):
    """
    A class representing an OEmbed Endpoint exposed by a provider.
    
    This class handles a number of URL schemes and manage resource retrieval.    
     
    """

    def __init__(self, url, url_schemes=None):
        """
        Create a new OEmbedEndpoint object. 
        
        Args:
            url: The url of a provider API (API endpoint).
            urlSchemes: A list of URL schemes for this endpoint. 
        
        """
        self._urlApi = url
        self._urlSchemes = {}
        self._init_request_headers()
        self._urllib = urllib2

        if url_schemes is not None:
            map(self.add_url_scheme, url_schemes)

        self._implicitFormat = self._urlApi.find('{format}') != -1
        
    def _init_request_headers(self):
        self._requestHeaders = {}
        self.set_user_agent('oembed/nnmware')

    def add_url_scheme(self, url):
        """
        Add a url scheme to this endpoint. It takes a url string and create
        the OEmbedUrlScheme object internally.
        
        Args:
            url: The url string that represents a url scheme to add.
            
        """
        if not isinstance(url, str):
            raise TypeError('url must be a string value')
        if not url in self._urlSchemes:
            self._urlSchemes[url] = OEmbedUrlScheme(url)
    
    def del_url_scheme(self, url):
        """
        Remove an OEmbedUrlScheme from the list of schemes.
        
        Args:
           url: The url used as key for the urlSchemes dict.
            
        """
        if url in self._urlSchemes:
            del self._urlSchemes[url]
    
    def clear_url_schemes(self):
        """Clear the schemes in this endpoint."""

        self._urlSchemes.clear()
            
    def get_url_schemes(self):
        """
        Get the url schemes in this endpoint. 
        
        Returns:
            A dict of OEmbedUrlScheme objects. k => url, v => OEmbedUrlScheme

        """    
        return self._urlSchemes

    def match(self, url):
        """
        Try to find if url matches against any of the schemes within this 
        endpoint.

        Args:
            url: The url to match against each scheme
            
        Returns:
            True if a matching scheme was found for the url, False otherwise

        """
        for urlScheme in self._urlSchemes.itervalues():
            if urlScheme.match(url):
                return True
        return False
        
    def request(self, url, **opt):
        """
        Format the input url and optional parameters, and provides the final url 
        where to get the given resource. 
        
        Args:
            url: The url of an OEmbed resource.
            **opt: Parameters passed to the url.
            
        Returns:
            The complete url of the endpoint and resource.
        
        """
        params = opt
        params['url'] = url       
        
        url_api = self._urlApi
        
        if 'format' in params and self._implicitFormat:
            url_api = self._urlApi.replace('{format}', params['format'])
            del params['format']
                
        return "%s?%s" % (url_api, urllib.urlencode(params))

    def get(self, url, **opt):
        """
        Convert the resource url to a complete url and then fetch the 
        data from it.
        
        Args:
            url: The url of an OEmbed resource.
            **opt: Parameters passed to the url.
            
        Returns:
            OEmbedResponse object according to data fetched             

        """
        return self.fetch(self.request(url, **opt))

    def fetch(self, url):
        """
        Fetch url and create a response object according to the mime-type.
        
        Args:
            url: The url to fetch data from
            
        Returns:
            OEmbedResponse object according to data fetched 
            
        """        
        proxy_support = urllib2.ProxyHandler({})
        opener = self._urllib.build_opener(proxy_support)
        opener.addheaders = self._requestHeaders.items()

        response = opener.open(url)

        headers = response.info()
        raw = response.read()

        if not 'Content-Type' in headers:
            raise OEmbedError('Missing mime-type in response')
        
        if headers['Content-Type'].find('application/xml') != -1 or headers['Content-Type'].find('text/xml') != -1:
            response = OEmbedResponse.new_from_xml(raw)
            
        elif headers['Content-Type'].find('application/json') != -1 or headers['Content-Type'].find('text/json') != -1:
            response = OEmbedResponse.new_from_json(raw)
        
        else:
            raise OEmbedError('Invalid mime-type in response - %s' % headers['Content-Type'])
        
        return response

    def set_urllib(self, url_library):
        """
        Override the default urllib implementation.

        Args:
            urllib: an instance that supports the same API as the urllib2 module
          
        """
        self._urllib = url_library

    def set_user_agent(self, user_agent):
        """
        Override the default user agent

        Args:
            user_agent: a string that should be send to the server as the User-agent
          
        """
        self._requestHeaders['User-Agent'] = user_agent


class OEmbedUrlScheme(object):
    """
    A class representing an OEmbed URL schema.

    """

    def __init__(self, url):
        """
        Create a new OEmbedUrlScheme instance.
        
        Args;
            url: The url scheme. It also takes the wildcard character (*).
            
        """
        self._url = url
        self._regex = re.compile(url.replace('.', '\.').replace('*', '.*'))

    def get_url(self):
        """
        Get the url scheme.
        
        Returns:
            The url scheme.
        """
        return self._url

    def match(self, url):
        """
        Match the url against this scheme.

        Args:
            url: The url to match against this scheme.
            
        Returns:
            True if a match was found for the url, False otherwise

        """
        return self._regex.match(url) is not None

    def __repr__(self):
        return "%s - %s" % (object.__repr__(self), self._url)


class OEmbedConsumer(object):
    """
    A class representing an OEmbed consumer.
    
    This class manages a number of endpoints, selects the corresponding one 
    according to the resource url passed to the embed function and fetches
    the data. 

    """    
    def __init__(self, link):
        self._endpoints = []
        self.url = link
        self.set_end_point()

    def add_endpoint(self, endpoint):
        """
        Add a new OEmbedEndpoint to be manage by the consumer.

        Args:
            endpoint: An instance of an OEmbedEndpoint class.

        """
        self._endpoints.append(endpoint)

    def set_end_point(self):
        if self.url[:8] != 'https://' and self.url[:7] != 'http://':
            self.url = 'http://%s' % self.url
        if self.url.find('youtu.be') != -1:
            self.url = self.url.replace('youtu.be/', 'www.youtube.com/watch?v=')
        prefix = 'http'
        if self.url.find('https://') != -1:
            prefix += 's'
        if self.url.find('youtube.com') != -1:
            self.add_endpoint(OEmbedEndpoint(prefix + '://www.youtube.com/oembed', [prefix + '://*.youtube.com/*']))
        elif self.url.find('vimeo.com') != -1:
            self.add_endpoint(OEmbedEndpoint(prefix + '://vimeo.com/api/oembed.json', [prefix + '://vimeo.com/*']))
        elif self.url.find('soundcloud.com') != -1:
            self.add_endpoint(OEmbedEndpoint(prefix + '://soundcloud.com/oembed', [prefix + '://soundcloud.com/*']))
        elif self.url.find('kickstarter.com') != -1:
            self.add_endpoint(OEmbedEndpoint(prefix + '://www.kickstarter.com/services/oembed', [prefix + '://www.kickstarter.com/projects/*']))
        elif self.url.find('slideshare.com') != -1:
            self.add_endpoint(OEmbedEndpoint(prefix + '://www.slideshare.net/api/oembed/2', [prefix + '://www.slideshare.net/*/*']))


    def del_endpoint(self, endpoint):
        """
        Remove an OEmbedEndpoint from this consumer.
        
        Args:
            endpoint: An instance of an OEmbedEndpoint class.
        
        """    
        self._endpoints.remove(endpoint)
        
    def clear_endpoints(self):
        """Clear all the endpoints managed by this consumer."""
        
        del self._endpoints[:]

    def get_endpoints(self):
        """
        Get the list of endpoints.
        
        Returns:
            The list of endpoints in this consumer.
        """
        return self._endpoints

    def _endpoint_for(self, url):
        for endpoint in self._endpoints:
            if endpoint.match(url):
                return endpoint
        return None
        
    def _request(self, url, **opt):
        endpoint = self._endpoint_for(url)
        if endpoint is None:
            raise OEmbedError('There are no endpoints available for %s' % url)
        return endpoint.get(url, **opt)
                    
    def embed(self, fmt='json', **opt):
        """
        Get an OEmbedResponse from one of the providers configured in this 
        consumer according to the resource url.
        
        Args:
            url: The url of the resource to get.
            format: Desired response format.
            **opt: Optional parameters to pass in the url to the provider.
        
        Returns:
            OEmbedResponse object.
            
        """
        if fmt not in ['json', 'xml']:
            raise OEmbedError('Format must be json or xml')
        opt['format'] = fmt
        return self._request(self.url, **opt)

    def result(self):
        if not self._endpoints:
            return None
        try:
            response = self.embed()
            return response.get_data()
        except:
            return None
