import os
import Image
import json
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, SiteProfileNotAvailable

from django.contrib.auth.forms import PasswordResetForm, AuthenticationForm, \
    PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseForbidden, Http404
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.views.generic.base import View, TemplateView
from django.views.generic import FormView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django.views.generic import YearArchiveView, MonthArchiveView, \
    DayArchiveView
from nnmware.core.ajax import AjaxLazyAnswer
from nnmware.core.imgutil import resize_image, remove_thumbnails, remove_file
from nnmware.core.utils import make_key, send_template_mail
from nnmware.core.views import AjaxFormMixin

from nnmware.apps.userprofile.models import Profile
from nnmware.core.models import EmailValidation
from nnmware.apps.userprofile.forms import *
from nnmware.core.imgutil import fit


@login_required
def avatardelete(request):
    if request.is_ajax():
        try:
            u = request.user
            remove_thumbnails(u.avatar.path)
            remove_file(u.avatar.path)
            u.avatar_complete = False
            u.avatar = None
            u.save()
            payload = {'success': True}
        except:
            payload = {'success': False}
        return AjaxLazyAnswer(payload)
    else:
        raise Http404()
