# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import glob
import os
import re
import shutil


class RobustusException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


def write_file(filename, mode, data):
    """
    write or append string to a file
    :param filename: name of a file to write into
    :param mode: 'w', 'a' or other file open mode
    :param data: string or data to write
    :return: None
    """
    f = open(filename, mode)
    f.write(data)


def cp(mask, dest_dir):
    """
    copy files satisfying mask as unix cp
    :param mask: mask as in unix shell e.g. '*.txt', 'config.ini'
    :param dest_dir: destination directory
    :return: None
    """
    for file in glob.iglob(mask):
        if os.path.isfile(file):
            shutil.copy2(file, dest_dir)


def parse_requirement(requirement):
    """
    Extract requirement name and version from requirement string
    >>> parse_requirement('numpy==1.7.2')
    ('numpy', '1.7.2')
    >>> parse_requirement('   numpy == 1.7.2  ')
    ('numpy', '1.7.2')
    >>> parse_requirement('   numpy >= 1.7.2  ')
    ('numpy', '1.7.2')
    >>> parse_requirement('   numpy == 1.7.2  # comment')
    ('numpy', '1.7.2')
    >>> parse_requirement('numpy')
    ('numpy', None)
    >>> parse_requirement('pytest-cache==0.7')
    ('pytest-cache', '0.7')
    >>> parse_requirement('theano==0.6rc3')
    ('theano', '0.6rc3')
    >>> parse_requirement('numpy==1.7.2==1.7.2')
    Traceback (most recent call last):
        ...
    RobustusException: invalid requirement specified "numpy==1.7.2==1.7.2"
    >>> parse_requirement('   ')
    Traceback (most recent call last):
        ...
    RobustusException: invalid requirement specified "   "
    >>> parse_requirement('numpy==')
    Traceback (most recent call last):
        ...
    RobustusException: invalid requirement specified "numpy=="
    """
    mo = re.match(r'^\s*([\w-]+)\s*(?:(?:[>=]=)?\s*([\w.]+))?\s*(?:#.*)?$', requirement)
    if mo is None:
        raise RobustusException('invalid requirement specified "%s"' % requirement)
    return mo.group(1, 2)


def package_str(package, version):
    """
    Get string to install package using pip.
    :param package: name of the package.
    :param version: version of the package
    :return: string representing package
    Examples:
    >>> package_str('numpy', '1.7.2')
    'numpy==1.7.2'
    >>> package_str('numpy', None)
    'numpy'
    """
    if version is not None:
        return '%s==%s' % (package, version)
    return package


def package_to_rob(package, version):
    """
    Get filename to store information about cached package.
    @param package: package name
    @param version: version of the package
    @return: filename to store package information <package_name>__<package_version>.rob
    (dots replaced with underscores)
    Examples:
    >>> package_to_rob('numpy', '1.7.2')
    'numpy__1_7_2.rob'
    >>> package_to_rob('scipy', None)
    'scipy.rob'
    """
    if version is not None:
        return '%s__%s.rob' % (package, version.replace('.', '_'))
    return '%s.rob' % package


def rob_to_package(rob_file):
    """
    Return package name and version from package rob file name
    @param rob_file: rob file name
    @return: (package name, package version)
    Examples:
    >>> rob_to_package('numpy__1_7_2.rob')
    ('numpy', '1.7.2')
    >>> rob_to_package('scipy.rob')
    ('scipy', None)
    >>> rob_to_package('/path/to/somewhere/scipy.rob')
    ('scipy', None)
    """
    assert(rob_file.endswith('.rob'))

    rob_basename = os.path.basename(rob_file)
    if rob_basename.find('__') != -1:
        package, version = rob_basename[:-4].split('__')
        version = version.replace('_', '.')
    else:
        package = rob_basename[:-4]
        version = None

    return package, version


def read_requirement_file(requirement_file):
    requirements = []
    for line in open(requirement_file, 'r'):
        if line[0] == '#' or len(line) < 2:
            continue
        requirements.append(parse_requirement(line))
    return requirements