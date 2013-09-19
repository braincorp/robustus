# This script should be sourced before using this repo (for development).
# It creates the python virtualenv and using pip to populate it
# This only run to setup the development environment.
# Installation is handled by setup.py/disttools.

# Robust way of locating script folder
# from http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in
SOURCE=${BASH_SOURCE:-$0}

DIR="$( dirname "$SOURCE" )"
while [ -h "$SOURCE" ]
do 
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
  DIR="$( cd -P "$( dirname "$SOURCE"  )" && pwd )"
done
WDIR="$( pwd )"
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"


if type python27 > /dev/null 2>/dev/null ; then
	PYTHONEXEC=python27
else
	PYTHONEXEC=python
fi

# create virtualenv
virtualenv $DIR/venv --python=$PYTHONEXEC --prompt "(robustus)"
source $DIR/venv/bin/activate
pip install -r requirements.txt
