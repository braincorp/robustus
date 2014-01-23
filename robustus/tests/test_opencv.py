# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
import logging
from robustus.detail import perform_standard_test


def test_opencv_installation_248(tmpdir):
    _do_test_opencv_installation(tmpdir, 'OpenCV==2.4.8')


def _do_test_opencv_installation(tmpdir, requirement):
    logging.getLogger().setLevel(logging.INFO)
    tmpdir.chdir()

    imports = ['import cv2',
               'from cv2 import imread']
    
    perform_standard_test(requirement, imports, [], ['patchelf==6fb4cdb', 'numpy==1.7.1'])


if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
