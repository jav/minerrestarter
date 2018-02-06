#!/usr/bin/env python3

#Made by Javier Ubillos, javier@ubillos.org, github.com/jav
#For donations: Monero: 45zBbvea3Hs2xR9AWcQkFy2BnPtoNSrDb59hTftst14qjeEsnzC9SXFXAVJBo3wh1EQzMUYDsGLggFox8hfmwtbxRQzq1Fm

import argparse
import configparser
import ctypes
import json
import os
import platform
import psutil
import re
import sys
import subprocess
import time
import urllib2

current_time = lambda: int(round(time.time() * 1000))

def is_windows_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

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

def get_config(argv):
    conf_parser = argparse.ArgumentParser(        )
    conf_parser.add_argument("-c", "--conf-file",
                        help="Specify config file", default="config.json", metavar="FILE")

    conf_parser.add_argument("-n", "--noop",
                        help="Don't do anything, just print out what's detected and what the expected action would be.",
                        default=False
                        )
    args = vars(conf_parser.parse_args())

    #Config file _must_ exist
    assert(os.path.isfile(args['conf_file']))
    config = json.load(open(args['conf_file']))

    config['noop'] = args.get('noop', False)

    config['start_cmd'] = args.get('start_cmd', config['start_cmd'])
    config['kill_cmd'] = args.get('kill_cmd', config['kill_cmd'])
    config['process_name'] = args.get('process_name', config['process_name'])
    config['monitor_interval'] = int(args.get('monitor_interval', config['monitor_interval']))
    config['wait_for_miner_to_start_time'] = int(args.get('wait_for_miner_to_start_time', config['wait_for_miner_to_start_time']))
    config['wait_for_miner_to_stop_time'] = int(args.get('wait_for_miner_to_stop_time', config['wait_for_miner_to_stop_time']))
    config['monitor_endpoint'] = str(args.get('monitor_endpoint', config['monitor_endpoint']))
    config['minimum_hashrate'] = int(args.get('minimum_hashrate', config['minimum_hashrate']))

    return config

def kill_miner(kill_cmd, noop=False):
    if(noop):
        print("Kill miner.")
        return
    try:
        subprocess.call(kill_cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("failed to kill '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

def run_miner(start_cmd, noop=False):
    if(noop):
        print("Start miner.")
        return
    # exceptions should cause a failure
    print("Running {}".format(start_cmd))
    subprocess.call(start_cmd, shell=True)

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

def main(config):


    print("!!! START !!!")
    print("Config: {}".format(json.dumps(config, indent=4, sort_keys=True)))

    start_time = current_time()

    hashrate = config['minimum_hashrate']
    #LOGIC LOOP
    while(True):
        # Check if miner is running
        if(not is_miner_process_running(config['process_name'])):
            print("Miner process is not running, starting the process.")
            run_miner(config['start_cmd'], config['noop'])
            countdown(config['wait_for_miner_to_start_time'])
            continue
        else:
            print("Miner is running.")
        #check hashrate

        if(is_miner_process_running(config['process_name'])):
            hashrate = get_hashrate(config['monitor_endpoint'], "60s")
            print("Miner process is running, and reporting hashrate %s.")

        if hashrate < config['minimum_hashrate']:
            print("Hashrate lower than minimum_hashrate: {} => Will restart miner.".format(config['minimum_hashrate']))
            kill_miner(config['kill_cmd'], config['noop'])
            print("Waiting for miner to stop")
            countdown(config['wait_for_miner_to_stop_time'], lambda : not is_miner_process_running(config['process_name']))
            print("Starting miner process")
            run_miner(config['start_cmd'], config['noop'])
            print("Waiting for miner to start before starting to monitor")
            countdown(config['wait_for_miner_to_start_time'])
            continue
        else:
            print("hashrate was ok: {} (limit: {})".format(hashrate, config['minimum_hashrate']))

        print("sleeping for {} seconds before checking again...".format(config['monitor_interval']))
        countdown(config['monitor_interval'])

    return(0)

if __name__ == "__main__":

    config = get_config(sys.argv)
    if platform.system() == "Linux" or is_windows_admin():
        sys.exit(main(config))
    else:
        # Re-run the program with admin rights
        print("Asking for admin access... (will spawn another window if access granted)")
        print("DEBUG: sys.executable: {}".format(sys.executable))
        print("DEBUG: __file__: {}".format(__file__))

        ## Call self, as admin
        ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__), None, 1)
