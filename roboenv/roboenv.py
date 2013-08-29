# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import argparse
import importlib
import logging
import os
import subprocess
import sys


class RoboenvException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


def parse_requirement(requirement):
    """
    Extract requirement name and version from requirement string
    >>> parse_requirement('numpy==1.7.2')
    ('numpy', '1.7.2')
    >>> parse_requirement('   numpy == 1.7.2  ')
    ('numpy', '1.7.2')
    >>> parse_requirement('numpy')
    ('numpy', None)
    >>> parse_requirement('numpy==1.7.2==1.7.2')
    Traceback (most recent call last):
        ...
    RoboenvException: invalid requirement specified "numpy==1.7.2==1.7.2"
    >>> parse_requirement('   ')
    Traceback (most recent call last):
        ...
    RoboenvException: invalid requirement specified "   "
    >>> parse_requirement('numpy==')
    Traceback (most recent call last):
        ...
    RoboenvException: invalid requirement specified "numpy=="
    """
    args = requirement.split('==')
    if len(args) == 1:
        package, version = args[0].strip(), None
    elif len(args) == 2:
        package, version = args[0].strip(), args[1].strip()
    else:
        raise RoboenvException('invalid requirement specified "%s"' % requirement)

    if not package or (version is not None and not version):
        raise RoboenvException('invalid requirement specified "%s"' % requirement)

    return package, version


def read_requirement_file(requirement_file):
    requirements = []
    for line in open(requirement_file, 'r'):
        if line[0] == '#' or len(line) < 2:
            continue
        requirements.append(parse_requirement(line))
    return requirements


class Roboenv(object):
    settings_file_path = '.roboenv'
    installed_requirements_file_path = 'installed_requirements.txt'
    default_settings = {
        'cache': 'wheelhouse'
    }

    def __init__(self, args):
        """
        Initialize roboenv tool. Should be called if sys.executable is in roboenv
        @param: args - command line arguments
        """
        self.env = os.path.abspath(os.path.join(sys.executable, os.pardir, os.pardir))
        self.pip_executable = None
        self.easy_install_executable = None
        self.settings = self._override_settings(Roboenv.default_settings, args)

        # check if we are in roboenv environment
        if not os.path.isfile(Roboenv.settings_file_path):
            raise RoboenvException('bad roboenv ' + self.env + ': .roboenv settings file not found')
        self.pip_executable = os.path.join(self.env, 'bin/pip')
        if not os.path.isfile(self.pip_executable):
            raise RoboenvException('bad roboenv ' + self.env + ': pip not found')
        self.easy_install_executable = os.path.join(self.env, 'bin/easy_install')
        if not os.path.isfile(self.easy_install_executable):
            raise RoboenvException('bad roboenv ' + self.env + ': easy_install not found')

        # read settings
        settings = eval(open(Roboenv.settings_file_path).read())
        settings = Roboenv._override_settings(settings, args)

        # read cached packages
        req_file = os.path.join(self.cache, Roboenv.installed_requirements_file_path)
        if os.path.isfile(req_file):
            self.cached_packages = read_requirement_file(req_file)
        else:
            self.cached_packages = []

    @staticmethod
    def _override_settings(settings, args):
        # override settings with command line arguments
        if args.cache is not None:
            settings['cache'] = args.cache
        return settings

    @staticmethod
    def init(args):
        """
        Create roboenv.
        @param args: command line arguments
        """
        # create virtualenv
        env = args.init_args[-1]
        logging.info('Creating virtualenv')
        subprocess.call(['virtualenv'] + args.init_args)

        python_executable = os.path.abspath(os.path.join(env, 'bin/python'))
        pip_executable = os.path.abspath(os.path.join(env, 'bin/pip'))
        easy_install_executable = os.path.abspath(os.path.join(env, 'bin/easy_install'))

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

        # compose settings file
        settings = Roboenv._override_settings(Roboenv.default_settings, args)
        with open(os.path.join(env, Roboenv.settings_file_path), 'w') as file:
            file.write(str(settings))

        # install roboenv
        cwd = os.getcwd()
        script_dir = os.path.dirname(os.path.realpath(__file__))
        setup_dir = os.path.abspath(os.path.join(script_dir, os.path.pardir))
        os.chdir(setup_dir)
        subprocess.call([python_executable, 'setup.py', 'install'])
        os.chdir(cwd)

    def install_through_wheeling(self, package, version):
        """
        Check if package cache already contains package of specified version, if so install it.
        Otherwise make a wheel and put it into cache.
        Hope manual check for requirements file won't be necessary, waiting for pip 1.5 https://github.com/pypa/pip/issues/855
        :param package: package name
        :param version: package version string
        :return: None
        """
        package_str = '%s==%s' % (package, version)

        # if wheelhouse doesn't contain necessary requirement - make a wheel
        if (package, version) not in self.cached_packages:
            logging.info('Wheel not found, downloading package')
            subprocess.call([self.pip_executable,
                             'install',
                             '--download',
                             self.cache,
                             package_str])
            logging.info('Building wheel')
            subprocess.call([self.pip_executable,
                             'wheel',
                             '--no-index',
                             '--find-links=%s' % self.cache,
                             '--wheel-dir=%s' % self.cache,
                             package_str])
            logging.info('Done')

        # install from prebuilt wheel
        logging.info('Installing package from wheel')
        subprocess.call([self.pip_executable,
                         'install',
                         '--no-index',
                         '--use-wheel',
                         '--find-links=%s' % self.cache,
                         package_str])

    def _flush_cached_packages(self):
        # write cached packages list to cache requirements file
        f = open(os.path.join(self.cache, Roboenv.installed_requirements_file_path))
        for package, version in self.cached_packages:
            f.write('%s==%s' % (package, version))

    def install_package(self, package, version):
        # install package
        logging.info('Installing %s==%s' % (package, version))
        try:
            # try to use specific install script
            install_module = importlib.import_module('install_%s' % package)
            install_module.install(self, version)
        except ImportError:
            self.install_through_wheeling(package, version)
        logging.info('Done')

        # make sure requirements are saved in case of crash
        self._flush_cached_packages()

    def install(self, args):
        if args.packages is None and args.requirement is None:
            raise RoboenvException('You must give at least one requirement to install (see "roboenv install -h")')

        # construct requirements list
        requirements = []
        for requirement in args.install.packages:
            requirements.append(parse_requirement(requirement))
        for requirement_file in args.requirement:
            requirements += read_requirement_file(requirement_file)

        # install
        for package, version in requirements:
            self.install_package(package, version)

    def download_cache(self, args):
        """
        Download wheels (binary package archives) from wheelhouse_url and unzip them in wheelhouse
        @param wheelhouse: directory to store wheels
        @param wheelhouse_url: url where to grap wheels archive
        @return: None
        """
        cwd = os.getcwd()
        os.chdir(wheelhouse)
        try:
            wheelhouse_archive = wheelhouse_url.split('/')[-1]
            logging.info('Downloading ' + wheelhouse_url)
            # with -c option wget won't download file if it has been already downloaded
            # and continue if it was partially downloaded
            subprocess.call(['wget', '-c', wheelhouse_url])
            logging.info('Unzipping')
            subprocess.call(['tar', 'xjvf', wheelhouse_archive])
            logging.info('Done')
        except Exception as exc:
            logging.error(exc.message)
        os.chdir(cwd)

    def upload_cache(self, args):
        self._read_settings()
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
                             default=['.env', '--prompt', 'roboenv'],
                             help='virtualenv arguments')
    init_parser.set_defaults(func=Roboenv.init)

    install_parser = subparsers.add_parser('install', help='install packages')
    install_parser.add_argument('-r', '--requirement',
                                nargs='+',
                                help='install all the packages listed in the given'
                                     'requirements file, this option can be used multiple times.')
    install_parser.add_argument('packages',
                                nargs='?',
                                help='packages to install in format <package name>==version')
    install_parser.set_defaults(func=Roboenv.install)

    download_cache_parser = subparsers.add_parser('download_cache', help='download cache from server or path')
    download_cache_parser.add_argument('url', help='cache url (directory, *.tar.gz, *.tar.bz or *.zip)')
    download_cache_parser.set_defaults(func=Roboenv.download_cache)

    upload_cache_parser = subparsers.add_parser('upload_cache', help='upload cache to server or path')
    upload_cache_parser.add_argument('url', help='cache url (directory, *.tar.gz, *.tar.bz or *.zip)')
    upload_cache_parser.set_defaults(func=Roboenv.upload_cache)

    args = parser.parse_args(argv)
    if args.func == Roboenv.init:
        Roboenv.init(args)
    else:
        try:
            roboenv = Roboenv(args)
            args.func(roboenv, args)
        except RoboenvException as exc:
            logging.critical(exc.message)
            exit(1)


if __name__ == '__main__':
    execute(sys.argv[1:])