# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
import platform
import subprocess
import shutil
import sys
from utility import cp
from requirement import RequirementException


def install(robustus, requirement_specifier, rob_file, ignore_index):
    try:
        import cv2
    except ImportError:
        if platform.linux_distribution()[0] == 'CentOS':
            # linking opencv for CentOs
            logging.info('Linking opencv for CentOS')
            os.symlink('/usr/lib64/python2.7/site-packages/cv2.so', os.path.join(robustus.env, 'lib/python2.7/site-packages/cv2.so'))
            os.symlink('/usr/lib64/python2.7/site-packages/cv.py', os.path.join(robustus.env, 'lib/python2.7/site-packages/cv.py'))
        elif requirement_specifier.version == '2.4.4' or requirement_specifier.version == '2.4.2':
            cwd = os.getcwd()
            if requirement_specifier.version == '2.4.4':
                cv_work_dir = os.path.join(cwd, 'opencv-2.4.4')
            elif requirement_specifier.version == '2.4.2':
                cv_work_dir = os.path.join(cwd, 'OpenCV-2.4.2')
            cv_install_dir = os.path.join(robustus.cache, 'opencv-%s' % requirement_specifier.version)
            cv2so = os.path.join(cv_install_dir, 'lib/python2.7/site-packages/cv2.so')

            def in_cache():
                return os.path.isfile(cv2so)

            if not in_cache() and not ignore_index:
                logging.info('Downloading OpenCV')
                cv_tar = os.path.join(cwd, 'opencv-%s.tar.bz2' % requirement_specifier.version)
                opencv_unix = 'http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/'
                if requirement_specifier.version == '2.4.4':
                    url = opencv_unix + '2.4.4/OpenCV-2.4.4a.tar.bz2/download'
                elif requirement_specifier.version == '2.4.2':
                    url = opencv_unix + '2.4.2/OpenCV-2.4.2.tar.bz2/download'
                subprocess.call(['wget', '-c', url, '-O', cv_tar])

                logging.info('Unpacking OpenCV')
                subprocess.call(['tar', 'xvjf', cv_tar])

                logging.info('Building OpenCV')
                cv_build_dir = os.path.join(cv_work_dir, 'build')
                if not os.path.isdir(cv_build_dir):
                    os.mkdir(cv_build_dir)
                os.chdir(cv_build_dir)
                subprocess.call(['cmake',
                                 '../',
                                 '-DPYTHON_EXECUTABLE=%s' % sys.executable,
                                 '-DBUILD_NEW_PYTHON_SUPPORT=ON',
                                 '-DBUILD_TESTS=OFF',
                                 '-DBUILD_PERF_TESTS=OFF',
                                 '-DBUILD_DOCS=OFF',
                                 '-DBUILD_opencv_apps=OFF',
                                 '-DBUILD_opencv_java=OFF',
                                 '-DWITH_CUDA=OFF',
                                 '-DCMAKE_INSTALL_PREFIX=%s' % cv_install_dir])
                subprocess.call(['make', '-j4'])

                # install into wheelhouse
                if not os.path.isdir(cv_install_dir):
                    os.mkdir(cv_install_dir)
                subprocess.call(['make', 'install'])

                # cleanup
                shutil.rmtree(cv_work_dir)
                os.chdir(cwd)

            if in_cache():
                logging.info('Linking OpenCV cv2.so to virtualenv')
                python_dir = os.path.join(os.path.dirname(sys.executable), os.path.pardir)
                cp(os.path.join(cv_install_dir, 'lib/python2.7/site-packages/*'),
                   os.path.join(python_dir, 'lib/python2.7/site-packages'))
            else:
                raise RequirementException('can\'t find opencv-%s in robustus cache' % requirement_specifier.version)
        else:
            raise RequirementException('Can install only opencv 2.4.2/2.4.4')
