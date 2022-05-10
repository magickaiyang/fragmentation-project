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
    "config",
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
    num_req: int = 100000
    num_thread: int = 1
    benchmark: str = 'memcached'

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
    taskset_cmd = 'taskset -c ' + p.cpu_list + ' /h/peili/fragmentation-project/memtier_benchmark/memtier_benchmark -p 11211' + ' --threads=' + str(
        p.num_thread) + ' --requests=' + str(
        p.num_req) + ' -P memcache_binary'
    print(taskset_cmd)
    save_path = os.path.join(result_dir, path + p.to_string() + "_" + '#' + str(iter)) + ".json"
    os.system(taskset_cmd + ' --json-out-file=' + save_path)


def save_meminfo():
    save_path = get_filename() + "_meminfo"
    os.system("cp /proc/meminfo " + save_path)
    print("Saving /proc/meminfo to {}".format(save_path))

def print_avg(summary: list):
    float_summary = [float(x) for x in summary]
    arr = np.array(float_summary)
    avg = np.average(arr)
    std = np.std(arr)
    print("average {}, standard deviation {}\n".format(avg, std))

def get_single_result(res_json):
    res = Result()
    res.ops_per_sec = float(str(res_json['Ops/sec']))
    res.hits_per_sec = float(str(res_json['Hits/sec']))
    res.misses_per_sec = float(str(res_json['Misses/sec']))
    res.latency = float(str(res_json['Latency']))
    res.avg_latency = float(str(res_json['Average Latency']))
    res.min_latency = float(str(res_json['Min Latency']))
    res.max_latency = float(str(res_json['Max Latency']))
    percentile_latencies = res_json['Percentile Latencies']
    res.p50_latency = percentile_latencies['p50.00']
    res.p99_latency = percentile_latencies['p99.00']
    res.p999_latency = percentile_latencies['p99.90']

    return res


def get_result():
    sets_results = {}
    gets_results = {}
    total_results = {}

    sets_avg_latency_summary = []
    gets_avg_latency_summary = []
    total_avg_latency_summary = []

    for summary_file in sorted(glob.glob(result_dir + "/*.json")):
        with open(summary_file) as summary:
            data = json.load(summary)

            sets = data['ALL STATS']['Sets']
            gets = data['ALL STATS']['Gets']
            total = data['ALL STATS']['Totals']

            sets_result = get_single_result(sets)
            sets_avg_latency_summary.append(sets_result.avg_latency)

            
            gets_result = get_single_result(gets)
            gets_avg_latency_summary.append(gets_result.avg_latency)

            total_result = get_single_result(total)
            total_avg_latency_summary.append(total_result.avg_latency)

            sets_results[os.path.basename(summary_file)] = sets_result
            gets_results[os.path.basename(summary_file)] = gets_result
            total_results[os.path.basename(summary_file)] = total_result

    # print(sets_results)
    # print(gets_results)
    # print(total_results)

    print("set: \n")
    print_avg(sets_avg_latency_summary)
    print("get: \n")
    print_avg(gets_avg_latency_summary)
    print("total: \n")
    print_avg(total_avg_latency_summary)

    return sets_results, gets_results, total_results


def get_rows(results: dict, key):
    res = results[key]
    return [key, res.ops_per_sec, res.hits_per_sec, res.misses_per_sec, res.latency, res.avg_latency, res.min_latency,
            res.max_latency, res.p50_latency, res.p99_latency, res.p999_latency, ]


def save_result(results: dict, method: str):
    res_file = get_filename() + method + ".csv"
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

    if not os.path.exists(result_dir):
        os.mkdir(result_dir)

    for i in range(args.iter):
        execute(iter=i)

    sets_results, gets_results, total_results = get_result()
    save_result(sets_results, "set")
    save_result(gets_results, "get")
    save_result(total_results, "total")
