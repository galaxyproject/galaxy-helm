#!/usr/bin/env python3

import argparse
import psycopg2
import socket
import sys

from datetime import datetime
from time import sleep


DEBUG=False

def dprint(msg):
    if DEBUG:
        print(msg)

parser = argparse.ArgumentParser()


def add_arg(shortname, longname, default=None, help_text=None):
    if len(shortname) != 1:
        print("ERROR: short flag for argument must be a single character")
        sys.exit(1)
    parser.add_argument("-{}".format(shortname), "--{}".format(longname), help=help_text, default=default)

#    parser.add_argument("-{}".format(shortname), "--{}".format(longname))

args = [
        { "shortname": "u", "longname": "username", "help_text": "postgres db user name" },
        { "shortname": "p", "longname": "password", "help_text": "postgres db user pass" },
        { "shortname": "d", "longname": "dbname", "help_text": "postgres db name to connect to" },
        { "shortname": "n", "longname": "hostname", "help_text": "name of host where postgres db lives" },
        { "shortname": "s", "longname": "servername", "help_text": "handler server name to be checked in postgres db", "default": socket.gethostname() }
]


def check_rows(args):
    def less_than_60s(a, b):
        if (b-a).seconds >= 60:
            dprint("time delta {} >= 60s".format((b-a).seconds))
            sys.exit(1)
        dprint("time delta {} < 60s".format((b-a).seconds))
        sys.exit(0)

    conn = psycopg2.connect("dbname='" + args.dbname + "' user='" + args.username + "' host='" + args.hostname + "' password='" + args.password + "'")
    cur = conn.cursor()
    cur.execute("""SELECT server_name, update_time FROM worker_process WHERE server_name LIKE '%""" + args.servername + "%';" )
    rows = cur.fetchall()
    if len(rows) != 1:
        dprint("ERROR: there should be only one row, but {} found".format(len(rows)))
        exit(1)
    for row in rows:
        now = datetime.now()
        less_than_60s(row[1], now)


for arg in args:
    add_arg(**arg)

args = parser.parse_args()
dprint("args: \n" + str(args))
check_rows(args)
