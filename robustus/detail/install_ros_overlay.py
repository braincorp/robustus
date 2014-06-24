# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
from requirement import RequirementException
import shutil
import sys
import platform
import importlib
import ros_utils
from utility import unpack, safe_remove, safe_move, run_shell, add_source_ref, check_module_available


def _make_overlay_folder(robustus, req_hash):
    overlay_folder = os.path.join(robustus.env, 'ros-overlay-source-' + req_hash)
    if not os.path.isdir(overlay_folder):
        os.makedirs(overlay_folder)

    logging.info('Overlay source folder %s' % overlay_folder)
    return overlay_folder


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

    cd_path = None
    if branch is None:
        arrow_pos = origin.find('->')
        if arrow_pos > 0:
            origin, cd_path = origin[:arrow_pos], origin[arrow_pos+2:]
    else:
        arrow_pos = branch.find('->')
        if arrow_pos > 0:
            branch, cd_path = branch[:arrow_pos], branch[arrow_pos+2:]

    ret_code = run_shell('git clone "%s"' % origin, shell=True)
    if ret_code != 0:
        raise Exception('git clone failed')

    clone_folder = os.path.splitext(os.path.basename(origin))[0]
    if branch is not None:
        ret_code = run_shell('cd "%s" && git checkout %s' % (clone_folder, branch), shell=True)
        if ret_code != 0:
            raise Exception('git checkout failed')

    if cd_path is not None:
        logging.info('Extracting %s package from %s repo' % (cd_path, origin))
        folder_to_take_out = os.path.join(clone_folder, cd_path)
        shutil.move(folder_to_take_out, './')
        shutil.rmtree(clone_folder)


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

    if platform.machine() == 'armv7l':
        # install dependencies in venv, may throw
        # NOTE: This should not be necessary for the ROS packages.
        robustus.execute(['install',
                          'catkin_pkg==0.1.24',
                          'rosinstall==0.6.30',
                          'rosinstall_generator==0.1.4',
                          'wstool==0.0.4',
                          'empy==3.3.2',
                          'rosdep==0.10.27',
                          'sip'])

        # init rosdep, rosdep can already be initialized resulting in error, that's ok
        os.system('sudo rosdep init') # NOTE: This is called by the "bstem.ros" Debian control scripts.

        # update ros dependencies # NOTE: This cannot be called by the "bstem.ros" Debian control scripts.
        retcode = run_shell('rosdep update',
                            shell=True,
                            verbose=robustus.settings['verbosity'] >= 1)
        if retcode != 0:
            raise RequirementException('Failed to update ROS dependencies')

        os.system('sudo apt-get update') # NOTE: This cannot be called by the "bstem.ros" Debian control scripts.
        rosdep = os.path.join('sudo rosdep')
    else:
        rosdep = os.path.join(robustus.env, 'bin/rosdep')

    retcode = run_shell(rosdep +
                        ' install -r --from-paths src --ignore-src -y',
                        shell=True,
                        verbose=robustus.settings['verbosity'] >= 1)
    if retcode != 0:
        logging.warning('Failed to update ROS dependencies')


def install(robustus, requirement_specifier, rob_file, ignore_index):
    assert requirement_specifier.name == 'ros_overlay'
    packages = requirement_specifier.version.split(',')
    
    cwd = os.getcwd()
    try:
        env_source = os.path.join(robustus.env, 'bin/activate')

        # NOTE: If ROS is not installed, the following returns an empty string.
        def get_ros_install_dir(env_source):
            ret_code, output = run_shell('. "%s" && python -c "import ros ; print ros.__file__"' % env_source, shell=True, return_output=True)
            if ret_code != 0:
                logging.info('get_ros_install_dir() failed: ret_code is %d: %s' % (ret_code, output))
                return ''
            if len(output.splitlines()) != 1:
                logging.info('get_ros_install_dir() failed: Too many lines in output: %s' % output)
                return ''
            output_dirname = os.path.dirname(output)
            ros_install_dir = os.path.abspath(os.path.join(output_dirname, os.pardir, os.pardir, os.pardir, os.pardir))
            if not os.path.isdir(ros_install_dir):
                logging.info('get_ros_install_dir() failed: ros_install_dir not a directory: %s' % ros_install_dir)
                return ''
            return ros_install_dir

        ros_install_dir = get_ros_install_dir(env_source)

        req_name = "ros-installed-overlay"
        ver_hash = requirement_specifier.version_hash()
        logging.info('Hashing ROS overlay on (robustus.env, ver_hash, ros_install_dir) = ("%s", "%s", "%s")' % (robustus.env, ver_hash, ros_install_dir))
        req_hash = ros_utils.hash_path(robustus.env, ver_hash, ros_install_dir)
        overlay_install_folder = os.path.join(robustus.cache, '%s-%s'
                                              % (req_name, req_hash))

        if not os.path.isdir(overlay_install_folder):
            overlay_archive = robustus.download_compiled_archive(req_name, req_hash)
            if overlay_archive:
                overlay_archive_name = unpack(overlay_archive)

                logging.info('Initializing compiled ROS overlay')
                # install into wheelhouse
                safe_move(overlay_archive_name, overlay_install_folder)
                safe_remove(overlay_archive)
            else:
                overlay_src_folder = _make_overlay_folder(robustus, req_hash)
                os.chdir(overlay_src_folder)

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
                                     ' --force-cmake --cmake-args -DCATKIN_ENABLE_TESTING=1 ',
                                     shell=True,
                                     verbose=robustus.settings['verbosity'] >= 1)
                if ret_code != 0:
                    raise RequirementException('Error during catkin_make')
        else:
            logging.info('ROS overlay cached %s' % overlay_install_folder)

        add_source_ref(robustus, os.path.join(overlay_install_folder, 'setup.sh'))

    except RequirementException:
        if robustus.settings['debug']:
            logging.info('Not removing folder %s due to debug flag.' % overlay_src_folder)
        else:
            shutil.rmtree(overlay_src_folder, ignore_errors=True)
            shutil.rmtree(overlay_install_folder, ignore_errors=True)
        raise
    finally:
        os.chdir(cwd)
