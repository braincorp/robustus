# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import glob
import os
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
    >>> parse_requirement('numpy')
    ('numpy', None)
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
    args = requirement.split('==')
    if len(args) == 1:
        package, version = args[0].strip(), None
    elif len(args) == 2:
        package, version = args[0].strip(), args[1].strip()
    else:
        raise RobustusException('invalid requirement specified "%s"' % requirement)

    if not package or (version is not None and not version):
        raise RobustusException('invalid requirement specified "%s"' % requirement)

    return package, version


def package_str(package, version):
    """
    Get string to install package using pip.
    :param package: name of the package.
    :param version: version of the package
    :return: string representing package
    Examples:
    >>> package_str('numpy', '1.7.2')
    numpy==1.7.2
    >>> package_str('numpy', None)
    numpy
    """
    if version is not None:
        return '%s==%s' % (package, version)
    return package


def read_requirement_file(requirement_file):
    requirements = []
    for line in open(requirement_file, 'r'):
        if line[0] == '#' or len(line) < 2:
            continue
        requirements.append(parse_requirement(line))
    return requirements