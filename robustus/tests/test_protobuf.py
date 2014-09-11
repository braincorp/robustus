# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
from robustus.detail import perform_standard_test


def test_protobuf_installation(tmpdir):
    tmpdir.chdir()

    protobuf_imports = ['import protobuf']

    perform_standard_test('protobuf==2.6.0', protobuf_imports, [], [])


if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
