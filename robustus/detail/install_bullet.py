# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
from requirement import RequirementException
import shutil
import subprocess


def install(robustus, requirement_specifier, rob_file, ignore_index):
    bullet_cache_dir = os.path.abspath(os.path.join(robustus.cache, 'bullet-%s' % requirement_specifier.version))

    def in_cache():
        return os.path.isfile(os.path.join(bullet_cache_dir, 'lib/libBulletCollision.a'))

    if requirement_specifier.version == '2.81' or requirement_specifier.version == 'bc1':
        cwd = os.getcwd()

        if not in_cache() and not ignore_index:
            logging.info('Downloading bullet')
            if requirement_specifier.version == '2.81':
                bullet_archive_name = 'bullet-2.81-rev2613'
                bullet_tgz = bullet_archive_name + '.tgz'
                url = 'http://bullet.googlecode.com/files/' + bullet_tgz
            else:
                bullet_archive_name = 'bullet-bc1'
                bullet_tgz = bullet_archive_name + '.tar.gz'
                url = 'https://s3.amazonaws.com/thirdparty-packages.braincorporation.net/' + bullet_tgz

            subprocess.call(['wget', '-c', url, '-O', bullet_tgz])

            logging.info('Unpacking bullet')
            subprocess.call(['tar', 'xvzf', bullet_tgz])

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
            subprocess.call(['make', '-j4'])
            subprocess.call(['make', 'install'])

            os.chdir(os.path.pardir)
            os.remove(bullet_tgz)
            shutil.rmtree(bullet_archive_name)

        if in_cache():
            # install bullet somewhere into venv
            bullet_install_dir = os.path.join(robustus.env, 'lib/bullet-%s' % requirement_specifier.version)
            shutil.copytree(bullet_cache_dir, bullet_install_dir)
        else:
            raise RequirementException('can\'t find bullet-%s in robustus cache' % requirement_specifier.version)

        os.chdir(cwd)
    else:
        raise RequirementException('Can install only bullet 2.81/bc1')
