# =============================================================================
# COPYRIGHT 2014 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
import logging
import os
from robustus.detail import perform_standard_test


@pytest.mark.skipif("'TRAVIS' in os.environ",
                    reason="gazebo compilation takes too long for travis")
def test_gazebo_installation(tmpdir):
    logging.getLogger().setLevel(logging.INFO)
    tmpdir.chdir()
    perform_standard_test('gazebo==2.2.1',
                          [],
                          ['lib/sdformat-1.4.11/lib/libsdformat.so',
                           'lib/gazebo-2.2.1/bin/gazebo',
                           'lib/gazebo-2.2.1/lib/libgazebo.so'],
                          ['patchelf==6fb4cdb', 'sdformat==1.4.11'])

if __name__ == '__main__':
    pytest.main('-s %s -n0' % os.path.abspath(__file__))
