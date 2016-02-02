from django.utils.translation import ugettext_lazy as _

import horizon
from openstack_dashboard.dashboards.metering import dashboard


class Underview(horizon.Panel):
    name = _("Underview")
    slug = 'underview'

dashboard.Metering.register(Underview)
