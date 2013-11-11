# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================


import subprocess
import tempfile
import shutil
import os


class GitAccessor(object):
    def access(self, repo_link, tag, path_to_file):
        '''
        Checksout a single file from git repo specified
        by 'repo_link' from branch 'tag' under path 'path_to_file'.
        @return: file content 
        '''
        tmp_dir = tempfile.mkdtemp()
        if tag is not None:
            subprocess.call(['git', 'clone', '--depth', '1', '-b', tag, repo_link, tmp_dir])
        else:
            subprocess.call(['git', 'clone', '--depth', '1', repo_link, tmp_dir])
        with open(os.path.join(tmp_dir, path_to_file)) as file:
            lines = file.readlines()
        shutil.rmtree(tmp_dir)
        return lines
