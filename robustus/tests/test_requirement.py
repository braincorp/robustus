# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================


import doctest
import robustus
import pytest
import mock


#FIXME: use from robustus.detail.requirement import ...
do_requirement_recursion = robustus.detail.requirement.do_requirement_recursion
RequirementSpecifier = robustus.detail.requirement.RequirementSpecifier
RequirementException = robustus.detail.requirement.RequirementException


def test_requirement_recursion_signle_item():
    mock_git = mock.MagicMock()
    reqs = do_requirement_recursion(mock_git, RequirementSpecifier(specifier='  -e    numpy == 1.7.2  # comment'))
    assert(not mock_git.called)
    assert(len(reqs) == 1)

    reqs = do_requirement_recursion(mock_git, RequirementSpecifier(specifier='git+ssh://git@github.com/company/my_package#egg=my_package'))
    assert(not mock_git.called)
    assert(len(reqs) == 1)
    assert(reqs[0].freeze() == 'git+ssh://git@github.com/company/my_package#egg=my_package')

    with pytest.raises(RequirementException):
        do_requirement_recursion(mock_git, RequirementSpecifier(specifier='-e git+https://github.com/company/my_package@branch_name'))


def test_requirement_recursion_single_retreive():
    mock_git = mock.MagicMock()
    mock_git.access.return_value = ['numpy==1', 'scipy==2']
    reqs = do_requirement_recursion(mock_git, RequirementSpecifier(
        specifier='-e git+ssh://git@github.com/company/my_package@branch_name#egg=my_package'))
    mock_git.access.assert_called_with('ssh://git@github.com/company/my_package',
                                       'branch_name', 'requirements.txt')
    assert(len(reqs) == 3)
    assert(reqs[0].freeze() == 'numpy==1')
    assert(reqs[1].freeze() == 'scipy==2')
    assert(reqs[2].freeze() == '-e git+ssh://git@github.com/company/my_package@branch_name#egg=my_package')


def test_requirement_recursion_two_levels():

    class MockGit(object):
        def access(self, link, branch, path):
            assert(path == 'requirements.txt')
            assert(link == 'https://github.com/company/my_package' or 
                   link == 'ssh://git@github.com/company/my_package')
            if branch == 'branch_name':
                return ['numpy==1', 
                        '-e git+ssh://git@github.com/company/my_package@another_branch#egg=my_package', 
                        'scipy==2']
            elif branch == 'another_branch':
                return ['numpy==1', 
                        'opencv==5']
            else:
                raise Exception('Unknown branch name %s' % branch)

    mock_git = MockGit()
    reqs = do_requirement_recursion(mock_git, RequirementSpecifier(
        specifier='-e git+https://github.com/company/my_package@branch_name#egg=my_package'))
    assert(len(reqs) == 6)
    assert(reqs[0].freeze() == 'numpy==1')
    assert(reqs[1].freeze() == 'numpy==1')
    assert(reqs[2].freeze() == 'opencv==5')
    assert(reqs[3].freeze() == '-e git+ssh://git@github.com/company/my_package@another_branch#egg=my_package')
    assert(reqs[4].freeze() == 'scipy==2')
    assert(reqs[5].freeze() == '-e git+https://github.com/company/my_package@branch_name#egg=my_package')
    
  
if __name__ == '__main__':
    doctest.testmod(robustus.detail.requirement)
    pytest.main('-s %s -n0' % __file__)
