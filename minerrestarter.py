#!/usr/bin/env python2

#Made by Javier Ubillos, javier@ubillos.org, github.com/jav
#For donations: Monero: 45zBbvea3Hs2xR9AWcQkFy2BnPtoNSrDb59hTftst14qjeEsnzC9SXFXAVJBo3wh1EQzMUYDsGLggFox8hfmwtbxRQzq1Fm

import argparse
import ConfigParser
import json
import os
import psutil
import re
import sys
import subprocess
import time
import urllib2

current_time = lambda: int(round(time.time() * 1000))
def countdown(from_time, func=None):
  number=''
  for i in xrange(int(from_time),-1,-1):
    for _ in xrange(len(number)):
      sys.stdout.write('\b')
      if func is not None:
          if func():
              return
    number=str(i)+' '
    sys.stdout.write(number)
    sys.stdout.flush()
    time.sleep(1)

def main(argv=None):
    # Do argv default this way, as doing it in the functional
    # declaration sets it at compile time.
    if argv is None:
        argv = sys.argv


    conf_parser = argparse.ArgumentParser(        )
    conf_parser.add_argument("-c", "--conf-file",
                        help="Specify config file", default="config.json", metavar="FILE")

    conf_parser.add_argument("-n", "--noop",
                        help="Don't do anything, just print out what's detected and what the expected action would be.",
                        )
    args = vars(conf_parser.parse_args())

    #Config file _must_ exist
    assert(os.path.isfile(args['conf_file']))
    config = json.load(open(args['conf_file']))

    start_cmd = args.get('start_cmd', config['start_cmd'])
    kill_cmd = args.get('kill_cmd', config['kill_cmd'])
    process_name = args.get('process_name', config['process_name'])
    monitor_interval = int(args.get('monitor_interval', config['monitor_interval']))
    wait_for_miner_to_start_time = int(args.get('wait_for_miner_to_start_time', config['wait_for_miner_to_start_time']))
    wait_for_miner_to_stop_time = int(args.get('wait_for_miner_to_stop_time', config['wait_for_miner_to_stop_time']))
    monitor_endpoint = str(args.get('monitor_endpoint', config['monitor_endpoint']))
    minimum_hashrate = int(args.get('minimum_hashrate', config['minimum_hashrate']))

    #start
    print "START"
    print "start_cmd: %s" % start_cmd
    print "kill_cmd: %s" % kill_cmd
    print "proces_name: %s" % process_name
    print "monitor_interval: %s" % monitor_interval
    print "wait_for_miner_to_start_time: %s" % wait_for_miner_to_start_time
    print "wait_for_miner_to_stop_time: %s" % wait_for_miner_to_stop_time
    print "monitor_endpoint: %s" % monitor_endpoint

    start_time = current_time()

    # Check if miner is running
    if(not is_miner_process_running(process_name)):
        run_miner(start_cmd)

    #Run loop

    while(True):
        #check hashrate
        print "checking hashrate..."
        hashrate = get_hashrate(monitor_endpoint, "60s")
        print "Hashrate found to be %s" % (hashrate, )

        if hashrate < minimum_hashrate:
            print "Hashrate lower than minimum_hashrate: %s" % (minimum_hashrate, )
            print "Killing miner process"
            kill_miner(kill_cmd)
            print "Waiting for miner to stop"
            countdown(wait_for_miner_to_stop_time, lambda : not is_miner_process_running(process_name))
            print "Starting miner process"
            run_miner(start_cmd)
            print "Waiting for miner to start before starting to monitor"
            countdown(wait_for_miner_to_start_time)
        else:
            print "hashrate was ok: %s (limit: %s)" % (hashrate, minimum_hashrate)
            print "sleeping for %s seconds" % monitor_interval
        countdown(monitor_interval)

    return(0)

def kill_miner(kill_cmd):
    try:
        subprocess.check_output(kill_cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print "failed to kill '%s' return with error (code %s): %s" % (e.cmd, e.returncode, e.output)

def run_miner(start_cmd):
    # exceptions should cause a failure
    subprocess.check_output(start_cmd, shell=True)

def is_miner_process_running(miner_process_name):
    return miner_process_name in (p.name() for p in psutil.process_iter())

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
