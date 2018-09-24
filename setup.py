#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import
from setuptools import setup
import re
import os
import ConfigParser
from io import open

MODULE = u'contract_payment_type'
PREFIX = u'nantic'
MODULE2PREFIX = {}


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_require_version(name):
    if minor_version % 2:
        require = u'%s >= %s.%s.dev0, < %s.%s'
    else:
        require = u'%s >= %s.%s, < %s.%s'
    require %= (name, major_version, minor_version,
        major_version, minor_version + 1)
    return require

config = ConfigParser.ConfigParser()
config.readfp(open(u'tryton.cfg'))
info = dict(config.items(u'tryton'))
for key in (u'depends', u'extras_depend', u'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()

version = info.get(u'version', u'0.0.1')
major_version, minor_version, _ = version.split(u'.', 2)
major_version = int(major_version)
minor_version = int(minor_version)

requires = []
for dep in info.get(u'depends', []):
    if not re.match(ur'(ir|res|webdav)(\W|$)', dep):
        prefix = MODULE2PREFIX.get(dep, u'trytond')
        requires.append(u'%s_%s >= %s.%s, < %s.%s' %
                (prefix, dep, major_version, minor_version,
                major_version, minor_version + 1))
requires.append(get_require_version(u'trytond'))

tests_require = [get_require_version(u'proteus')]

setup(name=u'%s_%s' % (PREFIX, MODULE),
    version=version,
    description=u'',
    long_description=read(u'README'),
    author=u'NaN·tic',
    author_email=u'info@nan-tic.com',
    url=u'http://www.nan-tic.com/',
    download_url=u"https://bitbucket.org/nantic/trytond-%s" % MODULE,
    package_dir={u'trytond.modules.%s' % MODULE: u'.'},
    packages=[
        u'trytond.modules.%s' % MODULE,
        u'trytond.modules.%s.tests' % MODULE,
        ],
    package_data={
        u'trytond.modules.%s' % MODULE: (info.get(u'xml', [])
            + [u'tryton.cfg', u'locale/*.po', u'tests/*.rst']),
        },
    classifiers=[
        u'Development Status :: 5 - Production/Stable',
        u'Environment :: Plugins',
        u'Framework :: Tryton',
        u'Intended Audience :: Developers',
        u'Intended Audience :: Financial and Insurance Industry',
        u'Intended Audience :: Legal Industry',
        u'License :: OSI Approved :: GNU General Public License (GPL)',
        u'Natural Language :: Bulgarian',
        u'Natural Language :: Catalan',
        u'Natural Language :: Czech',
        u'Natural Language :: Dutch',
        u'Natural Language :: English',
        u'Natural Language :: French',
        u'Natural Language :: German',
        u'Natural Language :: Russian',
        u'Natural Language :: Spanish',
        u'Operating System :: OS Independent',
        u'Programming Language :: Python :: 2.6',
        u'Programming Language :: Python :: 2.7',
        u'Topic :: Office/Business',
        ],
    license=u'GPL-3',
    install_requires=requires,
    zip_safe=False,
    entry_points=u"""
    [trytond.modules]
    %s = trytond.modules.%s
    """ % (MODULE, MODULE),
    test_suite=u'tests',
    test_loader=u'trytond.test_loader:Loader',
    tests_require=tests_require,
    )
