#!/bin/bash -e

BASEDIR=`dirname $0`

if [ ! -d "$BASEDIR/ve" ]; then
    virtualenv -q $BASEDIR/ve --no-site-packages
    echo "Virtualenv created."
fi

if [ ! -f "$BASEDIR/ve/updated" -o $BASEDIR/requirements.txt -nt $BASEDIR/ve/updated ]; then
    source $BASEDIR/ve/bin/activate
    pip install -r $BASEDIR/requirements.txt
    touch $BASEDIR/ve/updated
    echo "Requirements installed."
fi