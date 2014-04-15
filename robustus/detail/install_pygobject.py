# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
from requirement import RequirementException
import logging
from utility import ln


def install(robustus, requirement_specifier, rob_file, ignore_index):
    # Softlinking to existing PyGObject. TODO: install via configure
    if os.path.isdir('/usr/lib/python2.7/dist-packages/gobject'):
        logging.info('Linking PyGObject')
        site_packages_dir = os.path.join(robustus.env, 'lib/python2.7/site-packages')
        files = ['gobject', 'pygobject.py']
        for f in files:
            src = os.path.join('/usr/lib/python2.7/dist-packages', f)
            if not os.path.exists(src):
                raise RequirementException('Required packages for system-wide PyGObject missing, %s not found' % f)
            ln(src, os.path.join(site_packages_dir, f), force=True)
    else:
        raise RequirementException('System-wide PyGObject is missing')
