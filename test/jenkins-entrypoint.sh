#!/bin/sh
cp /tmp/config.xml /var/jenkins_home/config.xml
exec tini -- /usr/local/bin/jenkins.sh "$@"
