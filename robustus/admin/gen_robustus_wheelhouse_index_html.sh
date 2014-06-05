#!/bin/bash

set -x
set -u
set -e
set -E
set -o pipefail

SCRIPT_FILE_NAME=$(basename "$0")
SCRIPT_DIR_PATH=$(dirname "$0")

print_usage()
{
    cat<<DELIMITER
USAGE: $SCRIPT_FILE_NAME WHEELHOUSE_DIR_PATH
DELIMITER
}

print_usage_abort()
{
    if [[ $# -gt 0 ]] ; then echo "$@" ; fi
    print_usage
    exit 1
}

if [[ $# -ne 1 ]]
then
    print_usage_abort
fi

WHEELHOUSE_DIR_PATH="$1"
WHEELHOUSE_URL="http://thirdparty-packages.braincorporation.net/python-wheels"

cd "$WHEELHOUSE_DIR_PATH"
N_WHEELS=$(ls -1 *.whl | wc -l)
if [[ $N_WHEELS -lt 1 ]]
then
    echo "Found NO wheels in directory \"$WHEELHOUSE_DIR_PATH\"!  Aborting..."
    exit 1
fi

echo "Found $N_WHEELS wheel(s) in directory \"$WHEELHOUSE_DIR_PATH\"."

    cat << DELIMITER > "index.html"
<html>
<head><title>Index of $WHEELHOUSE_URL</title></head>
<body bgcolor="white">
<h1>Index of $WHEELHOUSE_URL</h1><hr><pre><a href="../">../</a>
$(ls -1 *.whl | sort | sed -e 's/.*/<a href="&">&<\/a>/')
</pre><hr></body>
</html>
DELIMITER
