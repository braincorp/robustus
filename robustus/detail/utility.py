# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import glob
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
import sys
import tty
import termios


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


def safe_move(src, dst):
    """
    safely move single file or directory as shutil.move
    with no overwrites
    :param src: source file/dir
    :param dst: destination file/dir
    :return: None
    """
    if not os.path.exists(src):
        raise RuntimeError('src does not exist: %s' % src)
    if os.path.exists(dst) and not os.path.isdir(dst):
        raise RuntimeError('dst exists and is not dir: %s' % dst)
    shutil.move(src, dst)


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


def is_self_test():
    """
    Check if this execution is robustus test run on Travis.
    """
    return 'TRAVIS' in os.environ and 'robustus' in os.environ['TRAVIS_REPO_SLUG']


class OutputCapture(object):
    """
    Helper to capture output produced by command and print dots instead.
    By default prints dots every ten seconds.
    """
    def __init__(self, verbose, secs_between_dots=10, logfile=None):
        self.verbose = verbose
        self.secs_between_dots = secs_between_dots
        if not verbose:
            self.logfile = tempfile.TemporaryFile() if logfile is None else logfile
        self.prev_time = time.time()
        self.dot_produced = False
        logging.getLogger().handlers[0].flush()
        # produce first dot during self test, because many small shell commands are executed and test
        # mail fail to produce output within 10 mins
        if not verbose and is_self_test():
            sys.stderr.write('.')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()

    def update(self, output=''):
        if not self.verbose:
            if len(output) > 0:
                self.logfile.write(output)
            if time.time() - self.prev_time > self.secs_between_dots:
                sys.stderr.write('.')
                self.prev_time = time.time()
                self.dot_produced = True
        elif len(output) > 0:
            sys.stderr.write(output,)

    def finish(self):
        if not self.verbose:
            # during self-test on TRAVIS we want to just see the dots during testing, i.e.
            # robustus/tests/test_bullet.py:10: test_bullet_installation ..................PASSED
            # while with regular robustus use we want regular line separation
            # Running shell command: ['cmd1']...
            # Running shell command: ['cmd2']...
            if not is_self_test() and self.dot_produced:
                sys.stderr.write('\n')
            self.logfile.close()

    def read_captured_output(self):
        self.logfile.seek(0)
        return self.logfile.read()


def download(url, filename=None, verbose=False):
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
    logging.info("Downloading: %s Bytes: %s" % (filename, file_size))

    with open(filename, 'wb') as f, OutputCapture(verbose) as oc:
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
                oc.update(status,)
                prev_percent = percent_downloaded
            else:
                oc.update()

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


def run_shell(command, verbose=False, return_output=False, **kwargs):
    """
    Run command logging accordingly to the verbosity level.
    """
    logging.info('Running shell command: %s' % command)
    # some problem using temporary files to capture output
    with OutputCapture(verbose) as oc, tempfile.TemporaryFile('w+') as stdout:
        # there is problem with PIPE in case of large output, so use logfile
        if 'stdout' in kwargs:
            stdout.close()
            stdout = kwargs['stdout']
        else:
            kwargs['stdout'] = stdout
        readable = 'r' in stdout.mode or '+' in stdout.mode
        if 'stderr' not in kwargs:
            # do not use subprocess.STDOUT
            # http://stackoverflow.com/questions/11495783/redirect-subprocess-stderr-to-stdout
            kwargs['stderr'] = stdout
        p = subprocess.Popen(command, **kwargs)
        s = 0
        while p.poll() is None:
            # writing to stdout moves cursor further, so need to seek back to read written data
            stdout.seek(s)
            oc.update(stdout.readline() if readable else '')
            s = stdout.tell()
        # read rest
        stdout.seek(s)
        oc.update(stdout.read() if readable else '')

        # print log in case of failure
        if not oc.verbose and p.returncode != 0:
            logging.error('Failed with output:\n%s' % oc.read_captured_output())

        if return_output:
            return p.returncode, oc.read_captured_output()

    return p.returncode


def check_run_shell(command, verbose=False, **kwargs):
    """
    run_shell with provided args, on failure raise subprocess.CalledProcessError
    """
    ret = run_shell(command, verbose, **kwargs)
    if ret != 0:
        raise subprocess.CalledProcessError(ret, command)


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


def fix_rpath(robustus, env, executable, rpath):
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
                run_shell('install_name_tool -change %s %s "%s"' % (lib, '@rpath/' + lib, executable), shell=True)
        try:
            run_shell('install_name_tool -delete_rpath "%s" "%s"' % (rpath, executable), shell=True)
        except:
            pass
        return run_shell('install_name_tool -add_rpath "%s" "%s"' % (rpath, executable), shell=True)
    else:
        patchelf_executable = os.path.join(env, 'bin/patchelf')
        if not os.path.isfile(patchelf_executable):
            logging.info('patchelf is not installed. Installing')
            robustus.install_requirement(RequirementSpecifier(name = 'patchelf',
                                                              version = '6fb4cdb'),
                                         ignore_index = False, tag = None)

        old_rpath = subprocess.check_output([patchelf_executable, '--print-rpath', executable])
        if len(old_rpath) > 1:
            new_rpath = old_rpath[:-1] + ':' + rpath
        else:
            new_rpath = rpath
        return run_shell('%s --set-rpath %s %s' % (patchelf_executable, new_rpath, executable), shell=True)


def get_single_char():
    """Get a single character of input from stdin (without waiting for a newline)."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch
