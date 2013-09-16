# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import glob
import os
import shutil


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


def ln(src, dst, force=False):
    """
    make symlink as unix ln
    :param src: source file
    :param dst: destination file
    :param force: remove destination file
    :return: None
    """
    if force and os.path.isfile(dst):
        os.remove(dst)
    os.symlink(src, dst)