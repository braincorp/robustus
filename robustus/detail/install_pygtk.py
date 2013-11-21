# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
from requirement import RequirementException
import logging
from utility import ln


def install(robustus, requirement_specifier, rob_file, ignore_index):
    # Softlinking to existing PyGtk. TODO: install via configure
    if os.path.isfile('/usr/lib/python2.7/dist-packages/pygtk.py'):
        logging.info('Linking pygtk')
        files = ['pygtk.py', 'pygtk.pyc', 'pygtk.pth']
        for f in files:
            ln('/usr/lib/python2.7/dist-packages/' + f,
               os.path.join(robustus.env, 'lib/python2.7/site-packages/' + f), force = True)
    else:
        raise RequirementException('System-wide PyGtk is missing')   
