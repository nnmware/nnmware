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
    hotel_recipients = []
    if booking.hotel.email:
        hotel_recipients.append(booking.hotel.email)
    elif booking.hotel.contact_email:
        hotel_recipients.append(booking.hotel.contact_email)
    for admin in booking.hotel.admins.all():
        if admin.email:
            hotel_recipients.append(admin.email)
    mail_dict = {'booking': booking,
        'site_name': settings.SITENAME}
    subject = 'booking/on_create_to_hotel_subject.txt'
    body = 'booking/on_create_to_hotel.txt'
    send_template_mail(subject,body,mail_dict,recipients)
    send_template_mail(subject,body,mail_dict,hotel_recipients)

def request_add_hotel_mail(req_add):
    recipients = settings.BOOKING_MANAGERS
    mail_dict = {'req_add': req_add, 'site_name': settings.SITENAME}
    subject = 'booking/request_add_hotel_subject.txt'
    body = 'booking/request_add_hotel.txt'
    send_template_mail(subject,body,mail_dict,recipients)







