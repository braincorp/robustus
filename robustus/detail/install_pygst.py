# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
from requirement import RequirementException
import logging
from utility import ln, write_file


def install(robustus, requirement_specifier, rob_file, ignore_index):
    if requirement_specifier.version != '0.10':
        raise RequirementException('Only 0.10 version of pygst is supported')

    # Softlinking to existing gst
    if os.path.isfile('/usr/lib/python2.7/dist-packages/pygst.py'):
        logging.info('Linking pygst')
        site_packages_dir = os.path.join(robustus.env, 'lib/python2.7/site-packages')
        files = ['pygst.py', 'gst-0.10', 'gstoption.so', 'glib', 'gobject']
        for f in files:
            src = os.path.join('/usr/lib/python2.7/dist-packages', f)
            if not os.path.exists(src):
                raise RequirementException('Required packages for system-wide pygst missing, %s not found' % f)
            ln(src, os.path.join(site_packages_dir, f), force=True)
        write_file(os.path.join(site_packages_dir, 'pygst.pth'),
                   'w',
                   os.path.join(site_packages_dir, 'gst-0.10'))
    else:
        raise RequirementException('System-wide pygst is missing')   
