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
    # Create links to system-wide PySide
    if sys.platform.startswith('darwin'):
        if os.path.isfile('/usr/local/lib/python2.7/site-packages/PySide/QtCore.so'):
            logging.info('Linking pyside on macos')
            ln('/usr/local/lib/python2.7/site-packages/sip.so',
                os.path.join(robustus.env, 'lib/python2.7/site-packages/sip.so'), force = True)
            ln('/usr/local/lib/python2.7/site-packages/PySide',
                os.path.join(robustus.env, 'lib/python2.7/site-packages/PySide'), force = True)
        else:
            raise RequirementException('System-wide PySide is missing, run: brew install pyside')   
    else:
        candidates = ['/usr/lib64/python2.7/site-packages/',
                      '/usr/lib/python2.7/dist-packages',
                      '/usr/local/lib/python2.7/dist-packages']
        for c in candidates:
            if os.path.isfile(os.path.join(c, 'PySide/QtCore.so')):
                logging.info('Linking pyside in %s' % c)
                ln(os.path.join(c, 'sip.so'),
                    os.path.join(robustus.env, 'lib/python2.7/site-packages/sip.so'), force = True)
                ln(os.path.join(c, 'PySide'),
                    os.path.join(robustus.env, 'lib/python2.7/site-packages/PySide'), force = True)
                break
        else:
            raise RequirementException('System-wide PySide is missing, run: sudo apt-get install python-pyside')
