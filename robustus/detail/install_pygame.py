# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
from requirement import RequirementException
import shutil
import subprocess
import sys


def install(robustus, requirement_specifier, rob_file):
    if requirement_specifier.version != '1.9.1':
        raise RequirementException('can only install pygame 1.9.1')

    if sys.platform.startswith('darwin'):
        subprocess.call([robustus.pip_executable, 'install', '-U', 'pyobjc-core'])
        subprocess.call([robustus.pip_executable, 'install', '-U', 'pyobjc'])

        print "#####################"
        print "You are on OSX"
        print "Make sure you have SDL installed"
        print "The easiest way to achieve this is using brew:"
        print "   brew install sdl sdl_image sdl_mixer sdl_ttf portmidi"
        print "#####################"

    # PYPI index is broken for pygame, download manually
    logging.info('Downloading pygame')
    pygame_archive_name = 'pygame-1.9.1release'
    pygame_tgz = pygame_archive_name + '.tar.gz'
    url = 'http://www.pygame.org/ftp/' + pygame_tgz
    subprocess.call(['wget', '-c', url, '-O', pygame_tgz])

    logging.info('Unpacking pygame')
    subprocess.call(['tar', 'xvzf', pygame_tgz])

    # Pygame asks to proceed without smpeg,
    # megahack to avoid asking to continue
    os.chdir(pygame_archive_name)
    config_unix_py = 'config_unix.py'
    config_unix_py_source = open(config_unix_py).read()
    with open(config_unix_py, 'w') as f:
        f.write(config_unix_py_source.replace('def confirm(message):',
                                              'def confirm(message):\n'
                                              '    return 1\n'))

    subprocess.call([robustus.python_executable, 'setup.py', 'install'])
    os.chdir(os.path.pardir)

    shutil.rmtree(pygame_archive_name)
    os.remove(pygame_tgz)
