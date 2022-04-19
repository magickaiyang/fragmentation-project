#!/usr/bin/python3

"""
python3 run.py -n $NUM_ITER -c $CPU_LIST -p $PAGE_SIZE
"""
import csv
import glob
import json
import os
import sys
import argparse
import subprocess
import json
import glob
import re

MEMCACHED_HEADERS = [
    "ops_per_sec",
    "hits_per_sec",
    "misses_per_sec",
    "avg_latency",
    "p50_latency",
    "p99_latency",
    "p999_Latency",
    "kb_per_sec",
]

result_dir = "./result"


class MemcachedResult:
    dict = {"ops_per_sec": "",
            "hits_per_sec": "",
            "misses_per_sec": "",
            "avg_latency": "",
            "p50_latency": "",
            "p99_latency": "",
            "p999_Latency": "",
            "kb_per_sec": ""
            }

    ops_per_sec, \
    hits_per_sec, misses_per_sec, avg_latency, \
    p50_latency, p99_latency, p999_Latency, kb_per_sec = "", "", "", "", "", "", "", ""

    def __init__(self, ops_per_sec,
                 hits_per_sec, misses_per_sec, avg_latency,
                 p50_latency, p99_latency, p999_Latency, kb_per_sec):
        self.dict = {"ops_per_sec": ops_per_sec,
                     "hits_per_sec": hits_per_sec,
                     "misses_per_sec": misses_per_sec,
                     "avg_latency": avg_latency,
                     "p50_latency": p50_latency,
                     "p99_latency": p99_latency,
                     "p999_Latency": p999_Latency,
                     "kb_per_sec": kb_per_sec
                     }

        self.ops_per_sec, \
        self.hits_per_sec, self.misses_per_sec, self.avg_latency, \
        self.p50_latency, self.p99_latency, self.p999_Latency, self.kb_per_sec \
            = ops_per_sec, hits_per_sec, misses_per_sec, avg_latency, \
              p50_latency, p99_latency, p999_Latency, kb_per_sec
        return

    def save(self):
        return [self.ops_per_sec,
                self.hits_per_sec, self.misses_per_sec, self.avg_latency,
                self.p50_latency, self.p99_latency, self.p999_Latency, self.kb_per_sec]


def execute(cpu_list='0',
            page_size='4k',
            num_iter=1,
            benchmark="",
            cmd=""):
    cmd = 'taskset -c ' + str(cpu_list) + ' ' + cmd
    process = subprocess.run(cmd.split(' '), check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    return output


def to_string(cpu_list='0-7',
              page_size='4k',
              num_iter=1,
              benchmark=""):
    return "{}_{}_{}_{}".format(cpu_list, page_size, num_iter, benchmark)


def save_meminfo(cpu_list='0',
                 page_size='4k',
                 num_iter=1,
                 benchmark=""):
    save_path = os.path.join(result_dir, to_string(cpu_list, page_size, num_iter, benchmark))
    os.system("cp /proc/meminfo " + save_path)
    print("Saving /proc/meminfo to {}".format(save_path))


if __name__ == "__main__":
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, required=True, help='# of iteration')
    parser.add_argument('--c', type=str, required=False, help='cpu list')
    parser.add_argument('--p', type=str, required=False, help='page size')
    args = parser.parse_args()

    os.system("sudo service memcached start")
    for i in range(args.n):
        cmd = "./memtier_benchmark -p 11211 --threads=8 --test-time=20 --ratio=0:1 -P memcache_binary"
        out = execute(cpu_list=args.c, page_size=args.p, num_iter=args.n, benchmark="memtier", cmd=cmd)
        results = []

        res = MemcachedResult("", "", "", "", "", "", "", "")
        for o in out:
            if "Totals" in o:
                data = o.split()
                res.ops_per_sec,\
                res.hits_per_sec, res.misses_per_sec, res.avg_latency,\
                res.p50_latency, res.p99_latency, res.p999_Latency, res.kb_per_sec = data[1:]

        save_meminfo(cpu_list=args.c, page_size=args.p, num_iter=args.n, benchmark="redis")

        res_file = to_string(args.c, args.p, args.n, "benchbase" + args.d)
        if not os.path.exists("./result"):
            os.mkdir("./result")

        with open(os.path.join("./result", res_file), 'w+') as f:
            writer = csv.writer(f)
            writer.writerow(MEMCACHED_HEADERS)
            for line in results:
                writer.writerow(line.save())
