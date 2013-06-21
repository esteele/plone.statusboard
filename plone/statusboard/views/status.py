import logging

from pyramid.view import view_config


log = logging.getLogger('HOME')


@view_config(route_name='home', renderer='plone.statusboard:templates/home.pt')
def homePage(context, request):
    info = {}
    return dict(info=info)


@view_config(route_name='open_pulls', renderer='plone.statusboard:templates/pulls.pt')
def openPulls(context, request):
    info = {}
    return dict(info=info)


@view_config(route_name='jenkins_status', renderer='plone.statusboard:templates/jenkins_status.pt')
def jenkinsStatus(context, request):
    info = {}
    return dict(info=info)
