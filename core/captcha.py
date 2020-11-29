# nnmware(c)2012-2020

from __future__ import unicode_literals
from urllib.request import urlopen, Request
from urllib.parse import urlencode

API_SSL_SERVER = "https://www.google.com/recaptcha/api"
API_SERVER = "http://www.google.com/recaptcha/api"
VERIFY_SERVER = "www.google.com"


class RecaptchaResponse(object):
    def __init__(self, is_valid, error_code=None):
        self.is_valid = is_valid
        self.error_code = error_code


def displayhtml(public_key, use_ssl=False, error=None):
    """Gets the HTML to display for reCAPTCHA

    public_key -- The public api key
    use_ssl -- Should the request be sent over ssl?
    error -- An error message to display (from RecaptchaResponse.error_code)"""

    error_param = ''
    if error:
        error_param = '&error=%s' % error

    if use_ssl:
        server = API_SSL_SERVER
    else:
        server = API_SERVER

    return """<script type="text/javascript" src="%(ApiServer)s/challenge?k=%(PublicKey)s%(ErrorParam)s"></script>

<noscript>
  <iframe src="%(ApiServer)s/noscript?k=%(PublicKey)s%(ErrorParam)s" height="300" width="500" frameborder="0"></iframe>
  <br /><textarea name="recaptcha_challenge_field" rows="3" cols="40"></textarea>
  <input type='hidden' name='recaptcha_response_field' value='manual_challenge' />
</noscript>
""" % {
        'ApiServer': server,
        'PublicKey': public_key,
        'ErrorParam': error_param}


def submit(recaptcha_challenge_field, recaptcha_response_field, private_key, remoteip):
    """
    Submits a reCAPTCHA request for verification. Returns RecaptchaResponse
    for the request

    recaptcha_challenge_field -- The value of recaptcha_challenge_field from the form
    recaptcha_response_field -- The value of recaptcha_response_field from the form
    private_key -- your reCAPTCHA private key
    remoteip -- the user's ip address
    """

    if not (recaptcha_response_field and recaptcha_challenge_field and
            len(recaptcha_response_field) and len(recaptcha_challenge_field)):
        return RecaptchaResponse(is_valid=False, error_code='incorrect-captcha-sol')

    params = urlencode({
        'privatekey': private_key,
        'remoteip': remoteip,
        'challenge': recaptcha_challenge_field,
        'response': recaptcha_response_field})
    request = Request(url="http://%s/recaptcha/api/verify" % VERIFY_SERVER, data=params,
                      headers={"Content-type": "application/x-www-form-urlencoded", "User-agent": "reCAPTCHA Python"})
    httpresp = urlopen(request)
    return_values = httpresp.read().splitlines()
    httpresp.close()
    return_code = return_values[0]
    if return_code == "true":
        return RecaptchaResponse(is_valid=True)
    else:
        return RecaptchaResponse(is_valid=False, error_code=return_values[1])
