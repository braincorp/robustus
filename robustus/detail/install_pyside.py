# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import argparse
import os
from requirement import RequirementException
import subprocess
from utility import unpack
import sys
import logging
from utility import ln


def install(robustus, requirement_specifier, rob_file, ignore_index):
    # If we are not on Travis, we only link to system-wide PySide (for now), and return
    # The reason we do this hack for now is to avoid installing qt sdk on bstem
    # So, on bstem and linux machines we will need to sudo apt-get install python-pyside
    # On Mac machines: to be updated soon! 
    if 'TRAVIS' not in os.environ: 
        # Create links to system-wide PySide
        if sys.platform.startswith('darwin'):
            raise RequirementException('On MacBook we are testing a solution. To be added soon...')
        else:
            if os.path.isfile('/usr/lib64/python2.7/site-packages/PySide/QtCore.so'):
                logging.info('Linking pyside on centos')
                ln('/usr/lib64/python2.7/site-packages/sip.so',
                    os.path.join(robustus.env, 'lib/python2.7/site-packages/sip.so'), force = True)
                ln('/usr/lib64/python2.7/site-packages/PySide',
                    os.path.join(robustus.env, 'lib/python2.7/site-packages/PySide'), force = True)
            elif os.path.isfile('/usr/lib/python2.7/dist-packages/PySide/QtCore.so'):
                logging.info('Linking pyside on ubuntu')
                ln('/usr/lib/python2.7/dist-packages/sip.so',
                    os.path.join(robustus.env, 'lib/python2.7/site-packages/sip.so'), force = True)
                ln('/usr/lib/python2.7/dist-packages/PySide',
                    os.path.join(robustus.env, 'lib/python2.7/site-packages/PySide'), force = True)
            else:
                raise RequirementException('System-wide PySide is missing, run: sudo apt-get install python-pyside')
    else:
        # If we are on Travis, then:
        # Install through wheeling
        robustus.install_through_wheeling(requirement_specifier, rob_file, ignore_index)
    
        # Need links to shared libraries
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
