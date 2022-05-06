# !/usr/bin/python3

"""
python3 run.py --iter $NUM_ITER
"""
import argparse
import csv
import glob
from operator import ne
import os
from dataclasses import dataclass
import sys
import numpy as np
import decimal

HEADER = [
    "config",
    "time",
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
    benchmark : str = ""
    time: int = 0  # request per second


p = Config()

result_dir = "./result"


def get_filename():
    return os.path.join(result_dir, p.to_string())


# def execute(iter=1):
#     taskset_cmd = 'taskset -c ' + p.cpu_list
#     os.system(taskset_cmd + " make run")
#     os.system("mv output.log ./result/output{}.log".format(iter))


def save_meminfo():
    save_path = get_filename() + "_meminfo"
    os.system("cat /proc/meminfo > " + save_path)
    print("Saving /proc/meminfo to {}".format(save_path))


def get_result():
    results = {}
    
    for summary_file in sorted(glob.glob(result_dir + "/*.log")):
        with open(summary_file) as summary:
            irofile = iter(summary)
            res = Result()
            for line in irofile:
                if "Benchmark:" in line:
                    res.benchmark = line.split(":")[1].strip()
                elif "finish" in line or \
                    "computing connected component" in line \
                        or "Shortest Path:" in line\
                        or "computing kCore" in line:
                    while line:
                        line = next(irofile)
                        if "time:" in line:
                            res.time = line.split("== time:")[1].split()[0].strip()
                            if "e" in res.time:
                                tmp = decimal.Decimal(res.time)
                            else:
                                tmp = res.time
                            if res.benchmark in results:
                                results[res.benchmark].append(float(tmp))
                            else:
                                results[res.benchmark] = [float(tmp)]
                            break
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

    if not os.path.exists(result_dir):
        os.mkdir(result_dir)

    save_meminfo()
    for i in range(args.iter):
        execute(iter=i)

    results = get_result()
    for key in results:
        arr = np.array(results[key])
        avg = np.average(arr)
        std = np.std(arr)
        print(key + ":")
        print(avg, std)
        print("\n")
    print(results)
