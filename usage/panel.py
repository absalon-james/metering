from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.metering import dashboard


class UsagePanel(horizon.Panel):
    name = _('Usage')
    slug = 'usage'


dashboard.MeteringDashboard.register(UsagePanel)
