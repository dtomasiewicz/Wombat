#!/usr/bin/env python

from argparse import ArgumentParser

from wclient.realmclient import RealmClient

parser = ArgumentParser(description="Combat client application.")
parser.add_argument('-g', action='store_true')
parser.add_argument('-r', default='127.0.0.1')
parser.add_argument('-c', type=int, default=10000)
parser.add_argument('-n', type=int, default=10001)
args = parser.parse_args()
client = RealmClient()
client.start(args.r, args.c, args.n, not args.g)

if args.g:
  from wclient.gui import ClientUI
  ClientUI(client).start()
else:
  from wclient.cli import ClientShell
  ClientShell(client).cmdloop()
