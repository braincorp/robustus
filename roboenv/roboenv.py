# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import argparse
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


def read_settings(env):
    # probably virtualenv wasn't created using roboenv, but that's ok
    if not os.path.isfile(roboenv_settings_file_path):
        return roboenv_default_settings

    return eval(open(roboenv_settings_file_path).read())


def init(args):
    env = args.init_args[-1]
    subprocess.call(['virtualenv'] + args.init_args)

    # save settings
    settings = roboenv_default_settings
    settings['cache'] = args.cache
    with open(os.path.join(env, roboenv_settings_file_path), 'w') as file:
        file.write(str(settings))


def install(args):
    if args.packages is None and args.requirement is None:
        print 'You must give at least one requirement to install (see "roboenv install -h")'
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