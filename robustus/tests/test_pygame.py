# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
import pytest
import logging
from robustus.detail import perform_standard_test


def test_pygame_installation(tmpdir):
    logging.getLogger().setLevel(logging.INFO)
    tmpdir.chdir()
    perform_standard_test('Pygame==bc1', ['import pygame'])
    # need lib4l-videodev for Pygame 1.9.1
    if os.path.isfile('/usr/include/libv4l1-videodev.h'):
        perform_standard_test('Pygame==1.9.1', ['import pygame'])

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
