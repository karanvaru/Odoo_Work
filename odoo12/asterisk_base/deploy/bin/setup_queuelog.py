#!/usr/bin/python3
from pwd import getpwuid
from grp import getgrgid
import os
import stat
import subprocess
import sys


QUEUE_LOG_PATH = os.getenv('QUEUE_LOG_PATH', '/var/log/asterisk/queue_log')
ASTERISK_USER = os.getenv('ASTERISK_USER', 'asterisk')
ASTERISK_GROUP = os.getenv('ASTERISK_GROUP', 'asterisk')
QUEUE_LOG_ENABLED = os.getenv('QUEUE_LOG_ENABLED', 'no')


def create():
    print('Making queue log as fifo')
    os.mkfifo(QUEUE_LOG_PATH)


def chown():
    if getpwuid(os.stat(QUEUE_LOG_PATH).st_uid).pw_name != ASTERISK_USER or \
            getgrgid(os.stat(QUEUE_LOG_PATH).st_gid).gr_name != ASTERISK_GROUP:
        print('Setting ownership to {}:{}'.format(
            ASTERISK_USER, ASTERISK_GROUP))
        subprocess.check_call(
            'chown {}:{} {}'.format(
                ASTERISK_USER, ASTERISK_GROUP, QUEUE_LOG_PATH),
            shell=True)


if __name__ == '__main__':
    if QUEUE_LOG_ENABLED != 'yes':
        print('Queue log FIFO setup is disabled.')
        if os.path.exists(QUEUE_LOG_PATH):
            if stat.S_ISFIFO(os.stat(QUEUE_LOG_PATH).st_mode):
                print('Removing FIFO file ', QUEUE_LOG_PATH)
                os.unlink(QUEUE_LOG_PATH)
        sys.exit(0)
    if not os.path.exists(QUEUE_LOG_PATH):
        print('Queue log', QUEUE_LOG_PATH, 'does not exist.')
        create()
        chown()
    elif os.path.exists(QUEUE_LOG_PATH):
        print('Checking queue log', QUEUE_LOG_PATH)
        if not stat.S_ISFIFO(os.stat(QUEUE_LOG_PATH).st_mode):
            print('Removing ordinary file ', QUEUE_LOG_PATH)
            os.unlink(QUEUE_LOG_PATH)
            create()
        chown()
