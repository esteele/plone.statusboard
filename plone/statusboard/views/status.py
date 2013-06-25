import csv
import datetime
import logging
import math
import urllib2

from github import Github
import keyring
from pyramid.view import view_config


log = logging.getLogger('HOME')

JENKINS_URL = "http://jenkins.plone.org"


@view_config(route_name='home', renderer='plone.statusboard:templates/home.pt')
def homePage(context, request):
    info = {}
    return dict(info=info)


class GitHubStats(object):

    GITHUB_CLIENT_ID = 'b9f6639835b8c9cf462a'
    GITHUB_USERNAME = 'esteele'

    PULLS = {}

    def __init__(self, organization_name="plone"):
        self.connection = Github(self.GITHUB_USERNAME,
                                 self.password,
                                 client_id=self.GITHUB_CLIENT_ID,
                                 client_secret=self.client_secret)
        self.organization = self.connection.get_organization(organization_name)
        self.last_calculated = None

    @property
    def client_secret(self):
        return keyring.get_password('esteele.manager', self.GITHUB_CLIENT_ID)

    @property
    def password(self):
        return keyring.get_password('github', self.GITHUB_USERNAME)
        # if password is None:
        #     password = getpass.getpass('Password: ')
        #     keyring.set_password('github', GITHUB_USERNAME, password)

    # def open_pull_requests(self):
    def open_pull_requests(self):
        """ Get current number of open pull requests. """

        pull_ages = []
        for repo in self.organization.get_repos():
            pull_ages.extend(self._get_pulls_for_repo(repo))

        print pull_ages
        total_pulls = len(pull_ages)

        pull_counts = {}
        for i in set(pull_ages):
            pull_counts[i] = pull_ages.count(i)

        return total_pulls, pull_counts

    def _get_pulls_for_repo(self, repo):
        pull_ages = []

        repo_name = repo.name
        if repo_name in self.PULLS:
            last_checked = self.PULLS[repo_name].get('last_checked', datetime.datetime.fromordinal(1))
            if datetime.datetime.now() - last_checked < datetime.timedelta(hours=1):
                pull_ages = self.PULLS[repo_name]['pull_ages']
                print "%s: %s" % (repo_name, pull_ages)
                return pull_ages
        print "Checking github for pulls from %s " % repo_name
        for pull in repo.get_pulls():
            updated_date = pull.updated_at
            delta = datetime.datetime.today() - updated_date
            days_old = delta.days
            pull_ages.append(days_old)

        self.PULLS[repo_name] = {'last_checked': datetime.datetime.now(),
                                 'pull_ages': pull_ages}
        return pull_ages

github = GitHubStats()


@view_config(route_name='open_pulls', renderer='plone.statusboard:templates/pulls.pt', http_cache=(3600, {'public': True}))
def openPulls(context, request):

    pulls, days_old = github.open_pull_requests()
    days_old_list = [list(a) for a in days_old.iteritems()]
    return {'value': str(pulls), 'days_old': str(days_old_list)}


@view_config(route_name='jenkins_status', renderer='plone.statusboard:templates/jenkins_status.pt')
def jenkinsStatus(context, request):
    info = {}
    return dict(info=info)


class GmaneListStats(object):

    def __init__(self, what_is_recent=30, group='gmane.comp.web.zope.plone.devel'):
        """
        @what_is_recent: how many days to keep in recent tally
        """
        self.data = {}
        # last what_is_recent days activity
        self.days = 0
        self.recent = what_is_recent

        stats_url = 'http://gmane.org/output-rate.php?group=%s' % group

        fp = urllib2.urlopen(stats_url)
        stats = fp.read()
        fp.close()

        for row in csv.reader(stats.split("\n")[1:], delimiter=' '):
            if len(row) < 3:
                continue

            date = row[0]
            messages = int(row[1])
            self.addDate(datetime.datetime.strptime(date, '%Y%m%d'), messages)

    def addDate(self, date, count):
        """
        Add a date to the collection of data. date is
        expected to be a datetime argument. this is un-granularizing
        the data a bit
        """
        if date.year not in self.data:
            self.data[date.year] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        year = self.data[date.year]
        year[date.month - 1] += count

        today = datetime.datetime.now()
        if (today - date).days <= self.recent:
            self.days += count

    def getTotal(self):
        total = 0
        for year, months in self.data.items():
            total += sum(months)
        return total

    def getYearlyAverage(self):
        return self.getTotal() / len(self.data.keys())

    def getYearlySummary(self):
        return [(year, self.getMonthlyAverage(year)) for year in sorted(self.data.keys())]

    def getMonthlyAverage(self, year=None):
        if not year:
            year = datetime.datetime.now().year

        year_total = sum(self.data[year])

        num_months = 12.0
        # skip months that haven't occured yet
        today = datetime.datetime.now()
        if today.year == year:
            num_months = (today.month - 1.0) + float(today.day) / 30.0  # approx
        return math.ceil(float(year_total) / num_months)

    def getCurrentHealth(self):
        return self.days / self.recent

    def getMonthlyStats(self, months=4):
        today = datetime.datetime.now()
        total = 0
        num = 0
        years = sorted(self.data.keys(), reverse=True)
        for year in years:
            # go through months in reverse
            for month in reversed(self.data[year]):
                if month == 0:  # hasn't occured yet
                    continue
                total += month
                num += 1
                if num == months:
                    # crunch
                    average = float(total) / float(months)
                    return {'average': average,
                            'stddev': 0,
                            }

    def isTrollRequired(self, months=4):
        """
        A troll is required if the activity in the last troll period months
        In theory this should be a standard deviation but for now I'll go with 30%
        """
        troll_level = self.getMonthlyStats(months)['average'] / 30.0 * .7
        return self.getCurrentHealth() < troll_level

gmane = GmaneListStats()


@view_config(route_name='list_activity', renderer='plone.statusboard:templates/list_activity.pt')
def listActivity(context, request):
    current_health = gmane.getCurrentHealth()
    return dict({'health': str(current_health)})
