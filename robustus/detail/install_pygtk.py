# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
from requirement import RequirementException
import logging
from utility import ln, write_file


def install(robustus, requirement_specifier, rob_file, ignore_index):
    # Softlinking to existing PyGtk. TODO: install via configure
    if os.path.isfile('/usr/lib/python2.7/dist-packages/pygtk.py'):
        logging.info('Linking pygtk')
        site_packages_dir = os.path.join(robustus.env, 'lib/python2.7/site-packages')
        files = ['pygtk.py', 'pygtk.pyc', 'gtk-2.0', 'glib', 'gobject', 'cairo']
        for f in files:
            ln('/usr/lib/python2.7/dist-packages/' + f,
               os.path.join(site_packages_dir, f), force = True)
        write_file(os.path.join(site_packages_dir, 'pygtk.pth'),
                   'w',
                   os.path.join(site_packages_dir, 'gtk-2.0'))
    else:
        raise RequirementException('System-wide PyGtk is missing')   
