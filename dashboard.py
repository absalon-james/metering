from django.utils.translation import ugettext_lazy as _

import horizon


class Metering(horizon.Dashboard):
    name = _('Metering')
    slug = 'metering'
    panels = ('usage', 'overview')
    default_panel = 'usage'
    permissions = ('openstack.roles.admin',)


horizon.register(Metering)
