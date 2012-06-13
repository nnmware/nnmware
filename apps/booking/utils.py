# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from nnmware.core.utils import send_template_mail

def guests_from_request(request):
    guests_get = request.GET.get('guests') or None
    if guests_get:
        guests = int(guests_get)
    else:
        guests = None
    return guests

def booking_new_client_mail(booking, username=''):
    if booking.email:
        recipients = [booking.email]
        mail_dict = {'booking': booking,
                    'site_name': settings.SITENAME, 'username': username}
        subject = 'booking/on_create_to_client_subject.txt'
        body = 'booking/on_create_to_client.txt'
        send_template_mail(subject,body,mail_dict,recipients)

def booking_new_hotel_mail(booking):
    recipients = settings.BOOKING_MANAGERS
    if booking.hotel.email:
        recipients.append(booking.hotel.email)
    elif booking.hotel.contact_email:
        recipients.append(booking.hotel.contact_email)
    for admin in booking.hotel.admins.all():
        if admin.email:
            recipients.append(admin.email)
    mail_dict = {'booking': booking,
        'site_name': settings.SITENAME}
    subject = 'booking/on_create_to_hotel_subject.txt'
    body = 'booking/on_create_to_hotel.txt'
    send_template_mail(subject,body,mail_dict,recipients)






