from django.utils.translation import ugettext_lazy as _

import horizon


class MeteringDashboard(horizon.Dashboard):
    name = _('Metering')
    slug = 'metering'
    panels = ('usage',)
    default_panel = 'usage'
    permissions = ('openstack.roles.admin',)


horizon.register(MeteringDashboard)
