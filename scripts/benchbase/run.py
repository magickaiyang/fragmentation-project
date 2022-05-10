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

BENCHBASE_HEADERS = [
    "dbms_type",
    "dbms_version",
    "benchmark",
    "goodput",
    "throughput",
    "latency",
    "max_latency",
    "median_latency",
    "avg_latency",
    "latency_25",
    "latency_75",
    "latency_90",
    "latency_95",
    "latency_99"
    "cpu_list",
    "page_size"
]


def to_string(cpu_list='0',
              page_size='4k',
              num_iter=1,
              benchmark=""):
    return "{}_{}_{}_{}".format(cpu_list, page_size, num_iter, benchmark)


class BenchbaseResult:
    dict = {"dbms_type": "",
            "dbms_version": "",
            "benchmark": "",
            "goodput": "",
            "throughput": "",
            "latency": "",
            "max_latency": "",
            "median_latency": "",
            "avg_latency": "",
            "latency_25": "",
            "latency_75": "",
            "latency_90": "",
            "latency_95": "",
            "latency_99": ""
            }
    dbms_type, dbms_version, benchmark, \
    goodput, throughput, latency, \
    max_latency, median_latency, avg_latency, \
    latency_25, latency_75, latency_90, \
    latency_95, latency_99 = "", "", "", "", "", "", "", "", "", "", "", "", "", ""

    def __init__(self, dbms_type,
                 dbms_version, benchmark, goodput, throughput, latency, max_latency,
                 median_latency, avg_latency, latency_25, latency_75, latency_90,
                 latency_95, latency_99):
        self.dbms_type = ""
        self.dbms_version = ""

        self.dict = {
            "dbms_type": dbms_type,
            "dbms_version": dbms_version,
            "benchmark": benchmark,
            "goodput": goodput,
            "throughput": throughput,
            "latency": latency,
            "max_latency": max_latency,
            "median_latency": median_latency,
            "avg_latency": avg_latency,
            "latency_25": latency_25,
            "latency_75": latency_75,
            "latency_90": latency_90,
            "latency_95": latency_95,
            "latency_99": latency_99
        }
        return

    def save(self):
        return [self.dbms_type, self.dbms_version, self.benchmark,
                self.goodput, self.throughput, self.latency,
                self.max_latency, self.median_latency, self.avg_latency,
                self.latency_25, self.latency_75, self.latency_90,
                self.latency_95, self.latency_99]


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

    for i in range(args.n):
        proc = subprocess.check_output(
            ['java', '-jar', 'benchbase.jar', '-b', dataset, '-c', config, '--create=true', '--load=true',
             '--execute=true'])
        out = proc.decode('utf-8').split('\n')
        print('*********************************************************************')
        for o in out:
            if "Rate limited reqs/s:" in o:
                res = re.split(": | = |, ", o.split(" - ")[1])
                throughput, goodput = "", ""
            if "Output summary data" in o:
                summary_file = os.path.join(result_path, o.split()[-1].strip())
                summary_files.append(summary_file)
        if args.d == "all":
            proc = subprocess.check_output(
                ['java', '-jar', 'benchbase.jar', '-b', 'tpcc', '-c', 'config/mysql/sample_tpcc_config.xml',
                 '--create=true', '--load=true', '--execute=true'])
            out = proc.decode('utf-8').split('\n')
            print('*********************************************************************')
            for o in out:
                if "Rate limited reqs/s:" in o:
                    res = re.split(": | = |, ", o.split(" - ")[1])
                if "Output summary data" in o:
                    summary_file = os.path.join(result_path, o.split()[-1].strip())
                    summary_files.append(summary_file)

    result = []

    for summary_json_file in sorted(glob.glob("./results/*.summary.json")):
        avg_latency_summary = []
        throughput_summary = []

        with open(summary_json_file) as summary_json:
            data = json.load(summary_json)

            res = BenchbaseResult()
            res.dbms_type = str(data['DBMS Type']).strip()
            res.dbms_version = str(data['DBMS Version']).strip()
            res.benchmark = str(data['Benchmark Type']).strip()
            res.goodput = str(data['Goodput (requests/second)']).strip()
            res.throughput = str(data['Throughput (requests/second)']).strip()
            latency = data['Latency Distribution']
            latency_data = res.latency
            res.max_latency = str(latency_data['Maximum Latency (microseconds)']).strip()
            res.median_latency = str(latency_data['Median Latency (microseconds)']).strip()
            res.min_latency = str(latency_data['Minimum Latency (microseconds)']).strip()
            res.latency_25 = str(latency_data['25th Percentile Latency (microseconds)']).strip()
            res.latency_90 = str(latency_data['90th Percentile Latency (microseconds)']).strip()
            res.latency_95 = str(latency_data['95th Percentile Latency (microseconds)']).strip()
            res.latency_99 = str(latency_data['99th Percentile Latency (microseconds)']).strip()
            res.latency_75 = str(latency_data['75th Percentile Latency (microseconds)']).strip()
            res.avg_latency = str(latency_data['Average Latency (microseconds)']).strip()

            output.append((res.benchmark, res.throughput, res.goodput))
            summary_latency.append((res.max_latency, res.median_latency, res.min_latency, res.avg_latency,
                                    res.latency_25, res.latency_75, res.latency_90, res.latency_95, res.latency_99))
            result.append(res)
            avg_latency_summary.append(res.avg_latency)
            throughput_summary.append(res.throughput_summary)

    print_avg(avg_latency_summary)
    print_avg(throughput_summary)
    os.chdir(curr_path)
    for res in result:
        res_file = to_string(args.c, args.p, args.n, "benchbase" + args.d)
        if not os.path.exists("./result"):
            os.mkdir("./result")

        with open(os.path.join("./result", res_file), 'w+') as f:
            writer = csv.writer(f)
            writer.writerow(BENCHBASE_HEADERS)
            for line in result:
                writer.writerow(line.save())

    for benchmark, throughput, goodput in output:
        print(benchmark + ', throughput: ' + throughput + ", goodput: " + goodput, end='\n')

    for max_latency, median_latency, min_latency, avg_latency, latency_25, latency_75, latency_90, latency_95, latency_99 in summary_latency:
        print(max_latency + ", " + median_latency + ", " + min_latency + ", " + avg_latency + ", " \
                  + latency_25 + ", " + latency_75 + ", " + latency_90 + ", " + latency_95 + ", " + latency_99)
