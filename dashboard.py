from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class NnmwareDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """
    
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        
        # append an app list module for "Applications"
        self.children.append(modules.Group(
            _('NNMWARE System:'),
            collapsible=True,
            column=1,
            children = [
                modules.AppList(
                    _('NNMWARE Core'),
                    column=1,
                    collapsible=False,
                    models=('nnmware.core.*',
                	    ),
                ),
                modules.AppList(
                    _('Money&Addresses&Video'),
                    column=1,
                    css_classes=('grp-collapse grp-closed',),
                    models=( 'nnmware.apps.money.*',
                	    'nnmware.apps.address.*',
                	    'nnmware.apps.video.*',
                	    ),
                ),
                modules.AppList(
                    _('Shop'),
                    column=1,
                    css_classes=('grp-collapse grp-closed',),
                    models=( 'nnmware.apps.shop.*',
                	    ),
                ),
                modules.AppList(
                    _('Booking'),
                    column=1,
                    css_classes=('grp-collapse grp-closed',),
                    models=( 'nnmware.apps.booking.*',
                	    ),
                ),
                modules.AppList(
                    _('Administration Module'),
                    column=1,
                    css_classes=('grp-collapse grp-closed',),
                    models=( 'django.contrib.auth.*', 'nnmware.apps.userprofile.models.Profile',
                	    'nnmware.apps.userprofile.models.EmailValidation',
                	    'django.contrib.sites.models.Site',
                	    'django.contrib.flatpages.models.FlatPage','nnmware.apps.social.models.UserSocialAuth',
                	    ),
                )

            ]

        ))
        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=10,
            column=2,
        ))


        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Nerd.do'),
            column=3,
            children=[
                {
                    'title': _('Main Page'),
                    'url': '/',
                    'external': False,
                },
                {
                    'title': _('Admin page'),
                    'url': '/is_not_adm/',
                    'external': False,
                },

            ]
        ))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Engine Support'),
            column=3,
            children=[
                {
                    'title': _('support@nnmware.com'),
                    'url': 'mailto:support@nnmware.com',
                    'external': True,
                },
            ]
        ))



