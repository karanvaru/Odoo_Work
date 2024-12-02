#!/bin/bash
set -e

# dockerize templates
for i in `find /etc -name '*.tmpl'`; do
  dockerize -template "$i":"${i%%.tmpl}"
done

# Setup rules
/usr/local/bin/setup_security.sh
# Setup queue log
/usr/local/bin/setup_queuelog.py

# Run Asterisk
if [ "$1" = "" ]; then
  exec /sbin/tini /usr/sbin/asterisk -Tfvvv
else
  exec "$@"
fi
