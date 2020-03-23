import argparse
import logging
import psycopg2
import socket
import sys


from datetime import datetime

log = logging.getLogger()
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))


def check_rows(connection_string, query_string, interval=60):
    error_prefix = "DB PROBE ERROR"

    def less_than_interval(a, b, interval=60):
        if (b-a).seconds > interval:
            log.debug("time delta {} > {}s".format((b-a).seconds, interval))
            return 1
        log.debug("time delta {} <= {}s".format((b-a).seconds, interval))
        return 0

    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    cur.execute(query_string)
    rows = cur.fetchall()
    if len(rows) != 1:
        log.debug("{}: there should be only one row, but {} found".format(
            error_prefix, len(rows)))
        return 1
    for row in rows:
        now = datetime.now()
        return less_than_interval(row[0], now, interval)
    log.info("{}: failure to determine interval".format(error_prefix))
    return 1


def main():
    # allowable seconds since db timestamp
    default_interval = 60

    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--interval",
                        help="how long (in seconds) to wait between probes")
    parser.add_argument("-v", "--verbose",
                        help="enable verbose output", action="store_true")
    parser.add_argument("-e", "--environmentvariable",
                        help="environment variable with connection string")
    parser.add_argument("-u", "--username", help="postgres db user name")
    parser.add_argument("-p", "--password", help="postgres db user pass")
    parser.add_argument("-d", "--dbname",
                        help="postgres db name to connect to")
    parser.add_argument("-b", "--dbhost",
                        help="name of host where postgres lives")
    parser.add_argument("-o", "--hostname",
                        help="handler host name to be checked in postgres db",
                        default=socket.gethostname())

    parsed_args = parser.parse_args()

    if parsed_args.verbose:
        log.setLevel(logging.DEBUG)

    connection_string = ""

    if parsed_args.environmentvariable:
        connection_string = parsed_args.environmentvariable
    else:
        connection_string = "dbname='" + parsed_args.dbname +\
                            "' user='" + parsed_args.username +\
                            "' host='" + parsed_args.dbhost +\
                            "' password='" + parsed_args.password + "'"

    query_string = "SELECT update_time FROM worker_process WHERE hostname='" +\
        parsed_args.hostname + "';"

    log.debug("provided arguments: \n" + str(parsed_args))
    log.debug("connection string: {}".format(connection_string))
    log.debug("query string: {}".format(query_string))

    return check_rows(connection_string, query_string,
                      parsed_args.interval if parsed_args.interval
                      else default_interval)


if __name__ == '__main__':
    sys.exit(main())
