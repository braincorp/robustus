# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import glob
import os
from requirement import RequirementException
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile
import logging
import urllib2
import os
import logging


def add_source_ref(robustus, source_path):
    """Add a line to the active file to source from source_path when
    activate is run.

    If the source line already exists we avoid duplication."""
    
    py_activate_file = os.path.join(robustus.env, 'bin', 'activate')
    
    source_line = '. ' + os.path.abspath(source_path) + '\n'
    if source_line not in open(py_activate_file, 'r').readlines():
        logging.info('Adding source line %s' % source_line)
        open(py_activate_file, 'a').write(
            '\n# Added by robustus\n' + source_line + '\n')
    else:
        logging.info('Source line %s already in activate file' % source_line)


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
    :param src: source file/dir
    :param dst: destination file/dir
    :param force: remove destination file/dir
    :return: None
    """
    # os.path.exists returns False for broken links. lexists returns True
    if force and os.path.lexists(dst):
        os.unlink(dst)
    os.symlink(src, dst)


def which(program):
    import os

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def download(url, filename=None):
    """
    download file from url, store it under name
    :param url: url to download file
    :param filename: location to store downloaded file, if None try to extract filename from url
    :return: filename of downloaded file
    """
    if filename is None:
        filename = url.split('/')[-1]

    u = urllib2.urlopen(url)
    file_size = int(u.info().getheaders("Content-Length")[0])
    logging.info("Downloading: %s Bytes: %s" % (file, file_size))

    with open(filename, 'wb') as f:
        file_size_dl = 0
        prev_percent = 0
        block_sz = 131072
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            percent_downloaded = file_size_dl * 100. / file_size
            if percent_downloaded > prev_percent + 1:
                status = "%10d  [%3.2f%%]\r" % (file_size_dl, percent_downloaded)
                logging.info(status,)
                prev_percent = percent_downloaded
        f.close()

    return filename


def unpack(archive, path='.'):
    """
    unpack '.tar', '.tar.gz', '.tar.bz2' or '.zip' to path
    :param archive: archive file
    :param path: path where to unpack
    :return: archive name without extension, this is convenient as most
    packages archives are compressed folders of the same name
    """
    logging.info('Unpacking ' + archive)
    if tarfile.is_tarfile(archive):
        f = tarfile.open(archive)
    elif zipfile.is_zipfile(archive):
        f = zipfile.ZipFile(archive)
    else:
        raise RuntimeError('unknown archive type %s' % archive)
    f.extractall(path)

    root, ext = os.path.splitext(archive)
    if ext in ['.gz', '.bz2']:
        root = os.path.splitext(root)[0]
    return os.path.abspath(root)


def safe_remove(path):
    """
    Remove file or directory if it exists.
    """
    if path is None:
        return
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)


def run_shell(command, shell=True, verbose=False, **kwargs):
    """
    Run command logging accordingly to the verbosity level.
    """
    logging.info('Running shell command: %s' % command)
    if verbose:
        # poll process for new output until finished
        p = subprocess.Popen(command,
                             shell=shell,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             **kwargs)
        while p.poll() is None:
            print p.stdout.readline(),
    else:
        # redirect log to temporary file
        with tempfile.TemporaryFile() as logfile:
            p = subprocess.Popen(command,
                                 shell=shell,
                                 stdout=logfile,
                                 stderr=subprocess.STDOUT,
                                 **kwargs)

            # print dots to wake TRAVIS
            secs = 0
            secs_between_dots = 10
            sys.stdout.write('Working')
            sys.stdout.flush()
            while p.poll() is None:
                # poll more frequently than print dots to stop as soon as process finished
                time.sleep(1)
                secs += 1
                if secs >= secs_between_dots:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    secs = 0
            sys.stdout.write('\n')

            # print log in case of failure
            if p.returncode != 0:
                print 'Shell command "%s" failed' % str(command)
                logfile.seek(0)
                print logfile.read()

    return p.returncode


def execute_python_expr(env, expr, shell_script=None):
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
    cmd = python_executable + ' -c "' + expr + '"'
    if shell_script is not None:
        cmd = shell_script + ' && ' + cmd
    return subprocess.call(cmd, shell=True)


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
        try:
            run_shell('install_name_tool -delete_rpath "%s" "%s"' % (rpath, executable))
        except:
            pass
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
