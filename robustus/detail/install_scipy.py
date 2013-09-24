# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
import sys


def install(robustus, requirement_specifier, rob_file, ignore_index):
    logging.info('Cheking for scipy')
    try:
        import scipy
    except ImportError:
        if sys.platform.startswith('darwin'):
            # to make scipy compile on OS X, this flag might be neccesary to
            # allow dynamic linking
            logging.info('Changing LDFLAGS on OS X to compile scipy')
            os.environ['CC'] = 'clang'
            os.environ['CXX'] = 'clang'
            try:
                old_ld_flags = os.environ['LDFLAGS']
            except KeyError:
                old_ld_flags = None
            os.environ['LDFLAGS'] = '-arch x86_64 -Wall -undefined dynamic_lookup -bundle'
            os.environ['FFLAGS'] = '-arch x86_64 -ff2c'

        robustus.install_through_wheeling(requirement_specifier, rob_file, ignore_index)

        if sys.platform.startswith('darwin'):
            # undo LDFLAGS changes on OS X
            if old_ld_flags is not None:
                os.environ['LDFLAGS'] = old_ld_flags
            else:
                del os.environ['LDFLAGS']
