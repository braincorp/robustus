# =============================================================================
# COPYRIGHT 2014 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
import sys


def install(robustus, requirement_specifier, rob_file, ignore_index):
    if sys.platform.startswith('darwin'):
        logging.info('Skipping installation of evdev on mac. evdev is a linux package only.')
    else:
        robustus.install_through_wheeling(requirement_specifier, rob_file, ignore_index)
