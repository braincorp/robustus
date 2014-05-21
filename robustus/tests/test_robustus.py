# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import doctest
import logging
import os
import pytest
import robustus
from robustus.detail import check_module_available
from robustus.detail.utility import run_shell
import shutil


def test_doc_tests():
    doctest.testmod(robustus, raise_on_error=True)
    doctest.testmod(robustus.detail.utility, raise_on_error=True)


def test_robustus(tmpdir):
    tmpdir.chdir()
    test_env = 'test_env'

    # create env and install some packages
    logging.info('creating ' + test_env)
    robustus.execute(['env', test_env])
    assert os.path.isdir(test_env)
    assert os.path.isfile(os.path.join(test_env, '.robustus'))
    robustus_executable = os.path.join(test_env, 'bin/robustus')
    assert os.path.isfile(robustus_executable)

    # install some packages
    logging.info('installing requirements into ' + test_env)
    run_shell([robustus_executable, 'install', 'pyserial'], False)
    test_requirements1 = 'test_requirements1.txt'
    with open(test_requirements1, 'w') as file:
        file.write('pep8==1.3.3\n')
        file.write('pytest==2.3.5\n')
    run_shell([robustus_executable, 'install', '-r', test_requirements1], False)

    # check packages are installed
    packages_to_check = ['pyserial', 'pep8==1.3.3', 'pytest==2.3.5']
    with open('freezed_requirements.txt', 'w') as req_file:
        run_shell([robustus_executable, 'freeze'], False, stdout=req_file)
    with open('freezed_requirements.txt') as req_file:
        installed_packages = [line.strip() for line in req_file]
    for package in packages_to_check:
        assert package in installed_packages

    assert check_module_available(test_env, 'serial')
    assert check_module_available(test_env, 'pep8')
    assert check_module_available(test_env, 'pytest')

    shutil.rmtree(test_env)


def test_pereditable(tmpdir):
    """Create a package with some editable requirements and check
    that perrepo runs as expected."""
    base_dir = str(tmpdir.mkdir('test_perrepo_env'))
    test_env = os.path.join(base_dir, 'env')
    working_dir = os.path.join(base_dir, 'working_dir')

    # create env and install some packages
    logging.info('creating ' + test_env)
    os.mkdir(working_dir)
    os.chdir(working_dir)
    os.system('git init .')
    robustus.execute(['env', test_env])

    os.chdir(working_dir)
    robustus_executable = os.path.join(test_env, 'bin/robustus')
    test_requirements = os.path.join(working_dir, 'requirements.txt')
    with open(test_requirements, 'w') as file:
        file.write('-e git+https://github.com/braincorp/robustus-test-repo.git@master#egg=ardrone\n')

    run_shell([robustus_executable, 'install', '-r', test_requirements], False)

    # Now check that robustus behaves as expected
    run_shell([robustus_executable, 'perrepo', 'touch', 'foo'], False)
    assert os.path.exists(os.path.join(working_dir, 'foo'))
    assert os.path.exists(os.path.join(test_env, 'src', 'ardrone', 'foo'))


def test_install_with_tag(tmpdir):
    """Create a package with some editable requirements and install using a tag."""
    base_dir = str(tmpdir.mkdir('test_perrepo_env'))
    test_env = os.path.join(base_dir, 'env')
    working_dir = os.path.join(base_dir, 'working_dir')

    # create env and install some packages
    logging.info('creating ' + test_env)
    os.mkdir(working_dir)
    os.chdir(working_dir)
    os.system('git init .')
    robustus.execute(['env', test_env])

    os.chdir(working_dir)
    robustus_executable = os.path.join(test_env, 'bin/robustus')
    test_requirements = os.path.join(working_dir, 'requirements.txt')
    with open(test_requirements, 'w') as file:
        file.write('-e git+https://github.com/braincorp/robustus-test-repo.git@master#egg=ardrone\n')

    run_shell([robustus_executable, 'install', '--tag', 'test-tag', '-r', test_requirements], False)

    # Now check that robustus behaves as expected
    assert os.path.exists(os.path.join(test_env, 'src', 'ardrone', 'test-tag'))
    

if __name__ == '__main__':
    test_doc_tests()
    pytest.main('-s %s -n0' % __file__)
