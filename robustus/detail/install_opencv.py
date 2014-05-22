# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
import platform
import glob
import sys
from utility import cp, unpack, safe_remove, fix_rpath, ln, run_shell, check_module_available
from requirement import RequirementException


def install(robustus, requirement_specifier, rob_file, ignore_index):
    # Make sure numpy is installed - to avoid weird error when bindings
    # are silently not generated.
    if not check_module_available(robustus.env, 'numpy'):
        raise RequirementException('numpy is required for opencv')

    if platform.linux_distribution()[0] == 'CentOS':
        # linking opencv for CentOs
        logging.info('Linking opencv for CentOS')
        os.symlink('/usr/lib64/python2.7/site-packages/cv2.so', os.path.join(robustus.env, 'lib/python2.7/site-packages/cv2.so'))
        os.symlink('/usr/lib64/python2.7/site-packages/cv.py', os.path.join(robustus.env, 'lib/python2.7/site-packages/cv.py'))
    else:
        cv_install_dir = os.path.join(robustus.cache, 'OpenCV-%s' % requirement_specifier.version)
        cv2so = os.path.join(cv_install_dir, 'lib/python2.7/site-packages/cv2.so')

        def in_cache():
            return os.path.isfile(cv2so)

        versions_to_fix_rpath = ['2.4.7', '2.4.8']

        if not in_cache() and not ignore_index:
            cwd = os.getcwd()
            opencv_archive = None
            opencv_archive_name = None
            try:
                opencv_archive = robustus.download('OpenCV', requirement_specifier.version)
                opencv_archive_name = unpack(opencv_archive)

                logging.info('Building OpenCV')
                cv_build_dir = os.path.join(opencv_archive_name, 'build')
                if not os.path.isdir(cv_build_dir):
                    os.mkdir(cv_build_dir)
                os.chdir(cv_build_dir)
                # TODO: check that PYTHON_LIBRARY variable is set up correctly
                run_shell(['cmake',
                           '../',
                           '-DPYTHON_EXECUTABLE=%s' % robustus.python_executable,
                           '-DBUILD_NEW_PYTHON_SUPPORT=ON',
                           '-DBUILD_TESTS=OFF',
                           '-DBUILD_PERF_TESTS=OFF',
                           '-DBUILD_DOCS=OFF',
                           '-DBUILD_opencv_apps=OFF',
                           '-DBUILD_opencv_java=OFF',
                           '-DWITH_CUDA=OFF',
                           '-DCMAKE_INSTALL_PREFIX=%s' % cv_install_dir],
                          verbose=robustus.settings['verbosity'] >= 1)
                retcode = run_shell(['make', '-j4'], verbose=robustus.settings['verbosity'] >= 1)
                if retcode != 0:
                    raise RequirementException('OpenCV build failed')

                # install into wheelhouse
                if not os.path.isdir(cv_install_dir):
                    os.mkdir(cv_install_dir)
                retcode = run_shell(['make', 'install'], verbose=robustus.settings['verbosity'] >= 1)
                if retcode != 0:
                    raise RequirementException('OpenCV installation failed')
            finally:
                safe_remove(opencv_archive)
                safe_remove(opencv_archive_name)
                os.chdir(cwd)

            if in_cache() and requirement_specifier.version in versions_to_fix_rpath:
                # fix rpath for all dynamic libraries of cv2
                all_cv_dlibs = os.path.abspath(os.path.join(cv_install_dir, 'lib'))
                if sys.platform.startswith('darwin'):
                    libs = glob.glob(os.path.join(all_cv_dlibs, '*.dylib'))
                else:
                    libs = glob.glob(os.path.join(all_cv_dlibs, '*.so'))
                for lib in libs:
                    fix_rpath(robustus, robustus.env, lib, cv_install_dir)

        if in_cache():
            logging.info('Copying OpenCV cv2.so to virtualenv')
            cp(os.path.join(cv_install_dir, 'lib/python2.7/site-packages/*'),
               os.path.join(robustus.env, 'lib/python2.7/site-packages'))
            if requirement_specifier.version in versions_to_fix_rpath:
                # fix rpath for cv2
                cv2lib = os.path.join(robustus.env, 'lib/python2.7/site-packages/cv2.so')
                fix_rpath(robustus, robustus.env, cv2lib, cv_install_dir)  
        else:
            raise RequirementException('can\'t find OpenCV-%s in robustus cache' % requirement_specifier.version)
