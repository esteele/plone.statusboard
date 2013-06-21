from setuptools import setup, find_packages
import os

version = '1.0'

long_description = (
    open('README.md').read())

setup(name='plone.statusboard',
      version=version,
      description="Plone Current Development Status",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://github.com/esteele/plone.statusboard',
      license='gpl',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'cornice',
          'configparser',
          'gitpython',
          'python-dateutil',
          'PyGithub',
          'persistent',
          'requests',
          'lxml',
          'python-jenkins',
          'pyramid_debugtoolbar',
      ],
      entry_points="""\
      [paste.app_factory]
      main = plone.statusboard:main
      """,
      )
