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


def add_arg(shortname, longname, default=None, help_text=None, action=None):
    if len(shortname) != 1:
        print("ERROR: short flag for argument must be a single character")
        sys.exit(1)
    parser.add_argument("-{}".format(shortname), "--{}".format(longname), help=help_text, default=default, action=action)

#    parser.add_argument("-{}".format(shortname), "--{}".format(longname))

args = [
    { "shortname": "i", "longname": "interval", "help_text": "how long (in seconds) to wait between probes"}
    { "shortname": "v", "longname": "verbose", "help_text": "enable verbose output", "action": "store_true" },
    { "shortname": "e", "longname": "environmentvariable", "help_text": "environment variable that contains connection string" },
    { "shortname": "u", "longname": "username", "help_text": "postgres db user name" },
    { "shortname": "p", "longname": "password", "help_text": "postgres db user pass" },
    { "shortname": "d", "longname": "dbname", "help_text": "postgres db name to connect to" },
    { "shortname": "b", "longname": "dbhost", "help_text": "name of host where postgres lives" },
    { "shortname": "o", "longname": "hostname", "help_text": "handler host name to be checked in postgres db", "default": socket.gethostname() },
]


def check_rows(connection_string, query_string):
    def less_than_60s(a, b):
        if (b-a).seconds >= 60:
            dprint("time delta {} >= 60s".format((b-a).seconds))
            sys.exit(1)
        dprint("time delta {} < 60s".format((b-a).seconds))
        sys.exit(0)

    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    cur.execute(query_string)
    rows = cur.fetchall()
    if len(rows) != 1:
        dprint("ERROR: there should be only one row, but {} found".format(len(rows)))
        exit(1)
    for row in rows:
        now = datetime.now()
        less_than_60s(row[1], now)


for arg in args:
    add_arg(**arg)

parsed_args = parser.parse_args()

connection_string = ""

if parsed_args.verbose:
    DEBUG=True

if parsed_args.environmentvariable:
    connection_string = parsed_args.environmentvariable
else:
    connection_string = "dbname='" + parsed_args.dbname + "' user='" + parsed_args.username + "' host='" + parsed_args.dbhost + "' password='" + parsed_args.password + "'"
query_string = """SELECT server_name, update_time FROM worker_process WHERE hostname='""" + parsed_args.hostname + "';"

dprint("provided arguments: \n" + str(parsed_args))
dprint("connection string: {}".format(connection_string))
dprint("query string: {}".format(query_string))
check_rows(connection_string, query_string)
