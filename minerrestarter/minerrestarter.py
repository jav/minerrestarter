#!/usr/bin/env python2

#Made by Javier Ubillos, javier@ubillos.org, github.com/jav
#For donations: Monero: 45zBbvea3Hs2xR9AWcQkFy2BnPtoNSrDb59hTftst14qjeEsnzC9SXFXAVJBo3wh1EQzMUYDsGLggFox8hfmwtbxRQzq1Fm

import argparse
import ConfigParser
import json
import re
import sys
import time
import urllib2

current_time = lambda: int(round(time.time() * 1000))
def countdown(from_time):
    for i in xrange(from_time,0,-1):
        time.sleep(1)
        sys.stdout.write(str(i)+' ')
        sys.stdout.flush()

def main(argv=None):
    # Do argv default this way, as doing it in the functional
    # declaration sets it at compile time.
    if argv is None:
        argv = sys.argv

    # Parse any conf_file specification
    # We make this parser with add_help=False so that
    # it doesn't parse -h and print help.
    conf_parser = argparse.ArgumentParser(
        description=__doc__, # printed with -h/--help
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # Turn off help, so we print all options in response to -h
        add_help=False
        )
    conf_parser.add_argument("-c", "--conf_file",
                        help="Specify config file", default="config.ini", metavar="FILE")
    args, remaining_argv = conf_parser.parse_known_args()

    defaults = {    "minercmd":"echo",
                    "monitorinterval":120}

    if args.conf_file:
        config = ConfigParser.SafeConfigParser()
        config.read([args.conf_file])
        defaults.update(dict(config.items("Defaults")))

    # Parse rest of arguments
    # Don't suppress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents=[conf_parser]
        )

    parser.add_argument ("--minercmd")
    parser.add_argument ("--monitorinterval");
    parser.set_defaults(**defaults)

    args = parser.parse_args(remaining_argv)

    miner_cmd = args.minercmd
    monitor_func = miner_monitor()
    monitor_interval = args.monitorinterval

    run_miner(miner_cmd, monitor_func, monitor_interval)

    return(0)

def miner_monitor():
    pass

def get_hashrate(endpoint, interval):
    req = urllib2.Request(url=endpoint)
    try:
        urlopen = urllib2.urlopen(req)
        response = urlopen.read()
    #if we get an exception, it's most likely because the miner isn't running
    #in these cases, consider hashrate to be = 0
    except (URLError, ValueError):
            return 0
    hashrates = re.search("<th>Totals:</th><td>([^<]*)</td><td>([^<]*)</td><td>([^<]*)</td>", response).group(1, 2, 3)
    hashrate = dict(zip(['10s', '60s', '15m'], hashrates))[interval]
    #hashrate '0' is often represented as a blank space
    if(len(hashrate) <= 0):
        return 0
    return float(hashrate.strip())

def run_miner(miner_cmd, monitor_func, monitor_interval):
    print "miner_cmd: %s" % miner_cmd
    print "monitor_func: %s" % monitor_func
    print "monitor_interval: %s" % monitor_interval



if __name__ == "__main__":
    sys.exit(main())
