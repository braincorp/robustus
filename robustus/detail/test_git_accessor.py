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
    test_file_content = accessor.access('https://github.com/braincorp/robustus',
                                        'test_git_accessor', 'test_git_accessor.txt')
    assert(test_file_content == ['This file exists only in test_git_accessor branch'
                                 ' and is used to test accessor on non-master branch.'])
    

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
