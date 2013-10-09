# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import glob
import os
from requirement import RequirementException
import robustus
import shutil
import subprocess
import sys
import tarfile
import zipfile
import logging


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
    if force and os.path.exists(dst):
        os.remove(dst)
    os.symlink(src, dst)


def unpack(archive, path='.'):
    """
    unpack '.tar', '.tar.gz', '.tar.bz2' or '.zip' to path
    :param archive: archive file
    :param path: path where to unpack
    :return: None
    """
    if tarfile.is_tarfile(archive):
        f = tarfile.open(archive)
    elif zipfile.is_zipfile(archive):
        f = zipfile.open(archive)
    else:
        raise RuntimeError('unknown archive type %s' % archive)
    f.extractall(path)


def run_shell(command):
    logging.info('Running shell command: %s' % command)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output = p.communicate()[0]
    if p.returncode != 0:
        raise Exception('Error running %s, code=%s' % (command, p.returncode))
    return output


def execute_python_expr(env, expr):
    """
    Execute expression using env python interpreter.
    :param env: path to python environment
    :param expr: python expression
    :return: return code
    """
    python_executable = os.path.join(env, 'bin/python')
    if not os.path.isfile(python_executable):
        python_executable = os.path.join(env, 'bin/python27')
    if not os.path.isfile(python_executable):
        raise RuntimeError('can\'t find python executable in %s' % env)
    return subprocess.call([python_executable, '-c', expr])


def check_module_available(env, module):
    """
    check if speicified module is available to specified python environment.
    :param env: path to python environment
    :param module: module name
    :return: True if module available, False otherwise
    """
    return execute_python_expr(env, 'import %s' % module) == 0


def fix_rpath(env, executable, rpath):
    """
    Add rpath to list of rpaths of given executable. For osx also add @rpath/
    prefix to dependent library names (absolute paths are not prefixed).
    """
    if sys.platform.startswith('darwin'):
        # extract list o dependent library names
        otool_output = subprocess.check_output(['otool', '-L', executable])
        for line in otool_output.splitlines()[1:]:
            lib = line.split()[0]
            if not os.path.isabs(lib) and lib != os.path.basename(executable) and not lib.startswith('@rpath'):
                run_shell('install_name_tool -change %s %s "%s"' % (lib, '@rpath/' + lib, executable))
        return run_shell('install_name_tool -add_rpath "%s" "%s"' % (rpath, executable))
    else:
        patchelf_executable = os.path.join(env, 'bin/patchelf')
        if not os.path.isfile(patchelf_executable):
            raise RequirementException('In order to modify rpath of executable on unix system '
                                       'you need to install patchelf: robustus install patchelf')
        old_rpath = subprocess.check_output([patchelf_executable, '--print-rpath', executable])
        if len(old_rpath) > 1:
            new_rpath = old_rpath[:-1] + ':' + rpath
        else:
            new_rpath = rpath
        return run_shell('%s --set-rpath %s %s' % (patchelf_executable, new_rpath, executable))


def perform_standard_test(package,
                          python_imports=[],
                          package_files=[],
                          dependencies=[],
                          test_env='test_env',
                          test_cache='test_wheelhouse'):
    """
    create env, install package, check package is available,
    remove env, install package without index, check package is available
    :return: None
    """
    # create env and install bullet into it
    test_env = os.path.abspath(test_env)
    test_cache = os.path.abspath(test_cache)

    def check_module():
        for imp in python_imports:
            assert execute_python_expr(test_env, imp) == 0
        for file in package_files:
            assert os.path.isfile(os.path.join(test_env, file))

    def install_dependencies():
        for dep in dependencies:
            robustus.execute(['--env', test_env, 'install', dep])

    robustus.execute(['--cache', test_cache, 'env', test_env])
    install_dependencies()
    robustus.execute(['--env', test_env, 'install', package])
    check_module()
    shutil.rmtree(test_env)

    # install again, but using only cache
    robustus.execute(['--cache', test_cache, 'env', test_env])
    install_dependencies()
    robustus.execute(['--env', test_env, 'install', package, '--no-index'])
    check_module()
    shutil.rmtree(test_env)
    shutil.rmtree(test_cache)
