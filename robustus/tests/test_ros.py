# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
import logging
from robustus.detail import perform_standard_test


@pytest.mark.skipif("'TRAVIS' in os.environ")
def test_ros_installation(tmpdir):
    logging.getLogger().setLevel(logging.INFO)
    tmpdir.chdir()

    imports = ['import rospy',
               'import boto']
    dependencies = ['boto==2.19.0']  # boto is just to ensure that non-ROS requirements are also in venv
    
    perform_standard_test('ros==hydro.ros_comm',
                          imports,
                          [],
                          dependencies,
                          postinstall_script='. test_env/bin/activate && . test_env/ros/setup.sh')


@pytest.mark.skipif("'TRAVIS' in os.environ")
def test_gscam_installation(tmpdir):
    logging.getLogger().setLevel(logging.INFO)
    tmpdir.chdir()

    imports = ['import rospy',
               'import boto']
    dependencies = ['boto==2.19.0', 'ros==hydro.ros_comm',
                    'opencv==2.4.4', 'numpy==1.7.1']
    
    perform_standard_test("""ros_overlay==https://github.com/ros-drivers/gscam.git#3d976c80324f5723cd7a23c18d452c4231044cc0,https://github.com/ros/nodelet_core.git#71a90d671e49f6e4b8b73d4e856f6335e9511dba,https://github.com/ros/bond_core.git#37a4f47699e2c262725a34a2a7104659664e9089,https://github.com/ros/dynamic_reconfigure.git#c12a36d00c720ca21ed5e8a43f3d8acb0c33daa8,https://github.com/ros/pluginlib.git#ccd88bc1c2b46847fc02c65dcc75524ca160ecd6,https://github.com/ros/class_loader.git#e75eeb7ff595618785461db6f0510ca5854b078a,https://github.com/ros-perception/image_common.git#a0e3c042f10ab3a1c9ae052b306b45f1fdc046ea,https://github.com/braincorp/image_pipeline.git#3343cb4fb53407bc880a920355e5b3f9d2a7ecc9,https://github.com/ros-perception/image_pipeline.git#53be3397d1e844a5854f0d8643fe9ad726d0d58a,https://github.com/ros/common_msgs.git#bd3b67b48eca80575f32640e8fc4c1549ecf6c5a,https://github.com/ros-perception/vision_opencv.git#9323c27a9337253b4e50eb8818b76fc799ab4f92,https://github.com/ros/geometry.git#2f4ecff64a13d0c41faf3f8859f210636d159669,https://github.com/ros-perception/perception_pcl.git#d49e78e05f2c8e589e758709d6d2cb93f26e119a,https://github.com/orocos/orocos_kinematics_dynamics.git#6d842711d2247c740a5ed16d043fd74ff3577f60,https://github.com/ros/geometry_experimental.git#ec3a4c035f44492abfa1f2d11b0cb08a26e22a27,https://github.com/ros/angles.git#3f94acf9926ee18174bb82748194d1ac6f5be5f9,https://github.com/ros/actionlib.git#1c6275607793eabd963cc1dc5b09d3975b52a2ed,https://github.com/ros-perception/pcl_conversions.git#5b52fedea20b383f19e82e1fcc892e7187782476,https://github.com/ros-perception/pcl_msgs.git#68e914f8a975dfba9827ae545f62e3b8280b8aaf""",
                          imports,
                          [],
                          dependencies,
                          postinstall_script='. test_env/bin/activate && . test_env/ros/setup.sh')


if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
