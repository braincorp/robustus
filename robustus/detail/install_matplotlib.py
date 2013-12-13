# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os


def install(robustus, requirement_specifier, rob_file, ignore_index):
    # First install it through the wheeling
    robustus.install_through_wheeling(requirement_specifier, rob_file, ignore_index)
    import matplotlib
    rcfile = matplotlib.matplotlib_fname()
    # Writing the settings to the file --- we may add more is needed
    logging.info('Writing the configuration file %s' % rcfile)
    with open(rcfile, 'w') as f:
        logging.info('Configuring matplotlib to use PySide as the backend...')
        f.write('backend : qt4agg\n')
        f.write('backend.qt4 : PySide\n')
