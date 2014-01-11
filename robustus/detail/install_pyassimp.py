# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
from requirement import RequirementException
import logging
from utility import ln


def install(robustus, requirement_specifier, rob_file, ignore_index):
    if os.path.isdir('/usr/lib/python2.7/dist-packages/pyassimp'):
        logging.info('Linking pyassimp on ubuntu...')
        ln('/usr/lib/python2.7/dist-packages/pyassimp', 
           os.path.join(robustus.env, 'lib/python2.7/site-packages/pyassimp'), force = True)
    else:
        raise RequirementException('System-wide pyassimp is missing, run: sudo apt-get install python-pyassimp')

