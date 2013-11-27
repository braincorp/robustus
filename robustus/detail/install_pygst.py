# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
from requirement import RequirementException
import logging
from utility import ln


def install(robustus, requirement_specifier, rob_file, ignore_index):
    if requirement_specifier.version != '0.10':
        raise RequirementException('Only 0.10 version of pygst is supported')

    # Softlinking to existing gst
    if os.path.isfile('/usr/lib/python2.7/dist-packages/pygst.py'):
        logging.info('Linking pygst')
        files = ['pygst.py', 'pygst.pyc', 'pygst.pth', 'gst-0.10',
                 'gstoption.so', 'gobject', 'glib']
        for f in files:
            ln('/usr/lib/python2.7/dist-packages/' + f,
               os.path.join(robustus.env, 'lib/python2.7/site-packages/' + f), force = True)
        
    else:
        raise RequirementException('System-wide pygst is missing')   
