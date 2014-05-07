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
    # So, on bstem and linux machines we will need to sudo apt-get install python-sip
    # On Mac machines use brew
    assert 'TRAVIS' not in os.environ
    # Create links to system-wide PySide
    if sys.platform.startswith('darwin'):
        if os.path.isfile('/usr/local/lib/python2.7/site-packages/sipconfig.py'):
            logging.info('Linking sipconfig on macos')
            files_to_link = ['sipconfig.py', 'sip.so', 'sipdistutils.py']
            for f in files_to_link:
                ln(os.path.join('/usr/local/lib/python2.7/site-packages/', f),
                   os.path.join(robustus.env, 'lib/python2.7/site-packages/', f),
                   force = True)
        else:
            raise RequirementException('System-wide SIP is missing, run: brew install sip')  
    elif sys.platform.startswith('linux'):
        if os.path.isfile('/usr/lib/python2.7/dist-packages/sipconfig.py'):
            logging.info('Linking pyside on centos')
            ln('/usr/lib/python2.7/dist-packages/sipconfig.py',
               os.path.join(robustus.env, 'lib/python2.7/site-packages/sipconfig.py'),
               force = True)
            ln('/usr/lib/python2.7/dist-packages/sipconfig_nd.py',
               os.path.join(robustus.env, 'lib/python2.7/site-packages/sipconfig_nd.py'),
               force = True)
        else:
            raise RequirementException('System-wide SIP is missing, run: sudo apt-get install python-sip')
    else:
        raise RequirementException('SIP not support on this platform')
