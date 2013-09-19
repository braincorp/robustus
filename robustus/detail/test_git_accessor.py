# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
from git_accessor import GitAccessor


def test_git_accessor():
    accessor = GitAccessor()
    license_content = accessor.access('https://github.com/braincorp/robustus',
                                      'master', 'LICENSE')
    assert(len(license_content) == 20)
    

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
