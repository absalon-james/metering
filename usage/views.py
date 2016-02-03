import datetime
from horizon import views
from openstack_dashboard.dashboards.metering.common.usage import NandyUsage
from nandy.utils import date_from_string
from nandy.utils import get_date_interval


class IndexView(views.APIView):
    template_name = 'metering/usage/index.html'

    def get_data(self, request, context, *args, **kwargs):

        # Default selected tenant to special all tenant in nandy db
        selected_tenant_id = request.GET.get('tenant', '0' * 32)
        context['tenant'] = selected_tenant_id

        # Default usage interval
        today, tomorrow = get_date_interval()
        if 'start' in request.GET:
            start = date_from_string(request.GET.get('start'))
        else:
            start = today

        # Convert to beginning of next day if provided.
        if 'end' in request.GET:
            end = date_from_string(request.GET.get('end'))
            end = end + datetime.timedelta(1)
        else:
            end = tomorrow

        # Swap dates if start > end
        if start > end:
            start, end = end, start
        context['start'] = start.date().isoformat()
        context['end'] = (end - datetime.timedelta(1)).date().isoformat()

        projects = [
            tenant for tenant in
            request.user.authorized_tenants if tenant.enabled
        ]
        context['projects'] = projects

        usage = NandyUsage(request, selected_tenant_id)
        usage.add_nandy_data(start, end)
        context["usage"] = usage
        return context
