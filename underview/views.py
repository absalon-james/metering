from horizon import messages
from horizon import views
from openstack_dashboard import usage
from openstack_dashboard.dashboards.project.overview.views \
    import ProjectUsageCsvRenderer

from nandy import config
from nandy.db import db
from nandy.db import ActiveVCPUS as vcpus
from nandy.db import ActiveMemoryMB as memory
from nandy.db import ActiveLocalStorageGB as storage

NANDY_DB_CONFIG = '/etc/nandy/db.yaml'


class NandyUsage(usage.ProjectUsage):

    def __init__(self, request, project_id=None):
        super(NandyUsage, self).__init__(request, project_id)
        self.vcpu_stats = None
        self.memory_stats = None
        self.storage_stats = None

    def dbdata(self, dbconf, start, end):
        def stat(v):
            return [v.time.isoformat(), v.value]

        db.get_engine(dbconf)
        with db.session_scope() as session:
            vcpu_stats = session.query(vcpus) \
                .filter(vcpus.time >= start) \
                .filter(vcpus.time <= end)
            vcpu_stats = map(stat, vcpu_stats)

            memory_stats = session.query(memory) \
                .filter(memory.time >= start) \
                .filter(memory.time <= end)
            memory_stats = map(stat, memory_stats)

            storage_stats = session.query(storage) \
                .filter(storage.time >= start) \
                .filter(storage.time <= end)
            storage_stats = map(stat, storage_stats)
        return (vcpu_stats, memory_stats, storage_stats)

    def summarize(self, start, end):
        super(NandyUsage, self).summarize(start, end)

        # Get database configuration
        try:
            dbconf = config.load(NANDY_DB_CONFIG)
        except:
            msg = ("Metering dashboard missing configuration "
                   "file {0}.".format(NANDY_DB_CONFIG))
            messages.error(self.request, msg)
            return

        messages.success(self.request, "Got the config")

        # Get database info
        try:
            v_stats, m_stats, s_stats = self.dbdata(dbconf, start, end)
            v_stats = map(lambda s: '["{0}",{1}]'.format(s[0], s[1]), v_stats)
            m_stats = map(lambda s: '["{0}",{1}]'.format(s[0], s[1]), m_stats)
            s_stats = map(lambda s: '["{0}",{1}]'.format(s[0], s[1]), s_stats)
            self.vcpu_stats = v_stats
            self.memory_stats = m_stats
            self.storage_stats = s_stats
        except:
            msg = 'Unable to read from nandy database.'
            messages.error(self.request, msg)


class ProjectOverview(usage.UsageView):
    table_class = usage.ProjectUsageTable
    usage_class = NandyUsage
    template_name = 'metering/underview/usage.html'
    csv_response_class = ProjectUsageCsvRenderer

    def get_data(self):
        super(ProjectOverview, self).get_data()
        return self.usage.get_instances()


class WarningView(views.HorizonTemplateView):
    template_name = "metering/_warning.html"
