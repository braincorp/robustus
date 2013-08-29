# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
import sys
from tools import install_through_wheeling


def install(roboenv, version):
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
            old_ld_flags = os.environ['LDFLAGS']
            os.environ['LDFLAGS'] = '-arch x86_64 -Wall -undefined dynamic_lookup -bundle'
            os.environ['FFLAGS'] = '-arch x86_64 -ff2c'

        roboenv.install_through_wheeling('scipy', version)

        if sys.platform.startswith('darwin'):
            # undo LDFLAGS changes on OS X
            os.environ['LDFLAGS'] = old_ld_flags

    return True