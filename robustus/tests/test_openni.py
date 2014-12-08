# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
from robustus.detail import perform_standard_test


def test_openni_installation(tmpdir):
    #tmpdir.chdir()
    imports = ['from primesense import openni2']
    dependencies = ['OpenNI==2.2-beta2']
    perform_standard_test('primesense==2.2.0.30-5', imports, [], dependencies)


if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)

