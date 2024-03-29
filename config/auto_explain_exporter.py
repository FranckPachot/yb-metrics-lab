#!/usr/bin/env python 

import os
import sys
import re
from time import sleep

from prometheus_client import start_http_server, Gauge


def main():
    start_http_server(8080)
    gather_metrics()

def gather_metrics():
    print("collecting httpd metrics")
    regex = r'^\t[ ->]*(.*) on ([^ "]+|"[^"]+").* (\(cost=([0-9.]+)\.\.([0-9.]+) rows=([0-9]+) width=([0-9]+)\) )\(actual time=([0-9.]+)\.\.([0-9.]+) rows=([0-9]+) loops=([0-9]+)\).*'
    explain_node_rows = Gauge('explain_node_total_rows', 'auto_explain rows*loop', ["node"])
    explain_node_exec = Gauge('explain_node_total_exec', 'auto_explain loop', ["node"])
    for line in follow_log( sys.argv[1] ):
        match = re.match(regex, line)
        if match:
            print(f"node: {line}")
            explain_node_rows.labels(node= (match.group(1)+" on "+match.group(2)) ).inc( (int(match.group(10)) * int(match.group(11)) ) )
            explain_node_exec.labels(node= (match.group(1)+" on "+match.group(2)) ).inc(                         int(match.group(11))   )


def follow_log(file):
    print(f"Reading {file}")
    with open(file, 'r') as f:
        f.seek(0, os.SEEK_END)
        # infinite loop
        while True:
            line = f.readline()
            if not line:
                sleep(0.1)
                continue

            yield line


if __name__ == '__main__':
    main()
