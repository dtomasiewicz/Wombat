#!/usr/bin/env python

from argparse import ArgumentParser
from configparser import SafeConfigParser as ConfigParser
from postgresql import driver

from wserver.realmserver import RealmServer

parser = ArgumentParser()
parser.add_argument('configfile')
args = parser.parse_args()

config = ConfigParser()
config.readfp(open(args.configfile))
srvcfg = dict(config.items('server'))
datacfg = dict(config.items('datasource'))

data = driver.connect(**datacfg)

server = RealmServer(data)
try:
  server.start(
      host=srvcfg['host'],
      cport=int(srvcfg['control_port']),
      nport=int(srvcfg['notify_port']),
      backlog=int(srvcfg['backlog']),
      ntimeout=float(srvcfg['notify_timeout']),
      pollrate=float(srvcfg['poll_rate'])
  )
except KeyboardInterrupt:
  pass
