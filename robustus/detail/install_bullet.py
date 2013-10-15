# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
from requirement import RequirementException
from utility import unpack, safe_remove
import shutil
import subprocess


def install(robustus, requirement_specifier, rob_file, ignore_index):
    bullet_cache_dir = os.path.abspath(os.path.join(robustus.cache, 'bullet-%s' % requirement_specifier.version))

    def in_cache():
        return os.path.isfile(os.path.join(bullet_cache_dir, 'lib/libBulletCollision.a'))

    if not in_cache() and not ignore_index:
        cwd = os.getcwd()
        bullet_archive = None
        bullet_archive_name = None
        try:
            bullet_archive = robustus.download('bullet', requirement_specifier.version)
            bullet_archive_name = unpack(bullet_archive)

            logging.info('Building bullet')
            os.chdir(bullet_archive_name)
            subprocess.call(['cmake', '.',
                             '-G', "Unix Makefiles",
                             '-DCMAKE_INSTALL_PREFIX=%s' % bullet_cache_dir,
                             '-DCMAKE_CXX_FLAGS=-fPIC',
                             '-DBUILD_NVIDIA_OPENCL_DEMOS:BOOL=OFF',
                             '-DBUILD_INTEL_OPENCL_DEMOS:BOOL=OFF',
                             '-DCMAKE_C_COMPILER=gcc',
                             '-DCMAKE_CXX_COMPILER=g++'])
            retcode = subprocess.call(['make', '-j4'])
            if retcode != 0:
                raise RequirementException('bullet build failed')
            retcode = subprocess.call(['make', 'install'])
            if retcode != 0:
                raise RequirementException('bullet "make install" failed')
        finally:
            safe_remove(bullet_archive)
            safe_remove(bullet_archive_name)
            os.chdir(cwd)

    if in_cache():
        # install bullet somewhere into venv
        bullet_install_dir = os.path.join(robustus.env, 'lib/bullet-%s' % requirement_specifier.version)
        if os.path.exists(bullet_install_dir):
            shutil.rmtree(bullet_install_dir)
        shutil.copytree(bullet_cache_dir, bullet_install_dir)
    else:
        raise RequirementException('can\'t find bullet-%s in robustus cache' % requirement_specifier.version)
