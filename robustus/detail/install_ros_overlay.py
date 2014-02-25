# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
from requirement import RequirementException
import shutil
import sys
import importlib
from utility import run_shell, add_source_ref, check_module_available


def _make_overlay_folder(robustus, requirement_specifier):
    overlay_folder = os.path.join(robustus.env, 'ros-overlay-source-', 
                                  requirement_specifier.rob_filename()[0:-3])
    if not os.path.isdir(overlay_folder):
        build = True
        os.makedirs(overlay_folder)
    else:
        build = False
    return overlay_folder, build


def _get_source(package):
    """Download source code for package."""
    logging.info('Obtaining ROS package %s' % package)
    # Break the git spec into components
    if package.startswith('git@'):
        # searching '@' after git@
        at_pos = package.find('@', 5) 
    else:
        at_pos = package.find('@')

    if at_pos > 0:
        origin, branch = package[:at_pos], package[at_pos+1:]
    else:
        origin, branch = package, None

    ret_code = run_shell('git clone "%s"' % origin)
    if ret_code != 0:
        raise Exception('git clone failed')

    if branch is not None:
        clone_folder = os.path.splitext(os.path.basename(origin))[0]
        ret_code = run_shell('cd "%s" && git checkout %s' %
                             (clone_folder, branch))
        if ret_code != 0:
            raise Exception('git checkout failed')


def _get_sources(packages):
    os.chdir('src')
    for p in packages:
        _get_source(p)
    os.chdir('..')


def _opencv_cmake_path(robustus):
    """Determine the path to the OpenCV cmake file (or None if
    OpenCV is not installed)."""

    opencv_packages = [p for p in robustus.cached_packages if p.name == 'opencv']

    if len(opencv_packages)==0:
        logging.info('No OpenCV found - ROS overlay will build without OpenCV')
        return None

    if len(opencv_packages)>1:
        logging.info('multiple opencv versions found: %s. ROS will build with %s' % (opencv_packages,
                                                                                     opencv_packages[-1]))

    cmake_path = os.path.join(robustus.cache, 'OpenCV-%s' % opencv_packages[-1].version,
                              'share', 'OpenCV')
    logging.info('OpenCV Cmake path is %s' % cmake_path)
    return cmake_path


def _ros_dep(env_source, robustus):
    """Run rosdep to install any dependencies (or error)."""

    logging.info('Running rosdep to install dependencies')
    rosdep = os.path.join(robustus.env, 'bin/rosdep')
    retcode = run_shell(rosdep +
                        ' install -r --from-paths src --ignore-src -y',
                        verbose=robustus.settings['verbosity'] >= 1)
    if retcode != 0:
        logging.warning('Failed to update ROS dependencies')


def install(robustus, requirement_specifier, rob_file, ignore_index):
    assert requirement_specifier.name == 'ros_overlay'
    packages = requirement_specifier.version.split(',')

    try:
        cwd = os.getcwd()
        overlay_src_folder, build = _make_overlay_folder(robustus, requirement_specifier)
        os.chdir(overlay_src_folder)
        overlay_install_folder = os.path.join(robustus.cache, 'ros-installed-overlay-%s'
                                              % requirement_specifier.version_hash())
        env_source = os.path.join(robustus.env, 'bin/activate')

        if build:
            logging.info('Building ros overlay in %s with versions %s'
                         ' install folder %s' % (overlay_src_folder, str(packages),
                                                 overlay_install_folder))

            os.mkdir(os.path.join(overlay_src_folder, 'src'))
            _get_sources(packages)
            _ros_dep(env_source, robustus)

            opencv_cmake_dir = _opencv_cmake_path(robustus)
            ret_code = run_shell('. "%s" && export OpenCV_DIR="%s" && catkin_make_isolated'
                                 ' --install-space %s --install' %
                                 (env_source, opencv_cmake_dir, overlay_install_folder) +
                                 ' --force-cmake --cmake-args -DCATKIN_ENABLE_TESTING=1',
                                 verbose=robustus.settings['verbosity'] >= 1)
            if ret_code != 0:
                raise RequirementException('Error during catkin_make')
        else:
            logging.info('ROS overlay cached %s' % overlay_install_folder)

        add_source_ref(robustus, os.path.join(overlay_install_folder, 'setup.sh'))

    except:
        if robustus.settings['debug']:
            logging.info('Not removing folder %s due to debug flag.' % overlay_src_folder)
        else:
            shutil.rmtree(overlay_src_folder, ignore_errors=True)
        raise
    finally:
        os.chdir(cwd)
