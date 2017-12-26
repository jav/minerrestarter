#!/usr/bin/env python2

#Made by Javier Ubillos, javier@ubillos.org, github.com/jav
#For donations: Monero: 45zBbvea3Hs2xR9AWcQkFy2BnPtoNSrDb59hTftst14qjeEsnzC9SXFXAVJBo3wh1EQzMUYDsGLggFox8hfmwtbxRQzq1Fm

import argparse
import ConfigParser
import json
import os
import re
import sys
import subprocess
import time
import urllib2

current_time = lambda: int(round(time.time() * 1000))
def countdown(from_time):
  number=''
  for i in xrange(int(from_time),-1,-1):
    for _ in xrange(len(number)):
      sys.stdout.write('\b')
    number=str(i)+' '
    sys.stdout.write(number)
    sys.stdout.flush()
    time.sleep(1)

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

    parser.add_argument("--startcmd")
    parser.add_argument("--killcmd")
    parser.add_argument("--monitorinterval");
    parser.set_defaults(**defaults)

    args = parser.parse_args(remaining_argv)

    start_cmd = args.startcmd.split(" ")
    kill_cmd = args.killcmd.split(" ")
    monitor_interval = int(args.monitorinterval)
    wait_for_miner_to_start_time = args.wait_for_miner_to_start_time
    wait_for_miner_to_stop_time = args.wait_for_miner_to_stop_time
    monitor_endpoint = args.monitor_endpoint
    minimum_hashrate = float(args.minimum_hashrate)

    #start

    print "starting"
    print "start_cmd: %s" % start_cmd
    print "kill_cmd: %s" % kill_cmd
    print "monitor_interval: %s" % monitor_interval
    print "wait_for_miner_to_start_time: %s" % wait_for_miner_to_start_time
    print "wait_for_miner_to_stop_time: %s" % wait_for_miner_to_stop_time
    print "monitor_endpoint: %s" % monitor_endpoint

    start_time = current_time()

    #Run loop

    while(True):
        #check hashrate
        print "checking hashrate..."
        hashrate = get_hashrate(monitor_endpoint, "60s")
        if hashrate < minimum_hashrate:
            print "Hashrate found to be %s, lower than the limit %s" % (hashrate, minimum_hashrate)
            print "Killing miner process"
            kill_miner(kill_cmd)
            print "Waiting for miner to stop"
            countdown(wait_for_miner_to_stop_time)
            print "Starting miner process"
            run_miner(start_cmd)
            print "Waiting for miner to start"
            countdown(wait_for_miner_to_start_time)
        else:
            print "hashrate was ok: %s (limit: %s)" % (hashrate, minimum_hashrate)
        print "sleeping for %s seconds" % monitor_interval
        countdown(monitor_interval)

    return(0)

def kill_miner(kill_cmd):
    try:
        subprocess.check_output([kill_cmd], shell=True)
    except subprocess.CalledProcessError as e:
        print "failed to kill '%s' return with error (code %s): %s" % (e.cmd, e.returncode, e.output)

def run_miner(start_cmd):
    # exceptions should cause a failure
    subprocess.check_output(start_cmd, shell=True)

def get_hashrate(endpoint, interval):
    req = urllib2.Request(url=endpoint)
    try:
        urlopen = urllib2.urlopen(req)
        response = urlopen.read()
    #if we get an exception, it's most likely because the miner isn't running
    #in these cases, consider hashrate to be = 0
    except (urllib2.URLError, ValueError):
            return 0
    hashrates = re.search("<th>Totals:</th><td>([^<]*)</td><td>([^<]*)</td><td>([^<]*)</td>", response).group(1, 2, 3)
    hashrate = dict(zip(['10s', '60s', '15m'], hashrates))[interval]
    #hashrate '0' is often represented as a blank space
    if(len(hashrate) <= 0):
        return 0
    return float(hashrate.strip())




if __name__ == "__main__":
    sys.exit(main())
