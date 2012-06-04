# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

def guests_from_get_request(request):
    guests_get = request.GET.get('guests') or None
    if guests_get:
        guests = int(guests_get)
    else:
        guests = None
    return guests

def booking_new_client_mail(booking, username=''):
    if booking.email:
        mail_dict = {'booking': booking,
                    'site_name': settings.SITENAME, 'username': username}
        subject = render_to_string('booking/new_client_subject.txt', mail_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        message = render_to_string('booking/new_client.txt', mail_dict)
        send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER,
            recipient_list=[booking.email])
