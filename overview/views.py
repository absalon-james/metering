from horizon import views
from openstack_dashboard.dashboards.metering.common.usage import NandyUsage
from openstack_dashboard.dashboards.project.overview.views \
    import ProjectUsageCsvRenderer
from openstack_dashboard.usage import ProjectUsageTable
from openstack_dashboard.usage import UsageView


class ProjectOverview(UsageView):
    table_class = ProjectUsageTable
    usage_class = NandyUsage
    template_name = 'metering/overview/usage.html'
    csv_response_class = ProjectUsageCsvRenderer

    def get_data(self):
        super(ProjectOverview, self).get_data()
        return self.usage.get_instances()


class WarningView(views.HorizonTemplateView):
    template_name = "metering/_warning.html"
