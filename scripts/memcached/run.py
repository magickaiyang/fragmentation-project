#!/usr/bin/python3

"""
python3 run.py -n $NUM_ITER -c $CPU_LIST -p $PAGE_SIZE
"""
import argparse
import csv
import glob
import json
import os
from dataclasses import dataclass
import numpy as np

MEMCACHED_HEADERS = [
    "ops_per_sec",
    "hits_per_sec",
    "misses_per_sec",
    "avg_latency",
    "min_latency",
    "max_latency",
    "p50_latency",
    "p99_latency",
    "p999_Latency",
    "kb_per_sec",
]


@dataclass
class Config:
    cpu_list: str = '0-7'
    page_size: str = '4k'
    num_iter: int = 1
    num_req: int = 10000
    num_thread: int = 1
    benchmark: str = 'redis'

    def to_string(self):
        return "{}_{}_{}_{}_{}_{}" \
            .format(self.cpu_list, self.page_size, self.num_iter, self.num_req, self.num_thread, self.benchmark)


@dataclass
class Result:
    ops_per_sec: float = 0
    hits_per_sec: float = 0
    misses_per_sec: float = 0
    latency: float = 0
    avg_latency: float = 0
    min_latency: float = 0
    max_latency: float = 0
    p50_latency: float = 0
    p99_latency: float = 0
    p999_Latency: float = 0


p = Config()

result_dir = "./memcached_result"


def get_filename():
    return os.path.join(result_dir, p.to_string())


def execute(path='memcached_result_', iter=1):
    taskset_cmd = 'taskset -c ' + p.cpu_list + ' ./memtier_benchmark' + ' --threads ' + str(
        p.num_thread) + ' -n ' + str(
        p.num_req) + '--test-time=20 -P memcache_binary'
    save_path = os.path.join(result_dir, path + p.to_string() + "_" + '#' + str(iter)) + ".json"
    os.system(taskset_cmd + ' ---json-out-file=' + save_path)


def save_meminfo():
    save_path = get_filename() + "_meminfo"
    os.system("cp /proc/meminfo " + save_path)
    print("Saving /proc/meminfo to {}".format(save_path))

def print_avg(summary: list):
    arr = np.array(summary)
    avg = np.average(arr)
    std = np.std(arr)
    print("average {}, standard deviation {}\n".format(avg, std))

def get_result():
    results = {}

    ops_per_sec_summary = []
    hits_per_sec_summary = []
    misses_per_sec_summary = []
    latency_summary = []
    avg_latency_summary = []
    min_latency_summary = []
    max_latency_summary = []
    p50_latency_summary = []
    p99_latency_summary = []
    p999_latency_summary = []

    for summary_file in sorted(glob.glob(result_dir + "/*.json")):
        with open(summary_file) as summary:
            data = json.load(summary)
            res = Result()

            total = data['ALL STATS']['Totals']
            res.ops_per_sec = float(str(total['Ops/sec']))
            res.hits_per_sec = float(str(total['Hits/sec']))
            res.misses_per_sec = float(str(total['Misses/sec']))
            res.latency = float(str(total['Latency']))
            res.avg_latency = float(str(total['Average Latency']))
            res.min_latency = float(str(total['Min Latency']))
            res.max_latency = float(str(total['Max Latency']))
            percentile_latencies = total['Percentile Latencies']
            res.p50_latency = percentile_latencies['p50.00']
            res.p99_latency = percentile_latencies['p99.00']
            res.p999_latency = percentile_latencies['p99.90']

            results[os.path.basename(summary_file)] = res

    print(results)

    print("ops per sec: ")
    print_avg(ops_per_sec_summary)
    print("hits per sec: ")
    print_avg(hits_per_sec_summary)
     print("misses per sec: ")
    print_avg(misses_per_sec_summary)
    print("avg latency: ")
    print_avg(avg_latency_summary)
    print("min latency: ")
    print_avg(min_latency_summary)
    print("max latency: ")
    print_avg(max_latency_summary)
    print("p50 latency: ")
    print_avg(p50_latency_summary)
    print("p99 latency: ")
    print_avg(p99_latency_summary)
    print("p999 latency: ")
    print_avg(p999_latency_summary)
    
    return results


def get_rows(results: dict, key):
    result = results[key]
    return [key, result.throughput, result.avg_latency, result.min_latency,
            result.p50_latency, result.p90_latency, result.p95_latency, result.max_latency]


def save_result(results: dict):
    res_file = get_filename() + ".csv"
    for result in results.keys():
        print(result)
        if not os.path.exists(res_file):
            with open(res_file, 'w+') as f:
                writer = csv.writer(f)
                writer.writerow(MEMCACHED_HEADERS)
        with open(res_file, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(get_rows(results, result))
    return


if __name__ == "__main__":
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--iter', type=int, required=True, help='# of iteration')
    parser.add_argument('--c', type=str, required=False, help='cpu list')
    parser.add_argument('--p', type=str, required=False, help='page size')
    parser.add_argument('-n', type=str, required=False, help='Total number of requests (default 100000)')
    parser.add_argument('--threads', type=int, required=False, help='Enable multi-thread mode')
    parser.add_argument('--mode', type=str, required=False, help='test mode (RD, WR, RDWR)')
    args = parser.parse_args()

    os.system("sudo service memcached start")

    if not os.path.exists(result_dir):
        os.mkdir(result_dir)

    for i in range(args.iter):
        execute(iter=i)

    results = get_result()
    save_result(results)
