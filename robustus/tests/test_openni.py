# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
from robustus.detail import perform_standard_test
import sys


def test_openni_installation(tmpdir):
    tmpdir.chdir()
    # ok if sensor is not connected, should fail if library not found
    exprs = ['from primesense import openni2\nopenni2.initialize()']
    if sys.platform == "linux" or sys.platform == "linux2":
        files = ['lib/libOpenNI2.so']
    else:
        files = []
    dependencies = ['OpenNI']
    perform_standard_test('primesense==2.2.0.30-5', exprs, files, dependencies)


if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
