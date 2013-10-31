# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
from requirement import RequirementException
import subprocess
from utility import unpack


def install(robustus, requirement_specifier, rob_file, ignore_index):
    robustus.install_through_wheeling(requirement_specifier, rob_file, ignore_index)

    # need links to shared libraries
    pyside_setup_dir = os.path.join(robustus.cache, 'pyside-setup-master')
    if not os.path.isdir(pyside_setup_dir) and not ignore_index:
        os.chdir(robustus.cache)
        pyside_setup_archive = robustus.download('pyside-setup', 'master')
        unpack(pyside_setup_archive)

    cwd = os.getcwd()
    try:
        # run postinstall
        if not os.path.isdir(pyside_setup_dir):
            raise RequirementException('can\'t find pyside-%s in robustus cache' % requirement_specifier.version)
        os.chdir(pyside_setup_dir)
        retcode = subprocess.call([robustus.python_executable, 'pyside_postinstall.py', '-install'])
        if retcode != 0:
            raise RequirementException('failed to execute pyside postinstall script')
    finally:
        os.chdir(cwd)

    try:
        # linking PySide
        if sys.platform.startswith('darwin'):
            logging.info('Linking qt for MacOSX')
            if os.path.isfile('/Library/Python/2.7/site-packages/PySide/Qt.so'):
                ln('/Library/Python/2.7/site-packages/sip.so',
                    os.path.join(args.env, 'lib/python2.7/site-packages/sip.so'), force = True)
                ln('/Library/Python/2.7/site-packages/PySide',
                    os.path.join(args.env, 'lib/python2.7/site-packages/PySide'), force = True)
            elif os.path.isfile('/usr/local/lib/python2.7/site-packages/PySide/Qt.so'):
                ln('/usr/local/lib/python2.7/site-packages/sip.so',
                    os.path.join(args.env, 'lib/python2.7/site-packages/sip.so'), force = True)
                ln('/usr/local/lib/python2.7/site-packages/PySide',
                    os.path.join(args.env, 'lib/python2.7/site-packages/PySide'), force = True)
        else:
            if os.path.isfile('/usr/lib64/python2.7/site-packages/PySide/QtCore.so'):
                logging.info('Linking qt for centos matplotlib backend')
                ln('/usr/lib64/python2.7/site-packages/sip.so',
                    os.path.join(args.env, 'lib/python2.7/site-packages/sip.so'), force = True)
                ln('/usr/lib64/python2.7/site-packages/PySide',
                    os.path.join(args.env, 'lib/python2.7/site-packages/PySide'), force = True)
            elif os.path.isfile('/usr/lib/python2.7/dist-packages/PySide/QtCore.so'):
                logging.info('Linking qt for ubuntu matplotlib backend')
                ln('/usr/lib/python2.7/dist-packages/sip.so',
                    os.path.join(args.env, 'lib/python2.7/site-packages/sip.so'), force = True)
                ln('/usr/lib/python2.7/dist-packages/PySide',
                    os.path.join(args.env, 'lib/python2.7/site-packages/PySide'), force = True)
    except:
        pass
