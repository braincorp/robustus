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
    # If we are not on Travis, we only link to system-wide PyQt (for now), and return
    # The reason we do this hack for now is to avoid installing qt sdk on bstem
    # So, on bstem and linux machines we will need to sudo apt-get install python-pyside
    # Create links to system-wide PySide
    if sys.platform.startswith('darwin'):
        if os.path.isfile('/usr/local/lib/python2.7/site-packages/PyQt4/QtCore.so'):
            logging.info('Linking PyQt4 on macos')
            ln('/usr/local/lib/python2.7/site-packages/sip.so',
                os.path.join(robustus.env, 'lib/python2.7/site-packages/sip.so'), force = True)
            ln('/usr/local/lib/python2.7/site-packages/PyQt4',
                os.path.join(robustus.env, 'lib/python2.7/site-packages/PyQt4'), force = True)
        else:
            raise RequirementException('System-wide PyQt4 is missing, run: brew install PyQt4')   
    else:
        if os.path.isfile('/usr/lib64/python2.7/site-packages/PyQt4/QtCore.so'):
            logging.info('Linking PyQt4 on centos')
            ln('/usr/lib64/python2.7/site-packages/sip.so',
                os.path.join(robustus.env, 'lib/python2.7/site-packages/sip.so'), force = True)
            ln('/usr/lib64/python2.7/site-packages/PyQt4',
                os.path.join(robustus.env, 'lib/python2.7/site-packages/PyQt4'), force = True)
        elif os.path.isfile('/usr/lib/python2.7/dist-packages/PyQt4/QtCore.so'):
            logging.info('Linking PyQt4 on ubuntu')
            ln('/usr/lib/python2.7/dist-packages/sip.so',
                os.path.join(robustus.env, 'lib/python2.7/site-packages/sip.so'), force = True)
            ln('/usr/lib/python2.7/dist-packages/PyQt4',
                os.path.join(robustus.env, 'lib/python2.7/site-packages/PyQt4'), force = True)
        else:
            raise RequirementException('System-wide PySide is missing, run: sudo apt-get install python-pyside')
