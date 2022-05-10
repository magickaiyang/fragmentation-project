#!/usr/bin/python3

"""
python3 run.py -n $NUM_ITER -d $DATASET -c $CPU_LIST -p $PAGE_SIZE
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
from dataclasses import dataclass
import numpy as np

@dataclass
class Result:
    avg_latency: int = 0
    throughput: int = 0

def print_avg(summary: list):
    float_summary = [float(x) for x in summary]
    arr = np.array(float_summary)
    avg = np.average(arr)
    std = np.std(arr)
    print("average {}, standard deviation {}\n".format(avg, std))


if __name__ == "__main__":
    curr_path = os.getcwd()
    os.chdir("/h/peili/fragmentation-project/benchbase-mysql")
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, required=True, help='# of iteration')
    parser.add_argument('--d', type=str, required=True, help='specific dataset: tpcc / ycsb / all')
    parser.add_argument('--c', type=str, required=False, help='cpu list')
    parser.add_argument('--p', type=str, required=False, help='page size')
    args = parser.parse_args()

    result_path = os.path.join(os.getcwd(), "result")
    dataset = 'tpcc' if args.d == "tpcc" else 'ycsb'
    config = 'config/mysql/sample_tpcc_config.xml' if args.d == "tpcc" else "config/mysql/sample_ycsb_config.xml"

    output = []

    summary_files = []
    summary_latency = []

    result = []
    avg_latency_summary = []
    throughput_summary = []
    for summary_json_file in sorted(glob.glob("./results/*.summary.json")):
        print(summary_json_file)
        
        with open(summary_json_file) as summary_json:
            res = Result()
            data = json.load(summary_json)
            res.throughput = str(data['Throughput (requests/second)']).strip()
            latency = data['Latency Distribution']
            res.avg_latency = str(latency['Average Latency (microseconds)']).strip()

            result.append(res)
            avg_latency_summary.append(res.avg_latency)
            throughput_summary.append(res.throughput)
    
    print_avg(avg_latency_summary)
    print_avg(throughput_summary)

