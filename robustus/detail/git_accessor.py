# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import tempfile
import shutil
import os
from utility import check_run_shell


class GitAccessor(object):
    def access(self, repo_link, tag, path_to_file):
        '''
        Checkout a single file from git repo specified
        by 'repo_link' from branch 'tag' under path 'path_to_file'.
        @return: file content 
        '''
        tmp_dir = tempfile.mkdtemp()
        if tag is not None:
            check_run_shell(['git', 'clone', repo_link, tmp_dir], False)
            check_run_shell('cd "' + tmp_dir + '" && git checkout ' + tag, True)
        else:
            check_run_shell(['git', 'clone', '--depth', '1', repo_link, tmp_dir], False)
        with open(os.path.join(tmp_dir, path_to_file)) as file:
            lines = file.readlines()
        shutil.rmtree(tmp_dir)
        return lines
