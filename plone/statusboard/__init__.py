from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    # adds cornice
    config.include("cornice")

    # # plone versions
    # config.registry.settings['plone_versions'] = ast.literal_eval(settings['plone_versions'])

    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')
    config.add_route('open_pulls', '/open-pulls')
    config.add_route('jenkins_status', '/jenkins-status')

    config.scan("plone.statusboard.views")

    config.end()

    return config.make_wsgi_app()
