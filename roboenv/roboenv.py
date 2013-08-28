# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import argparse
import logging
import os
import subprocess
import sys


roboenv_settings_file_path = '.roboenv'
roboenv_default_settings = {
    'cache': 'wheelhouse'
}


class RoboenvException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


def save_settings(env, settings, args):
    # override settings with command line arguments
    if args.cache is not None:
        settings['cache'] = args.cache

    with open(os.path.join(env, roboenv_settings_file_path), 'w') as file:
        file.write(str(settings))


def read_settings(env, args):
    settings = roboenv_default_settings

    # probably virtualenv wasn't created using roboenv, but that's ok
    if not os.path.isfile(roboenv_settings_file_path):
        save_settings(roboenv_default_settings)
    else:
        settings = eval(open(roboenv_settings_file_path).read())

    # override settings with command line arguments
    if args.cache is not None:
        settings['cache'] = args.cache

    return settings


def init(args):
    env = args.init_args[-1]
    logging.info('Creating virtualenv')
    subprocess.call(['virtualenv'] + args.init_args)

    pip_executable = os.path.join(env, 'bin/pip')
    easy_install_executable = os.path.join(env, 'bin/easy_install')

    # check for katipo assembly file
    katipo_assembly = '.katipo/assembly'
    if os.path.isfile(katipo_assembly):
        assembly_opts = eval(open(katipo_assembly).read())
        # add search path for katipo repos
        with open('%s/lib/python2.7/site-packages/katipo_repos.pth' % env, 'w') as f:
            for repo in assembly_opts.repos:
                f.write('%s/%s' % (os.getcwd(), repo['path']))

    # http://wheel.readthedocs.org/en/latest/
    # wheel is binary packager for python/pip
    # we store all packages in binary wheel somewhere on the PC to avoid recompilation of packages

    # wheel needs pip 1.4, at the moment of writing it was development version
    # and we can't reinstall pip after virtualenv activation
    subprocess.call([pip_executable,
                     'install',
                     '-e',
                     'git+https://github.com/pypa/pip.git@978662b08b118bbeaae5aba57c823090b1c3b3ee#egg=pip'])

    # install requirements for wheel
    # need to uninstall distribute, because they conflict with setuptools
    subprocess.call([pip_executable, 'uninstall', 'distribute'])
    subprocess.call([pip_executable, 'install', 'https://bitbucket.org/pypa/setuptools/downloads/setuptools-0.8b3.tar.gz'])
    subprocess.call([pip_executable, 'install', 'wheel==0.16.0'])

    # adding BLAS and LAPACK libraries for CentOS installation
    if os.path.isfile('/usr/lib64/libblas.so.3'):
        logging.info('Linking libblas to venv')
        blas_so = os.path.join(env, 'lib64/libblas.so')
        os.symlink('/usr/lib64/libblas.so.3', blas_so)
        os.environ['BLAS'] = blas_so

    if os.path.isfile('/usr/lib64/liblapack.so.3'):
        logging.info('Linking liblapack to venv')
        lapack_so = os.path.join(env, 'lib64/liblapack.so')
        os.symlink('/usr/lib64/liblapack.so.3', lapack_so)
        os.environ['LAPACK'] = blas_so

    # linking PyQt for CentOS installation
    if os.path.isfile('/usr/lib64/python2.7/site-packages/PyQt4/QtCore.so'):
        logging.info('Linking qt for centos matplotlib backend')
        os.symlink('/usr/lib64/python2.7/site-packages/sip.so', os.path.join(env, 'lib/python2.7/site-packages/sip.so'))
        os.symlink('/usr/lib64/python2.7/site-packages/PyQt4', os.path.join(env, 'lib/python2.7/site-packages/PyQt4'))

    # readline must be come before everything else
    subprocess.call([easy_install_executable, '-q', 'readline==6.2.2'])

    # save settings
    settings = roboenv_default_settings
    save_settings(env, settings, args)


def install(args):
    if args.packages is None and args.requirement is None:
        logging.critical('You must give at least one requirement to install (see "roboenv install -h")')
        exit(1)


def download_cache(args):
    pass


def upload_cache(args):
    pass


def execute(argv):
    parser = argparse.ArgumentParser(description='Tool to make and configure python virtualenv,'
                                                 'setup necessary packages and cache them if necessary.',
                                     prog='roboenv')
    parser.add_argument('--cache', default='wheelhouse', help='binary package cache directory')
    subparsers = parser.add_subparsers(help='roboenv commands')

    init_parser = subparsers.add_parser('init', help='make roboenv')
    init_parser.add_argument('init_args',
                             nargs='+',
                             default=['.env'],
                             help='virtualenv arguments')
    init_parser.set_defaults(func=init)

    install_parser = subparsers.add_parser('install', help='install packages')
    install_parser.add_argument('-r', '--requirement',
                                nargs='+',
                                help='install all the packages listed in the given'
                                     'requirements file, this option can be used multiple times.')
    install_parser.add_argument('packages',
                                nargs='?',
                                help='packages to install in format <package name>==version')
    install_parser.set_defaults(func=install)

    download_cache_parser = subparsers.add_parser('download_cache', help='download cache from server or path')
    download_cache_parser.add_argument('url', help='cache url (directory, *.tar.gz, *.tar.bz or *.zip)')
    download_cache_parser.set_defaults(func=download_cache)

    upload_cache_parser = subparsers.add_parser('upload_cache', help='upload cache to server or path')
    upload_cache_parser.add_argument('url', help='cache url (directory, *.tar.gz, *.tar.bz or *.zip)')
    upload_cache_parser.set_defaults(func=upload_cache)

    args = parser.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    execute(sys.argv[1:])