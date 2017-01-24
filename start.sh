#!/bin/sh

echo Launching the openHAB runtime...

DIRNAME=`dirname "$0"`

export CLASSPATH="/opt/jython/jython.jar"
export EXTRA_JAVA_OPTS=" -Dpython.home=/opt/jython -Dpython.path=/openhab/userdata/automation/pylib"

exec "${DIRNAME}/runtime/bin/karaf" "${@}"

