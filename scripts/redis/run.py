# !/usr/bin/python3

"""
python3 run.py --iter $NUM_ITER
"""
import argparse
import csv
import glob
import os
from dataclasses import dataclass
import numpy as np

RDONLY = 0
WRONLY = 1
RDWR = 2

HEADER = [
    "config",
    "throughput",
    "avg_latency",
    "min_latency",
    "max_latency",
    "p50_latency",
    "p90_latency",
    "p95_latency",
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
    throughput: int = 0  # request per second
    avg_latency: int = 0
    min_latency: int = 0
    max_latency: int = 0
    p50_latency: int = 0
    p90_latency: int = 0
    p95_latency: int = 0


p = Config()

result_dir = "./redis_result"


def get_filename():
    return os.path.join(result_dir, p.to_string())


def execute(mode, path='redis_result_', iter=1):
    taskset_cmd = 'taskset -c ' + p.cpu_list + ' redis-benchmark' + ' --threads ' + str(p.num_thread) + ' -n ' + str(
        p.num_req)
    if mode == WRONLY:
        for m in ['RPUSH', 'SPOP', 'RPOP']:
            new_cmd = taskset_cmd + ' -t ' + m
            print(new_cmd)
            save_path = os.path.join(result_dir, path + p.to_string() + "_" + m + '#' + str(iter)) + ".log"
            os.system(new_cmd + ' > ' + save_path)
    elif mode == RDONLY:
        for m in ['GET', 'LRANGE']:
            new_cmd = taskset_cmd + ' -t ' + m
            print(new_cmd)
            save_path = os.path.join(result_dir, path + p.to_string() + "_" + m + '#' + str(iter)) + ".log"
            os.system(new_cmd + ' > ' + save_path)
    elif mode == RDWR:
        for m in ['RPUSH', 'SPOP', 'RPOP', 'GET', 'LRANGE']:
            new_cmd = taskset_cmd + ' -t ' + m
            print(new_cmd)
            save_path = os.path.join(result_dir, path + p.to_string() + "_" + m + '#' + str(iter)) + ".log"
            os.system(new_cmd + ' > ' + save_path)


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

    throughput_summary = []
    avg_latency_summary = []
    min_latency_summary = []
    p50_latency_summary = []
    p90_latency_summary = []
    p95_latency_summary = []
    max_latency_summary = []

    for summary_file in sorted(glob.glob(result_dir + "/*.log")):
        with open(summary_file) as summary:
            irofile = iter(summary)
            res = Result()
            for line in irofile:
                if "throughput summary" in line:
                    res.throughput = line.split(":")[1].strip().split(" ")[0]
                    throughput_summary.append(res.throughput)
                elif "avg       min       p50       p95       p99       max" in line:
                    line = next(irofile)
                    res.avg_latency, res.min_latency, res.p50_latency, \
                    res.p90_latency, res.p95_latency, res.max_latency = line.split()
                    results[os.path.basename(summary_file)] = res
                    avg_latency_summary.append(res.avg_latency)
                    min_latency_summary.append(res.min_latency)
                    p50_latency_summary.append(res.p50_latency)
                    p90_latency_summary.append(res.p90_latency)
                    p95_latency_summary.append(res.p95_latency)
                    max_latency_summary.append(res.max_latency)
    print(results)

    print("throughput: ")
    print_avg(throughput_summary)
    print("avg latency: ")
    print_avg(avg_latency_summary)
    print("min latency: ")
    print_avg(min_latency_summary)
    print("p50 latency: ")
    print_avg(p50_latency_summary)
    print("p90 latency: ")
    print_avg(p90_latency_summary)
    print("p95 latency: ")
    print_avg(p95_latency_summary)
    print("max latency: ")
    print_avg(max_latency_summary)
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
                writer.writerow(HEADER)
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

    # Redis Benchmark’s three most kernel-intensive write tests, responsible for inserting
    # (RPUSH) or deleting (SPOP, RPOP)

    # two most kernel-intensive read tests
    # responsible for returning the value of a key (GET) and returning a range of values for a key (LRANGE)

    if not os.path.exists(result_dir):
        os.mkdir(result_dir)

    save_meminfo()
    for i in range(args.iter):
        execute(mode=WRONLY if args.mode == 'WR' else RDONLY if args.mode == 'RD' else RDWR, iter=i)

    results = get_result()
    save_result(results)
