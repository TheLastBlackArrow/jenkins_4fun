#!/bin/bash
/usr/sbin/sshd
exec /usr/bin/tini -- /usr/local/bin/jenkins.sh
