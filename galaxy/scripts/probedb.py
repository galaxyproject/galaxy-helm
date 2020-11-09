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

    def less_than_interval(a, b, interval=60):
        if (b-a).seconds > interval:
            log.debug("time delta {} > {}s".format((b-a).seconds, interval))
            return False
        log.debug("time delta {} <= {}s".format((b-a).seconds, interval))
        return True

    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    cur.execute(query_string)
    rows = cur.fetchall()
    log.debug(f"matching rows {str(rows)}")
    # At least one matching handler must be alive
    matches = any(less_than_interval(row[0], datetime.now(), interval) for row in rows)
    log.debug(f"health check {'succeeded' if matches else 'failed'}.")
    return 0 if matches else 1


def main():
    # allowable seconds since db timestamp
    default_interval = 60

    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--connection", required=True,
                        help="connection string to galaxy database")
    parser.add_argument("-s", "--server_name", required=True,
                        help="handler's server_name to be checked in postgres db")
    parser.add_argument("-o", "--hostname",
                        help="handler host name to be checked in postgres db",
                        default=socket.gethostname())
    parser.add_argument("-i", "--interval",
                        type=int,
                        help="how long (in seconds) since heartbeat to determine probe failure")
    parser.add_argument("-v", "--verbose",
                        help="enable verbose output", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)

    db_query = f"SELECT update_time FROM worker_process WHERE hostname='{args.hostname}'" \
               f" AND server_name='{args.server_name}';"

    log.debug(f"provided arguments: {str(args)}")
    log.debug(f"db connection string: {args.connection}")
    log.debug(f"db query: {db_query}")

    return check_rows(args.connection, db_query, args.interval if args.interval else default_interval)


if __name__ == '__main__':
    sys.exit(main())
