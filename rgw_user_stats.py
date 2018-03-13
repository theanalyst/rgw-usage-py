#!/usr/bin/env python

from __future__ import print_function
import subprocess
import argparse
import json

DEFAULT_STATS = {
                    "entries" : 0,
                    "total_bytes": 0,
                    "total_bytes_rounded":0
                }

class RGWAdmin(object):
    def __init__(self, name=None):
        self.name = name
        self.cmd_args = ['radosgw-admin']
        if self.name:
            self.cmd_args.extend(['--name', self.name])

    def exec_cmd(self, args):
        try:
            cmd_args = self.cmd_args
            cmd_args.extend(args)
            out = subprocess.check_output(cmd_args)
            return json.loads(out.decode())
        except Exception as e:
            print (' '.join(cmd_args), "encountered exception: ",  str(e))

def parse_bucket_stats(rgw_admin, uid):
    stats = rgw_admin.exec_cmd(['bucket','stats'])
    # TODO cache this in a file for subsequent calls
    user_stats = dict()
    for bucket_stat in stats:
        try:
            owner = bucket_stat['owner']
            if owner not in user_stats:
                user_stats[owner] = {
                    "entries" : 0,
                    "total_bytes": 0,
                    "total_bytes_rounded":0
                }
        except KeyError:
            # ignore if no owner
            continue

        stats = bucket_stat.get('usage',{})
        for _, kv in stats.items():
            user_stats[owner]["entries"] += kv.get('num_objects', 0)
            user_stats[owner]["total_bytes"] += kv.get('size', 0)
            user_stats[owner]["total_bytes_rounded"] = kv.get('size_kb',0)*1024


    if uid in user_stats:
        return user_stats[uid]

    return DEFAULT_STATS

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='aggregate bucket usage stats')
    parser.add_argument('--uid', type=str, help='user id')
    parser.add_argument('--name', type=str, help='rgw name to connect to',
                        default='client.admin')

    args = parser.parse_args()
    rgw_admin = RGWAdmin(args.name)
    print(parse_bucket_stats(rgw_admin, args.uid))
