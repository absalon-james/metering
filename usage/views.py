import config
import datetime
from horizon import messages
from horizon import views
from horizon.exceptions import Http302
from nandy.utils import date_from_string
from nandy.utils import get_date_interval
from nandy.db import db
from nandy.db import ActiveVCPUS as vcpus
from nandy.db import ActiveMemoryMB as memory
from nandy.db import ActiveLocalStorageGB as storage

NANDY_DB_CONFIG = '/etc/nandy/db.yaml'


class IndexView(views.APIView):
    template_name = 'metering/usage/index.html'

    def dbconf(self, filename=NANDY_DB_CONFIG):
        """Returns dictionary of config file loaded as yaml.

        :param filename: String name of file containing configuration.
        :returns dict:
        """
        return config.load(filename)

    def dbdata(self, dbconf, start, end):
        """Returns stat triple tuple.

        :param dbconf: Dictionary with database configuration
        :param start: Datetime start
        :param end: Datetime end
        :return: Tuple of three lists of datapoints.
        """
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

        # Gather data from nandy database.
        try:
            dbconf = self.dbconf()
        except:
            msg = ("Metering dashboard missing configuration "
                   "file {0}.".format(NANDY_DB_CONFIG))
            messages.error(request, msg)
            raise Http302('/')

        try:
            v_stats, m_stats, s_stats = self.dbdata(dbconf, start, end)
            # @TODO - Fix this
            # Data points are converted to string ease of templating.
            v_stats = map(lambda s: '["{0}",{1}]'.format(s[0], s[1]), v_stats)
            m_stats = map(lambda s: '["{0}",{1}]'.format(s[0], s[1]), m_stats)
            s_stats = map(lambda s: '["{0}",{1}]'.format(s[0], s[1]), s_stats)
            context['vcpu_stats'] = v_stats
            context['memory_stats'] = m_stats
            context['storage_stats'] = s_stats
        except:
            msg = "Unable to read from nandy database."
            messages.error(request, msg)
            context['vcpu_stats'] = []
            context['memory_stats'] = []
            context['storage_stats'] = []

        return context
