# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
from requirement import RequirementException
from utility import cp, unpack
import shutil
import subprocess


def install(robustus, requirement_specifier, rob_file, ignore_index):
    patchelf_cache_dir = os.path.abspath(os.path.join(robustus.cache, 'patchelf-%s' % requirement_specifier.version))

    def in_cache():
        return os.path.isfile(os.path.join(patchelf_cache_dir, 'patchelf'))

    cwd = os.getcwd()
    if not in_cache() and not ignore_index:
        logging.info('Downloading patchelf')
        patchelf_tgz = robustus.download('patchelf', requirement_specifier.version)
        patchelf_archive_name = unpack(patchelf_tgz)

        logging.info('Building patchelf')
        os.chdir(patchelf_archive_name)
        subprocess.call(['./bootstrap.sh'])
        subprocess.call(['./configure'])
        subprocess.call(['make'])

        if os.path.isdir(patchelf_cache_dir):
            shutil.rmtree(patchelf_cache_dir)
        os.mkdir(patchelf_cache_dir)
        cp('./src/patchelf', patchelf_cache_dir)

        os.chdir(os.path.pardir)
        os.remove(patchelf_tgz)
        shutil.rmtree(patchelf_archive_name)
    os.chdir(cwd)

    if in_cache():
        patchelf_install_dir = os.path.join(robustus.env, 'bin')
        cp(os.path.join(patchelf_cache_dir, 'patchelf'), patchelf_install_dir)
    else:
        raise RequirementException('can\'t find patchelf-%s in robustus cache' % requirement_specifier.version)
