# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

from setuptools import setup
import roboenv


setup(name='roboenv',
      author='Brain Corporation',
      author_email='trifonov@braincorporation.com',
      url='https://github.com/braincorp/roboenv',
      long_description='Tool to make and configure python virtualenv, setup necessary packages and cache them if necessary.',
      version=roboenv.__version__,
      packages=['roboenv'],
      scripts=['bin/roboenv'],
      install_requires=['virtualenv==1.10.1'])