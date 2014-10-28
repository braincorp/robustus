# =============================================================================
# COPYRIGHT 2014 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
import shutil
import subprocess


def install(robustus, requirement_specifier, rob_file, ignore_index):
    cwd = os.getcwd()
    os.chdir(robustus.cache)

    install_dir = os.path.join(robustus.cache, 'vowpal_wabbit-%s' % requirement_specifier.version)
    if not os.path.isdir(install_dir) and not ignore_index:
        archive_name = '%s.tar.gz' % requirement_specifier.version
        subprocess.call(['wget', '-c', 'https://github.com/JohnLangford/vowpal_wabbit/archive/%s' % (archive_name,)])

        subprocess.call(['tar', '-xvzf', archive_name])

        # move sources to a folder in order to use a clean name for installation
        src_dir = 'vowpal_wabbit-%s' % requirement_specifier.version

        shutil.move(src_dir, src_dir + '_src')
        src_dir += '_src'

        src_dir = os.path.abspath(src_dir)
        os.mkdir(install_dir)
        os.chdir(src_dir)
        subprocess.call('make', shell=True)

        shutil.copy(os.path.join(src_dir, "vowpalwabbit/active_interactor"), os.path.join(install_dir, "active_interactor"))
        shutil.copy(os.path.join(src_dir, "vowpalwabbit/vw"), os.path.join(install_dir, "vw"))

        os.chdir(robustus.cache)
        shutil.rmtree(src_dir)

    venv_install_folder = os.path.join(robustus.env, 'vowpal_wabbit')
    if os.path.exists(venv_install_folder):
        shutil.rmtree(venv_install_folder)

    # copy to venv/bin
    venv_bin_folder = os.path.join(venv_install_folder, "bin")
    shutil.copy(os.path.join(install_dir, 'active_interactor'), venv_bin_folder)
    shutil.copy(os.path.join(install_dir, 'vw'), venv_bin_folder)

    os.chdir(cwd)
