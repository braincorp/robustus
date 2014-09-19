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
from robustus.detail.utility import run_shell, check_run_shell
import shutil
import subprocess
import tempfile


def test_doc_tests():
    doctest.testmod(robustus, raise_on_error=True)
    doctest.testmod(robustus.detail.utility, raise_on_error=True)
 
 
def test_run_shell():
    def check(command, expected_ret_code, expected_output, verbose):
        tf = tempfile.TemporaryFile('w+')
        assert run_shell(command, shell=True, stdout=tf, verbose=verbose) == expected_ret_code
        tf.seek(0)
        assert tf.read() == expected_output
        try:
            exception_occured = False
            check_run_shell(command, shell=True, verbose=verbose)
        except subprocess.CalledProcessError:
            exception_occured = True
        assert exception_occured == (exception_occured != 0)
 
    check('echo robustus', 0, 'robustus\n', verbose=True)
    check('echo robustus', 0, 'robustus\n', verbose=False)
    check('echo robustus && exit 1', 1, 'robustus\n', verbose=True)
    check('echo robustus && exit 1', 1, 'robustus\n', verbose=False)
 
 
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
    run_shell([robustus_executable, 'install', 'pyserial'])
    test_requirements1 = 'test_requirements1.txt'
    with open(test_requirements1, 'w') as file:
        file.write('pep8==1.3.3\n')
        file.write('pytest==2.3.5\n')
    run_shell([robustus_executable, 'install', '-r', test_requirements1])
 
    # check packages are installed
    packages_to_check = ['pyserial', 'pep8==1.3.3', 'pytest==2.3.5']
    with open('freezed_requirements.txt', 'w') as req_file:
        run_shell([robustus_executable, 'freeze'], stdout=req_file)
    with open('freezed_requirements.txt') as req_file:
        installed_packages = [line.strip() for line in req_file]
    for package in packages_to_check:
        assert package in installed_packages
 
    assert check_module_available(test_env, 'serial')
    assert check_module_available(test_env, 'pep8')
    assert check_module_available(test_env, 'pytest')
 
    shutil.rmtree(test_env)
 
 
def create_editable_environment(tmpdir):
    """Create an environment with an editable (shared between some tests) and
    chdir into it."""
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
 
    run_shell([robustus_executable, 'install', '-r', test_requirements])
    return working_dir, test_env, robustus_executable
 
 
def test_pereditable(tmpdir):
    """Create a package with some editable requirements and check
    that perrepo runs as expected."""
    working_dir, test_env, robustus_executable = create_editable_environment(tmpdir)
    # Now check that robustus behaves as expected
    run_shell([robustus_executable, 'perrepo', 'touch', 'foo'])
    assert os.path.exists(os.path.join(working_dir, 'foo'))
    assert os.path.exists(os.path.join(test_env, 'src', 'ardrone', 'foo'))
 
 
def test_reset(tmpdir):
    """Try reset the environment"""
    working_dir, test_env, robustus_executable = create_editable_environment(tmpdir)
 
    # Change a file in the repo and check it is reset
    changed_filepath = os.path.join(test_env, 'src', 'ardrone', 'README')
    original_content = open(changed_filepath, 'r').read()
 
    f = open(changed_filepath, 'w')
    f.write('junk')
    f.close()
 
    run_shell([robustus_executable, 'reset', '-f'])
    assert original_content == open(changed_filepath, 'r').read()
 
     
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
        file.write('-e git+https://github.com/braincorp/robustus-test-repo.git@master#egg=robustus-test-repo\n')
 
    run_shell([robustus_executable, 'install', '--tag', 'test-tag', '-r', test_requirements])
 
    # Now check that robustus behaves as expected
    assert os.path.exists(os.path.join(test_env, 'src', 'robustus-test-repo', 'test-tag'))


def test_install_with_branch_testing(tmpdir):
    """Create a package with some editable requirements and install using a branch
    and check that one repo with the branch gets checked out using the branch
    and the other ends up on master (this is how testing is often done)."""
 
    base_dir = str(tmpdir.mkdir('test_perrepo_env'))
    test_env = os.path.join(base_dir, 'env')
    working_dir = os.path.join(base_dir, 'working_dir')
 
    # create env and install some packages
    logging.info('creating ' + test_env)
    os.mkdir(working_dir)
    os.chdir(working_dir)
    
    # creat a new local repo
    os.system('git init .')

    setup_file_content =\
        '''
from setuptools import setup, find_packages


setup(
    name='test_perrepo_env',
    author='Brain Corporation',
    author_email='sinyavskiy@braincorporation.com',
    url='https://github.com/braincorp/test_perrepo_env',
    long_description='',
    version='dev',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[])
'''    
    setup_file = os.path.join(working_dir, 'setup.py')
    with open(setup_file, 'w') as file:
        file.write(setup_file_content)

    test_requirements = os.path.join(working_dir, 'requirements.txt')
    with open(test_requirements, 'w') as file:
        file.write('-e git+https://github.com/braincorp/robustus-test-repo.git@master#egg=robustus-test-repo\nmock==0.8.0\n-e git+https://github.com/braincorp/filecacher.git@master#egg=filecacher\n')
    
    os.system('git add setup.py')
    os.system('git add requirements.txt')
    os.system('git commit -am "setup and reqs"')
    
    # create test branch
    os.system('git checkout -b test-branch')
    test_file_on_test_branch = os.path.join(working_dir, 'root_test_branch.file')
    with open(test_file_on_test_branch, 'w') as file:
        file.write('root test')
    os.system('git add root_test_branch.file')
    os.system('git commit -am "root_test_branch.file"')
    os.system('git checkout master')
        
    robustus.execute(['env', test_env])
 
    os.chdir(working_dir)
    robustus_executable = os.path.join(test_env, 'bin/robustus')
    run_shell([robustus_executable, 'install', '-e', '.', '--tag', 'test-branch', '--ignore-missing-refs'], verbose = True)
 
    # Now check that robustus behaves as expected
    assert os.path.exists(os.path.join(test_env, 'src', 'robustus-test-repo', 'test_branch.file'))
    assert os.path.exists(os.path.join(test_env, 'lib', 'python2.7', 'site-packages',
                                       'python-ardrone.egg-link'))
 
    assert os.path.exists(os.path.join(test_env, 'src', 'filecacher', 'requirements.txt'))
    assert os.path.exists(os.path.join(test_env, 'lib', 'python2.7', 'site-packages',
                                       'filecacher.egg-link'))

    # Now check that the repo itself is on the test branch
    assert os.path.exists(test_file_on_test_branch)
    

if __name__ == '__main__':
    test_doc_tests()
    pytest.main('-s %s -n0' % __file__)
